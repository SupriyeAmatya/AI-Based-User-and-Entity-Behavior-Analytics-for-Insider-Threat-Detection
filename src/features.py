"""Behavioral features and the shared model-input helper (owner: Supriye; tasks S9-S16).

Build the v0 feature table (S9) from the repo root, after `python -m src.labels`:
    python -m src.features v0
-> data/processed/features_v0.parquet, one row per user-day in TEAM_PLAN 5.1 format.

Every model turns a feature table into inputs with the same helper (TEAM_PLAN 5.5):
    from src.features import get_model_matrix
    X_train, y_train, feature_names = get_model_matrix(df, split="train")
"""
import sys

import numpy as np
import pandas as pd

from src.config import (
    COMPANY_DOMAIN, PROCESSED_DIR, RANDOM_STATE, V0_N_INSIDERS, V0_N_NORMAL, WORK_END_HOUR,
    WORK_START_HOUR,
)
from src.data_loader import (
    load_device, load_email, load_file, load_ldap, load_logon, recipient_domains,
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
    """Aggregate an event table to (user, date) using named boolean/count columns."""
    return events.rename(columns={"day": "date"}).groupby(KEY).agg(**aggregations)


def ldap_context(keys: pd.DataFrame) -> pd.DataFrame:
    """role and department for each (user, date) row of `keys`, from that month's LDAP snapshot.

    Users missing from a month (e.g. after leaving) keep their last known values.
    Returns a frame aligned row-by-row with `keys`.
    """
    ldap = load_ldap()
    ldap = ldap[ldap["user_id"].isin(keys["user"].unique())]
    ldap = (ldap[["user_id", "month", "role", "department"]]
            .rename(columns={"user_id": "user"}).sort_values("month"))
    left = pd.DataFrame({"row": np.arange(len(keys)), "user": keys["user"].to_numpy(),
                         "month": keys["date"].dt.to_period("M").dt.to_timestamp().to_numpy()})
    merged = pd.merge_asof(left.sort_values("month"), ldap, on="month", by="user",
                           direction="backward")
    return merged.sort_values("row")[["role", "department"]].reset_index(drop=True)


# ---------------------------------------------------------------- feature table v0 (S9)
def sample_v0_users(labels: pd.DataFrame, all_users, seed=RANDOM_STATE):
    """~V0_N_INSIDERS insiders spread over the 3 scenarios + V0_N_NORMAL random normal users."""
    rng = np.random.default_rng(seed)
    by_scenario = labels.groupby("scenario")["user"].unique()
    per_scenario = np.array_split(np.arange(V0_N_INSIDERS), len(by_scenario))
    insiders = []
    for (scenario, users), share in zip(by_scenario.items(), per_scenario):
        take = min(len(share), len(users))
        insiders += list(rng.choice(sorted(users), size=take, replace=False))
    normal_pool = sorted(set(all_users) - set(labels["user"]))
    normal = list(rng.choice(normal_pool, size=V0_N_NORMAL, replace=False))
    return sorted(insiders), sorted(normal)


def build_v0(labels: pd.DataFrame) -> tuple:
    """S9: basic counts for a 100-user sample, all dates. Returns (features, report)."""
    all_users = load_logon(columns=["user"])["user"].unique()
    insiders, normal = sample_v0_users(labels, all_users)
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
    features["insider"] = features.index.get_level_values("user").isin(labels["user"]).astype(int)

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


def main(argv):
    if argv[:1] != ["v0"]:
        print(__doc__)
        return
    labels = pd.read_parquet(PROCESSED_DIR / "labels.parquet")
    features, report = build_v0(labels)
    features.to_parquet(PROCESSED_DIR / "features_v0.parquet", index=False)
    for k, v in report.items():
        print(f"{k}: {v}")
    X, y, cols = get_model_matrix(features, split="train")
    print(f"get_model_matrix(train): X {X.shape}, positives {int(y.sum())}, features {cols}")


if __name__ == "__main__":
    main(sys.argv[1:])
