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

The A18 outputs (both models retrained, both ranked tables, precision_at_20.csv and figure F8):
    python -m src.pipeline --prototype
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
from src.risk_scoring import (MEDIUM, HIGH, f8_user, plot_risk_timeline, precision_at_k, rank_users,
                              score_risk)

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


# ---------------------------------------------------------------- A18: prototype outputs on v1
PROTOTYPE_MODELS = ("iforest", "autoencoder")


def output_name(model_name) -> str:
    """top_risky_users.csv for the default model (iforest), top_risky_users_<model>.csv otherwise."""
    return OUTPUT if model_name == "iforest" else OUTPUT.replace(".csv", f"_{model_name}.csv")


def precision_table_name(top=20) -> str:
    """precision_at_20.csv for the default top 20; the name follows `top`."""
    return f"precision_at_{top}.csv"


def prototype(features_path, models=PROTOTYPE_MODELS, top=20, f8_model="iforest", params=None,
              verbose=True):
    """The A18 outputs in one call. Each model is retrained (so no stale saved model is reused),
    its ranked table is saved (top_risky_users.csv, top_risky_users_autoencoder.csv), and one row
    per model goes to precision_at_<top>.csv: how many of the listed users are test-period insiders,
    and what share of all test insiders they are. Figure F8 is the risk timeline of f8_user() from
    `f8_model`'s risk scores, saved as F8_risk_timeline.png/.pdf.

    params: optional {model: {parameter: value}} overrides (the tests use it to train faster).
    Returns (precision table, the F8 user).
    """
    rows, user = [], None
    for model in models:
        table, risk = run(features_path, model, top, retrain=True, params=(params or {}).get(model),
                          output=output_name(model), verbose=verbose)
        rows.append({"model": model, **precision_at_k(table, risk, k=top)})
        if model == f8_model:
            user = f8_user(risk)
            plot_risk_timeline(risk, user)
    precision = pd.DataFrame(rows)
    path = TABLES_DIR / precision_table_name(top)
    precision.to_csv(path, index=False)
    if verbose:
        print(f"\nprecision@{top} -> {path.relative_to(ROOT)}; "
              f"F8 user ({f8_model}): {user}")
        print(precision.drop(columns="insiders_listed").to_string(index=False))
    return precision, user


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--features", default=str(ROOT / "data/processed/features_v1.parquet"))
    parser.add_argument("--model", default="iforest", choices=sorted(DETECTORS))
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--date", help="rank users for this day instead of the test period")
    parser.add_argument("--retrain", action="store_true", help="ignore a saved model")
    parser.add_argument("--prototype", action="store_true",
                        help="A18: retrain iforest and autoencoder, save both ranked tables, "
                             "precision_at_20.csv and figure F8")
    args = parser.parse_args(argv)
    if args.prototype:
        prototype(args.features, top=args.top)
    else:
        run(args.features, args.model, args.top, args.date, args.retrain)


if __name__ == "__main__":
    main()
