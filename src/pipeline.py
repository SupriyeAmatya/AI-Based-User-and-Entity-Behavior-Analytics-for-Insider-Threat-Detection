"""End-to-end UEBA prototype (owner: Arva; A11 pipeline, A12 alert reasons).

One command shows the whole flow, from the repo root:
    python src/pipeline.py --features data/processed/features_v1.parquet --model iforest --top 20
    python -m src.pipeline --features data/processed/features_v0.parquet --model autoencoder

Steps: load the feature table -> get_model_matrix() -> load the trained model from models/ (train
and save it if it is missing or was trained on other features) -> score every user-day -> daily
risk -> 7-day user risk -> alert levels -> top-N users of the test period, each with the 3 features
that contributed most on their riskiest day -> results/tables/top_risky_users.csv (and printed).

The table is what an analyst would see, so it holds no labels. With --date it ranks users for one
day instead of the whole test period.
"""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):  # run as `python src/pipeline.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.config import ROOT, TABLES_DIR
from src.features import NOT_COUNTS, get_model_matrix
from src.models_unsupervised import DETECTORS, SCORE_KEYS, load_detector, save_detector
from src.risk_scoring import MEDIUM, HIGH, rank_users, score_risk

MODELS_DIR = ROOT / "models"
OUTPUT = "top_risky_users.csv"
N_REASONS = 3
# A z-score closer to its baseline than this is never given as a reason (review of #57: the
# autoencoder named features "0.0σ above own baseline"). PROVISIONAL: Arva sets the floor.
MIN_REASON_Z = 1.0
# Non-count features whose 0 means "nothing happened" (no email sent): never a reason at 0.
ZERO_IS_NOTHING = ("f_email_size",)

# Readable names for the reasons column (A12 step 2), keyed by the feature name without its prefix.
PHRASES = {
    "logon_count": "logons", "logoff_count": "logoffs", "first_logon_hour": "first logon hour",
    "last_logoff_hour": "last logoff hour", "work_duration": "hours between first logon and last logoff",
    "n_pcs": "PCs used", "logon_other_pc": "logons on a non-primary PC",
    "afterhours_logon": "after-hours logons", "afterhours_events": "after-hours events",
    "afterhours_ratio": "share of activity after hours", "weekend": "weekend day",
    "usb_connect": "USB connects", "usb_afterhours": "after-hours USB connects",
    "usb_n_pcs": "PCs with USB use", "usb_duration": "minutes of USB use",
    "file_copy": "files copied", "file_doc": "documents copied", "file_exe": "executables copied",
    "file_zip": "archives copied", "file_img": "images copied",
    "file_afterhours": "after-hours file copies", "email_sent": "emails sent",
    "email_recipients": "email recipients", "email_external": "external emails",
    "email_attach": "email attachments", "email_external_attach": "external emails with attachments",
    "email_size": "mean email size (bytes)", "email_bcc": "emails using BCC",
    "email_afterhours": "after-hours emails", "http_count": "web visits",
    "http_domains": "distinct web domains", "http_afterhours": "after-hours web visits",
    "http_job": "job-site visits", "http_leak": "leak-site visits",
    "http_cloud": "file-sharing site visits", "http_hack": "keylogger/hacking-site visits",
    "http_competitor": "competitor-site visits",
    "ctx_O": "openness score", "ctx_C": "conscientiousness score", "ctx_E": "extraversion score",
    "ctx_A": "agreeableness score", "ctx_N": "neuroticism score",
    "usb_user": "first-ever USB use", "pc": "first logon on a new PC",
    "leak_site": "first-ever leak or file-sharing site visit",
    "afterhours": "first-ever after-hours logon",
}


def _phrase(feature):
    for prefix in ("z_user_", "z_peer_", "new_", "f_"):
        if feature.startswith(prefix):
            return PHRASES.get(feature[len(prefix):], feature[len(prefix):].replace("_", " "))
    return feature


def describe(feature, value) -> str:
    """One readable reason, e.g. 'USB connects 6.2σ above own baseline' or '37 files copied'."""
    if feature.startswith(("z_user_", "z_peer_")):
        side = "above" if value >= 0 else "below"
        who = "own baseline" if feature.startswith("z_user_") else "peers"
        return f"{_phrase(feature)} {abs(value):.1f}σ {side} {who}"
    if feature.startswith("new_"):
        return _phrase(feature)
    return f"{_phrase(feature)}: {value:g}" if feature.endswith(("hour", "ratio", "size")) \
        or "_ctx_" in feature else f"{value:g} {_phrase(feature)}"


