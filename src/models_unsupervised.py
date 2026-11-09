"""Unsupervised detectors (owner: Arva; A4 skeleton, A5 Isolation Forest, A6 autoencoder, A8 extras,
A13 One-Class SVM).

Usage:
    from src.models_unsupervised import train_and_score
    scores, info = train_and_score(df, "iforest")                     # df = feature table (TEAM_PLAN 5.1)
    scores, info = train_and_score(df, "autoencoder", {"epochs": 30})
    scores, info = train_and_score(df, "iforest", train_on="all")     # A8: saved as iforest_contam
    errors = info["detector"].feature_errors(X)                       # A8: AE error per feature

Every detector follows the team rules:
- inputs come from get_model_matrix() (TEAM_PLAN 5.5), and StandardScaler is fitted on the training
  rows only;
- it trains on split == "train" and label == 0 (TEAM_PLAN 5.4); the A8 contamination variant
  (train_on="all") trains on every training row, malicious ones included, and is saved as
  <model_name>_contam;
- it scores every row, higher = more suspicious, and the scores are saved to
  results/scores/<model_name>.parquet with user, date, split, label, scenario, score (TEAM_PLAN 5.2).
`info` holds the fit and scoring times, for detection time (a) in A17.

Demo on synthetic data (the A5 and A6 "done when" checks):
    python -m src.models_unsupervised demo

Tuning (A9-A10): one call runs a whole grid, scores the val split and appends one row per run
to the tuning log results/tables/tuning_log_unsupervised.csv; the best run is the one with the
highest val PR-AUC (never test, never accuracy):
    log, best = tune(df, "iforest")                    # IF_GRID, 18 runs
    log, best = tune(df, "autoencoder", dataset="v0")  # AE_GRID, 16 runs
    clear_log("v1")                                    # A15: before re-running v1; v0 rows stay

Final score files (A16), every row, with the detector defaults:
    python -m src.models_unsupervised final                                        # features_v1
    python -m src.models_unsupervised final data/processed/features_v1_1.parquet

Extra results for Ayo (A17) from those score files -> results/tables/unsupervised_extra.csv:
    python -m src.models_unsupervised extra [features]
"""
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import joblib
import psutil

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from torch import nn

from src.config import FIGURES_DIR, PROCESSED_DIR, RANDOM_STATE, SCORES_DIR, TABLES_DIR
from src.evaluate import evaluate_file, ranking_metrics, threshold_metrics, threshold_top_k
from src.features import get_model_matrix

SCORE_KEYS = ["user", "date", "split", "label", "scenario"]

# On macOS, PyTorch and xgboost (src/models_supervised.py) each load their own copy of the OpenMP
# runtime. Once xgboost has run, a multi-threaded PyTorch step in the same process waits forever
# (e.g. `python -m pytest tests` stalled in the autoencoder tests). This small network trains just
# as fast on one thread, so PyTorch always uses one.
torch.set_num_threads(1)


# ---------------------------------------------------------------- A4: common interface
class UnsupervisedDetector:
    """fit() on normal training rows, score() any rows; higher score = more suspicious."""

    name = "base"
    card = {}       # the values suggested in the task card, kept for table T4 (A16 step 2)
    defaults = {}   # the values every run uses unless params override them

    def __init__(self, **params):
        unknown = set(params) - set(self.defaults)
        if unknown:
            raise ValueError(f"{self.name}: unknown parameters {sorted(unknown)}")
        self.params = {**self.defaults, **params}

    def fit(self, X_train_normal, X_val_normal=None):
        raise NotImplementedError

    def score(self, X) -> np.ndarray:
        raise NotImplementedError


# ---------------------------------------------------------------- A5: Isolation Forest
class IsolationForestDetector(UnsupervisedDetector):
    name = "iforest"
    card = {"n_estimators": 200, "max_samples": "auto", "max_features": 1.0,
            "contamination": "auto", "random_state": RANDOM_STATE}           # A5 card
    # PROVISIONAL (A16, Arva): replace with the best v1 setting by val PR-AUC.
    defaults = dict(card)

    def fit(self, X_train_normal, X_val_normal=None):
        self.pipeline = Pipeline([("scaler", StandardScaler()),
                                  ("model", IsolationForest(n_jobs=-1, **self.params))])
        self.pipeline.fit(X_train_normal)
        return self

    def score(self, X):
        return -self.pipeline.decision_function(X)


