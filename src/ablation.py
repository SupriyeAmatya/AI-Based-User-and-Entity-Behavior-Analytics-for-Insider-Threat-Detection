"""Feature-group ablation, table T7 (owner: Supriye; S22), and the data-processing time for T8.

Answers "which behavioral features contribute most to detection?" from a second angle (Ayo's SHAP
is the first). Ayo's XGBoost and Arva's Isolation Forest are retrained with their **current module
default settings** on these feature sets and scored on `test` with evaluate.py (S22 steps 2-3):
    (a) raw f_* only    (b) f_* + z_user_*    (c) full = f_* + z_user_* + z_peer_* + new_*
    (d) full minus one group at a time: logon, time, usb, file, email, http, context

The defaults are the card settings until Arva's A16 and Ayo's Y15 merge their tuned settings, so
run the ablation for T7 only after that. Every row of ablation.csv records the model settings it
used (`params`) and the commit, so an untuned run can't pass for the final table.

    python -m src.ablation            # -> results/tables/ablation.csv (T7)
    python -m src.ablation time       # -> results/tables/data_processing_time.csv (for T8)

No score files are needed: every model is retrained here (TEAM_PLAN 2.5.12).
`time` runs on Supriye's machine only: it needs data/parquet/http.parquet (not in the data drop) and
rewrites the web-log cache data/processed/http_user_day_domain.parquet, so run it before
`python scripts/data_drop.py make`.
"""
import json
import os
import platform
import subprocess
import sys
import time

import pandas as pd

from src.config import PARQUET_DIR, ROOT, TABLES_DIR
from src.evaluate import evaluate_df
from src.features import feature_columns

GROUPS = ("logon", "time", "usb", "file", "email", "http", "context")
MODELS = ("xgboost", "iforest")
SUPERVISED = ("random_forest", "xgboost")
UNSUPERVISED = ("iforest", "autoencoder", "ocsvm")
TABLE = "ablation.csv"
TIME_TABLE = "data_processing_time.csv"
CONVERSION_SECONDS = 600.0   # S4 conversion on Nov 3: "~10 min" from the run notes; never timed
# The settings worth showing per row (the full XGBoost parameter list is long).
PARAM_KEYS = ("n_estimators", "max_depth", "learning_rate", "subsample", "colsample_bytree",
              "min_child_weight", "scale_pos_weight", "class_weight", "min_samples_leaf",
              "max_features", "max_samples", "contamination", "hidden", "bottleneck", "dropout", "lr")

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
    if model in UNSUPERVISED:
        from src.models_unsupervised import train_and_score
        return train_and_score(df, model, save=False, columns=columns)
    if model in SUPERVISED:
        from src.models_supervised import train_and_score_supervised
        return train_and_score_supervised(df, model, save=False, columns=columns)
    raise ValueError(f"unknown model {model!r}; choose from {SUPERVISED + UNSUPERVISED}")


def _settings(info) -> str:
    """The model settings a run used, as compact JSON (for the `params` column)."""
    params = {k: v for k, v in info["params"].items() if k in PARAM_KEYS and v is not None}
    if info.get("best_iteration") is not None:
        params["best_iteration"] = info["best_iteration"]
    return json.dumps(params, default=str, sort_keys=True)


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run_ablation(df, models=MODELS, k=0.01, save=True) -> pd.DataFrame:
    """One row per model x feature set: test PR-AUC, ROC-AUC, recall at the top-k budget and at the
    best-F1 threshold (S22 step 3), the change in test PR-AUC against the full set, and the model
    settings + commit that produced the row."""
    top = f"recall_top_{100 * k:g}pct"
    commit = _commit()
    rows = []
    for name, columns in feature_sets(feature_columns(df)).items():
        if not columns:
            raise ValueError(f"feature set {name} is empty")
        for model in models:
            scores, info = _scores(df, model, columns)
            r = evaluate_df(scores, k)
            rows.append({"model": model, "feature_set": name, "n_features": len(columns),
                         "test_pr_auc": r["ranking"]["pr_auc"], "test_roc_auc": r["ranking"]["roc_auc"],
                         top: r["operating_points"]["top_1pct"]["recall"],
                         "recall_best_f1": r["operating_points"]["best_f1"]["recall"],
                         "fit_seconds": round(info["fit_seconds"], 2),
                         "params": _settings(info), "commit": commit})
    table = pd.DataFrame(rows)
    full = table[table["feature_set"] == "c_full"].set_index("model")["test_pr_auc"]
    table.insert(table.columns.get_loc("fit_seconds"), "delta_pr_auc_vs_full",
                 table["test_pr_auc"] - table["model"].map(full))
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        table.to_csv(TABLES_DIR / TABLE, index=False)
    return table


def machine() -> dict:
    """CPU, threads and RAM of this machine, for the T8 footnote."""
    info = {"cpu": platform.processor() or platform.machine(), "threads": os.cpu_count()}
    try:
        import psutil
        info["ram_gb"] = round(psutil.virtual_memory().total / 2**30, 1)
    except ImportError:
        info["ram_gb"] = None
    return info


def data_processing_time(repeats=3, save=True) -> pd.DataFrame:
    """Wall-clock time from the Parquet logs to feature table v1, for T8 (detection time): labels,
    the one pass over the 28.4M-row web log, and v1 (behavior features + baselines), each the mean
    of `repeats` runs (like the model timings). The one-off archive conversion is listed as an
    estimate (`measured` = False): it was not timed on Nov 3 and is not re-run here."""
    from src import features, labels

    if not (PARQUET_DIR / "http.parquet").is_file():
        raise FileNotFoundError("data/parquet/http.parquet is needed (Supriye's machine only)")
    totals = {"labels (S6)": 0.0, "web-log pass, 28.4M rows (S15)": 0.0,
              "feature table v1 incl. baselines (S10-S18)": 0.0}
    names = list(totals)
    for _ in range(repeats):
        started = time.perf_counter()
        lab, _, _ = labels.build_labels()
        totals[names[0]] += time.perf_counter() - started
        started = time.perf_counter()
        features.http_user_day_domains(refresh=True)
        totals[names[1]] += time.perf_counter() - started
        started = time.perf_counter()
        table, _ = features.build_v1(lab)
        totals[names[2]] += time.perf_counter() - started
    rows = [{"step": "archive -> Parquet conversion (S4, one-off; estimate ~10 min, not timed)",
             "seconds": CONVERSION_SECONDS, "runs": 0, "measured": False}]
    rows += [{"step": name, "seconds": round(total / repeats, 2), "runs": repeats, "measured": True}
             for name, total in totals.items()]
    out = pd.DataFrame(rows)
    out["user_days"] = len(table)
    out["seconds_per_1000_user_days"] = (1000 * out["seconds"] / len(table)).round(4)
    for key, value in machine().items():
        out[key] = value
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        out.to_csv(TABLES_DIR / TIME_TABLE, index=False)
    return out


def main(argv):
    if argv[:1] == ["time"]:
        print(data_processing_time().to_string(index=False))
    elif argv[:1] in ([], ["run"]):
        from src.config import PROCESSED_DIR
        df = pd.read_parquet(PROCESSED_DIR / "features_v1.parquet")
        print(run_ablation(df).round(4).to_string(index=False))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
