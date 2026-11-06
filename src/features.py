"""Behavioral features and the shared model-input helper (owner: Supriye; tasks S9-S16).

Build a feature table from the repo root, after `python -m src.labels`:
    python -m src.features v0   # S9: 100-user sample, 7 basic counts -> features_v0.parquet
    python -m src.features v1   # S10-S16: every user, all behavior groups -> features_v1.parquet
One row per user-day in TEAM_PLAN 5.1 format, in data/processed/. v1 also writes
results/tables/v1_behavior_checks.csv. The first v1 run makes one pass over the 28M-row web log
and caches it in data/processed/http_user_day_domain.parquet.

Every model turns a feature table into inputs with the same helper (TEAM_PLAN 5.5):
    from src.features import get_model_matrix
    X_train, y_train, feature_names = get_model_matrix(df, split="train")
"""
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.config import (
    COMPANY_DOMAIN, EMAIL_COUNT_PERSONAL, HTTP_CATEGORIES, PROCESSED_DIR, RANDOM_STATE,
    TABLES_DIR, V0_N_INSIDERS, V0_N_NORMAL, WORK_END_HOUR, WORK_START_HOUR,
)
from src.data_loader import (
    iter_http_batches, load_device, load_email, load_file, load_insiders, load_ldap, load_logon,
    load_psychometric, recipient_domains,
)
from src.labels import assign_split

KEY = ["user", "date"]
META_COLUMNS = ["user", "date", "split", "label", "scenario", "insider", "role", "department"]
FEATURE_PREFIXES = ("f_", "z_user_", "z_peer_", "new_")
# f_* features that are not counts, so get_model_matrix() leaves them unlogged.
NOT_COUNTS = {
    "f_first_logon_hour", "f_last_logoff_hour", "f_work_duration", "f_afterhours_ratio",
    "f_weekend", "f_email_size", "f_ctx_O", "f_ctx_C", "f_ctx_E", "f_ctx_A", "f_ctx_N",
}


# ---------------------------------------------------------------- shared model input (TEAM_PLAN 5.5)
def feature_columns(df: pd.DataFrame) -> list:
    """Every model-input column: f_*, z_user_*, z_peer_*, new_*."""
    return [c for c in df.columns if c.startswith(FEATURE_PREFIXES)]


def get_model_matrix(df, split=None, columns=None):
    """Return X (DataFrame), y (Series), feature_names.

    - split: 'train' / 'val' / 'test' / None (all rows)
    - columns: list of feature columns to use (default: every f_*, z_user_*, z_peer_*, new_* column)
    Applies log1p to f_* count columns and fills missing values with 0.
    X keeps the row index of `df`, so scores can be written back next to the keys.
    """
    rows = df if split is None else df[df["split"] == split]
    cols = list(columns) if columns is not None else feature_columns(df)
    not_features = [c for c in cols if not c.startswith(FEATURE_PREFIXES)]
    if not_features:
        raise ValueError(f"not model inputs (TEAM_PLAN 5.1): {not_features}")
    X = rows[cols].astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    counts = [c for c in cols if c.startswith("f_") and c not in NOT_COUNTS]
    X[counts] = np.log1p(X[counts].clip(lower=0))
    return X, rows["label"].astype(int), cols


# ---------------------------------------------------------------- shared helpers
def is_after_hours(hour: pd.Series) -> pd.Series:
    """Outside working hours as set in src/config.py (PROVISIONAL until Supriye decides, S11)."""
    return (hour < WORK_START_HOUR) | (hour >= WORK_END_HOUR)


def per_user_day(events: pd.DataFrame, **aggregations) -> pd.DataFrame:
    """Aggregate an event table to (user, date), where date is the event's `day` (midnight)."""
    days = events.drop(columns="date").rename(columns={"day": "date"})
    return days.groupby(KEY).agg(**aggregations)