# ---------------------------------------------------------------- A6: autoencoder
class AutoencoderDetector(UnsupervisedDetector):
    """Dense autoencoder: n -> 64 -> 32 -> 16 -> 32 -> 64 -> n, ReLU, linear output (A6 card).

    Trained with MSE and Adam; early stopping on the validation normal rows (patience 5) keeps
    the best epoch. score() = mean squared reconstruction error per row.
    """

    name = "autoencoder"
    card = {"hidden": (64, 32), "bottleneck": 16, "dropout": 0.0, "lr": 1e-3,
            "batch_size": 256, "epochs": 50, "patience": 5, "seed": RANDOM_STATE}  # A6 card
    # PROVISIONAL (A16, Arva): replace with the best v1 setting by val PR-AUC.
    defaults = dict(card)

    def _network(self, n_features):
        sizes = [n_features, *self.params["hidden"], self.params["bottleneck"]]
        layers = []
        for a, b in zip(sizes[:-1], sizes[1:]):                      # encoder
            layers += [nn.Linear(a, b), nn.ReLU()]
            if self.params["dropout"]:
                layers.append(nn.Dropout(self.params["dropout"]))
        back = sizes[::-1]
        for i, (a, b) in enumerate(zip(back[:-1], back[1:])):        # decoder, linear output
            layers.append(nn.Linear(a, b))
            if i < len(back) - 2:
                layers.append(nn.ReLU())
        return nn.Sequential(*layers)

    def _tensor(self, X):
        return torch.tensor(self.scaler.transform(X), dtype=torch.float32)

    def fit(self, X_train_normal, X_val_normal=None):
        seed = self.params["seed"]
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.scaler = StandardScaler().fit(X_train_normal)
        train = self._tensor(X_train_normal)
        val = self._tensor(X_val_normal) if X_val_normal is not None and len(X_val_normal) else None
        self.network = self._network(train.shape[1])
        optimizer = torch.optim.Adam(self.network.parameters(), lr=self.params["lr"])
        loss_fn = nn.MSELoss()
        generator = torch.Generator().manual_seed(seed)
        self.history = {"train_loss": [], "val_loss": []}
        best, best_state, waited = float("inf"), None, 0
        for _ in range(self.params["epochs"]):
            self.network.train()
            order = torch.randperm(len(train), generator=generator)
            total = 0.0
            for start in range(0, len(train), self.params["batch_size"]):
                batch = train[order[start:start + self.params["batch_size"]]]
                optimizer.zero_grad()
                loss = loss_fn(self.network(batch), batch)
                loss.backward()
                optimizer.step()
                total += loss.item() * len(batch)
            self.history["train_loss"].append(total / len(train))
            monitored = self._mean_loss(val) if val is not None else self.history["train_loss"][-1]
            self.history["val_loss"].append(monitored if val is not None else float("nan"))
            if monitored < best - 1e-6:
                best, waited = monitored, 0
                best_state = {k: v.detach().clone() for k, v in self.network.state_dict().items()}
            else:
                waited += 1
                if waited >= self.params["patience"]:
                    break
        self.network.load_state_dict(best_state)
        self.best_epoch = int(np.argmin(self.history["val_loss"] if val is not None
                                        else self.history["train_loss"])) + 1
        return self

    def _errors(self, tensor):
        self.network.eval()
        with torch.no_grad():
            return ((self.network(tensor) - tensor) ** 2).numpy()

    def _mean_loss(self, tensor):
        return float(self._errors(tensor).mean())

    def score(self, X):
        return self._errors(self._tensor(X)).mean(axis=1)

    def feature_residuals(self, X) -> pd.DataFrame:
        """Scaled input minus its reconstruction, per feature: > 0 where the value was higher than
        the autoencoder expected (A12 uses this to name only above-normal features)."""
        tensor = self._tensor(X)
        self.network.eval()
        with torch.no_grad():
            residuals = (tensor - self.network(tensor)).numpy()
        columns = X.columns if isinstance(X, pd.DataFrame) else None
        index = X.index if isinstance(X, pd.DataFrame) else None
        return pd.DataFrame(residuals, index=index, columns=columns)

    def feature_errors(self, X) -> pd.DataFrame:
        """Squared reconstruction error per feature, same shape as X (A8 step 1). Its row mean is
        score(X); the largest entries say which features the autoencoder found unusual (A12)."""
        return self.feature_residuals(X) ** 2


