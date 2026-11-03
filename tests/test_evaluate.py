"""Tests for src/evaluate.py. Run from the repo root: python -m pytest tests"""
import math

import numpy as np
import pandas as pd
import pytest

from src import evaluate as ev


def test_threshold_metrics_hand_example():
    # 10 user-days, 3 malicious. Threshold 0.5 flags the four scores >= 0.5:
    # 0.9 (mal), 0.8 (mal), 0.7 (normal), 0.6 (normal) -> TP=2, FP=2; 0.3 is a missed malicious -> FN=1; TN=5
    y = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    s = [0.9, 0.8, 0.3, 0.7, 0.6, 0.2, 0.1, 0.05, 0.4, 0.0]
    m = ev.threshold_metrics(y, s, 0.5)
    assert (m["tp"], m["fp"], m["tn"], m["fn"]) == (2, 2, 5, 1)
    assert m["accuracy"] == pytest.approx(7 / 10)
    assert m["precision"] == pytest.approx(2 / 4)
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["f1"] == pytest.approx(2 * 0.5 * (2 / 3) / (0.5 + 2 / 3))
    assert m["fpr"] == pytest.approx(2 / 7)
    assert m["fnr"] == pytest.approx(1 / 3)


def test_threshold_metrics_flags_nothing_without_crashing():
    m = ev.threshold_metrics([1, 0, 0], [0.1, 0.2, 0.3], 1.0)
    assert m["precision"] == 0 and m["recall"] == 0 and m["f1"] == 0


def test_ranking_metrics_single_class_is_nan():
    r = ev.ranking_metrics([0, 0, 0], [0.1, 0.2, 0.3])
    assert math.isnan(r["roc_auc"]) and math.isnan(r["pr_auc"])


def test_thresholds():
    val = pd.DataFrame({"label": [0, 0, 1, 1], "score": [0.1, 0.2, 0.8, 0.9]})
    assert ev.threshold_best_f1(val) == pytest.approx(0.8)  # flags exactly the two malicious rows
    assert ev.threshold_best_f1(val.assign(label=0)) == float("inf")
    test = pd.DataFrame({"score": np.arange(100)})
    assert (test["score"] >= ev.threshold_top_k(test, 0.01)).sum() == 1


def test_detection_delay_and_user_recall():
    d = pd.to_datetime
    test = pd.DataFrame({
        "user": ["A"] * 4 + ["B"] * 2,
        "date": d(["2011-01-01", "2011-01-03", "2011-01-04", "2011-01-05", "2011-01-03", "2011-01-04"]),
        "label": [0, 1, 1, 0, 1, 0],
        "scenario": [0, 1, 1, 0, 2, 0],
        "score": [0.9, 0.1, 0.8, 0.2, 0.1, 0.1],
    })
    # A: first malicious day Jan 3, first alert on/after it Jan 4 -> 1 day (the Jan 1 alert is earlier, ignored)
    # B: never flagged -> missed
    delay = ev.detection_delay(test, 0.5)
    assert delay["n_insiders"] == 2 and delay["n_missed"] == 1
    assert delay["median_delay_days"] == 1
    assert ev.user_level_recall(test, 0.5) == pytest.approx(0.5)


def test_evaluate_and_compare_on_synthetic(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "FIGURES_DIR", tmp_path / "figures")
    df = ev.make_synthetic_scores()
    assert len(df) == 10_000
    assert 0.003 < df["label"].mean() < 0.007
    for split in ("train", "val", "test"):
        assert set(df.loc[(df["split"] == split) & (df["label"] == 1), "scenario"]) == {1, 2, 3}

    path = tmp_path / "xgboost.parquet"
    df.to_parquet(path)
    r = ev.evaluate_file(path)
    assert r["model"] == "xgboost"
    assert set(r["operating_points"]) == {"best_f1", "top_1pct"}
    assert set(r["per_scenario"]) == {1, 2, 3}
    assert r["ranking"]["roc_auc"] > 0.8  # positives are shifted by +1.5

    table = ev.compare_files([path])
    assert list(table["operating_point"]) == ["best_f1", "top_1pct"]

    for plot in (ev.plot_roc([path]), ev.plot_pr([path]), ev.plot_confusion(path),
                 ev.plot_score_distribution(path)):
        assert plot is not None
    assert (tmp_path / "figures" / "roc_curves.png").exists()