def ldap_context(keys: pd.DataFrame) -> pd.DataFrame:
    """role and department for each (user, date) row of `keys`, from that month's LDAP snapshot.

    Users missing from a month (e.g. after leaving) keep their last known values.
    14 senior staff (vice presidents, administrative assistants) have no department in LDAP;
    they get their functional unit instead, or "(none)", so peer groups always have a value.
    Returns a frame aligned row-by-row with `keys`.
    """
    ldap = load_ldap()
    ldap = ldap[ldap["user_id"].isin(keys["user"].unique())].copy()
    ldap["department"] = ldap["department"].fillna(ldap["functional_unit"]).fillna("(none)")
    ldap = (ldap[["user_id", "month", "role", "department"]]
            .rename(columns={"user_id": "user"}).sort_values("month"))
    left = pd.DataFrame({"row": np.arange(len(keys)), "user": keys["user"].to_numpy(),
                         "month": keys["date"].dt.to_period("M").dt.to_timestamp().to_numpy()})
    merged = pd.merge_asof(left.sort_values("month"), ldap, on="month", by="user",
                           direction="backward")
    return merged.sort_values("row")[["role", "department"]].reset_index(drop=True)


# ---------------------------------------------------------------- web log, one pass (S15 step 2)
def url_domains(urls: pd.Series) -> pd.Series:
    """Lower-cased host of each URL, without a leading 'www.'."""
    host = urls.str.extract(r"^[a-zA-Z]+://([^/:?#]+)", expand=False).str.lower()
    return host.str.replace(r"^www\.", "", regex=True)


def http_user_day_domains(refresh=False) -> pd.DataFrame:
    """Visits and after-hours visits per (user, date, domain), from one chunked pass over http.

    http has ~28M rows, so it is read in batches and aggregated as it goes. The result is cached in
    data/processed/http_user_day_domain.parquet: the keyword lists (HTTP_CATEGORIES) are applied
    afterwards, so changing a list never needs another pass over the log.
    The after-hours counts depend on the working hours, so the cache records the window it was built
    with (Parquet metadata `work_hours`) and is rebuilt automatically when the window changes (S11).
    A cache without that stamp (built before Nov 5) is rebuilt too. Each build also writes
    data/processed/http_domain_counts.csv (every domain with its visits, for the S15 keyword lists).
    """
    cache = PROCESSED_DIR / "http_user_day_domain.parquet"
    window = work_hours_stamp()
    built_with = cache_work_hours(cache) if cache.exists() else None
    if built_with == window and not refresh:
        return pd.read_parquet(cache)
    parts = []
    try:
        for batch in iter_http_batches(columns=("user", "date", "url")):
            batch = batch.dropna(subset=["user", "date"])
            date = pd.to_datetime(batch["date"])
            part = pd.DataFrame({"user": batch["user"].str.strip(), "date": date.dt.normalize(),
                                 "domain": url_domains(batch["url"]).fillna("(none)"),
                                 "afterhours": is_after_hours(date.dt.hour + date.dt.minute / 60)})
            parts.append(part.groupby(["user", "date", "domain"])
                         .agg(visits=("afterhours", "size"), afterhours=("afterhours", "sum")))
    except FileNotFoundError as missing:
        found = f"built with working hours {built_with}" if built_with else (
            "without a working-hours stamp" if cache.exists() else "missing")
        raise FileNotFoundError(
            f"The web-log cache {cache.name} is {found}, but src/config.py says {window}. Rebuilding "
            f"it needs the full web log (data/parquet/http.parquet), which is not on this machine "
            f"({missing}). Get a data drop built with these working hours from Supriye.") from missing
    out = pd.concat(parts).groupby(level=[0, 1, 2]).sum().reset_index()
    out = out.astype({"visits": "int32", "afterhours": "int32"})
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(out, preserve_index=False)
    meta = {**(table.schema.metadata or {}), b"work_hours": window.encode()}
    pq.write_table(table.replace_schema_metadata(meta), cache)
    counts = out.groupby("domain")["visits"].sum().sort_values(ascending=False)
    counts.to_csv(PROCESSED_DIR / "http_domain_counts.csv", index_label="domain")
    return out