# ---------------------------------------------------------------- A13: One-Class SVM (optional)
class OneClassSVMDetector(UnsupervisedDetector):
    """RBF One-Class SVM in the same scaler pipeline. It scales poorly with rows, so it is fitted on
    a random sample of at most `max_train` normal training rows (A13 card: 20,000)."""

    name = "ocsvm"
    card = {"nu": 0.01, "gamma": "scale", "kernel": "rbf", "max_train": 20_000,
            "random_state": RANDOM_STATE}                                     # A13 card
    defaults = dict(card)

    def fit(self, X_train_normal, X_val_normal=None):
        p = self.params
        if len(X_train_normal) > p["max_train"]:
            X_train_normal = X_train_normal.sample(p["max_train"], random_state=p["random_state"])
        self.n_fitted = len(X_train_normal)
        self.pipeline = Pipeline([("scaler", StandardScaler()),
                                  ("model", OneClassSVM(kernel=p["kernel"], nu=p["nu"],
                                                        gamma=p["gamma"]))])
        self.pipeline.fit(X_train_normal)
        return self

    def score(self, X):
        return -self.pipeline.decision_function(X)


DETECTORS = {d.name: d for d in (IsolationForestDetector, AutoencoderDetector, OneClassSVMDetector)}


# ---------------------------------------------------------------- A11: saving trained detectors
def save_detector(detector, path):
    """Isolation Forest -> joblib.dump; autoencoder -> torch.save of its weights, parameters and
    scaler (plain tensors and lists, so torch.load(weights_only=True) can read it back)."""
    if isinstance(detector, AutoencoderDetector):
        torch.save({"params": detector.params, "state_dict": detector.network.state_dict(),
                    "scaler_mean": detector.scaler.mean_.tolist(),
                    "scaler_scale": detector.scaler.scale_.tolist(),
                    "feature_names": list(getattr(detector, "feature_names", []) or []),
                    "history": detector.history, "best_epoch": detector.best_epoch}, path)
    else:
        joblib.dump(detector, path)


def load_detector(path):
    """Inverse of save_detector()."""
    path = Path(path)
    if path.suffix != ".pt":
        return joblib.load(path)
    saved = torch.load(path, weights_only=True)
    detector = AutoencoderDetector(**saved["params"])
    names = saved["feature_names"]
    scaler = StandardScaler()
    scaler.mean_ = np.array(saved["scaler_mean"])
    scaler.scale_ = np.array(saved["scaler_scale"])
    scaler.var_ = scaler.scale_ ** 2
    scaler.n_features_in_ = len(scaler.mean_)
    if names:
        scaler.feature_names_in_ = np.array(names, dtype=object)
    detector.scaler = scaler
    detector.network = detector._network(len(scaler.mean_))
    detector.network.load_state_dict(saved["state_dict"])
    detector.feature_names, detector.history = names, saved["history"]
    detector.best_epoch = saved["best_epoch"]
    return detector


# ---------------------------------------------------------------- A4: train and score
def train_and_score(df, model_name, params=None, save=True, save_as=None, train_on="normal",
                    columns=None):
    """Fit `model_name` on training rows, score every row, optionally save the score file.

    train_on="normal" (TEAM_PLAN 5.4) fits on split == "train" & label == 0 and stops the AE early
    on the normal val rows. train_on="all" (A8 contamination variant) uses no labels at all: it fits
    on every train row and stops early on every val row, and saves as <model_name>_contam.
    columns: feature subset passed to get_model_matrix() (default: every model input).

    Returns (scores, info). scores has TEAM_PLAN 5.2 columns; info has the timings (A17).
    save_as overrides the file name (e.g. "iforest_synthetic"), so demo runs never overwrite
    the real results/scores/<model_name>.parquet.
    """
    if model_name not in DETECTORS:
        raise ValueError(f"unknown model {model_name!r}; choose from {sorted(DETECTORS)}")
    if train_on not in ("normal", "all"):
        raise ValueError(f"train_on must be 'normal' or 'all', not {train_on!r}")
    X_all, _, feature_names = get_model_matrix(df, columns=columns)
    use = df["label"] == 0 if train_on == "normal" else pd.Series(True, index=df.index)
    X_train = X_all[(df["split"] == "train") & use]
    X_val = X_all[(df["split"] == "val") & use]
    detector = DETECTORS[model_name](**(params or {}))

    started = time.perf_counter()
    detector.fit(X_train, X_val)
    fit_seconds = time.perf_counter() - started
    started = time.perf_counter()
    score = detector.score(X_all)
    score_seconds = time.perf_counter() - started

    scores = df[SCORE_KEYS].copy()
    scores["score"] = np.asarray(score, dtype=float)
    path = None
    if save:
        SCORES_DIR.mkdir(parents=True, exist_ok=True)
        default = model_name if train_on == "normal" else f"{model_name}_contam"
        path = SCORES_DIR / f"{save_as or default}.parquet"
        scores.to_parquet(path, index=False)
    info = {"model": model_name, "train_on": train_on, "params": detector.params,
            "features": feature_names,
            "n_train": len(X_train), "n_scored": len(X_all), "fit_seconds": fit_seconds,
            "score_seconds": score_seconds,
            "score_seconds_per_1000": 1000 * score_seconds / max(len(X_all), 1),
            "path": path, "detector": detector}
    return scores, info


