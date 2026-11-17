"""Tests for the optional Streamlit dashboard (A21). Run: python -m pytest tests"""
import pandas as pd
import pytest
import xgboost  # noqa: F401  (macOS: load xgboost's OpenMP before torch's, or test_ablation segfaults)

from app import dashboard
from src import pipeline
from src.risk_scoring import HIGH, MEDIUM
from src.synthetic import make_synthetic_features


@pytest.fixture
def features_file(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "MODELS_DIR", tmp_path / "models")
    monkeypatch.setattr(pipeline, "TABLES_DIR", tmp_path / "tables")
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(dashboard, "SCRATCH_TABLE", tmp_path / "scratch" / "dashboard_top.csv")
    (tmp_path / "scratch").mkdir()
    path = tmp_path / "features_synthetic.parquet"
    make_synthetic_features().to_parquet(path, index=False)
    return path


@pytest.fixture
def scored(features_file):
    table, risk = dashboard.ranked_users(features_file, "iforest", top=10)
    return features_file, table, risk


# ---------------------------------------------------------------- part 1
def test_ranked_users_is_the_pipeline_table_and_leaves_results_tables_alone(scored, tmp_path):
    features_file, table, risk = scored
    assert len(table) == 10 and table["rank"].tolist() == list(range(1, 11))
    assert "reasons" in table.columns and "label" not in table.columns        # analyst view
    assert (tmp_path / "scratch" / "dashboard_top.csv").exists()
    assert not (tmp_path / "tables" / pipeline.OUTPUT).exists()   # top_risky_users.csv untouched
    assert {"daily_risk", "user_risk", "alert_level"} <= set(risk.columns)
    day = risk.loc[risk["split"] == "test", "date"].max()
    one_day, _ = dashboard.ranked_users(features_file, "iforest", top=5, date=str(day.date()))
    assert len(one_day) == 5 and "user_risk" in one_day.columns


def test_display_table_shows_plain_dates_and_rounded_risk(scored):
    _, table, _ = scored
    shown = dashboard.display_table(table)
    assert shown["peak_date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all()
    assert shown["first_alert"].str.fullmatch(r"(\d{4}-\d{2}-\d{2})?").all()   # empty: no alert
    assert (shown["peak_risk"] == table["peak_risk"].round(2)).all()
    assert shown["user"].tolist() == table["user"].tolist() and len(shown.columns) == len(table.columns)
    assert pd.api.types.is_datetime64_any_dtype(table["peak_date"])            # the input is untouched


# ---------------------------------------------------------------- part 2
def test_timeline_has_both_risks_and_the_two_levels(scored):
    _, table, risk = scored
    user = table["user"].iloc[0]
    line = dashboard.timeline(risk, user)
    assert line.index.is_monotonic_increasing and len(line) == (risk["user"] == user).sum()
    assert line.columns.tolist()[:2] == ["Daily risk", "User risk (7-day max)"]
    assert (line[f"High ({HIGH:g})"] == HIGH).all() and (line[f"Medium ({MEDIUM:g})"] == MEDIUM).all()
    assert (line["User risk (7-day max)"] >= line["Daily risk"]).all()
    assert not {"label", "scenario"} & set(line.columns)
    with pytest.raises(ValueError):
        dashboard.timeline(risk, "nobody")


def test_user_summary_matches_the_ranked_table(scored):
    _, table, risk = scored
    top = table.iloc[0]
    summary = dashboard.user_summary(risk, top["user"])
    assert summary["peak_risk"] == pytest.approx(top["peak_risk"])
    assert summary["high_days"] == top["high_days"] and summary["medium_days"] == top["medium_days"]
    assert summary["active_days"] == top["active_days"]
    assert summary["peak_date"] == pd.Timestamp(top["peak_date"])
    assert dashboard.user_summary(risk, "nobody")["active_days"] == 0


# ---------------------------------------------------------------- part 3
def test_user_days_are_test_days_riskiest_first(scored):
    _, table, risk = scored
    user = table["user"].iloc[0]
    days = dashboard.user_days(risk, user)
    assert days["daily_risk"].is_monotonic_decreasing
    assert (risk.loc[days.index, "split"] == "test").all() and (risk.loc[days.index, "user"] == user).all()
    assert days["date"].iloc[0] == pd.Timestamp(table["peak_date"].iloc[0])


def test_day_reasons_match_the_table_for_the_peak_day(scored):
    features_file, table, risk = scored
    df, X, detector = dashboard.load_inputs(features_file, "iforest")
    assert len(df) == len(X) == len(risk)
    top = table.iloc[0]
    got = dashboard.day_reasons(df, X, detector, "iforest", risk, top["user"], top["peak_date"])
    assert got["reasons"] == top["reasons"].split("; ") and 1 <= len(got["reasons"]) <= 3
    assert got["daily_risk"] == pytest.approx(top["peak_risk"])
    assert got["alert_level"] in ("High", "Medium", "Low") and got["user_risk"] >= got["daily_risk"]
    with pytest.raises(ValueError):
        dashboard.day_reasons(df, X, detector, "iforest", risk, top["user"], "1999-01-01")


def test_default_features_follows_the_environment(monkeypatch):
    monkeypatch.delenv("UEBA_FEATURES", raising=False)
    assert dashboard.default_features() == str(dashboard.DEFAULT_FEATURES)
    monkeypatch.setenv("UEBA_FEATURES", "somewhere/else.parquet")
    assert dashboard.default_features() == "somewhere/else.parquet"


# ---------------------------------------------------------------- the page itself
def test_the_app_starts_and_shows_all_three_parts(features_file, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("UEBA_FEATURES", str(features_file))
    app = AppTest.from_file(str(dashboard.__file__), default_timeout=120).run()
    assert not app.exception, app.exception
    headers = [h.value for h in app.subheader]
    assert len(headers) == 3 and headers[0].startswith("1. Top 20 users")
    assert headers[1].startswith("2. Risk timeline") and headers[2].startswith("3. Why")
    assert len(app.dataframe) == 1 and len(app.dataframe[0].value) == 20        # part 1
    assert len(app.metric) == 7                                                  # parts 2 and 3
    ranked = app.dataframe[0].value
    assert app.selectbox(key="user").value == ranked["user"].iloc[0]             # part 2 selector
    first, second = ranked["user"].iloc[0], ranked["user"].iloc[1]
    assert app.selectbox(key=f"day_{first}").value == pd.Timestamp(ranked["peak_date"].iloc[0])
    assert any(m.value.startswith("1. ") for m in app.markdown)                  # a reason is listed

    # choosing another user, then the autoencoder, redraws all three parts without an error
    app.selectbox(key="user").select(second).run()
    assert not app.exception and len(app.subheader) == 3
    # the day selector starts again at the new user's riskiest day
    assert app.selectbox(key=f"day_{second}").value == pd.Timestamp(ranked["peak_date"].iloc[1])
    app.selectbox(key="model").select("autoencoder").run()
    assert not app.exception and len(app.subheader) == 3 and len(app.dataframe[0].value) == 20


def test_the_app_says_so_when_the_feature_table_is_missing(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("UEBA_FEATURES", str(tmp_path / "missing.parquet"))
    app = AppTest.from_file(str(dashboard.__file__), default_timeout=60).run()
    assert not app.exception and len(app.error) == 1 and "not found" in app.error[0].value
    assert len(app.subheader) == 0