def work_hours_stamp() -> str:
    """The working-hours window as stored in the web-log cache, e.g. '7-19' (7.0 and 7 match)."""
    return f"{WORK_START_HOUR:g}-{WORK_END_HOUR:g}"


def cache_work_hours(path) -> str | None:
    """The working-hours stamp a web-log cache was built with, or None if it has none."""
    stamp = (pq.read_schema(path).metadata or {}).get(b"work_hours")
    return stamp.decode() if stamp else None


# ---------------------------------------------------------------- feature table v0 (S9)
def sample_v0_users(labels: pd.DataFrame, all_users, real_insiders, seed=RANDOM_STATE):
    """~V0_N_INSIDERS insiders spread over the 3 scenarios + V0_N_NORMAL random normal users.

    Insiders are drawn only from `real_insiders` (answers/insiders.csv). The labels also contain
    the two supervisor accounts hijacked in scenario 3, but those people are victims, not insiders.
    Within each scenario, one insider with malicious days in every split it can cover is taken
    first, so train, val and test all get malicious rows for every scenario where that is possible;
    the rest are random. Accounts with any malicious day are never sampled as normal users.
    """
    rng = np.random.default_rng(seed)
    labels = labels.assign(split=assign_split(labels["day"]).to_numpy())
    labels_real = labels[labels["user"].isin(real_insiders)]
    by_scenario = labels_real.groupby("scenario")["user"].unique()
    per_scenario = np.array_split(np.arange(V0_N_INSIDERS), len(by_scenario))
    insiders = []
    for (scenario, users), share in zip(by_scenario.items(), per_scenario):
        take = min(len(share), len(users))
        chosen = []
        for split in ("test", "val", "train"):  # rarest split first
            in_split = labels_real.loc[(labels_real["scenario"] == scenario)
                                       & (labels_real["split"] == split), "user"]
            have = labels_real.loc[labels_real["user"].isin(chosen) & (labels_real["split"] == split)]
            if len(chosen) < take and have.empty and not in_split.empty:
                pool = sorted(set(in_split) - set(chosen))
                chosen.append(rng.choice(pool))
        rest = sorted(set(users) - set(chosen))
        chosen += list(rng.choice(rest, size=take - len(chosen), replace=False))
        insiders += chosen
    normal_pool = sorted(set(all_users) - set(labels["user"]))
    normal = list(rng.choice(normal_pool, size=V0_N_NORMAL, replace=False))
    return sorted(insiders), sorted(normal)