# ---------------------------------------------------------------- A9-A10: tuning
IF_GRID = {"n_estimators": [100, 200, 500], "max_samples": [256, 1024, "auto"],
           "max_features": [0.5, 1.0]}
AE_GRID = {"bottleneck": [8, 16], "hidden": [(64, 32), (128, 64)], "dropout": [0.0, 0.1],
           "lr": [1e-3, 1e-4]}
GRIDS = {"iforest": IF_GRID, "autoencoder": AE_GRID}
TUNING_LOG = "tuning_log_unsupervised.csv"


def val_metrics(scores: pd.DataFrame, k: float = 0.01) -> dict:
    """Val-split ROC-AUC, PR-AUC and recall when the top k of val user-days are flagged."""
    val = scores[scores["split"] == "val"]
    out = {f"val_{m}": v for m, v in ranking_metrics(val["label"], val["score"]).items()
           if m != "positive_rate"}
    out["val_recall_top1pct"] = threshold_metrics(val["label"], val["score"],
                                                  threshold_top_k(val, k))["recall"]
    return out


def tune(df, model_name, grid=None, dataset="v0", fixed=None, log_name=TUNING_LOG,
         train_on="normal"):
    """Run every parameter combination of `grid` (default: the card grid), score val, and append one
    row per run to results/tables/<log_name>. Returns (this run's log rows, best params by
    val PR-AUC). `fixed` adds parameters to every run (e.g. {"epochs": 30})."""
    grid = GRIDS[model_name] if grid is None else grid
    rows = []
    for params in ParameterGrid(grid):
        params = {**(fixed or {}), **params}
        scores, info = train_and_score(df, model_name, params, save=False, train_on=train_on)
        rows.append({"model": model_name, "dataset": dataset, "train_on": train_on,
                     "params": json.dumps(params, default=str), **val_metrics(scores),
                     "fit_seconds": round(info["fit_seconds"], 2), "n_train": info["n_train"],
                     "n_features": len(info["features"])})
    log = pd.DataFrame(rows)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = TABLES_DIR / log_name
    old = pd.read_csv(path) if path.exists() else pd.DataFrame()
    pd.concat([old, log], ignore_index=True).to_csv(path, index=False)   # A15: columns stay aligned
    best = json.loads(log.loc[log["val_pr_auc"].idxmax(), "params"])
    if "hidden" in best:
        best["hidden"] = tuple(best["hidden"])
    return log, best


def clear_log(dataset, log_name=TUNING_LOG):
    """Remove one dataset's rows from the tuning log and keep every other dataset's rows (A15).
    The notebook calls it before re-running a dataset, so e.g. the v0 history survives a v1 run."""
    path = TABLES_DIR / log_name
    if not path.exists():
        return
    log = pd.read_csv(path)
    log[log["dataset"] != dataset].to_csv(path, index=False)


def _without_seed(params):
    return json.dumps({k: v for k, v in params.items() if k not in ("random_state", "seed")},
                      default=str)


