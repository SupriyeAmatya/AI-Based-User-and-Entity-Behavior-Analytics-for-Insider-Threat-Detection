"""Supervised detectors (owner: Ayo; Y7 models, Y9 tuning, Y10 imbalance experiment, Y12 LOSO).

Usage:
    from src.models_supervised import train_and_score_supervised
    scores, info = train_and_score_supervised(df, "random_forest")    # df = feature table (TEAM_PLAN 5.1)
    scores, info = train_and_score_supervised(df, "xgboost")

Same inputs and outputs as Arva's train_and_score():
- inputs come from get_model_matrix() (TEAM_PLAN 5.5), inside a Pipeline whose StandardScaler is
  fitted on the training rows only (trees don't need scaling; it is kept for consistency);
- it trains on **all** split == "train" rows, malicious ones included (TEAM_PLAN 5.4);
- it scores every row with P(malicious), higher = more suspicious, and saves
  results/scores/<model_name>.parquet with user, date, split, label, scenario, score (TEAM_PLAN 5.2).
XGBoost stops early on the val rows (eval_metric="aucpr", 50 rounds).

Tuning (Y9) and the imbalance experiment (Y10) evaluate on val only and log to results/tables/:
    log, best = tune_supervised(df, "xgboost")       # -> tuning_log_supervised.csv
    table = imbalance_experiment(df)                 # -> imbalance.csv

Final set-up and tuning on v1 (Y14): SMOTE on the training rows only (Y10 decision), the Y9 grids,
best settings by val PR-AUC -> results/tables/best_params_supervised.json:
    python -m src.models_supervised tune v1

Leave-one-scenario-out (Y12), the "unseen anomaly" experiment:
    scores, metrics = run_loso(df, "xgboost", held_out=2)   # -> results/scores/xgboost_loso_s2.parquet
    table = loso_table(df, unsupervised={"iforest": iforest_scores})

Demo on Arva's synthetic features (the Y7 "done when" check):
    python -m src.models_supervised demo
"""
import json
import sys
import time

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.config import PROCESSED_DIR, RANDOM_STATE, SCORES_DIR, TABLES_DIR
from src.evaluate import ranking_metrics, threshold_metrics, threshold_top_k
from src.features import get_model_matrix

SCORE_KEYS = ["user", "date", "split", "label", "scenario"]
MODELS = ("random_forest", "xgboost")
RF_DEFAULTS = {"n_estimators": 300, "class_weight": "balanced", "n_jobs": -1,
               "random_state": RANDOM_STATE}
XGB_DEFAULTS = {"n_estimators": 1000, "max_depth": 6, "learning_rate": 0.05, "subsample": 0.8,
                "colsample_bytree": 0.8, "eval_metric": "aucpr", "early_stopping_rounds": 50,
                "random_state": RANDOM_STATE, "n_jobs": -1}
# Y9 grids (the card's). XGB's number of trees comes from early stopping.
RF_GRID = {"n_estimators": [200, 500], "max_depth": [None, 10, 20], "min_samples_leaf": [1, 5],
           "max_features": ["sqrt", 0.5]}
XGB_GRID = {"max_depth": [3, 6], "learning_rate": [0.05, 0.1], "subsample": [0.8, 1.0],
            "min_child_weight": [1, 5]}
GRIDS = {"random_forest": RF_GRID, "xgboost": XGB_GRID}
TUNING_LOG = "tuning_log_supervised.csv"
IMBALANCE_TABLE = "imbalance.csv"
SMOTE_RATIO = 0.1


def _estimator(model_name, params, n_pos, n_neg, weighting=True):
    """The classifier with the card settings, `params` on top. weighting=False drops the class
    weights (Y10 set-ups a and c)."""
    if model_name == "random_forest":
        p = {**RF_DEFAULTS, **params}
        if not weighting:
            p["class_weight"] = None
        return RandomForestClassifier(**p)
    if model_name == "xgboost":
        p = {**XGB_DEFAULTS, "scale_pos_weight": n_neg / max(n_pos, 1) if weighting else 1.0,
             **params}
        return XGBClassifier(**p)
    raise ValueError(f"unknown model {model_name!r}; choose from {MODELS}")


