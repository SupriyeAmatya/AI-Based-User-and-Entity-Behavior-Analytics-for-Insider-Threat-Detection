"""Tests for src/models_supervised.py (Y7, Y9, Y10) on Arva's synthetic data. Run: python -m pytest tests"""
import json

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


# ---------------------------------------------------------------- Y12: LOSO
@pytest.mark.parametrize("held_out", [1, 2, 3])
def test_loso_never_trains_on_the_held_out_accounts(df, held_out, tmp_outputs):
    train, val, test, held = ms.loso_masks(df, held_out)
    assert held and not df.loc[train | val, "user"].isin(held).any()
    assert set(df.loc[test, "scenario"]) == {0, held_out} and set(df.loc[test, "split"]) == {"test"}
    assert df.loc[train, "label"].sum() > 0                        # other scenarios still teach it
    scores, metrics = ms.run_loso(df, "xgboost", held_out=held_out)
    assert len(scores) == int(test.sum()) and metrics["n_train"] == int(train.sum())
    assert set(scores.loc[scores["label"] == 1, "scenario"]) == {held_out}
    assert (tmp_outputs / "scores" / f"xgboost_loso_s{held_out}.parquet").exists()
    assert 0 <= metrics["pr_auc"] <= 1 and 0 <= metrics["recall_top1pct"] <= 1


def test_loso_table_puts_unsupervised_on_the_same_rows(df, tmp_outputs):
    from src.models_unsupervised import train_and_score
    iforest, _ = train_and_score(df, "iforest", save=False)
    table = ms.loso_table(df, unsupervised={"iforest": iforest},
                          params={"random_forest": {"n_estimators": 50}})
    assert len(table) == 9 and set(table["held_out"]) == {1, 2, 3}
    for s, rows in table.groupby("held_out"):
        assert rows["n_rows"].nunique() == 1 and rows["n_malicious"].nunique() == 1  # same test rows
    assert (tmp_outputs / "tables" / ms.LOSO_TABLE).exists()


# ---------------------------------------------------------------- Y14: final set-up and v1 tuning
TINY_GRIDS = {"random_forest": {"n_estimators": [50], "max_depth": [3, None]},
              "xgboost": {"max_depth": [2, 4], "learning_rate": [0.1]}}


@pytest.mark.parametrize("name", ms.MODELS)
def test_final_setup_is_smote_without_class_weights(df, name):
    # Y10 decision (Ayo, Nov 6): SMOTE on training rows only, no class weights on top
    _, info = ms.train_and_score_supervised(df, name, save=False, **ms.FINAL_SETUP)
    pipeline = info["pipeline"]
    assert list(pipeline.named_steps) == ["scaler", "smote", "model"]
    params = pipeline.named_steps["model"].get_params()
    if name == "random_forest":
        assert params["class_weight"] is None
    else:
        assert params["scale_pos_weight"] == 1.0


def test_tune_final_writes_best_params_by_val_pr_auc(df, tmp_outputs):
    best = ms.tune_final(df, dataset="v1", grids=TINY_GRIDS)
    log = pd.read_csv(tmp_outputs / "tables" / ms.TUNING_LOG)
    assert set(log["dataset"]) == {"v1"} and len(log) == 4
    saved = json.loads((tmp_outputs / "tables" / ms.BEST_PARAMS).read_text())
    for name in ms.MODELS:
        runs = log[log["model"] == name]
        top = runs.loc[runs["val_pr_auc"].idxmax()]
        assert best[name]["params"] == saved[name]["params"] == json.loads(top["params"])
        assert saved[name]["val_pr_auc"] == pytest.approx(top["val_pr_auc"])
        assert saved[name]["setup"] == "c_smote_train_only" and saved[name]["dataset"] == "v1"


def test_tune_final_never_looks_at_test_labels(df, tmp_outputs):
    first = ms.tune_final(df, dataset="v1", grids=TINY_GRIDS, save=False)
    shuffled = df.copy()
    test = shuffled["split"] == "test"
    shuffled.loc[test, "label"] = shuffled.loc[test, "label"].sample(frac=1, random_state=0).to_numpy()
    second = ms.tune_final(shuffled, dataset="v1", grids=TINY_GRIDS, save=False)
    assert first == second


def test_hyperparameter_table_uses_only_the_requested_dataset(tmp_outputs):
    (tmp_outputs / "tables").mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {"model": "xgboost", "dataset": "v0", "params": '{"max_depth": 3}', "val_pr_auc": 0.9, "val_roc_auc": 0.9},
        {"model": "xgboost", "dataset": "v1", "params": '{"max_depth": 6}', "val_pr_auc": 0.4, "val_roc_auc": 0.8},
    ]).to_csv(tmp_outputs / "tables" / ms.TUNING_LOG, index=False)
    table = ms.hyperparameter_table(dataset="v1").set_index("model")
    assert table.loc["xgboost", "best_params"] == '{"max_depth": 6}'
    assert table.loc["xgboost", "dataset"] == "v1" and table.loc["xgboost", "runs"] == 1