def hyperparameter_table(log_path=None, name="T4_hyperparameters_unsupervised.csv",
                         dataset=None) -> pd.DataFrame:
    """Table T4 (A14 step 2, A15 step 3): per model, the card values, the current defaults, the grid
    searched and the best setting by val PR-AUC from the tuning log, saved to results/tables/<name>.

    Only runs trained on normal days (train_on == "normal") count, and with `dataset` (e.g. "v1")
    only that dataset's runs, so T4 shows the choice made on that dataset.
    """
    log_path = TABLES_DIR / TUNING_LOG if log_path is None else log_path
    log = pd.read_csv(log_path) if Path(log_path).exists() else pd.DataFrame()
    if len(log):
        log = log[log["train_on"] == "normal"]
        if dataset is not None:
            log = log[log["dataset"] == dataset]
    rows = []
    for model, cls in DETECTORS.items():
        row = {"model": model, "card": _without_seed(cls.card),
               "defaults": _without_seed(cls.defaults),
               "grid": json.dumps(GRIDS.get(model, {}), default=str)}
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


def plot_loss_curves(history, name="autoencoder_loss"):
    """Training and validation loss per epoch (A6 step 5), saved as PNG and PDF."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(4.5, 3))
    epochs = range(1, len(history["train_loss"]) + 1)
    ax.plot(epochs, history["train_loss"], label="train (normal days)")
    if not all(np.isnan(history["val_loss"])):
        ax.plot(epochs, history["val_loss"], label="validation (normal days)")
    ax.set(xlabel="Epoch", ylabel="MSE", title="Autoencoder loss")
    ax.legend(fontsize=8)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES_DIR / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    return fig


# ---------------------------------------------------------------- A16: final score files
# (model, train_on) of every final score file. OCSVM is optional (A13); keep or drop it is Arva's
# decision (DEC-A), so it stays in the list until then.
FINAL_RUNS = [("iforest", "normal"), ("autoencoder", "normal"),
              ("iforest", "all"), ("autoencoder", "all"), ("ocsvm", "normal")]


def final(features_path=None, df=None, params=None):
    """Write the final score files for every row with the detector defaults, no grid search (A16):
    iforest, autoencoder, iforest_contam, autoencoder_contam and ocsvm in results/scores/.
    Teammates run this themselves instead of receiving score files (TEAM_PLAN 2.5.12).

    features_path defaults to data/processed/features_v1.parquet; pass df to skip reading a file.
    params: optional {model: {parameter: value}} overrides (the tests use it to train faster).
    Returns the paths written.
    """
    if df is None:
        features_path = features_path or PROCESSED_DIR / "features_v1.parquet"
        df = pd.read_parquet(features_path)
    paths = []
    for model, train_on in FINAL_RUNS:
        _, info = train_and_score(df, model, (params or {}).get(model), train_on=train_on)
        print(f"{info['path'].name:28s} {info['n_scored']:,} rows scored, "
              f"fit {info['fit_seconds']:.1f}s on {info['n_train']:,} rows")
        paths.append(info["path"])
    return paths


# ---------------------------------------------------------------- A17: extra results for Ayo (M3)
EXTRA_TABLE = "unsupervised_extra.csv"
OPERATING_POINTS = ("best_f1", "top_1pct")


def alerts_per_day(scores: pd.DataFrame, threshold) -> float:
    """Mean number of flagged user-days (score >= threshold) per test day."""
    test = scores[scores["split"] == "test"]
    return int((test["score"] >= threshold).sum()) / test["date"].nunique()


def cpu_name() -> str:
    """The processor's name, e.g. "Apple M2" (macOS) or "Intel64 Family 6 ..." (Windows)."""
    if platform.system() == "Darwin":
        result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                capture_output=True, text=True)
        if result.stdout.strip():
            return result.stdout.strip()
    return platform.processor() or platform.machine()


def timing(df, model, repeats=3, train_on="normal") -> dict:
    """Detection time (a): mean fit seconds and inference seconds per 1,000 user-days over
    `repeats` runs (time.perf_counter() inside train_and_score), plus the machine it ran on."""
    runs = [train_and_score(df, model, save=False, train_on=train_on)[1] for _ in range(repeats)]
    return {"fit_seconds": float(np.mean([r["fit_seconds"] for r in runs])),
            "score_seconds_per_1000": float(np.mean([r["score_seconds_per_1000"] for r in runs])),
            "timing_runs": repeats,
            "cpu": cpu_name(),
            "cores": psutil.cpu_count(logical=False), "threads": psutil.cpu_count(logical=True),
            "ram_gb": round(psutil.virtual_memory().total / 1e9, 1)}


