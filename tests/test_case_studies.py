"""Tests for the A19 case-study helpers in src/pipeline.py. Run: python -m pytest tests"""
import numpy as np
import pandas as pd
import pytest

from src import pipeline
from src.models_unsupervised import train_and_score
from src.risk_scoring import score_risk
from src.synthetic import make_synthetic_features


def _risk(rows):
    """rows: (user, date, split, label, scenario, score) -> a risk table like score_risk()'s."""
    frame = pd.DataFrame(rows, columns=["user", "date", "split", "label", "scenario", "score"])
    frame["date"] = pd.to_datetime(frame["date"])
    return frame.assign(daily_risk=50.0, user_risk=60.0, alert_level="Low")


# ---------------------------------------------------------------- step 1: the picks
def test_pick_cases_takes_the_top_flagged_day_per_scenario_and_the_top_normal_day():
    risk = _risk([
        ("A", "2011-03-01", "test", 1, 1, 0.9),    # scenario 1: flagged, highest -> picked
        ("A", "2011-03-02", "test", 1, 1, 0.7),
        ("B", "2011-03-01", "test", 1, 2, 0.3),    # scenario 2: nothing flagged -> highest missed
        ("B", "2011-03-02", "test", 1, 2, 0.4),
        ("C", "2011-03-01", "test", 0, 0, 0.8),    # top normal day, flagged -> false positive
        ("C", "2011-03-02", "test", 0, 0, 0.1),
        ("D", "2010-05-01", "train", 1, 3, 5.0),   # not in test: ignored (no scenario-3 case)
        ("E", "2010-12-01", "val", 0, 0, 9.0),     # not in test: ignored
    ])
    cases = pipeline.pick_cases(risk, threshold=0.5)
    assert cases["case"].tolist() == ["scenario 1", "scenario 2", "top normal day"]
    assert cases["kind"].tolist() == ["true positive", "missed", "false positive"]
    assert cases.index.tolist() == [0, 3, 4]                    # row labels of the risk table
    assert cases["score"].tolist() == [0.9, 0.4, 0.8] and (cases["threshold"] == 0.5).all()
    assert {"user", "date", "daily_risk", "user_risk", "alert_level"} <= set(cases.columns)


def test_pick_cases_adds_role_and_names_an_unflagged_normal_day():
    risk = _risk([("A", "2011-03-01", "test", 1, 3, 0.9), ("C", "2011-03-01", "test", 0, 0, 0.2)])
    df = pd.DataFrame({"role": ["ITAdmin", "Salesman"], "department": ["IT", "Sales"]})
    cases = pipeline.pick_cases(risk, threshold=0.5, df=df)
    assert cases["role"].tolist() == ["ITAdmin", "Salesman"]
    assert cases["department"].tolist() == ["IT", "Sales"]
    assert cases["kind"].tolist() == ["true positive", "normal, not flagged"]


# ---------------------------------------------------------------- step 3: baseline vs. the day
def test_baseline_vs_day_uses_the_previous_30_active_days_and_sorts_by_abs_z_user():
    days = pd.date_range("2010-01-01", periods=41, freq="D")
    df = pd.DataFrame({
        "user": "A", "date": days,
        "f_usb_connect": [100.0] * 10 + [2.0] * 30 + [9.0],      # the first 10 days are too old
        "f_file_copy": [0.0] * 40 + [5.0],
        "f_logon_count": 3.0,
        "z_user_usb_connect": 0.0, "z_user_file_copy": 0.0, "z_user_logon_count": 0.0,
        "z_peer_usb_connect": 0.0, "z_peer_file_copy": 0.0,
    })
    df.loc[40, ["z_user_usb_connect", "z_user_file_copy", "z_user_logon_count"]] = [3.5, -7.0, np.nan]
    df.loc[40, "z_peer_usb_connect"] = 1.25
    other = df.assign(user="B", f_usb_connect=999.0)             # another user never counts
    df = pd.concat([df, other], ignore_index=True)

    table = pipeline.baseline_vs_day(df, 40, k=5)
    assert table["feature"].tolist() == ["f_file_copy", "f_usb_connect", "f_logon_count"]
    usb = table.set_index("feature").loc["f_usb_connect"]
    assert usb["value"] == 9 and usb["mean_previous_days"] == 2 and usb["previous_days"] == 30
    assert usb["z_user"] == 3.5 and usb["z_peer"] == 1.25 and usb["what"] == "USB connects"
    assert np.isnan(table.set_index("feature").loc["f_logon_count", "z_peer"])   # no z_peer column
    assert len(pipeline.baseline_vs_day(df, 40, k=2)) == 2
    first = pipeline.baseline_vs_day(df, 0)                      # a user's first day: no history
    assert (first["previous_days"] == 0).all() and first["mean_previous_days"].isna().all()


