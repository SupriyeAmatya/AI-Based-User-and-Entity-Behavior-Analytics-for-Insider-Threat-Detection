"""Tests for the shared model-input helper (S9). Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest

from src.features import get_model_matrix, is_after_hours, sample_v0_users


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


def test_v0_sampler_never_picks_hijacked_accounts(monkeypatch):
    # Scenario 3: the insider (C1) logs in as the supervisor (SUP), so SUP has a malicious day too.
    from src import features
    monkeypatch.setattr(features, "V0_N_INSIDERS", 3)
    monkeypatch.setattr(features, "V0_N_NORMAL", 4)
    days = pd.to_datetime(["2010-03-01", "2010-12-01", "2011-03-01"])
    rows = [(u, d, s) for u, s in [("A1", 1), ("B1", 2), ("C1", 3)] for d in days]
    rows.append(("SUP", days[2], 3))
    labels = pd.DataFrame(rows, columns=["user", "day", "scenario"])
    all_users = ["A1", "B1", "C1", "SUP", "N1", "N2", "N3", "N4"]
    for seed in range(30):
        insiders, normal = sample_v0_users(labels, all_users, {"A1", "B1", "C1"}, seed=seed)
        assert "SUP" not in insiders and "SUP" not in normal
        assert set(insiders) <= {"A1", "B1", "C1"}


# ---------------------------------------------------------------- v1 behavior features (S10-S15)
def _events(rows, columns):
    df = pd.DataFrame(rows, columns=columns)
    df["date"] = pd.to_datetime(df["date"])
    df["day"] = df["date"].dt.normalize()
    df["hour"] = df["date"].dt.hour + df["date"].dt.minute / 60
    return df


def test_login_features_primary_pc_and_missing_logoff():
    from src.features import login_features, primary_pcs
    logon = _events([
        ("A", "2010-01-04 08:00", "PC-1", "Logon"), ("A", "2010-01-04 17:30", "PC-1", "Logoff"),
        ("A", "2010-01-05 08:00", "PC-1", "Logon"), ("A", "2010-01-05 21:00", "PC-2", "Logon"),
        ("B", "2011-03-01 09:00", "PC-9", "Logon"),          # no train logons -> fallback
    ], ["user", "date", "pc", "activity"])
    primary = primary_pcs(logon)
    assert primary.to_dict() == {"A": "PC-1", "B": "PC-9"}
    out = login_features(logon, primary)
    day1, day2 = out.loc[("A", pd.Timestamp("2010-01-04"))], out.loc[("A", pd.Timestamp("2010-01-05"))]
    assert day1["f_first_logon_hour"] == 8 and day1["f_last_logoff_hour"] == 17.5
    assert day1["f_work_duration"] == 9.5 and day1["f_logon_other_pc"] == 0
    assert day2["f_last_logoff_hour"] == 21          # no logoff: last event of the day
    assert day2["f_n_pcs"] == 2 and day2["f_logon_other_pc"] == 1 and day2["f_afterhours_logon"] == 1


def test_usb_duration_pairs_and_caps_at_midnight():
    from src.features import usb_features
    device = _events([
        ("A", "2010-01-04 10:00", "PC-1", "Connect"), ("A", "2010-01-04 10:30", "PC-1", "Disconnect"),
        ("A", "2010-01-04 23:00", "PC-1", "Connect"),          # unmatched: capped at midnight
        ("A", "2010-01-04 20:00", "PC-2", "Connect"), ("A", "2010-01-05 01:00", "PC-2", "Disconnect"),
    ], ["user", "date", "pc", "activity"])
    out = usb_features(device).loc[("A", pd.Timestamp("2010-01-04"))]
    assert out["f_usb_connect"] == 3 and out["f_usb_n_pcs"] == 2
    assert out["f_usb_duration"] == pytest.approx(30 + 60 + 240)
    assert out["f_usb_afterhours"] == 2


def test_file_groups_and_email_features():
    from src.features import email_features, file_features
    files = _events([("A", "2010-01-04 10:00", "x/a.DOC"), ("A", "2010-01-04 10:01", "b.zip"),
                     ("A", "2010-01-04 22:00", "c.exe"), ("A", "2010-01-04 10:02", "d.jpg")],
                    ["user", "date", "filename"])
    f = file_features(files).iloc[0]
    assert (f["f_file_copy"], f["f_file_doc"], f["f_file_zip"], f["f_file_exe"], f["f_file_img"],
            f["f_file_afterhours"]) == (4, 1, 1, 1, 1, 1)
    email = _events([
        ("A", "2010-01-04 10:00", "x@dtaa.com;y@dtaa.com", None, None, "a@dtaa.com", 100, 0),
        ("A", "2010-01-04 20:00", "z@gmail.com", None, "w@dtaa.com", "a@dtaa.com", 300, 2),
        ("A", "2010-01-04 11:00", "q@dtaa.com", None, None, "a@hotmail.com", 200, 1),
    ], ["user", "date", "to", "cc", "bcc", "from", "size", "attachments"])
    e = email_features(email, count_personal=True).iloc[0]
    assert (e["f_email_sent"], e["f_email_recipients"], e["f_email_external"], e["f_email_attach"],
            e["f_email_external_attach"], e["f_email_bcc"], e["f_email_afterhours"]) == (3, 5, 1, 3, 1, 1, 1)
    assert e["f_email_size"] == 200
    assert email_features(email, count_personal=False).iloc[0]["f_email_sent"] == 2


def test_http_domains_and_categories():
    from src.features import domain_categories, http_features, url_domains
    urls = pd.Series(["http://www.WikiLeaks.org/x", "https://jobs.monster.com/a?b", "http://cnn.com"])
    assert url_domains(urls).tolist() == ["wikileaks.org", "jobs.monster.com", "cnn.com"]
    cats = {"job": ["monster.com"], "leak": ["wikileaks.org"], "cloud": [], "hack": []}
    assert domain_categories(url_domains(urls), cats).tolist() == ["leak", "job", "other"]
    visits = pd.DataFrame({"user": ["A"] * 3, "date": pd.to_datetime(["2010-01-04"] * 3),
                           "domain": ["wikileaks.org", "jobs.monster.com", "cnn.com"],
                           "visits": [2, 3, 5], "afterhours": [2, 0, 1]})
    h = http_features(visits, cats).iloc[0]
    assert (h["f_http_count"], h["f_http_domains"], h["f_http_afterhours"]) == (10, 3, 3)
    assert (h["f_http_job"], h["f_http_leak"], h["f_http_cloud"]) == (3, 2, 0)