def build_v0(labels: pd.DataFrame) -> tuple:
    """S9: basic counts for a 100-user sample, all dates. Returns (features, report)."""
    all_users = load_logon(columns=["user"])["user"].unique()
    real_insiders = set(load_insiders()["user"])
    insiders, normal = sample_v0_users(labels, all_users, real_insiders)
    users = insiders + normal

    logon = load_logon(columns=["user", "date", "activity"], users=users)
    logon["is_logon"] = logon["activity"].eq("Logon")
    logon["is_logoff"] = logon["activity"].eq("Logoff")
    logon["afterhours_logon"] = logon["is_logon"] & is_after_hours(logon["hour"])
    # Rows = user-days with at least one logon (S9 step 2)
    base = per_user_day(logon, f_logon_count=("is_logon", "sum"),
                        f_logoff_count=("is_logoff", "sum"),
                        f_afterhours_logon=("afterhours_logon", "sum"))
    base = base[base["f_logon_count"] > 0]

    device = load_device(columns=["user", "date", "activity"], users=users)
    device["connect"] = device["activity"].eq("Connect")
    usb = per_user_day(device, f_usb_connect=("connect", "sum"))

    files = load_file(columns=["user", "date", "filename"], users=users)
    file_copy = per_user_day(files, f_file_copy=("filename", "size"))

    email = load_email(columns=["user", "date", "to", "cc", "bcc", "from"], users=users)
    domains = recipient_domains(email)
    email["external"] = domains.apply(lambda ds: any(d != COMPANY_DOMAIN for d in ds))
    mail = per_user_day(email, f_email_sent=("external", "size"),
                        f_email_external=("external", "sum"))

    features = base.join([usb, file_copy, mail], how="left").fillna(0)
    features = features.astype({c: "int64" for c in features.columns})

    # labels, scenario, insider flag (TEAM_PLAN 5.1)
    lab = labels.rename(columns={"day": "date"}).set_index(KEY)
    features = features.join(lab[["scenario"]], how="left")
    features["label"] = features["scenario"].notna().astype(int)
    features["scenario"] = features["scenario"].fillna(0).astype(int)
    features["insider"] = features.index.get_level_values("user").isin(real_insiders).astype(int)

    features = features.reset_index()
    features[["role", "department"]] = ldap_context(features[KEY]).to_numpy()
    features["split"] = assign_split(features["date"]).to_numpy()

    feature_cols = [c for c in features.columns if c.startswith("f_")]
    features = features[META_COLUMNS + feature_cols].sort_values(KEY).reset_index(drop=True)

    sample_labels = labels[labels["user"].isin(insiders)]
    kept = sample_labels.merge(features[KEY], left_on=["user", "day"], right_on=KEY)
    report = {
        "users": len(users), "insiders": len(insiders), "normal_users": len(normal),
        "insiders_per_scenario": sample_labels.groupby("scenario")["user"].nunique().to_dict(),
        "rows": len(features),
        "malicious_rows": int(features["label"].sum()),
        "malicious_days_without_logon_dropped": len(sample_labels) - len(kept),
        "rows_per_split": features["split"].value_counts().to_dict(),
        "malicious_rows_per_split_scenario":
            features[features["label"] == 1].groupby(["split", "scenario"]).size().to_dict(),
        "external_email_share": float(email["external"].mean()) if len(email) else float("nan"),
    }
    return features, report


# ---------------------------------------------------------------- feature table v1 (S10-S16)
FILE_GROUPS = {"doc": {"doc", "docx", "pdf", "txt"}, "exe": {"exe"},
               "zip": {"zip", "rar", "7z", "tar", "gz", "tgz"}, "img": {"jpg", "jpeg", "png"}}
CTX_COLUMNS = ["f_ctx_O", "f_ctx_C", "f_ctx_E", "f_ctx_A", "f_ctx_N"]


def primary_pcs(logon: pd.DataFrame, fallback_days=30) -> pd.Series:
    """Each user's primary PC: the PC with the most logons in the train split (S10).

    A user with no train logons (e.g. hired later) gets the most used PC of their first
    `fallback_days` active days instead, so the choice never looks further ahead than needed.
    """
    logons = logon[logon["activity"] == "Logon"]
    train = logons[assign_split(logons["day"]).to_numpy() == "train"]
    primary = train.groupby("user")["pc"].agg(lambda s: s.value_counts().idxmax())
    rest = logons[~logons["user"].isin(primary.index)]
    if len(rest):
        rank = rest.groupby("user")["day"].rank(method="dense")
        early = rest[rank <= fallback_days]
        primary = pd.concat([primary, early.groupby("user")["pc"].agg(
            lambda s: s.value_counts().idxmax())])
    return primary


