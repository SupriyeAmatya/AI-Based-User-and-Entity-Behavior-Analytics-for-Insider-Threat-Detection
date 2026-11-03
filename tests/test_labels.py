"""Tests for split assignment and the split check (S8). Run: python -m pytest tests"""
import pandas as pd

from src.labels import assign_split, check_split, propose_split, split_is_valid


def test_assign_split():
    split = assign_split(pd.to_datetime(["2010-10-31", "2010-11-01", "2011-01-31", "2011-02-01"]),
                         "2010-10-31", "2011-01-31")
    assert split.tolist() == ["train", "val", "val", "test"]


def test_propose_and_check_split():
    train_end, val_end, n = propose_split("2010-01-02", "2011-05-16")
    assert n == 17 and (train_end, val_end) == ("2010-10-31", "2011-01-31")
    labels = pd.DataFrame({"user": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
                           "day": pd.to_datetime(["2010-03-01"] * 3 + ["2010-12-01"] * 3
                                                 + ["2011-03-01"] * 3),
                           "scenario": [1, 2, 3] * 3})
    assert split_is_valid(check_split(labels, train_end, val_end))
    assert not split_is_valid(check_split(labels.iloc[:6], train_end, val_end))  # no test rows
