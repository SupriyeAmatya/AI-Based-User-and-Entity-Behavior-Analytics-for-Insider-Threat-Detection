"""Tests for the shared model-input helper (S9). Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest

from src.features import get_model_matrix, is_after_hours


def _table():
    return pd.DataFrame({
        "user": ["A", "A", "B", "B"],
        "date": pd.to_datetime(["2010-01-04", "2011-03-01", "2010-01-04", "2010-12-01"]),
        "split": ["train", "test", "train", "val"],
        "label": [0, 1, 0, 0],
        "scenario": [0, 2, 0, 0],
        "insider": [1, 1, 0, 0],
        "role": ["x", "x", "y", "y"],
        "department": ["d", "d", "e", "e"],
        "f_logon_count": [3, 0, 7, np.nan],
        "f_first_logon_hour": [8.5, 9.0, 7.0, 6.0],
        "z_user_logon_count": [0.5, -1.0, np.inf, 2.0],
    })


def test_get_model_matrix_selects_logs_and_fills():
    X, y, cols = get_model_matrix(_table(), split="train")
    assert cols == ["f_logon_count", "f_first_logon_hour", "z_user_logon_count"]
    assert list(y) == [0, 0]
    assert X["f_logon_count"].tolist() == pytest.approx([np.log1p(3), np.log1p(7)])
    assert X["f_first_logon_hour"].tolist() == [8.5, 7.0]           # not a count: no log1p
    assert X["z_user_logon_count"].tolist() == [0.5, 0.0]           # inf -> 0
    X_all, _, _ = get_model_matrix(_table())
    assert X_all.loc[3, "f_logon_count"] == 0                        # NaN -> 0
    assert X_all.index.tolist() == [0, 1, 2, 3]                      # keeps the row index


def test_get_model_matrix_columns_argument_and_guard():
    X, _, cols = get_model_matrix(_table(), columns=["f_logon_count"])
    assert cols == ["f_logon_count"] and X.shape == (4, 1)
    with pytest.raises(ValueError):
        get_model_matrix(_table(), columns=["f_logon_count", "label"])


def test_after_hours():
    # PROVISIONAL hours in src/config.py: 07:00-19:00 (S11)
    assert is_after_hours(pd.Series([6.9, 7.0, 18.99, 19.0])).tolist() == [True, False, False, True]