def results_extra(df, repeats=3, save=True) -> pd.DataFrame:
    """One row per final score file in results/scores/ (A17); missing files are skipped.

    Columns: test PR-AUC and ROC-AUC; precision, recall and user-level recall at best-F1 and
    top-1%; recall per scenario at both thresholds and PR-AUC per scenario; alerts per test day at
    both thresholds; contam_delta_pr_auc (<model>_contam PR-AUC minus <model> PR-AUC, on the
    <model> row); and the timing() columns, measured on the feature table df.
    Saved to results/tables/unsupervised_extra.csv.
    """
    rows = []
    for model, train_on in FINAL_RUNS:
        name = model if train_on == "normal" else f"{model}_contam"
        path = SCORES_DIR / f"{name}.parquet"
        if not path.exists():
            print(f"skipped {name}: no {path.name} (run `python -m src.models_unsupervised final`)")
            continue
        result = evaluate_file(path)
        scores = pd.read_parquet(path)
        row = {"model": name, "test_pr_auc": result["ranking"]["pr_auc"],
               "test_roc_auc": result["ranking"]["roc_auc"]}
        for op in OPERATING_POINTS:
            point = result["operating_points"][op]
            row.update({f"precision_{op}": point["precision"], f"recall_{op}": point["recall"],
                        f"user_recall_{op}": point["user_recall"],
                        f"alerts_per_day_{op}": alerts_per_day(scores, result["thresholds"][op])})
        for s in (1, 2, 3):
            per = result["per_scenario"].get(s, {})
            for op in OPERATING_POINTS:
                row[f"s{s}_recall_{op}"] = per.get(f"recall_{op}", np.nan)
            row[f"s{s}_pr_auc"] = per.get("pr_auc", np.nan)
        row.update(timing(df, model, repeats, train_on))
        rows.append(row)
    table = pd.DataFrame(rows)
    if len(table):
        pr_auc = table.set_index("model")["test_pr_auc"]
        table["contam_delta_pr_auc"] = [pr_auc.get(f"{m}_contam", np.nan) - pr_auc[m]
                                        if not m.endswith("_contam") else np.nan
                                        for m in table["model"]]
    if save:
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        table.to_csv(TABLES_DIR / EXTRA_TABLE, index=False)
    return table


def demo():
    """A5/A6 checks on synthetic data: ROC-AUC of both detectors and the autoencoder loss curve."""
    from src.synthetic import make_synthetic_features

    df = make_synthetic_features()
    for name in DETECTORS:
        scores, info = train_and_score(df, name, save_as=f"{name}_synthetic")
        test = scores[scores["split"] == "test"]
        normal, bad = scores.loc[scores["label"] == 0, "score"], scores.loc[scores["label"] == 1, "score"]
        print(f"{name:12s} ROC-AUC all rows {roc_auc_score(scores['label'], scores['score']):.3f}, "
              f"test {roc_auc_score(test['label'], test['score']):.3f} | mean score normal "
              f"{normal.mean():.3f} vs malicious {bad.mean():.3f} | trained on {info['n_train']} rows "
              f"in {info['fit_seconds']:.1f}s | saved {info['path']}")
        if name == "autoencoder":
            h = info["detector"].history
            print(f"{'':12s} epochs run {len(h['train_loss'])}, best epoch {info['detector'].best_epoch}, "
                  f"train loss {h['train_loss'][0]:.3f} -> {h['train_loss'][-1]:.3f}, "
                  f"val loss {h['val_loss'][0]:.3f} -> {min(h['val_loss']):.3f}")
            plot_loss_curves(h, "autoencoder_loss_synthetic")


if __name__ == "__main__":
    if sys.argv[1:] == ["demo"]:
        demo()
    elif sys.argv[1:2] == ["final"] and len(sys.argv) <= 3:
        final(*sys.argv[2:])
    elif sys.argv[1:2] == ["extra"] and len(sys.argv) <= 3:
        features = sys.argv[2] if len(sys.argv) == 3 else PROCESSED_DIR / "features_v1.parquet"
        print(results_extra(pd.read_parquet(features)).round(4).to_string(index=False))
    else:
        print(__doc__)