# ---------------------------------------------------------------- step 4: the F7 halves
@pytest.fixture(scope="module")
def synthetic():
    df = make_synthetic_features(n_users=20, n_days=200)
    X, _, _ = pipeline.get_model_matrix(df)
    return df, X


def test_plot_ae_errors_saves_the_ten_largest_errors(synthetic, tmp_path, monkeypatch):
    from src import config
    monkeypatch.setattr(config, "FIGURES_DIR", tmp_path / "figures")
    df, X = synthetic
    _, info = train_and_score(df, "autoencoder", {"epochs": 3}, save=False)
    row = df.index[df["label"] == 1][0]
    _, table = pipeline.plot_ae_errors(info["detector"], X, row, "F7_test")
    errors = info["detector"].feature_errors(X.loc[[row]]).iloc[0].sort_values(ascending=False)
    assert table["feature"].tolist() == errors.index[:10].tolist()
    np.testing.assert_allclose(table["error"], errors.to_numpy()[:10], rtol=1e-5)
    assert table["above_expected"].dtype == bool
    for ext in ("png", "pdf"):
        assert (tmp_path / "figures" / f"F7_test.{ext}").exists()


def test_shap_for_row_explains_one_day_with_raw_values(synthetic):
    df, X = synthetic
    _, info = train_and_score(df, "iforest", {"n_estimators": 20}, save=False)
    row = df.index[df["label"] == 1][0]
    sv, X_row = pipeline.shap_for_row(info["detector"], X, df, row)
    assert sv.values.shape == (1, X.shape[1]) and X_row.index.tolist() == [row]
    np.testing.assert_allclose(sv.data[0], df.loc[row, X.columns].to_numpy(dtype=float))


# ---------------------------------------------------------------- step 5: raw evidence
def test_raw_evidence_keeps_one_user_day_in_time_order(tmp_path):
    def events(users):
        assert users == ["A"]                                     # the user filter is pushed down
        frame = pd.DataFrame({
            "date": pd.to_datetime(["2011-03-01 18:30", "2011-03-01 08:00", "2011-03-02 09:00"]),
            "id": ["x", "y", "z"], "user": "A", "pc": ["PC-2", "PC-1", "PC-1"],
            "activity": ["Logoff", "Logon", "Logon"]})
        return frame.assign(day=frame["date"].dt.normalize(), hour=frame["date"].dt.hour)

    web = pd.DataFrame({"user": ["A", "A", "A", "B"],
                        "date": pd.to_datetime(["2011-03-01", "2011-03-01", "2011-03-02", "2011-03-01"]),
                        "domain": ["wikileaks.org", "a.com", "c.com", "d.com"],
                        "visits": [2, 7, 1, 50], "afterhours": [0, 3, 0, 0]})
    web.to_parquet(tmp_path / "web.parquet", index=False)

    out = pipeline.raw_evidence("A", "2011-03-01", loaders={"logon": events, "device": events},
                                web_path=tmp_path / "web.parquet")
    assert list(out) == ["logon", "device", "web"]
    assert out["logon"]["activity"].tolist() == ["Logon", "Logoff"]            # time order, 1 day
    assert "day" not in out["logon"].columns and "hour" not in out["logon"].columns
    # the leak site comes first although it has fewer visits
    assert out["web"].to_dict("list") == {"domain": ["wikileaks.org", "a.com"],
                                          "category": ["leak", "other"], "visits": [2, 7],
                                          "afterhours": [0, 3]}
    assert "id" not in out["logon"].columns
    assert pipeline.raw_evidence("A", "2011-04-01", loaders={"logon": events},
                                 web_path=tmp_path / "web.parquet")["web"].empty


def test_competitor_visits_have_a_readable_phrase():
    assert pipeline.describe("z_user_http_competitor", 3.7) == \
        "competitor-site visits 3.7σ above own baseline"


def test_cases_run_end_to_end_on_synthetic_scores(synthetic):
    df, _ = synthetic
    scores, _ = train_and_score(df, "iforest", {"n_estimators": 20}, save=False)
    risk = score_risk(scores)
    cases = pipeline.pick_cases(risk, risk.loc[risk["split"] == "test", "score"].quantile(0.9), df)
    assert cases["case"].iloc[-1] == "top normal day" and cases["label"].iloc[-1] == 0
    assert (df.loc[cases.index, "user"].to_numpy() == cases["user"].to_numpy()).all()
