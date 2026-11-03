"""Smoke test for the M1 hand-off: the v0 table works with get_model_matrix() and evaluate.py.

Skipped until data/processed/features_v0.parquet exists. This is only a compatibility check
(TEAM_PLAN 5.1 / 5.2 / 5.5). The real models are Arva's and Ayo's.
"""
import pandas as pd
import pytest
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import PROCESSED_DIR, RANDOM_STATE
from src.features import META_COLUMNS, get_model_matrix

V0 = PROCESSED_DIR / "features_v0.parquet"
pytestmark = pytest.mark.skipif(not V0.exists(), reason="features_v0.parquet not built yet")


def test_v0_follows_the_feature_table_contract():
    df = pd.read_parquet(V0)
    assert list(df.columns[:len(META_COLUMNS)]) == META_COLUMNS
    assert not df.duplicated(["user", "date"]).any()
    assert set(df["split"]) == {"train", "val", "test"}
    assert df["label"].isin([0, 1]).all() and df.loc[df["label"] == 1, "scenario"].gt(0).all()
    assert df[["role", "department"]].notna().all().all()


def test_v0_runs_through_a_model_and_evaluate(tmp_path):
    # evaluate.py lives on Ayo's branch (ayo/Y3-evaluate) until it is merged into main
    evaluate_file = pytest.importorskip("src.evaluate").evaluate_file
    df = pd.read_parquet(V0)
    X_train, y_train, _ = get_model_matrix(df, split="train")
    model = make_pipeline(StandardScaler(), IsolationForest(n_estimators=100, random_state=RANDOM_STATE))
    model.fit(X_train[y_train == 0])
    X_all, _, _ = get_model_matrix(df)
    scores = df[["user", "date", "split", "label", "scenario"]].assign(score=-model.decision_function(X_all))
    path = tmp_path / "smoke_iforest.parquet"
    scores.to_parquet(path)
    result = evaluate_file(path)
    assert 0 <= result["ranking"]["roc_auc"] <= 1
