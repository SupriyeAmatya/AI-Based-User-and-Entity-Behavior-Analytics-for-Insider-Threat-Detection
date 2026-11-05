"""Unsupervised detectors (owner: Arva; A4 skeleton, A5 Isolation Forest, A6 autoencoder).

Usage:
    from src.models_unsupervised import train_and_score
    scores, info = train_and_score(df, "iforest")                     # df = feature table (TEAM_PLAN 5.1)
    scores, info = train_and_score(df, "autoencoder", {"epochs": 30})

Every detector follows the team rules:
- inputs come from get_model_matrix() (TEAM_PLAN 5.5), and StandardScaler is fitted on the training
  rows only;
- it trains on split == "train" and label == 0 (TEAM_PLAN 5.4);
- it scores every row, higher = more suspicious, and the scores are saved to
  results/scores/<model_name>.parquet with user, date, split, label, scenario, score (TEAM_PLAN 5.2).
`info` holds the fit and scoring times, for detection time (a) in A17.

Demo on synthetic data (the A5 and A6 "done when" checks):
    python -m src.models_unsupervised demo
"""
import sys
import time

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn

from src.config import FIGURES_DIR, RANDOM_STATE, SCORES_DIR
from src.features import get_model_matrix

SCORE_KEYS = ["user", "date", "split", "label", "scenario"]


# ---------------------------------------------------------------- A4: common interface
class UnsupervisedDetector:
    """fit() on normal training rows, score() any rows; higher score = more suspicious."""

    name = "base"
    defaults = {}

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
    defaults = {"n_estimators": 200, "max_samples": "auto", "max_features": 1.0,
                "contamination": "auto", "random_state": RANDOM_STATE}

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
    defaults = {"hidden": (64, 32), "bottleneck": 16, "dropout": 0.0, "lr": 1e-3,
                "batch_size": 256, "epochs": 50, "patience": 5, "seed": RANDOM_STATE}

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


DETECTORS = {d.name: d for d in (IsolationForestDetector, AutoencoderDetector)}


# ---------------------------------------------------------------- A4: train and score
def train_and_score(df, model_name, params=None, save=True, save_as=None):
    """Fit `model_name` on normal training rows, score every row, optionally save the score file.

    Returns (scores, info). scores has TEAM_PLAN 5.2 columns; info has the timings (A17).
    save_as overrides the file name (e.g. "iforest_synthetic"), so demo runs never overwrite
    the real results/scores/<model_name>.parquet.
    """
    if model_name not in DETECTORS:
        raise ValueError(f"unknown model {model_name!r}; choose from {sorted(DETECTORS)}")
    X_all, _, feature_names = get_model_matrix(df)
    normal = df["label"] == 0
    X_train = X_all[(df["split"] == "train") & normal]
    X_val = X_all[(df["split"] == "val") & normal]
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
        path = SCORES_DIR / f"{save_as or model_name}.parquet"
        scores.to_parquet(path, index=False)
    info = {"model": model_name, "params": detector.params, "features": feature_names,
            "n_train": len(X_train), "n_scored": len(X_all), "fit_seconds": fit_seconds,
            "score_seconds": score_seconds,
            "score_seconds_per_1000": 1000 * score_seconds / max(len(X_all), 1),
            "path": path, "detector": detector}
    return scores, info


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
    else:
        print(__doc__)
