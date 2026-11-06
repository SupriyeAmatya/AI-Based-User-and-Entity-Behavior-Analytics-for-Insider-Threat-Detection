"""Feature-group ablation, table T7 (owner: Supriye; S22), and the data-processing time for T8.

Answers "which behavioral features contribute most to detection?" from a second angle (Ayo's SHAP
is the first). Ayo's XGBoost and Arva's Isolation Forest are retrained with their **current default
settings** (the tuned v1 settings once A16 and Y15 are merged) on these feature sets, and scored on
`test` with evaluate.py (S22 steps 2-3):
    (a) raw f_* only    (b) f_* + z_user_*    (c) full = f_* + z_user_* + z_peer_* + new_*
    (d) full minus one group at a time: logon, time, usb, file, email, http, context

    python -m src.ablation            # -> results/tables/ablation.csv (T7)
    python -m src.ablation time       # -> results/tables/data_processing_time.csv (for T8)

No score files are needed: every model is retrained here (TEAM_PLAN 2.5.12).
"""
import os
import platform
import sys
import time

import pandas as pd

from src.config import PROCESSED_DIR, TABLES_DIR
from src.evaluate import evaluate_df
from src.features import feature_columns

GROUPS = ("logon", "time", "usb", "file", "email", "http", "context")
MODELS = ("xgboost", "iforest")
TABLE = "ablation.csv"
TIME_TABLE = "data_processing_time.csv"
CONVERSION_SECONDS = 600.0   # S4 conversion of the 4.8 GB archive on Nov 3 (~10 min, one-off)

# Feature names (without their f_ / z_user_ / z_peer_ / new_ prefix) whose first word is not
# their group. Every other name is grouped by its first word (_FIRST_WORD).
_SPECIAL = {
    "logoff_count": "logon", "first_logon_hour": "logon", "last_logoff_hour": "logon",
    "work_duration": "logon", "n_pcs": "logon", "pc": "logon",
    "afterhours_logon": "time", "afterhours_events": "time", "afterhours_ratio": "time",
    "weekend": "time", "afterhours": "time",
    "usb_user": "usb", "leak_site": "http",
}
_FIRST_WORD = {"logon": "logon", "usb": "usb", "file": "file", "email": "email", "http": "http",
               "ctx": "context"}


def feature_group(column: str) -> str:
    """Behavior group of a model-input column. z_user_*, z_peer_* and new_* belong to the group of
    the behavior they describe: z_user_usb_connect -> usb, new_leak_site -> http, new_pc -> logon."""
    for prefix in ("z_user_", "z_peer_", "new_", "f_"):
        if column.startswith(prefix):
            name = column[len(prefix):]
            break
    else:
        raise ValueError(f"not a model input: {column}")
    group = _SPECIAL.get(name) or _FIRST_WORD.get(name.split("_")[0])
    if group is None:
        raise ValueError(f"no feature group for {column}")
    return group


def feature_sets(columns) -> dict:
    """The S22 step-2 feature sets as {name: [columns]}; a (d) set only when the group exists."""
    cols = list(columns)
    raw = [c for c in cols if c.startswith("f_")]
    z_user = [c for c in cols if c.startswith("z_user_")]
    sets = {"a_raw": raw, "b_raw_z_user": raw + z_user, "c_full": cols}
    for group in GROUPS:
        kept = [c for c in cols if feature_group(c) != group]
        if len(kept) < len(cols):
            sets[f"d_full_minus_{group}"] = kept
    return sets


def _scores(df, model, columns):
    """Retrain one model on `columns` with its module defaults and score every row."""
    if model == "iforest":
        from src.models_unsupervised import train_and_score
        return train_and_score(df, "iforest", save=False, columns=columns)
    from src.models_supervised import train_and_score_supervised
    return train_and_score_supervised(df, model, save=False, columns=columns)


def run_ablation(df, models=MODELS, k=0.01, save=True) -> pd.DataFrame:
    """One row per model x feature set: test PR-AUC, ROC-AUC, recall at the top-1% budget and at the
    best-F1 threshold (S22 step 3), and the change in test PR-AUC against the full set."""
    rows = []
    for name, columns in feature_sets(feature_columns(df)).items():
        for model in models:
            scores, info = _scores(df, model, columns)
            r = evaluate_df(scores, k)
            rows.append({"model": model, "feature_set": name, "n_features": len(columns),
                         "test_pr_auc": r["ranking"]["pr_auc"], "test_roc_auc": r["ranking"]["roc_auc"],
                         "recall_top_1pct": r["operating_points"]["top_1pct"]["recall"],
                         "recall_best_f1": r["operating_points"]["best_f1"]["recall"],
                         "fit_seconds": round(info["fit_seconds"], 2)})
    table = pd.DataFrame(rows)
    full = table[table["feature_set"] == "c_full"].set_index("model")["test_pr_auc"]
    table["delta_pr_auc_vs_full"] = table["test_pr_auc"] - table["model"].map(full)
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        table.to_csv(TABLES_DIR / TABLE, index=False)
    return table


def data_processing_time(save=True) -> pd.DataFrame:
    """Wall-clock time from the Parquet logs to feature table v1, for T8 (detection time): labels,
    the one pass over the 28.4M-row web log, and v1 (behavior features + baselines). The archive
    conversion is a one-off listed from the Nov 3 run, not re-run."""
    from src import features, labels

    steps = []
    started = time.perf_counter()
    labels.build_labels()
    steps.append(("labels (S6)", time.perf_counter() - started))
    started = time.perf_counter()
    features.http_user_day_domains(refresh=True)
    steps.append(("web-log pass, 28.4M rows (S15)", time.perf_counter() - started))
    started = time.perf_counter()
    table, _ = features.build_v1(pd.read_parquet(PROCESSED_DIR / "labels.parquet"))
    steps.append(("feature table v1 incl. baselines (S10-S18)", time.perf_counter() - started))
    out = pd.DataFrame([("archive -> Parquet conversion (S4, one-off, Nov 3)", CONVERSION_SECONDS),
                        *steps], columns=["step", "seconds"])
    out["seconds"] = out["seconds"].round(1)
    out["user_days"] = len(table)
    out["seconds_per_1000_user_days"] = (1000 * out["seconds"] / len(table)).round(3)
    out["cpu"] = platform.processor() or platform.machine()   # T8 lists the machine next to times
    out["threads"] = os.cpu_count()
    try:
        import psutil
        out["ram_gb"] = round(psutil.virtual_memory().total / 2**30, 1)
    except ImportError:
        out["ram_gb"] = None
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        out.to_csv(TABLES_DIR / TIME_TABLE, index=False)
    return out


def main(argv):
    if argv[:1] == ["time"]:
        print(data_processing_time().to_string(index=False))
    elif argv[:1] in ([], ["run"]):
        df = pd.read_parquet(PROCESSED_DIR / "features_v1.parquet")
        print(run_ablation(df).round(4).to_string(index=False))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
