"""Tests for src/explain.py (Y11) on Arva's synthetic data. Run: python -m pytest tests"""
import numpy as np
import pandas as pd
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


# ---------------------------------------------------------------- Y18
def _explanation(values, names):
    values = np.asarray(values, dtype=float)
    return explain.shap.Explanation(values=values, base_values=np.zeros(len(values)),
                                    data=np.zeros_like(values), feature_names=names)


def test_importance_table_ranks_every_feature_per_model():
    names = ["f_logon_count", "z_user_usb_connect", "f_http_leak_site"]
    svs = {"xgboost": _explanation([[1, -3, 0], [-1, 1, 2]], names),
           "iforest": _explanation([[0, 0, 4], [0, 2, 0]], names)}
    table = explain.importance_table(svs)
    assert list(table.columns) == ["model", "rank", "feature", "group", "mean_abs_shap"]
    xgb = table[table["model"] == "xgboost"]
    assert list(xgb["feature"]) == ["z_user_usb_connect", "f_logon_count", "f_http_leak_site"] \
        or list(xgb["feature"]) == ["z_user_usb_connect", "f_http_leak_site", "f_logon_count"]
    assert xgb["mean_abs_shap"].tolist()[0] == 2.0 and list(xgb["rank"]) == [1, 2, 3]
    assert dict(zip(table["feature"], table["group"]))["z_user_usb_connect"] == "usb"
    assert len(table) == 6


def test_top10_overlap_counts_shared_features_per_pair():
    rankings = {"a": ["x1", "x2", "x3", "x4"], "b": ["x3", "x1", "x9", "x8"], "c": ["y1", "y2"]}
    table = explain.top10_overlap(rankings, k=3)
    assert list(table.columns) == ["model_a", "model_b", "k", "n_shared", "shared"]
    assert len(table) == 3                                              # 3 pairs
    ab = table[(table["model_a"] == "a") & (table["model_b"] == "b")].iloc[0]
    assert ab["n_shared"] == 2 and ab["shared"] == "x1;x3"              # sorted
    ac = table[(table["model_a"] == "a") & (table["model_b"] == "c")].iloc[0]
    assert ac["n_shared"] == 0 and ac["shared"] == ""
    # also accepts top_features() tables
    frame = explain.top10_overlap({"a": pd.DataFrame({"feature": ["x1", "x2"]}),
                                   "b": pd.DataFrame({"feature": ["x2"]})}, k=10)
    assert frame.loc[0, "n_shared"] == 1


def test_per_scenario_importance_uses_each_scenarios_malicious_rows():
    names = ["f_logon_count", "f_usb_connect"]
    sv = _explanation([[1, 0], [3, 0], [0, 5], [9, 9]], names)
    rows = pd.DataFrame({"label": [1, 1, 1, 0], "scenario": [1, 1, 2, 0]})
    table = explain.per_scenario_importance(sv, rows)
    assert list(table.columns) == ["scenario", "n_rows", "rank", "feature", "group", "mean_abs_shap"]
    s1 = table[table["scenario"] == 1].set_index("feature")
    assert s1.loc["f_logon_count", "mean_abs_shap"] == 2.0 and s1.loc["f_logon_count", "rank"] == 1
    assert (s1["n_rows"] == 2).all()
    s2 = table[table["scenario"] == 2].set_index("feature")
    assert s2.loc["f_usb_connect", "rank"] == 1 and s2.loc["f_usb_connect", "mean_abs_shap"] == 5.0
    assert set(table["scenario"]) == {1, 2}                             # normal rows left out
    with pytest.raises(ValueError, match="rows"):
        explain.per_scenario_importance(sv, rows.iloc[:3])


def test_shap_analysis_writes_f6_and_both_tables(tmp_figures, tmp_path, monkeypatch):
    monkeypatch.setattr(explain, "TABLES_DIR", tmp_path)
    df = make_synthetic_features()
    result = explain.shap_analysis(df=df, n_negatives=200,
                                   params={"random_forest": {"n_estimators": 20}})
    assert set(result["importance"]["model"]) == {"xgboost", "random_forest", "iforest"}
    assert (tmp_path / explain.IMPORTANCE_TABLE).exists()
    assert (tmp_path / explain.PER_SCENARIO_TABLE).exists()
    assert (tmp_path / explain.OVERLAP_TABLE).exists()
    for name in ("F6_shap_summary_xgboost", "shap_summary_random_forest", "shap_summary_iforest"):
        assert (tmp_figures / f"{name}.png").exists() and (tmp_figures / f"{name}.pdf").exists()
    per = pd.read_csv(tmp_path / explain.PER_SCENARIO_TABLE)
    assert set(per["model"]) == {"xgboost", "random_forest", "iforest"}
    assert len(result["overlap"]) == 3
    assert result["setups"]["random_forest"] == "c_smote_train_only"