def contributions(detector, model_name, X: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """How much each feature contributed to each row's score (A12 step 1), same shape as X.

    - autoencoder: the per-feature reconstruction error (feature_errors()) where the value was
      higher than the reconstruction; below-expected values count 0.
    - iforest: |z_user_*| when the table has per-user baselines (A12 card), plus the novelty flags
      (a first-time event counts as 3σ); on a table without baselines (v0) how far each feature
      lies *above* the normal training mean, in training standard deviations (below-normal values
      count 0: less activity than usual is not the reason for an alert).
    """
    if model_name == "autoencoder":
        residuals = detector.feature_residuals(X)
        return (residuals ** 2).where(residuals > 0, 0.0)
    z_user = [c for c in X.columns if c.startswith("z_user_")]
    if z_user:
        out = pd.DataFrame(0.0, index=X.index, columns=X.columns)
        out[z_user] = df.loc[X.index, z_user].abs().to_numpy()
        flags = [c for c in X.columns if c.startswith("new_")]
        out[flags] = 3.0 * df.loc[X.index, flags].to_numpy()
        return out
    scaler = detector.pipeline.named_steps["scaler"]
    above = np.clip(scaler.transform(X), 0, None)
    return pd.DataFrame(above, index=X.index, columns=X.columns)


def alert_reasons(contrib: pd.DataFrame, df: pd.DataFrame, k=N_REASONS) -> pd.Series:
    """The k largest contributions of each row as readable text, joined with '; '.
    Never given as a reason: a count of 0, a novelty flag that is off, a ZERO_IS_NOTHING feature
    at 0, and a z-score with |z| < MIN_REASON_Z (or missing). A row can so have fewer than k."""
    reasons = {}
    raw = df.loc[contrib.index, contrib.columns]
    zero_count = [c for c in contrib.columns
                  if (c.startswith("f_") and c not in NOT_COUNTS) or c.startswith("new_")
                  or c in ZERO_IS_NOTHING]
    z_scores = [c for c in contrib.columns if c.startswith(("z_user_", "z_peer_"))]
    contrib = contrib.copy()
    contrib[zero_count] = contrib[zero_count].where(raw[zero_count].to_numpy() != 0, 0.0)
    contrib[z_scores] = contrib[z_scores].where(
        raw[z_scores].abs().to_numpy() >= MIN_REASON_Z, 0.0)
    values = contrib.to_numpy()
    for i, idx in enumerate(contrib.index):
        top = np.argsort(-values[i])[:k]
        parts = [describe(contrib.columns[j], df.at[idx, contrib.columns[j]]) for j in top
                 if values[i, j] > 0]
        reasons[idx] = "; ".join(parts)
    return pd.Series(reasons)


# ---------------------------------------------------------------- A19: case studies
CASE_SCENARIOS = (1, 2, 3)
N_BASELINE_DAYS = 30        # the per-user baseline window of src/baseline.py (WINDOW)
EVIDENCE_LOGS = ("logon", "device", "file", "email")
WEB_CACHE = "http_user_day_domain.parquet"


def pick_cases(risk: pd.DataFrame, threshold, df: pd.DataFrame = None) -> pd.DataFrame:
    """The 4 test-period cases of A19 step 1, from a risk table (score_risk output) and a score
    threshold (Isolation Forest's best-F1 threshold in the notebook).

    For each scenario: its highest-scoring malicious day that is flagged (score >= threshold), a
    "true positive"; if no day of that scenario is flagged, its highest-scoring malicious day, a
    "missed" case. Then the highest-scoring normal day, the top "false positive".
    The index is the row's index in the feature table; with `df`, role and department are added
    (the context of A19 step 2).
    """
    test = risk[risk["split"] == "test"]
    picks = []
    for s in CASE_SCENARIOS:
        bad = test[(test["label"] == 1) & (test["scenario"] == s)]
        if bad.empty:
            continue
        flagged = bad[bad["score"] >= threshold]
        kind = "true positive" if len(flagged) else "missed"
        picks.append((f"scenario {s}", kind, (flagged if len(flagged) else bad)["score"].idxmax()))
    normal = test[test["label"] == 0]
    if len(normal):
        top = normal["score"].idxmax()
        kind = "false positive" if normal.at[top, "score"] >= threshold else "normal, not flagged"
        picks.append(("top normal day", kind, top))
    rows = [idx for _, _, idx in picks]
    cases = risk.loc[rows, ["user", "date", "scenario", "label", "score", "daily_risk",
                            "user_risk", "alert_level"]].copy()
    cases.insert(0, "kind", [kind for _, kind, _ in picks])
    cases.insert(0, "case", [name for name, _, _ in picks])
    cases.insert(cases.columns.get_loc("score") + 1, "threshold", threshold)
    if df is not None:
        for i, col in enumerate(c for c in ("role", "department") if c in df.columns):
            cases.insert(4 + i, col, df.loc[rows, col].to_numpy())
    return cases


def baseline_vs_day(df: pd.DataFrame, row, k=5, window=N_BASELINE_DAYS) -> pd.DataFrame:
    """A19 step 3 for one row (an index label of the feature table): the k baselined features with
    the largest |z_user| that day. Columns: the day's value, the mean over the user's previous
    `window` active days (and how many such days there were), z_user and z_peer."""
    user, date = df.at[row, "user"], df.at[row, "date"]
    past = df[(df["user"] == user) & (df["date"] < date)].sort_values("date").tail(window)
    rows = []
    for z in (c for c in df.columns if c.startswith("z_user_")):
        short = z[len("z_user_"):]
        rows.append({"feature": f"f_{short}", "what": _phrase(f"f_{short}"),
                     "value": df.at[row, f"f_{short}"],
                     "mean_previous_days": past[f"f_{short}"].mean(), "previous_days": len(past),
                     "z_user": df.at[row, z],
                     "z_peer": df.at[row, f"z_peer_{short}"] if f"z_peer_{short}" in df else np.nan})
    table = pd.DataFrame(rows)
    order = table["z_user"].abs().sort_values(ascending=False, na_position="last").index
    return table.loc[order].head(k).reset_index(drop=True)


def shap_for_row(detector, X: pd.DataFrame, df: pd.DataFrame, row):
    """SHAP explanation of one user-day for a tree detector (Isolation Forest), ready for
    explain.plot_waterfall(sv, X_row, 0, name). The explanation shows the raw feature values of
    the table, not the log1p values the model saw."""
    from src.explain import get_shap_values

    X_row = X.loc[[row]]
    sv = get_shap_values(detector, X_row)
    sv.data = df.loc[[row], X.columns].to_numpy(dtype=float)
    return sv, X_row


def plot_ae_errors(detector, X: pd.DataFrame, row, name, k=10, title=None):
    """Bar chart of the k largest per-feature reconstruction errors of one user-day (A19 step 4,
    the autoencoder half of F7), saved as PNG and PDF. Red bars: the value was above what the
    autoencoder expected; grey: below. Returns (figure, the k errors as a table)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from src.config import FIGURES_DIR

    residuals = detector.feature_residuals(X.loc[[row]]).iloc[0]
    errors = (residuals ** 2).sort_values(ascending=False).head(k)
    table = pd.DataFrame({"feature": errors.index, "error": errors.to_numpy(),
                          "above_expected": (residuals[errors.index] > 0).to_numpy()})
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.barh(table["feature"][::-1], table["error"][::-1],
            color=["tab:red" if up else "0.6" for up in table["above_expected"][::-1]])
    ax.set(xlabel="Squared reconstruction error (scaled units)",
           title=title or "Autoencoder: largest feature errors")
    ax.tick_params(axis="y", labelsize=7)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES_DIR / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return fig, table


def raw_evidence(user, date, loaders=None, web_path=None) -> dict:
    """A19 step 5: every logon, device (USB), file and email event of `user` on `date` from the 4
    small Parquet logs, and that day's web domains with visits and after-hours visits from the web
    cache (http.parquet is never needed). Returns {"logon": ..., "device": ..., "file": ...,
    "email": ..., "web": ...}, events in time order. The web table names each domain's keyword
    category (job, leak, cloud, hack, competitor or other) and lists the categorised domains first,
    then the rest by visits.

    loaders: {log: function(users=[...]) -> events}; default: the src.data_loader loaders.
    """
    from src.features import domain_categories

    if loaders is None:
        from src import data_loader
        loaders = {log: getattr(data_loader, f"load_{log}") for log in EVIDENCE_LOGS}
    day = pd.Timestamp(date).normalize()
    out = {}
    for log, load in loaders.items():
        events = load(users=[user])
        events = events[pd.to_datetime(events["date"]).dt.normalize() == day].sort_values("date")
        out[log] = events.drop(columns=[c for c in ("id", "day", "hour", "content") if c in events]
                               ).reset_index(drop=True)
    if web_path is None:
        from src.config import PROCESSED_DIR
        web_path = PROCESSED_DIR / WEB_CACHE
    web = pd.read_parquet(web_path, filters=[("user", "==", user)])
    web = web[pd.to_datetime(web["date"]).dt.normalize() == day].drop(columns=["user", "date"])
    web.insert(1, "category", domain_categories(web["domain"]))
    web = web.assign(_other=web["category"] == "other")
    out["web"] = web.sort_values(["_other", "visits", "domain"], ascending=[True, False, True]
                                 ).drop(columns="_other").reset_index(drop=True)
    return out


def model_path(model_name, features_path) -> Path:
    suffix = ".pt" if model_name == "autoencoder" else ".joblib"
    return MODELS_DIR / f"{model_name}_{Path(features_path).stem}{suffix}"


def get_detector(df, model_name, features_path, params=None, retrain=False):
    """Load the saved detector, or train it on the normal training rows and save it (A11 step 3).
    A saved model trained on different feature columns is retrained."""
    X, _, names = get_model_matrix(df)
    path = model_path(model_name, features_path)
    if path.exists() and not retrain:
        detector = load_detector(path)
        if getattr(detector, "feature_names", None) == names:
            return detector, path, False
    detector = DETECTORS[model_name](**(params or {}))
    train = (df["split"] == "train") & (df["label"] == 0)
    val = (df["split"] == "val") & (df["label"] == 0)
    detector.fit(X[train], X[val])
    detector.feature_names = names
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    save_detector(detector, path)
    return detector, path, True


def top_users(risk: pd.DataFrame, top=20) -> pd.DataFrame:
    """Users ranked over the test period by their highest daily risk, then by alert days."""
    test = risk[risk["split"] == "test"]
    peak = test.loc[test.groupby("user")["daily_risk"].idxmax(), ["user", "date", "daily_risk"]]
    peak = peak.rename(columns={"date": "peak_date", "daily_risk": "peak_risk"}).set_index("user")
    agg = test.groupby("user").agg(
        high_days=("daily_risk", lambda r: int((r >= HIGH).sum())),
        medium_days=("daily_risk", lambda r: int(((r >= MEDIUM) & (r < HIGH)).sum())),
        active_days=("date", "nunique"))
    first = test[test["daily_risk"] >= MEDIUM].groupby("user")["date"].min().rename("first_alert")
    table = peak.join(agg).join(first)
    table["alert_level"] = np.select([table["peak_risk"] >= HIGH, table["peak_risk"] >= MEDIUM],
                                     ["High", "Medium"], default="Low")
    table = table.sort_values(["peak_risk", "high_days", "medium_days"], ascending=False).head(top)
    table = table.reset_index()
    table.insert(0, "rank", np.arange(1, len(table) + 1))
    return table


def run(features_path, model_name="iforest", top=20, date=None, retrain=False, params=None,
        output=OUTPUT, verbose=True):
    df = pd.read_parquet(features_path)
    detector, path, trained = get_detector(df, model_name, features_path, params, retrain)
    X, _, _ = get_model_matrix(df)
    scores = df[SCORE_KEYS].copy()
    scores["score"] = detector.score(X)
    risk = score_risk(scores)
    if date is None:
        table = top_users(risk, top)
        window = risk[risk["split"] == "test"]
    else:
        table = rank_users(risk, date, top)
        day = pd.Timestamp(date).normalize()
        window = risk[(risk["date"] > day - pd.Timedelta(days=7)) & (risk["date"] <= day)]
    # each listed user's riskiest day in the window is the alert row to explain (A12)
    alert_rows = window.groupby("user")["daily_risk"].idxmax().reindex(table["user"]).to_numpy()
    contrib = contributions(detector, model_name, X.loc[alert_rows], df)
    table["reasons"] = alert_reasons(contrib, df).reindex(alert_rows).to_numpy()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / output, index=False)
    if verbose:
        how = "trained and saved" if trained else "loaded"
        print(f"{model_name}: {how} {path.relative_to(ROOT)}")
        period = f"on {pd.Timestamp(date).date()}" if date else "over the test period"
        print(f"Top {len(table)} users {period} -> {(TABLES_DIR / output).relative_to(ROOT)}")
        with pd.option_context("display.max_colwidth", 120, "display.width", 200):
            print(table.to_string(index=False))
    return table, risk


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--features", default=str(ROOT / "data/processed/features_v1.parquet"))
    parser.add_argument("--model", default="iforest", choices=sorted(DETECTORS))
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--date", help="rank users for this day instead of the test period")
    parser.add_argument("--retrain", action="store_true", help="ignore a saved model")
    args = parser.parse_args(argv)
    run(args.features, args.model, args.top, args.date, args.retrain)


if __name__ == "__main__":
    main()
