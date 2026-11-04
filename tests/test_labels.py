"""Tests for split assignment and the split check (S8). Run: python -m pytest tests"""
import pandas as pd

from src.labels import assign_split, check_split, propose_split, split_is_valid


def test_assign_split():
    split = assign_split(pd.to_datetime(["2010-10-31 23:59", "2010-11-01 00:00", "2011-01-31 00:00", "2011-02-01 00:00"]),
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


def test_check_split_separates_insiders_from_hijacked_accounts():
    # Scenario 3's only test-split day is on the hijacked supervisor account SUP.
    days = pd.to_datetime(["2010-03-01", "2010-12-01", "2011-03-01"])
    rows = [(u, d, s) for u, s in [("A", 1), ("B", 2)] for d in days]
    rows += [("C", days[0], 3), ("C", days[1], 3), ("SUP", days[2], 3)]
    labels = pd.DataFrame(rows, columns=["user", "day", "scenario"])
    by_account = check_split(labels, "2010-10-31", "2011-01-31")
    by_insider = check_split(labels, "2010-10-31", "2011-01-31", real_insiders={"A", "B", "C"})
    assert split_is_valid(by_account)                     # counting accounts hides the gap
    assert not split_is_valid(by_insider)                 # no real scenario-3 insider in test
    assert by_insider.loc["test", "accounts_s3"] == 1 and by_insider.loc["test", "insiders_s3"] == 0
