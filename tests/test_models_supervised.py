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
    _, info = ms.train_and_score_supervised(df, "random_forest", ms.RF_CARD, save=False,
                                            weighting=True, smote=False, base="card")
    rf = info["pipeline"].named_steps["model"]
    assert (rf.n_estimators, rf.class_weight, rf.random_state) == (300, "balanced", 42)
    _, info = ms.train_and_score_supervised(df, "xgboost", ms.XGB_CARD, save=False,
                                            weighting=True, smote=False, base="card")
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
    assert str(table["n_train"].dtype) == "Int64" and table["n_train"].isna().sum() == 3


# ---------------------------------------------------------------- Y16: T6 pivot
def test_loso_pivot_has_one_row_per_model_and_one_column_per_scenario(tmp_outputs):
    table = pd.DataFrame({"held_out": [1, 1, 2, 2, 3, 3],
                          "model": ["xgboost", "iforest"] * 3,
                          "kind": ["supervised (LOSO)", "unsupervised"] * 3,
                          "pr_auc": [0.9, 0.1, 0.8, 0.2, 0.7, 0.3]})
    pivot = ms.loso_pivot(table)
    assert list(pivot.columns) == ["kind", "s1", "s2", "s3"]
    assert list(pivot.index) == ["xgboost", "iforest"]                 # order of first appearance
    assert pivot.loc["xgboost", "s2"] == 0.8 and pivot.loc["iforest", "s3"] == 0.3
    saved = pd.read_csv(tmp_outputs / "tables" / ms.LOSO_PIVOT, index_col="model")
    assert saved.loc["iforest", "s1"] == 0.1


def test_loso_table_also_saves_the_pivot(df, tmp_outputs):
    ms.loso_table(df, models=("xgboost",), held_out=(1, 2))
    pivot = pd.read_csv(tmp_outputs / "tables" / ms.LOSO_PIVOT)
    assert list(pivot.columns) == ["model", "kind", "s1", "s2"] and len(pivot) == 1


# ---------------------------------------------------------------- Y14: final set-up and v1 tuning
TINY_GRIDS = {"random_forest": {"n_estimators": [50], "max_depth": [3, None]},
              "xgboost": {"max_depth": [2, 4], "learning_rate": [0.1]}}


@pytest.mark.parametrize("name", ms.MODELS)
@pytest.mark.parametrize("setup", list(ms.SETUPS))
def test_each_setup_builds_the_matching_pipeline(df, name, setup):
    _, info = ms.train_and_score_supervised(df, name, save=False, **ms.SETUPS[setup])
    pipeline = info["pipeline"]
    smote = setup == "c_smote_train_only"
    assert list(pipeline.named_steps) == (["scaler", "smote", "model"] if smote else ["scaler", "model"])
    params = pipeline.named_steps["model"].get_params()
    weighted = setup == "b_class_weights"                         # SMOTE never adds weights on top
    if name == "random_forest":
        assert (params["class_weight"] == "balanced") == weighted
    else:
        assert (params["scale_pos_weight"] != 1.0) == weighted


def test_final_setup_names_a_setup_per_model():
    assert set(ms.FINAL_SETUP) == set(ms.MODELS) and set(ms.FINAL_SETUP.values()) <= set(ms.SETUPS)


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
        assert saved[name]["setup"] == ms.FINAL_SETUP[name] and saved[name]["dataset"] == "v1"
        assert set(runs["setup"]) == {ms.FINAL_SETUP[name]}


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


# ---------------------------------------------------------------- Y14 (Plans v2): log, set-ups
@pytest.mark.parametrize("options, name", [
    ({"weighting": False, "smote": False}, "a_no_weighting"),
    ({"weighting": True, "smote": False}, "b_class_weights"),
    ({"weighting": False, "smote": True}, "c_smote_train_only"),
    ({"weighting": True, "smote": True}, "c_smote_train_only"),   # SMOTE replaces the weights
    ({}, "b_class_weights"),                                       # the function defaults
])
def test_setup_name_per_option_pair(options, name):
    assert ms.setup_name(**options) == name


