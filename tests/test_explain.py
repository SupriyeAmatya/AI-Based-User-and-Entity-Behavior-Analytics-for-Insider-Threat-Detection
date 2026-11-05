"""Tests for src/explain.py (Y11) on Arva's synthetic data. Run: python -m pytest tests"""
import numpy as np
import pytest

from src import explain
from src.features import get_model_matrix
from src.models_supervised import train_and_score_supervised
from src.models_unsupervised import train_and_score
from src.synthetic import make_synthetic_features


@pytest.fixture(scope="module")
def data():
    df = make_synthetic_features()
    rows = explain.explain_sample(df, n_negatives=300)
    X, _, names = get_model_matrix(rows)
    return df, rows, X, names


@pytest.fixture(autouse=True)
def tmp_figures(tmp_path, monkeypatch):
    monkeypatch.setattr(explain, "FIGURES_DIR", tmp_path)
    return tmp_path


def test_explain_sample_keeps_every_positive(data):
    df, rows, _, _ = data
    test = df[df["split"] == "test"]
    assert set(rows["split"]) == {"test"}
    assert rows["label"].sum() == test["label"].sum()
    assert (rows["label"] == 0).sum() == 300


def test_xgboost_shap_adds_up_to_the_log_odds(data):
    df, _, X, names = data
    pipeline = train_and_score_supervised(df, "xgboost", save=False)[1]["pipeline"]
    sv = explain.get_shap_values(pipeline, X)
    assert sv.values.shape == X.shape and sv.feature_names == names
    margin = pipeline.named_steps["model"].predict(
        pipeline.named_steps["scaler"].transform(X), output_margin=True)
    np.testing.assert_allclose(sv.values.sum(axis=1) + sv.base_values, margin, atol=1e-3)
    np.testing.assert_allclose(sv.data, X.to_numpy())             # plots show unscaled values


def test_random_forest_keeps_class_one(data):
    df, _, X, _ = data
    pipeline = train_and_score_supervised(df, "random_forest", {"n_estimators": 30}, save=False)[1]["pipeline"]
    sv = explain.get_shap_values(pipeline, X)
    proba = pipeline.predict_proba(X)[:, 1]
    np.testing.assert_allclose(sv.values.sum(axis=1) + sv.base_values, proba, atol=1e-6)


def test_isolation_forest_sign_points_to_anomalies(data):
    df, rows, X, _ = data
    detector = train_and_score(df, "iforest", save=False)[1]["detector"]
    sv = explain.get_shap_values(detector, X)
    total = sv.values.sum(axis=1)
    assert np.corrcoef(total, detector.score(X))[0, 1] > 0.9     # positive = more anomalous
    assert total[rows["label"].to_numpy() == 1].mean() > total[rows["label"].to_numpy() == 0].mean()


def test_top_features_and_plots(data, tmp_figures):
    df, _, X, names = data
    pipeline = train_and_score_supervised(df, "xgboost", save=False)[1]["pipeline"]
    sv = explain.get_shap_values(pipeline, X)
    top = explain.top_features(sv, names, k=5)
    assert len(top) == 5 and top["mean_abs_shap"].is_monotonic_decreasing
    assert top.loc[0, "mean_abs_shap"] == np.abs(sv.values).mean(axis=0).max()
    explain.plot_summary(sv, X, name="summary")
    explain.plot_waterfall(sv, X, 0, name="waterfall")
    explain.plot_waterfall(sv, X, X.index[1], name="waterfall_by_label")
    for name in ("summary", "waterfall", "waterfall_by_label"):
        assert (tmp_figures / f"{name}.png").exists() and (tmp_figures / f"{name}.pdf").exists()