def login_features(logon: pd.DataFrame, primary_pc: pd.Series) -> pd.DataFrame:
    """S10 + the logon part of S11. Rows: every user-day with at least one logon event."""
    lg = logon.assign(is_logon=logon["activity"].eq("Logon"), is_logoff=logon["activity"].eq("Logoff"))
    lg["logon_hour"] = lg["hour"].where(lg["is_logon"])
    lg["logoff_hour"] = lg["hour"].where(lg["is_logoff"])
    lg["other_pc"] = lg["is_logon"] & lg["pc"].ne(lg["user"].map(primary_pc))
    lg["afterhours"] = is_after_hours(lg["hour"])
    lg["afterhours_logon"] = lg["is_logon"] & lg["afterhours"]
    out = per_user_day(lg, f_logon_count=("is_logon", "sum"), f_logoff_count=("is_logoff", "sum"),
                       f_first_logon_hour=("logon_hour", "min"),
                       f_last_logoff_hour=("logoff_hour", "max"), last_event=("hour", "max"),
                       f_n_pcs=("pc", "nunique"), f_logon_other_pc=("other_pc", "sum"),
                       f_afterhours_logon=("afterhours_logon", "sum"),
                       n_events=("hour", "size"), n_afterhours=("afterhours", "sum"))
    out["f_last_logoff_hour"] = out["f_last_logoff_hour"].fillna(out.pop("last_event"))
    out["f_work_duration"] = out["f_last_logoff_hour"] - out["f_first_logon_hour"]
    return out


def usb_features(device: pd.DataFrame) -> pd.DataFrame:
    """S12. Each Connect is paired with the next event on the same user + PC: if that is a
    Disconnect on the same day it ends the session, otherwise the session is capped at midnight."""
    d = device.sort_values(["user", "pc", "date"]).copy()
    g = d.groupby(["user", "pc"], sort=False)
    next_activity, next_date = g["activity"].shift(-1), g["date"].shift(-1)
    midnight = d["day"] + pd.Timedelta(days=1)
    ends = next_date.where(next_activity.eq("Disconnect") & (next_date < midnight), midnight)
    d["connect"] = d["activity"].eq("Connect")
    d["minutes"] = ((ends - d["date"]).dt.total_seconds() / 60).where(d["connect"], 0.0)
    d["afterhours"] = is_after_hours(d["hour"])
    d["connect_afterhours"] = d["connect"] & d["afterhours"]
    d["connect_pc"] = d["pc"].where(d["connect"])
    return per_user_day(d, f_usb_connect=("connect", "sum"),
                        f_usb_afterhours=("connect_afterhours", "sum"),
                        f_usb_n_pcs=("connect_pc", "nunique"), f_usb_duration=("minutes", "sum"),
                        n_events=("hour", "size"), n_afterhours=("afterhours", "sum"))


def file_extensions(filenames: pd.Series) -> pd.Series:
    return filenames.str.extract(r"\.([A-Za-z0-9]+)\s*$", expand=False).str.lower()


def file_features(files: pd.DataFrame) -> pd.DataFrame:
    """S13: copies to removable media, by extension group (FILE_GROUPS)."""
    f = files.assign(ext=file_extensions(files["filename"]))
    for group, exts in FILE_GROUPS.items():
        f[group] = f["ext"].isin(exts)
    f["afterhours"] = is_after_hours(f["hour"])
    return per_user_day(f, f_file_copy=("ext", "size"), f_file_doc=("doc", "sum"),
                        f_file_exe=("exe", "sum"), f_file_zip=("zip", "sum"),
                        f_file_img=("img", "sum"), f_file_afterhours=("afterhours", "sum"),
                        n_events=("ext", "size"), n_afterhours=("afterhours", "sum"))


def email_features(email: pd.DataFrame, count_personal=None) -> pd.DataFrame:
    """S14. Every row of email.csv is an email sent by `user`: from the work address or, for
    37.6% of rows, from personal webmail on the work PC (see EMAIL_COUNT_PERSONAL)."""
    count_personal = EMAIL_COUNT_PERSONAL if count_personal is None else count_personal
    e = email
    if not count_personal:
        e = e[e["from"].str.lower().str.endswith("@" + COMPANY_DOMAIN, na=False)]
    e = e.copy()
    domains = recipient_domains(e)
    e["n_recipients"] = domains.str.len()
    e["external"] = domains.apply(lambda ds: any(d != COMPANY_DOMAIN for d in ds))
    e["attachments"] = e["attachments"].fillna(0).astype(int)
    e["external_attach"] = e["external"] & (e["attachments"] > 0)
    e["has_bcc"] = e["bcc"].fillna("").str.strip().ne("")
    e["afterhours"] = is_after_hours(e["hour"])
    return per_user_day(e, f_email_sent=("external", "size"),
                        f_email_recipients=("n_recipients", "sum"),
                        f_email_external=("external", "sum"), f_email_attach=("attachments", "sum"),
                        f_email_external_attach=("external_attach", "sum"),
                        f_email_size=("size", "mean"), f_email_bcc=("has_bcc", "sum"),
                        f_email_afterhours=("afterhours", "sum"),
                        n_events=("external", "size"), n_afterhours=("afterhours", "sum"))