def fit_pipeline(model_name, X_train, y_train, X_val=None, y_val=None, params=None,
                 weighting=True, smote=False):
    """Fit scaler (+ SMOTE) + classifier on the training rows. SMOTE sits inside an imblearn
    Pipeline, so oversampling happens only during fit and never touches val or test (Y10)."""
    n_pos, n_neg = int(y_train.sum()), int(len(y_train) - y_train.sum())
    model = _estimator(model_name, params or {}, n_pos, n_neg, weighting and not smote)
    scaler = StandardScaler().fit(X_train)
    steps = [("scaler", scaler)]
    if smote:
        steps.append(("smote", SMOTE(sampling_strategy=SMOTE_RATIO, random_state=RANDOM_STATE)))
    steps.append(("model", model))
    pipeline = (ImbPipeline if smote else Pipeline)(steps)
    fit_params = {}
    if model_name == "xgboost":
        if X_val is None or y_val is None or not len(X_val):
            raise ValueError("xgboost needs val rows for early stopping")
        fit_params = {"model__eval_set": [(scaler.transform(X_val), y_val)], "model__verbose": False}
    pipeline.fit(X_train, y_train, **fit_params)
    return pipeline


def predict_scores(pipeline, X) -> np.ndarray:
    """P(malicious) for each row. Without SMOTE in it, predict_proba never resamples."""
    return pipeline.predict_proba(X)[:, 1]


def train_and_score_supervised(df, model_name, params=None, save=True, save_as=None,
                               columns=None, weighting=True, smote=False, train_mask=None,
                               val_mask=None):
    """Fit on the training rows, score every row, optionally save the score file.

    train_mask (default: split == "train") and val_mask (default: split == "val", used only for
    XGBoost's early stopping) restrict the rows, e.g. for LOSO (Y12).
    Returns (scores, info) like Arva's train_and_score(); info["pipeline"] is the fitted model.
    """
    if model_name not in MODELS:
        raise ValueError(f"unknown model {model_name!r}; choose from {MODELS}")
    X_all, y_all, feature_names = get_model_matrix(df, columns=columns)
    train = (df["split"] == "train") if train_mask is None else train_mask
    val = (df["split"] == "val") if val_mask is None else val_mask
    started = time.perf_counter()
    pipeline = fit_pipeline(model_name, X_all[train], y_all[train], X_all[val], y_all[val],
                            params, weighting, smote)
    fit_seconds = time.perf_counter() - started
    started = time.perf_counter()
    score = predict_scores(pipeline, X_all)
    score_seconds = time.perf_counter() - started

    scores = df[SCORE_KEYS].copy()
    scores["score"] = np.asarray(score, dtype=float)
    path = None
    if save:
        SCORES_DIR.mkdir(parents=True, exist_ok=True)
        path = SCORES_DIR / f"{save_as or model_name}.parquet"
        scores.to_parquet(path, index=False)
    model = pipeline.named_steps["model"]
    info = {"model": model_name, "params": model.get_params(), "features": feature_names,
            "n_train": int(train.sum()), "n_train_positive": int(y_all[train].sum()),
            "n_scored": len(X_all), "fit_seconds": fit_seconds, "score_seconds": score_seconds,
            "score_seconds_per_1000": 1000 * score_seconds / max(len(X_all), 1),
            "best_iteration": getattr(model, "best_iteration", None), "path": path,
            "pipeline": pipeline}
    return scores, info


# ---------------------------------------------------------------- Y9: tuning
def val_metrics(scores: pd.DataFrame, k: float = 0.01) -> dict:
    """Val-split ROC-AUC, PR-AUC and recall when the top k of val user-days are flagged."""
    val = scores[scores["split"] == "val"]
    m = ranking_metrics(val["label"], val["score"])
    recall = threshold_metrics(val["label"], val["score"], threshold_top_k(val, k))["recall"]
    return {"val_roc_auc": m["roc_auc"], "val_pr_auc": m["pr_auc"], "val_recall_top1pct": recall}


def tune_supervised(df, model_name, grid=None, dataset="v0", log_name=TUNING_LOG, save=True,
                    **kwargs):
    """Every combination of `grid` (default: the card grid), scored on val; one row per run is
    appended to results/tables/<log_name> (save=False: not written). Returns (this run's rows,
    best params by val PR-AUC). Never looks at test."""
    grid = GRIDS[model_name] if grid is None else grid
    rows = []
    for params in ParameterGrid(grid):
        scores, info = train_and_score_supervised(df, model_name, params, save=False, **kwargs)
        rows.append({"model": model_name, "dataset": dataset,
                     "params": json.dumps(params, default=str), **val_metrics(scores),
                     "best_iteration": info["best_iteration"],
                     "fit_seconds": round(info["fit_seconds"], 2),
                     "n_features": len(info["features"])})
    log = pd.DataFrame(rows)
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        path = TABLES_DIR / log_name
        log.to_csv(path, mode="a", header=not path.exists(), index=False)
    return log, json.loads(log.loc[log["val_pr_auc"].idxmax(), "params"])


