"""Tests for src/models_supervised.py (Y7, Y9, Y10) on Arva's synthetic data. Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from src import models_supervised as ms
from src.evaluate import evaluate_file
from src.synthetic import make_synthetic_features


@pytest.fixture(scope="module")
def df():
    return make_synthetic_features()


@pytest.fixture(autouse=True)
def tmp_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(ms, "SCORES_DIR", tmp_path / "scores")
    monkeypatch.setattr(ms, "TABLES_DIR", tmp_path / "tables")
    return tmp_path


@pytest.mark.parametrize("name", ms.MODELS)
def test_scores_every_row_in_the_contract_format(df, name, tmp_outputs):
    scores, info = ms.train_and_score_supervised(df, name)
    assert list(scores.columns) == ["user", "date", "split", "label", "scenario", "score"]
    assert len(scores) == len(df) and scores["score"].between(0, 1).all()
    assert (scores[["user", "date"]].to_numpy() == df[["user", "date"]].to_numpy()).all()
    # TEAM_PLAN 5.4: supervised models train on ALL training rows, malicious ones included
    assert info["n_train"] == int((df["split"] == "train").sum())
    assert info["n_train_positive"] == int(df.loc[df["split"] == "train", "label"].sum()) > 0
    assert info["path"] == tmp_outputs / "scores" / f"{name}.parquet"
    assert 0 <= evaluate_file(info["path"])["ranking"]["pr_auc"] <= 1     # Y7 "done when"


@pytest.mark.parametrize("name", ms.MODELS)
def test_higher_scores_for_the_synthetic_anomalies(df, name):
    scores, _ = ms.train_and_score_supervised(df, name, save=False)
    test = scores[scores["split"] == "test"]
    assert roc_auc_score(test["label"], test["score"]) > 0.85


def test_card_settings(df):
    _, info = ms.train_and_score_supervised(df, "random_forest", save=False)
    rf = info["pipeline"].named_steps["model"]
    assert (rf.n_estimators, rf.class_weight, rf.random_state) == (300, "balanced", 42)
    _, info = ms.train_and_score_supervised(df, "xgboost", save=False)
    xgb = info["pipeline"].named_steps["model"]
    train = df[df["split"] == "train"]
    n_pos = train["label"].sum()
    assert xgb.get_params()["scale_pos_weight"] == pytest.approx((len(train) - n_pos) / n_pos)
    assert xgb.get_params()["eval_metric"] == "aucpr" and info["best_iteration"] is not None
    assert list(info["pipeline"].named_steps) == ["scaler", "model"]


def test_xgboost_needs_val_rows(df):
    with pytest.raises(ValueError):
        ms.train_and_score_supervised(df[df["split"] != "val"], "xgboost", save=False)


def test_smote_only_resamples_the_training_rows(df):
    scores, info = ms.train_and_score_supervised(df, "random_forest", save=False, smote=True)
    smote = info["pipeline"].named_steps["smote"]
    n_neg = int(((df["split"] == "train") & (df["label"] == 0)).sum())
    assert smote.sampling_strategy_[1] + df.loc[df["split"] == "train", "label"].sum() \
        == pytest.approx(0.1 * n_neg, abs=1)                         # 10% minority after SMOTE
    assert len(scores) == len(df)                                     # val/test rows untouched
    assert info["pipeline"].named_steps["model"].class_weight is None  # SMOTE replaces weights


def test_tune_logs_every_run_and_picks_best_by_val_pr_auc(df, tmp_outputs):
    log, best = ms.tune_supervised(df, "random_forest", {"n_estimators": [50], "max_depth": [3, None]},
                                   dataset="synthetic")
    assert len(log) == 2 and best == ms.json.loads(log.loc[log["val_pr_auc"].idxmax(), "params"])
    ms.tune_supervised(df, "xgboost", {"max_depth": [3]})
    saved = pd.read_csv(tmp_outputs / "tables" / ms.TUNING_LOG)
    assert len(saved) == 3 and {"val_pr_auc", "val_roc_auc", "fit_seconds"} <= set(saved.columns)


def test_card_grid_sizes():
    from sklearn.model_selection import ParameterGrid
    assert len(ParameterGrid(ms.RF_GRID)) == 24 and len(ParameterGrid(ms.XGB_GRID)) == 16


def test_imbalance_experiment_table(df, tmp_outputs):
    table = ms.imbalance_experiment(df, params={"random_forest": {"n_estimators": 50}})
    assert len(table) == 6 and set(table["setup"]) == set(ms.SETUPS)
    assert (tmp_outputs / "tables" / ms.IMBALANCE_TABLE).exists()
    assert table["val_pr_auc"].between(0, 1).all()


def test_same_seed_same_scores(df):
    for name in ms.MODELS:
        a, _ = ms.train_and_score_supervised(df, name, save=False)
        b, _ = ms.train_and_score_supervised(df, name, save=False)
        np.testing.assert_allclose(a["score"], b["score"], rtol=1e-6)


def test_hyperparameter_table_draft(df, tmp_outputs):
    ms.tune_supervised(df, "xgboost", {"max_depth": [3, 6]})
    table = ms.hyperparameter_table().set_index("model")
    assert table.loc["xgboost", "runs"] == 2 and "best_params" in table.columns
    assert (tmp_outputs / "tables" / "T4_hyperparameters_supervised.csv").exists()