def domain_categories(domains: pd.Series, categories=None) -> pd.Series:
    """Category of each domain ('other' if none): equal to a list entry or a sub-domain of one."""
    categories = HTTP_CATEGORIES if categories is None else categories
    lookup = {}
    for d in pd.unique(domains):
        lookup[d] = next((cat for cat, entries in categories.items()
                          if any(d == e or str(d).endswith("." + e) for e in entries)), "other")
    return domains.map(lookup)


def http_features(visits: pd.DataFrame, categories=None) -> pd.DataFrame:
    """S15 step 3, from the (user, date, domain) visit table of http_user_day_domains()."""
    categories = HTTP_CATEGORIES if categories is None else categories
    v = visits.assign(category=domain_categories(visits["domain"], categories))
    g = v.groupby(KEY)
    out = pd.DataFrame({"f_http_count": g["visits"].sum(), "f_http_domains": g["domain"].nunique(),
                        "f_http_afterhours": g["afterhours"].sum()})
    per_cat = v.pivot_table(index=KEY, columns="category", values="visits", aggfunc="sum",
                            fill_value=0)
    for cat in categories:
        out[f"f_http_{cat}"] = per_cat[cat] if cat in per_cat else 0
    out["n_events"], out["n_afterhours"] = out["f_http_count"], out["f_http_afterhours"]
    return out


def psychometric_features(users: pd.Series) -> pd.DataFrame:
    """S16 step 2 (optional group): the Big-Five scores, constant per user, aligned with `users`."""
    p = load_psychometric().set_index("user_id")[["O", "C", "E", "A", "N"]].astype(float)
    p.columns = CTX_COLUMNS
    return p.reindex(users.to_numpy()).reset_index(drop=True)


