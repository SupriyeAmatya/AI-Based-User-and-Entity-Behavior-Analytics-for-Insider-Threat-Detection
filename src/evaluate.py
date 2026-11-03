"""Evaluation used by every model in the project (owner: Ayo; tasks Y3–Y6).

Usage:
    from src.evaluate import evaluate_file, compare_files
    results = evaluate_file("results/scores/iforest.parquet")
    table = compare_files(["results/scores/iforest.parquet", "results/scores/xgboost.parquet"])

A score file follows TEAM_PLAN 5.2: one row per user-day with the columns
user, date, split, label, scenario, score  (higher score = more suspicious).

Thresholds follow TEAM_PLAN 5.6:
    best_f1   - the threshold that maximises F1 on the val split, applied unchanged to test
    top_1pct  - flag the top 1% of test user-days (fixed analyst alert budget)
All reported numbers are on the test split (TEAM_PLAN 10.2).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

from src.config import FIGURES_DIR, RANDOM_STATE

# One fixed color per model so every figure in the paper matches (Y5 step 4).
MODEL_COLORS = {
    "iforest": "#1f77b4",
    "autoencoder": "#ff7f0e",
    "ocsvm": "#9467bd",
    "random_forest": "#2ca02c",
    "xgboost": "#d62728",
    "iforest_contam": "#aec7e8",
    "autoencoder_contam": "#ffbb78",
}
OPERATING_POINTS = ["best_f1", "top_1pct"]
SCORE_COLUMNS = ["user", "date", "split", "label", "scenario", "score"]


# ---------------------------------------------------------------- core metrics (Y3)
def threshold_metrics(y_true, scores, threshold) -> dict:
    """Confusion-matrix metrics when every score >= threshold is flagged."""
    y = np.asarray(y_true).astype(int)
    flagged = np.asarray(scores) >= threshold
    tp = int(np.sum(flagged & (y == 1)))
    fp = int(np.sum(flagged & (y == 0)))
    tn = int(np.sum(~flagged & (y == 0)))
    fn = int(np.sum(~flagged & (y == 1)))

    def ratio(a, b):
        return a / b if b else 0.0  # zero_division=0

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    return {
        "accuracy": ratio(tp + tn, tp + tn + fp + fn),
        "precision": precision,
        "recall": recall,
        "f1": ratio(2 * precision * recall, precision + recall),
        "fpr": ratio(fp, fp + tn),
        "fnr": ratio(fn, fn + tp),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


def ranking_metrics(y_true, scores) -> dict:
    """Threshold-free metrics. ROC-AUC/PR-AUC are NaN when only one class is present."""
    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores)
    both_classes = 0 < y.sum() < len(y)
    return {
        "roc_auc": roc_auc_score(y, s) if both_classes else float("nan"),
        "pr_auc": average_precision_score(y, s) if both_classes else float("nan"),
        "positive_rate": float(y.mean()) if len(y) else float("nan"),
    }


# ---------------------------------------------------------------- thresholds (Y4)
def threshold_best_f1(val_df: pd.DataFrame) -> float:
    """Score threshold with the highest F1 on the val rows.

    If val has no malicious rows the threshold flags nothing (+inf).
    """
    y, s = val_df["label"].to_numpy(), val_df["score"].to_numpy()
    if y.sum() == 0:
        return float("inf")
    precision, recall, thresholds = precision_recall_curve(y, s)
    # precision/recall have one more entry than thresholds; the last point has no threshold
    p, r = precision[:-1], recall[:-1]
    f1 = np.divide(2 * p * r, p + r, out=np.zeros_like(p), where=(p + r) > 0)
    return float(thresholds[int(np.argmax(f1))])


def threshold_top_k(test_df: pd.DataFrame, k: float = 0.01) -> float:
    """Threshold that flags the top k share of test user-days (k=0.01 -> top 1%)."""
    return float(np.quantile(test_df["score"].to_numpy(), 1 - k))


# ---------------------------------------------------------------- insider-level metrics (Y6)
def detection_delay(test_df: pd.DataFrame, threshold: float) -> dict:
    """Days from each test insider's first malicious day to their first alert on or after it.

    An insider is any user with at least one label == 1 row in test_df.
    """
    rows = []
    malicious = test_df[test_df["label"] == 1]
    for user, mal in malicious.groupby("user"):
        d0 = mal["date"].min()
        user_rows = test_df[(test_df["user"] == user) & (test_df["date"] >= d0)]
        alerts = user_rows.loc[user_rows["score"] >= threshold, "date"]
        delay = (alerts.min() - d0).days if len(alerts) else None
        rows.append({"user": user, "scenario": int(mal["scenario"].iloc[0]),
                     "first_malicious_day": d0, "delay_days": delay})
    per_user = pd.DataFrame(rows, columns=["user", "scenario", "first_malicious_day", "delay_days"])
    detected = per_user["delay_days"].dropna()
    return {
        "n_insiders": len(per_user),
        "n_detected": int(detected.size),
        "n_missed": int(per_user["delay_days"].isna().sum()),
        "median_delay_days": float(detected.median()) if detected.size else float("nan"),
        "mean_delay_days": float(detected.mean()) if detected.size else float("nan"),
        "per_user": per_user,
    }


def user_level_recall(test_df: pd.DataFrame, threshold: float) -> float:
    """Share of test insiders flagged on at least one of their malicious days."""
    malicious = test_df[test_df["label"] == 1]
    if malicious.empty:
        return float("nan")
    caught = malicious.groupby("user")["score"].max() >= threshold
    return float(caught.mean())


# ---------------------------------------------------------------- full evaluation (Y4, Y6)
def load_scores(path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    missing = set(SCORE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing columns {sorted(missing)} (TEAM_PLAN 5.2)")
    df["date"] = pd.to_datetime(df["date"])
    return df


def evaluate_df(df: pd.DataFrame, k: float = 0.01) -> dict:
    """Evaluate one model's scores (TEAM_PLAN 5.2 format) following TEAM_PLAN 10.2."""
    val, test = df[df["split"] == "val"], df[df["split"] == "test"]
    if test.empty:
        raise ValueError("score file has no test rows")
    thresholds = {"best_f1": threshold_best_f1(val), "top_1pct": threshold_top_k(test, k)}

    result = {"thresholds": thresholds, "ranking": ranking_metrics(test["label"], test["score"]),
              "operating_points": {}, "per_scenario": {}}
    for name, t in thresholds.items():
        point = threshold_metrics(test["label"], test["score"], t)
        delay = detection_delay(test, t)
        point.update({
            "user_recall": user_level_recall(test, t),
            "median_delay_days": delay["median_delay_days"],
            "mean_delay_days": delay["mean_delay_days"],
            "n_insiders": delay["n_insiders"],
            "n_missed": delay["n_missed"],
        })
        result["operating_points"][name] = point
        result.setdefault("delay_per_user", {})[name] = delay["per_user"]

    for s in sorted(test.loc[test["scenario"] > 0, "scenario"].unique()):
        subset = test[test["scenario"].isin([0, s])]
        result["per_scenario"][int(s)] = {
            "n_malicious_days": int(subset["label"].sum()),
            "pr_auc": ranking_metrics(subset["label"], subset["score"])["pr_auc"],
            **{f"recall_{name}": threshold_metrics(subset["label"], subset["score"], t)["recall"]
               for name, t in thresholds.items()},
        }
    return result