# ---------------------------------------------------------------- Y10: imbalance experiment
SETUPS = {"a_no_weighting": {"weighting": False, "smote": False},
          "b_class_weights": {"weighting": True, "smote": False},
          "c_smote_train_only": {"weighting": False, "smote": True}}


def imbalance_experiment(df, models=MODELS, params=None, dataset="v0", save=True):
    """Y10: no weighting vs. class weights vs. SMOTE (training rows only), on val.
    Returns one row per model x set-up; saved as results/tables/imbalance.csv."""
    rows = []
    for model_name in models:
        for setup, options in SETUPS.items():
            scores, info = train_and_score_supervised(
                df, model_name, (params or {}).get(model_name), save=False, **options)
            rows.append({"model": model_name, "setup": setup, "dataset": dataset,
                         **val_metrics(scores), "fit_seconds": round(info["fit_seconds"], 2)})
    table = pd.DataFrame(rows)
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        table.to_csv(TABLES_DIR / IMBALANCE_TABLE, index=False)
    return table


# ---------------------------------------------------------------- Y14: final set-up, tuning on v1
# Y10 decision (Ayo, Nov 6): the final models use set-up (c), SMOTE on the training rows only and no
# class weights on top. On v0 val it was best for both models (PR-AUC RF 0.245, XGB 0.413; recall
# at top-1% 0.32 / 0.39), while class weights (b) hurt (RF 0.078, XGB 0.296). imbalance.csv.
FINAL_SETUP_NAME = "c_smote_train_only"
FINAL_SETUP = SETUPS[FINAL_SETUP_NAME]
BEST_PARAMS = "best_params_supervised.json"


def tune_final(df=None, dataset="v1", grids=None, save=True):
    """Y14: the Y9 grids (or `grids`) with FINAL_SETUP, scored on val only. Appends every run to
    the tuning log and writes the best params per model (by val PR-AUC) to
    results/tables/best_params_supervised.json. df=None loads data/processed/features_<dataset>.
    Returns {model: {"params", "setup", "dataset", "val_pr_auc", "val_roc_auc", "val_recall_top1pct"}}."""
    if df is None:
        df = pd.read_parquet(PROCESSED_DIR / f"features_{dataset}.parquet")
    best = {}
    for model_name in MODELS:
        grid = (grids or GRIDS)[model_name]
        log, params = tune_supervised(df, model_name, grid, dataset=dataset, save=save, **FINAL_SETUP)
        top = log.loc[log["val_pr_auc"].idxmax()]
        best[model_name] = {"params": params, "setup": FINAL_SETUP_NAME, "dataset": dataset,
                            **{k: float(top[k]) for k in ("val_pr_auc", "val_roc_auc",
                                                          "val_recall_top1pct")}}
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        (TABLES_DIR / BEST_PARAMS).write_text(json.dumps(best, indent=2, default=str))
    return best


# ---------------------------------------------------------------- Y12: leave-one-scenario-out
LOSO_TABLE = "loso.csv"


def loso_masks(df, held_out):
    """Rows for one LOSO run. The held-out scenario's accounts (every user with a malicious day of
    that scenario, including scenario 3's hijacked supervisor accounts) are removed from training
    and early stopping completely, normal days included, so the model never sees those people.
    Test = split == "test" with scenario 0 or `held_out`: only the unseen attack is measured."""
    held_users = set(df.loc[df["scenario"] == held_out, "user"])
    unseen = ~df["user"].isin(held_users)
    train = (df["split"] == "train") & unseen
    val = (df["split"] == "val") & unseen
    test = (df["split"] == "test") & df["scenario"].isin([0, held_out])
    return train, val, test, held_users


def loso_metrics(scores: pd.DataFrame, k: float = 0.01) -> dict:
    """PR-AUC, ROC-AUC and recall at the top k of the given rows (no val threshold needed)."""
    m = ranking_metrics(scores["label"], scores["score"])
    recall = threshold_metrics(scores["label"], scores["score"],
                               threshold_top_k(scores, k))["recall"]
    return {"n_rows": len(scores), "n_malicious": int(scores["label"].sum()),
            "pr_auc": m["pr_auc"], "roc_auc": m["roc_auc"], "recall_top1pct": recall}