def build_v1(labels: pd.DataFrame, users=None, baselines=True) -> tuple:
    """S10-S18 for every user (or only `users`), all dates. Returns (features, report).

    With `baselines`, src/baseline.py adds z_user_*, z_peer_* and new_* (S17-S18).

    Rows are user-days with at least one logon event, as in v0 (S9 step 2); activity on other
    days is dropped and counted in the report. No "days until leaving" feature (S16 step 3).
    """
    real_insiders = set(load_insiders()["user"])
    logon = load_logon(columns=["user", "date", "pc", "activity"], users=users)
    login = login_features(logon, primary_pcs(logon))
    base_index = login.index[login["f_logon_count"] > 0]

    usb = usb_features(load_device(columns=["user", "date", "pc", "activity"], users=users))
    files = load_file(columns=["user", "date", "filename"], users=users)
    fil = file_features(files)
    mail = email_features(load_email(columns=["user", "date", "to", "cc", "bcc", "from", "size",
                                              "attachments"], users=users))
    visits = http_user_day_domains()
    if users is not None:
        visits = visits[visits["user"].isin(users)]
    web = http_features(visits)

    groups = [login, usb, fil, mail, web]
    events = sum(g["n_events"].reindex(base_index, fill_value=0) for g in groups)
    afterhours = sum(g["n_afterhours"].reindex(base_index, fill_value=0) for g in groups)
    parts = [g.drop(columns=["n_events", "n_afterhours"]) for g in groups]
    features = parts[0].loc[base_index].join(parts[1:], how="left")
    features["f_afterhours_events"] = afterhours
    features["f_afterhours_ratio"] = afterhours / events
    features["f_weekend"] = (features.index.get_level_values("date").day_of_week >= 5).astype(int)
    features = features.fillna({c: 0 for c in features.columns})

    lab = labels.rename(columns={"day": "date"}).set_index(KEY)
    features = features.join(lab[["scenario"]], how="left")
    features["label"] = features["scenario"].notna().astype(int)
    features["scenario"] = features["scenario"].fillna(0).astype(int)
    features["insider"] = features.index.get_level_values("user").isin(real_insiders).astype(int)
    features = features.reset_index()
    features[["role", "department"]] = ldap_context(features[KEY]).to_numpy()
    features["split"] = assign_split(features["date"]).to_numpy()
    features = features.join(psychometric_features(features["user"]))

    feature_cols = [c for c in features.columns if c.startswith("f_")]
    features = features[META_COLUMNS + feature_cols].sort_values(KEY).reset_index(drop=True)
    int_cols = [c for c in feature_cols if c not in NOT_COUNTS and c != "f_usb_duration"]
    features[int_cols] = features[int_cols].astype("int64")
    if baselines:
        from src.baseline import add_baselines  # baseline.py imports this module
        features = add_baselines(features, logon)

    keys = labels.rename(columns={"day": "date"})[KEY]
    if users is not None:
        keys = keys[keys["user"].isin(users)]
    active = set().union(*(set(g.index) for g in groups[1:]))
    ext = file_extensions(files["filename"])
    report = {
        "users": features["user"].nunique(), "rows": len(features),
        "malicious_rows": int(features["label"].sum()),
        "malicious_days_without_logon_dropped": len(keys) - len(keys.merge(features[KEY])),
        "activity_days_without_logon_dropped": len(active - set(base_index)),
        "rows_per_split": features["split"].value_counts().to_dict(),
        "malicious_rows_per_split_scenario":
            features[features["label"] == 1].groupby(["split", "scenario"]).size().to_dict(),
        "file_extension_coverage":
            float(ext.isin(set().union(*FILE_GROUPS.values())).mean()) if len(ext) else float("nan"),
        "features": len(feature_columns(features)),
    }
    return features, report


def behavior_checks(features: pd.DataFrame) -> pd.DataFrame:
    """The "Done when" checks of S12, S14 and S15: per scenario, a feature's mean on the
    malicious days of the labeled accounts vs. the same accounts' other days."""
    checks = [(1, "f_usb_connect"), (1, "f_http_leak"), (1, "f_afterhours_logon"),
              (2, "f_http_job"), (2, "f_usb_connect"), (3, "f_email_recipients"),
              (3, "f_http_hack"), (3, "f_logon_other_pc")]
    rows = []
    for scenario, col in checks:
        accounts = features.loc[features["scenario"] == scenario, "user"].unique()
        acc = features[features["user"].isin(accounts)]
        bad = acc["scenario"] == scenario
        rows.append({"scenario": scenario, "feature": col, "accounts": len(accounts),
                     "mean_malicious_days": acc.loc[bad, col].mean(),
                     "mean_other_days": acc.loc[~bad, col].mean(),
                     "share_malicious_days_gt0": (acc.loc[bad, col] > 0).mean()})
    return pd.DataFrame(rows)


def main(argv):
    if argv[:1] not in (["v0"], ["v1"]):
        print(__doc__)
        return
    labels = pd.read_parquet(PROCESSED_DIR / "labels.parquet")
    version = argv[0]
    features, report = build_v0(labels) if version == "v0" else build_v1(labels)
    features.to_parquet(PROCESSED_DIR / f"features_{version}.parquet", index=False)
    for k, v in report.items():
        print(f"{k}: {v}")
    if version == "v1":
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        checks = behavior_checks(features)
        checks.to_csv(TABLES_DIR / "v1_behavior_checks.csv", index=False)
        print(checks.to_string(index=False))
    X, y, cols = get_model_matrix(features, split="train")
    print(f"get_model_matrix(train): X {X.shape}, positives {int(y.sum())}, features {cols}")


if __name__ == "__main__":
    main(sys.argv[1:])