def evaluate_file(path, k: float = 0.01) -> dict:
    """Load a score file and evaluate it; the model name is the file name."""
    result = evaluate_df(load_scores(path), k)
    result["model"] = Path(path).stem
    return result


def compare_files(paths, k: float = 0.01) -> pd.DataFrame:
    """One row per model x operating point (table T5)."""
    rows = []
    for path in paths:
        r = evaluate_file(path, k)
        for name in OPERATING_POINTS:
            rows.append({"model": r["model"], "operating_point": name,
                         "threshold": r["thresholds"][name],
                         **r["operating_points"][name], **r["ranking"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- plots (Y5)
def _save(fig, name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES_DIR / f"{name}.{ext}", dpi=300, bbox_inches="tight")


def _color(model):
    return MODEL_COLORS.get(model)


def plot_roc(paths, name="roc_curves"):
    fig, ax = plt.subplots(figsize=(4.5, 4))
    for path in paths:
        test = load_scores(path).query("split == 'test'")
        fpr, tpr, _ = roc_curve(test["label"], test["score"])
        model = Path(path).stem
        auc = roc_auc_score(test["label"], test["score"])
        ax.plot(fpr, tpr, color=_color(model), label=f"{model} (AUC {auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="random")
    ax.set(xlabel="False positive rate", ylabel="True positive rate", title="ROC (test)")
    ax.legend(fontsize=8)
    _save(fig, name)
    return fig


def plot_pr(paths, name="pr_curves"):
    fig, ax = plt.subplots(figsize=(4.5, 4))
    base_rate = None
    for path in paths:
        test = load_scores(path).query("split == 'test'")
        precision, recall, _ = precision_recall_curve(test["label"], test["score"])
        model = Path(path).stem
        ap = average_precision_score(test["label"], test["score"])
        ax.plot(recall, precision, color=_color(model), label=f"{model} (PR-AUC {ap:.3f})")
        base_rate = test["label"].mean()
    if base_rate is not None:
        ax.axhline(base_rate, color="k", ls="--", lw=0.8, label=f"random ({base_rate:.4f})")
    ax.set(xlabel="Recall", ylabel="Precision", title="Precision-recall (test)")
    ax.legend(fontsize=8)
    _save(fig, name)
    return fig


def plot_confusion(path, threshold_type="best_f1"):
    df = load_scores(path)
    r = evaluate_df(df)
    m = r["operating_points"][threshold_type]
    matrix = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
    model = Path(path).stem
    fig, ax = plt.subplots(figsize=(3.2, 3))
    ax.imshow(matrix, cmap="Blues")
    for (i, j), v in np.ndenumerate(matrix):
        ax.text(j, i, f"{v:,}", ha="center", va="center",
                color="white" if v > matrix.max() / 2 else "black")
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["normal", "malicious"],
           yticklabels=["normal", "malicious"], xlabel="Predicted", ylabel="Actual",
           title=f"{model} ({threshold_type})")
    _save(fig, f"confusion_{model}_{threshold_type}")
    return fig


def plot_score_distribution(path):
    test = load_scores(path).query("split == 'test'")
    model = Path(path).stem
    fig, ax = plt.subplots(figsize=(4.5, 3))
    bins = np.histogram_bin_edges(test["score"], bins=60)
    ax.hist(test.loc[test["label"] == 0, "score"], bins=bins, alpha=0.6, label="normal")
    ax.hist(test.loc[test["label"] == 1, "score"], bins=bins, alpha=0.8, label="malicious")
    ax.set_yscale("log")
    ax.set(xlabel="Score", ylabel="User-days (log)", title=f"{model}: score distribution (test)")
    ax.legend(fontsize=8)
    _save(fig, f"score_distribution_{model}")
    return fig


# ---------------------------------------------------------------- synthetic scores for testing (Y3 step 1)
def make_synthetic_scores(n_users=50, n_days=200, seed=RANDOM_STATE) -> pd.DataFrame:
    """~10,000 user-days in TEAM_PLAN 5.2 format with ~0.5% malicious rows.

    Nine insiders (three per scenario) each have one run of 5-6 malicious days, placed so that
    train, val and test all contain every scenario. score = noise + 1.5 * label.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2010-01-04", periods=n_days, freq="D")
    users = [f"U{i:03d}" for i in range(n_users)]
    df = pd.DataFrame([(u, d) for u in users for d in dates], columns=["user", "date"])
    cut1, cut2 = dates[int(n_days * 0.60)], dates[int(n_days * 0.75)]
    df["split"] = np.where(df["date"] < cut1, "train", np.where(df["date"] < cut2, "val", "test"))
    df["label"], df["scenario"] = 0, 0
    windows = {"train": (0, int(n_days * 0.60)), "val": (int(n_days * 0.60), int(n_days * 0.75)),
               "test": (int(n_days * 0.75), n_days)}
    insiders = rng.choice(users, size=9, replace=False)
    for i, user in enumerate(insiders):
        scenario, split = i % 3 + 1, ["train", "val", "test"][i // 3]
        lo, hi = windows[split]
        length = int(rng.integers(5, 7))
        start = int(rng.integers(lo, hi - length))
        run = (df["user"] == user) & df["date"].isin(dates[start:start + length])
        df.loc[run, ["label", "scenario"]] = [1, scenario]
    df["score"] = rng.normal(size=len(df)) + 1.5 * df["label"]
    return df