def test_log_stays_aligned_after_a_new_column(df, tmp_outputs):
    # an old log written before the `setup` column, with its columns in another order
    (tmp_outputs / "tables").mkdir(parents=True, exist_ok=True)
    old = pd.DataFrame([{"params": '{"max_depth": 3}', "model": "xgboost", "dataset": "v0",
                         "val_pr_auc": 0.41, "val_roc_auc": 0.96, "fit_seconds": 1.0}])
    old.to_csv(tmp_outputs / "tables" / ms.TUNING_LOG, index=False)
    ms.tune_supervised(df, "random_forest", {"n_estimators": [50]}, dataset="v1", smote=True)
    saved = pd.read_csv(tmp_outputs / "tables" / ms.TUNING_LOG)
    first = saved.iloc[0]
    assert (first["model"], first["dataset"], first["params"]) == ("xgboost", "v0", '{"max_depth": 3}')
    assert first["val_pr_auc"] == pytest.approx(0.41) and first["setup"] == "b_class_weights"
    assert saved.iloc[1]["setup"] == "c_smote_train_only" and saved.iloc[1]["dataset"] == "v1"


def test_clear_log_drops_only_that_dataset(df, tmp_outputs):
    ms.tune_supervised(df, "xgboost", {"max_depth": [3]}, dataset="v0")
    ms.tune_supervised(df, "xgboost", {"max_depth": [3, 6]}, dataset="v1")
    ms.clear_log("v1")
    saved = pd.read_csv(tmp_outputs / "tables" / ms.TUNING_LOG)
    assert list(saved["dataset"]) == ["v0"]
    ms.clear_log("v1")                                            # nothing left to drop: no error


def test_imbalance_csv_keeps_other_datasets(df, tmp_outputs):
    fast = {"random_forest": {"n_estimators": 50}}
    ms.imbalance_experiment(df, params=fast, dataset="v0")
    ms.imbalance_experiment(df, params=fast, dataset="v1")
    ms.imbalance_experiment(df, params=fast, dataset="v1")       # a rerun replaces v1, keeps v0
    saved = pd.read_csv(tmp_outputs / "tables" / ms.IMBALANCE_TABLE)
    assert saved.groupby("dataset").size().to_dict() == {"v0": 6, "v1": 6}


def test_hyperparameter_table_shows_the_setup(df, tmp_outputs):
    ms.tune_supervised(df, "xgboost", {"max_depth": [3]}, dataset="v1", weighting=False)
    table = ms.hyperparameter_table(dataset="v1").set_index("model")
    assert table.loc["xgboost", "setup"] == "a_no_weighting"


def test_tune_final_takes_a_setup_per_model(df, tmp_outputs):
    setups = {"random_forest": "a_no_weighting", "xgboost": "b_class_weights"}
    best = ms.tune_final(df, dataset="v1", grids=TINY_GRIDS, setups=setups)
    log = pd.read_csv(tmp_outputs / "tables" / ms.TUNING_LOG)
    assert log.groupby("model")["setup"].unique().map(list).to_dict() == \
        {"random_forest": ["a_no_weighting"], "xgboost": ["b_class_weights"]}
    assert {m: best[m]["setup"] for m in ms.MODELS} == setups


# ---------------------------------------------------------------- Y15: tuned defaults, final, timing
def test_tuned_defaults_sit_on_top_of_the_card():
    best = {"random_forest": {"max_depth": 20, "max_features": 0.5, "min_samples_leaf": 5,
                              "n_estimators": 500},
            "xgboost": {"learning_rate": 0.1, "max_depth": 3, "min_child_weight": 5, "subsample": 1.0}}
    assert ms.RF_DEFAULTS == {**ms.RF_CARD, **best["random_forest"]}
    assert ms.XGB_DEFAULTS == {**ms.XGB_CARD, **best["xgboost"]}
    assert ms.RF_CARD["n_estimators"] == 300 and ms.XGB_CARD["learning_rate"] == 0.05


