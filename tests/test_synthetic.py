"""Tests for src/synthetic.py (A3). Run from the repo root: python -m pytest tests"""
import pandas as pd
import pytest

from src.features import META_COLUMNS, feature_columns, get_model_matrix
from src.synthetic import BASE_RATES, SCENARIO_FEATURES, make_synthetic_features


@pytest.fixture(scope="module")
def df():
    return make_synthetic_features()


def test_follows_the_feature_table_contract(df):
    assert list(df.columns[:len(META_COLUMNS)]) == META_COLUMNS
    assert feature_columns(df) == list(df.columns[len(META_COLUMNS):])  # only model inputs after META
    assert len(df) == 50 * 300 and not df.duplicated(["user", "date"]).any()
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df[list(BASE_RATES)].ge(0).all().all()
    assert df[["role", "department"]].notna().all().all() and df["role"].nunique() == 3


def test_labels_scenarios_and_insiders(df):
    assert df["label"].isin([0, 1]).all()
    assert ((df["label"] == 1) == (df["scenario"] > 0)).all()
    assert df["label"].mean() == pytest.approx(0.005, abs=0.001)
    bad_users = set(df.loc[df["label"] == 1, "user"])
    assert set(df.loc[df["insider"] == 1, "user"]) == bad_users and len(bad_users) == 9
    # every split has malicious days from every scenario (TEAM_PLAN 5.3)
    per_split = df[df["label"] == 1].groupby("split")["scenario"].unique()
    assert all(set(per_split[s]) == {1, 2, 3} for s in ("train", "val", "test"))


def test_split_is_by_date(df):
    days = sorted(df["date"].unique())
    first = df.groupby("split")["date"].min()
    last = df.groupby("split")["date"].max()
    assert first["train"] == days[0] and last["train"] < first["val"]
    assert last["val"] < first["test"] and last["test"] == days[-1]
    assert df.drop_duplicates("date")["split"].value_counts().to_dict() == {
        "train": 180, "val": 45, "test": 75}


def test_scenario_features_are_inflated(df):
    normal = df[df["label"] == 0]
    for scenario, cols in SCENARIO_FEATURES.items():
        bad = df[df["scenario"] == scenario]
        assert (bad[cols].mean() > 2.5 * normal[cols].mean()).all()


def test_same_seed_same_table_and_model_matrix_works(df):
    pd.testing.assert_frame_equal(df, make_synthetic_features())
    assert not df.equals(make_synthetic_features(seed=1))
    X, y, cols = get_model_matrix(df, split="train")
    assert X.shape == (9000, len(cols)) and y.sum() == 24