def run_loso(df, model_name, params=None, held_out=1, save=True, **kwargs):
    """Train without scenario `held_out`, score its test rows (Y12 step 1). Saves the scored test
    rows as results/scores/<model>_loso_s<held_out>.parquet. Returns (scores, metrics)."""
    train, val, test, held_users = loso_masks(df, held_out)
    scores, info = train_and_score_supervised(df, model_name, params, save=False,
                                              train_mask=train, val_mask=val, **kwargs)
    scores = scores[test.to_numpy()]
    if save:
        SCORES_DIR.mkdir(parents=True, exist_ok=True)
        scores.to_parquet(SCORES_DIR / f"{model_name}_loso_s{held_out}.parquet", index=False)
    metrics = {"held_out": held_out, "model": model_name, "kind": "supervised (LOSO)",
               "n_train": int(train.sum()), "held_out_accounts": len(held_users),
               **loso_metrics(scores)}
    return scores, metrics


def loso_table(df, models=MODELS, unsupervised=None, params=None, held_out=(1, 2, 3), save=True):
    """Y12 step 2: per held-out scenario, RF and XGB trained without it next to the unsupervised
    models evaluated on the same test rows (they never use labels, so every scenario is unseen
    for them). `unsupervised` maps a model name to its score DataFrame or score-file path."""
    rows = []
    for s in held_out:
        for model_name in models:
            _, metrics = run_loso(df, model_name, (params or {}).get(model_name), s, save=save)
            rows.append(metrics)
        test_keys = df.loc[loso_masks(df, s)[2], ["user", "date"]]
        for name, source in (unsupervised or {}).items():
            scores = source if isinstance(source, pd.DataFrame) else pd.read_parquet(source)
            same_rows = scores.merge(test_keys, on=["user", "date"])
            rows.append({"held_out": s, "model": name, "kind": "unsupervised",
                         **loso_metrics(same_rows)})
    table = pd.DataFrame(rows)
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        table.to_csv(TABLES_DIR / LOSO_TABLE, index=False)
    return table


# ---------------------------------------------------------------- Y13: table T4 draft
def hyperparameter_table(log_name=TUNING_LOG, name="T4_hyperparameters_supervised.csv",
                         dataset=None):
    """Draft of table T4 for RF and XGB: card settings, grid searched and the best run so far by
    val PR-AUC (from the tuning log; only `dataset`'s runs if given, e.g. "v1"), saved to
    results/tables/<name>."""
    path = TABLES_DIR / log_name
    log = pd.read_csv(path) if path.exists() else pd.DataFrame()
    if dataset is not None and len(log):
        log = log[log["dataset"] == dataset]
    rows = []
    for model, defaults in (("random_forest", RF_DEFAULTS), ("xgboost", XGB_DEFAULTS)):
        row = {"model": model,
               "defaults": json.dumps({k: v for k, v in defaults.items()
                                       if k not in ("random_state", "n_jobs")}, default=str),
               "grid": json.dumps(GRIDS[model], default=str)}
        runs = log[log["model"] == model] if len(log) else log
        if len(runs):
            best = runs.loc[runs["val_pr_auc"].idxmax()]
            row.update({"best_params": best["params"], "dataset": best["dataset"],
                        "val_pr_auc": best["val_pr_auc"], "val_roc_auc": best["val_roc_auc"],
                        "runs": len(runs)})
        rows.append(row)
    table = pd.DataFrame(rows)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / name, index=False)
    return table


def demo():
    """Y7 check: both models on Arva's synthetic features, then evaluate_file() on the score files."""
    from src.evaluate import evaluate_file
    from src.synthetic import make_synthetic_features

    df = make_synthetic_features()
    for name in MODELS:
        scores, info = train_and_score_supervised(df, name, save_as=f"{name}_synthetic")
        result = evaluate_file(info["path"])
        print(f"{name:14s} test ROC-AUC {result['ranking']['roc_auc']:.3f}, PR-AUC "
              f"{result['ranking']['pr_auc']:.3f} | trained on {info['n_train']} rows "
              f"({info['n_train_positive']} malicious) in {info['fit_seconds']:.1f}s"
              + (f", best iteration {info['best_iteration']}" if info["best_iteration"] is not None else "")
              + f" | saved {info['path']}")


if __name__ == "__main__":
    if sys.argv[1:] == ["demo"]:
        demo()
    elif sys.argv[1:2] == ["tune"]:                       # Y14: python -m src.models_supervised tune v1
        version = sys.argv[2] if len(sys.argv) > 2 else "v1"
        print(json.dumps(tune_final(dataset=version), indent=2, default=str))
        print(hyperparameter_table(dataset=version).to_string())
    else:
        print(__doc__)
