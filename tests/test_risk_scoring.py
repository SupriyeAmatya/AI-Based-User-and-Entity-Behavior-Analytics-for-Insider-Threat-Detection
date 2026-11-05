"""Tests for src/risk_scoring.py (A7). Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest

from src import risk_scoring as rs
from src.evaluate import make_synthetic_scores


def test_to_risk_is_a_percentile_of_the_reference():
    ref = np.arange(1, 101)                      # 1..100
    assert rs.to_risk([50, 0, 100, 1000], ref).tolist() == [50.0, 0.0, 100.0, 100.0]
    assert np.all(np.diff(rs.to_risk(np.linspace(-5, 105, 50), ref)) >= 0)   # monotonic
    with pytest.raises(ValueError):
        rs.to_risk([1], [])


def test_alert_level_boundaries():
    assert rs.alert_level([94.99, 95, 98.99, 99, 100]).tolist() == ["Low", "Medium", "Medium", "High", "High"]


def _frame():
    d = pd.to_datetime
    return pd.DataFrame({
        "user": ["A", "A", "A", "A", "B"],
        "date": d(["2011-01-01", "2011-01-03", "2011-01-08", "2011-01-09", "2011-01-03"]),
        "split": "test", "label": 0, "scenario": 0,
        "score": [0.0] * 5,
        "daily_risk": [90.0, 10.0, 20.0, 5.0, 50.0],
    }, index=[10, 11, 12, 13, 14])


def test_user_risk_is_the_max_over_the_last_7_calendar_days():
    f = _frame()
    got = rs._window_max(f)
    # Jan 8: window Jan 2..8 drops Jan 1 (90) -> max(10, 20); Jan 9: Jan 3..9 -> max(10, 20, 5)
    assert got.loc[[10, 11, 12, 13, 14]].tolist() == [90.0, 90.0, 20.0, 20.0, 50.0]


def test_decayed_risk_halves_every_3_days():
    f = _frame()
    got = rs._decayed_sum(f)
    assert got.loc[10] == pytest.approx(90)
    assert got.loc[11] == pytest.approx(90 * 0.5 ** (2 / 3) + 10)
    assert got.loc[14] == pytest.approx(50)                    # B is separate


def test_score_risk_on_synthetic_scores():
    scores = make_synthetic_scores()
    risk = rs.score_risk(scores)
    assert risk.index.equals(scores.index) and (risk["score"] == scores["score"]).all()
    assert {"daily_risk", "user_risk", "user_risk_decayed", "alert_level"} <= set(risk.columns)
    assert risk["daily_risk"].between(0, 100).all()
    assert (risk["user_risk"] >= risk["daily_risk"]).all()
    # reference = normal training days, so those spread evenly over 0-100
    ref = risk.loc[(risk["split"] == "train") & (risk["label"] == 0), "daily_risk"]
    assert ref.median() == pytest.approx(50, abs=2)
    assert risk.loc[risk["label"] == 1, "daily_risk"].mean() > risk.loc[risk["label"] == 0, "daily_risk"].mean()


def test_rank_users_window_order_and_no_labels():
    risk = rs.score_risk(make_synthetic_scores())
    day = risk["date"].max()
    table = rs.rank_users(risk, day)
    assert table["rank"].tolist() == list(range(1, len(table) + 1))
    assert table["user_risk"].is_monotonic_decreasing
    assert "label" not in table.columns and "scenario" not in table.columns
    one = table.iloc[0]
    window = risk[(risk["user"] == one["user"]) & (risk["date"] > day - pd.Timedelta(days=7))
                  & (risk["date"] <= day)]
    assert one["user_risk"] == window["daily_risk"].max()
    assert len(rs.rank_users(risk, day, top=5)) == 5
    assert rs.rank_users(risk, "1999-01-01").empty            # nobody active then
