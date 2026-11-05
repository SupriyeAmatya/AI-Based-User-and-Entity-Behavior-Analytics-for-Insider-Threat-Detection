"""Tests for per-user / peer baselines and novelty flags (S17-S19). Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest

from src.baseline import (
    add_baselines, leakage_check, new_pc_days, novelty_flags, peer_baselines, peer_groups,
    user_baselines,
)

COLS = ["f_usb_connect"]


def _user(values, user="A", start="2010-01-04", role="Clerk", dept="D1"):
    n = len(values)
    return pd.DataFrame({"user": user, "date": pd.date_range(start, periods=n, freq="D"),
                         "role": role, "department": dept, "f_usb_connect": values,
                         "f_http_leak": 0, "f_http_cloud": 0, "f_afterhours_logon": 0})


def test_user_baseline_uses_previous_days_only():
    df = _user([1.0] * 10 + [5.0, 1.0])
    z = user_baselines(df, COLS, window=30, min_periods=10)["z_user_usb_connect"]
    assert z.iloc[:10].isna().all()                      # cold start: fewer than 10 past days
    assert z.iloc[10] == pytest.approx((5 - 1) / (0 + 1))  # today's 5 is not in its own baseline
    past = pd.Series([1.0] * 10 + [5.0])
    assert z.iloc[11] == pytest.approx((1 - past.mean()) / (past.std() + 1))


def test_user_baseline_is_per_user_and_keeps_index_order():
    a, b = _user([1.0] * 12), _user([3.0] * 11 + [9.0], user="B")
    df = pd.concat([b, a], ignore_index=True).sample(frac=1, random_state=0)  # shuffled
    z = user_baselines(df, COLS)
    assert z.index.equals(df.index)
    assert z.loc[(df["user"] == "B") & (df["f_usb_connect"] == 9), "z_user_usb_connect"].item() == 6


def test_peer_group_falls_back_to_department():
    df = pd.concat([_user([1.0], user=f"U{i}", role="Big", dept="D1") for i in range(5)]
                   + [_user([1.0], user=f"S{i}", role="Small", dept="D2") for i in range(2)])
    groups = peer_groups(df, min_users=5)
    assert set(groups[df["role"] == "Big"]) == {"Big"} and set(groups[df["role"] == "Small"]) == {"dept:D2"}
    df["f_usb_connect"] = [0, 0, 0, 0, 10, 2, 2]
    z = peer_baselines(df, COLS, min_users=5)["z_peer_usb_connect"]
    big = df["f_usb_connect"].iloc[:5]
    assert z.iloc[4] == pytest.approx((10 - big.mean()) / (big.std() + 1))
    assert z.iloc[5] == 0                                  # same as the peer mean


def test_novelty_flags_first_time_from_past_only():
    df = _user([2, 0, 0, 3, 4])
    df["f_http_cloud"] = [0, 0, 1, 1, 0]
    df["f_afterhours_logon"] = [0, 1, 0, 1, 0]
    logon = pd.DataFrame({"user": "A", "activity": "Logon",
                          "pc": ["P1", "P1", "P2", "P1", "P3"], "day": df["date"]})
    flags = novelty_flags(df, logon)
    # day 0 starts the history (never "new"); USB used on day 0, so day 3 is not new either
    assert flags["new_usb_user"].tolist() == [0, 0, 0, 0, 0]
    assert flags["new_leak_site"].tolist() == [0, 0, 1, 0, 0]
    assert flags["new_afterhours"].tolist() == [0, 1, 0, 0, 0]
    assert flags["new_pc"].tolist() == [0, 0, 1, 0, 1]
    assert len(new_pc_days(logon)) == 3


def test_add_baselines_fills_cold_start_and_leakage_check():
    df = pd.concat([_user(list(np.arange(40) % 3), user=f"U{i}") for i in range(5)],
                   ignore_index=True)
    out = add_baselines(df, cols=COLS)
    z_cols = [c for c in out.columns if c.startswith(("z_", "new_"))]
    assert not out[z_cols].isna().any().any()
    first = out.groupby("user").head(10)                   # cold start rows take the peer value
    assert (first["z_user_usb_connect"] == first["z_peer_usb_connect"]).all()
    assert leakage_check(df, COLS) == 0.0