@pytest.mark.parametrize("name", ms.MODELS)
def test_default_call_uses_final_setup_and_tuned_defaults(df, name):
    _, info = ms.train_and_score_supervised(df, name, save=False)
    pipeline = info["pipeline"]
    assert ("smote" in pipeline.named_steps) == (ms.FINAL_SETUP[name] == "c_smote_train_only")
    assert info["setup"] == ms.FINAL_SETUP[name]
    params = pipeline.named_steps["model"].get_params()
    defaults = ms.RF_DEFAULTS if name == "random_forest" else ms.XGB_DEFAULTS
    assert all(params[k] == v for k, v in defaults.items() if k != "class_weight")


def test_explicit_options_still_override_final_setup(df):
    _, info = ms.train_and_score_supervised(df, "random_forest", save=False, smote=False)
    assert "smote" not in info["pipeline"].named_steps and info["setup"] == "b_class_weights"


def test_tuning_still_starts_from_the_card(df, tmp_outputs):
    # the grid runs layer on the card values, so the logged v0/v1 runs stay reproducible
    log, _ = ms.tune_supervised(df, "random_forest", {"n_estimators": [50]})
    _, info = ms.train_and_score_supervised(df, "random_forest", {"n_estimators": 50}, save=False,
                                            weighting=True, smote=False, base="card")
    assert info["pipeline"].named_steps["model"].max_depth is None          # the card has no depth
    assert log.loc[0, "setup"] == "b_class_weights"
    assert log.loc[0, "val_pr_auc"] == pytest.approx(ms.val_metrics(_scores_of(df, info))["val_pr_auc"])


def _scores_of(df, info):
    X, _, _ = ms.get_model_matrix(df)
    return df[ms.SCORE_KEYS].assign(score=ms.predict_scores(info["pipeline"], X))


FAST = {"random_forest": {"n_estimators": 20}, "xgboost": {"n_estimators": 50}}


def test_final_writes_both_score_files_for_every_row(df, tmp_outputs):
    paths = ms.final(df=df, params=FAST)
    assert [p.name for p in paths] == ["random_forest.parquet", "xgboost.parquet"]
    for path in paths:
        scores = pd.read_parquet(path)
        assert list(scores.columns) == ms.SCORE_KEYS + ["score"] and len(scores) == len(df)
        assert set(scores["split"]) == {"train", "val", "test"}
        assert 0 <= evaluate_file(path)["ranking"]["pr_auc"] <= 1


def test_final_reads_the_features_file(df, tmp_path, tmp_outputs):
    path = tmp_path / "features_test.parquet"
    df.to_parquet(path, index=False)
    paths = ms.final(path, params=FAST)
    assert all(p.exists() for p in paths)


def test_timing_averages_repeats_and_records_the_machine(df, tmp_outputs):
    row = ms.timing(df, "xgboost", repeats=2, params=FAST["xgboost"])
    assert row["repeats"] == 2 and row["setup"] == ms.FINAL_SETUP["xgboost"]
    assert row["fit_seconds_mean"] > 0 and row["score_seconds_per_1000_mean"] > 0
    assert row["n_scored"] == len(df) and row["threads"] >= 1 and row["ram_gb"] > 0 and row["cpu"]
    ms.timing(df, "random_forest", repeats=1, params=FAST["random_forest"])
    ms.timing(df, "xgboost", repeats=1, params=FAST["xgboost"])          # rerun replaces its row
    saved = pd.read_csv(tmp_outputs / "tables" / ms.TIMING_TABLE)
    assert sorted(saved["model"]) == ["random_forest", "xgboost"]
    assert saved.set_index("model").loc["xgboost", "repeats"] == 1
