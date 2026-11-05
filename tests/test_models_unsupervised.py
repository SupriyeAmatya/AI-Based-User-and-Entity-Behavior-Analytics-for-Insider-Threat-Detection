"""Tests for src/models_unsupervised.py (A4-A6) on Arva's synthetic data. Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from src import models_unsupervised as mu
from src.evaluate import evaluate_file
from src.synthetic import make_synthetic_features

FAST_AE = {"epochs": 15}  # enough to separate the synthetic anomalies, quick to run


@pytest.fixture(scope="module")
def df():
    return make_synthetic_features()


@pytest.fixture(autouse=True)
def tmp_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(mu, "SCORES_DIR", tmp_path / "scores")
    monkeypatch.setattr(mu, "FIGURES_DIR", tmp_path / "figures")
    return tmp_path


@pytest.mark.parametrize("name, params", [("iforest", {}), ("autoencoder", FAST_AE)])
def test_scores_every_row_in_the_contract_format(df, name, params, tmp_outputs):
    scores, info = mu.train_and_score(df, name, params)
    assert list(scores.columns) == ["user", "date", "split", "label", "scenario", "score"]
    assert len(scores) == len(df) and scores["score"].notna().all()
    assert (scores[["user", "date"]].to_numpy() == df[["user", "date"]].to_numpy()).all()
    assert info["path"] == tmp_outputs / "scores" / f"{name}.parquet" and info["path"].exists()
    # TEAM_PLAN 5.4: trained on the normal training rows only
    assert info["n_train"] == int(((df["split"] == "train") & (df["label"] == 0)).sum())
    assert info["fit_seconds"] > 0 and info["score_seconds_per_1000"] > 0
    assert 0 <= evaluate_file(info["path"])["ranking"]["roc_auc"] <= 1


@pytest.mark.parametrize("name, params", [("iforest", {}), ("autoencoder", FAST_AE)])
def test_higher_scores_for_the_synthetic_anomalies(df, name, params):
    scores, _ = mu.train_and_score(df, name, params, save=False)
    assert roc_auc_score(scores["label"], scores["score"]) > 0.85


def test_autoencoder_shape_loss_and_early_stopping(df):
    _, info = mu.train_and_score(df, "autoencoder", {"epochs": 40, "patience": 2}, save=False)
    detector = info["detector"]
    sizes = [m.out_features for m in detector.network if hasattr(m, "out_features")]
    assert sizes == [64, 32, 16, 32, 64, len(info["features"])]   # A6 card architecture
    assert isinstance(detector.network[-1], mu.nn.Linear)           # linear output layer
    loss = detector.history["train_loss"]
    assert loss[-1] < loss[0] / 5                                   # it actually learns
    assert 1 <= detector.best_epoch <= len(loss) <= 40


def test_same_seed_same_scores(df):
    for name, params in [("iforest", {}), ("autoencoder", {"epochs": 3})]:
        a, _ = mu.train_and_score(df, name, params, save=False)
        b, _ = mu.train_and_score(df, name, params, save=False)
        np.testing.assert_allclose(a["score"], b["score"], rtol=1e-6)


def test_save_as_and_bad_inputs(df, tmp_outputs):
    _, info = mu.train_and_score(df, "iforest", save_as="iforest_synthetic")
    assert info["path"].name == "iforest_synthetic.parquet"
    with pytest.raises(ValueError):
        mu.train_and_score(df, "lstm")
    with pytest.raises(ValueError):
        mu.train_and_score(df, "iforest", {"n_trees": 10})


def test_loss_curve_figure(df, tmp_outputs):
    _, info = mu.train_and_score(df, "autoencoder", {"epochs": 3}, save=False)
    mu.plot_loss_curves(info["detector"].history, "ae_loss_test")
    assert (tmp_outputs / "figures" / "ae_loss_test.png").exists()


# ---------------------------------------------------------------- A8
def test_feature_errors_shape_and_mean_equals_score(df):
    _, info = mu.train_and_score(df, "autoencoder", {"epochs": 3}, save=False)
    X, _, cols = mu.get_model_matrix(df.head(50))
    errors = info["detector"].feature_errors(X)
    assert errors.shape == X.shape and list(errors.columns) == cols
    assert errors.index.equals(X.index) and (errors.to_numpy() >= 0).all()
    np.testing.assert_allclose(errors.mean(axis=1), info["detector"].score(X), rtol=1e-5)


@pytest.mark.parametrize("name, params", [("iforest", {}), ("autoencoder", {"epochs": 3})])
def test_contamination_variant_trains_on_all_train_rows(df, name, params, tmp_outputs):
    scores, info = mu.train_and_score(df, name, params, train_on="all")
    assert info["n_train"] == int((df["split"] == "train").sum())    # malicious rows included
    assert info["path"] == tmp_outputs / "scores" / f"{name}_contam.parquet" and info["path"].exists()
    assert info["train_on"] == "all" and len(scores) == len(df)
    with pytest.raises(ValueError):
        mu.train_and_score(df, name, params, save=False, train_on="some")
