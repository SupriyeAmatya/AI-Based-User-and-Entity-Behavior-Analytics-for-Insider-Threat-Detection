"""UEBA dashboard (owner: Arva; A21, optional). From the repo root:

    streamlit run app/dashboard.py

Three parts, built on the prototype in src/pipeline.py:
1. the ranked table of risky users (pipeline.run(): the test period, or one chosen day);
2. a user selector with that user's risk timeline (daily risk, 7-day user risk, the High and
   Medium levels);
3. a day selector with the reasons for that user-day (contributions() + alert_reasons()).

It is the analyst's view, so it shows no labels. The first run with a model trains it and saves
it in models/; later runs load it (the "Retrain" box ignores a saved model).

The functions above main() do the work and never import Streamlit, so tests/test_dashboard.py
checks them directly; main() only draws what they return.
"""
import os
import sys
import tempfile
from pathlib import Path

if __package__ in (None, ""):  # run as `streamlit run app/dashboard.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src import pipeline
from src.config import PROCESSED_DIR
from src.features import get_model_matrix
from src.risk_scoring import HIGH, MEDIUM, WINDOW_DAYS

MODELS = ("iforest", "autoencoder")
# The table to open; UEBA_FEATURES overrides it (the tests point it at a synthetic table).
DEFAULT_FEATURES = PROCESSED_DIR / "features_v1.parquet"
# pipeline.run() always saves its table. The dashboard sends it to the temp folder (an absolute
# path replaces results/tables/), so browsing never overwrites the committed top_risky_users.csv.
SCRATCH_TABLE = Path(tempfile.gettempdir()) / "ueba_dashboard_top_users.csv"


def default_features() -> str:
    return os.environ.get("UEBA_FEATURES", str(DEFAULT_FEATURES))


# ---------------------------------------------------------------- part 1: the ranked table
def ranked_users(features_path, model="iforest", top=20, date=None, retrain=False):
    """(ranked table with reasons, risk table of every user-day) from pipeline.run(): users ranked
    over the test period, or for one day when `date` is given."""
    return pipeline.run(features_path, model, top=top, date=date, retrain=retrain,
                        output=str(SCRATCH_TABLE), verbose=False)


def display_table(table: pd.DataFrame) -> pd.DataFrame:
    """The ranked table as shown on the page: dates without a time, risks with 2 decimals."""
    shown = table.copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d").fillna("")
        elif col.endswith("_risk"):
            shown[col] = shown[col].round(2)
    return shown


def load_inputs(features_path, model="iforest"):
    """(feature table, model matrix, detector) for the reasons of a chosen day. The detector is
    the one ranked_users() just used: get_detector() loads it from models/."""
    df = pd.read_parquet(features_path)
    X, _, _ = get_model_matrix(df)
    detector, _, _ = pipeline.get_detector(df, model, features_path)
    return df, X, detector


# ---------------------------------------------------------------- part 2: one user's timeline
def timeline(risk: pd.DataFrame, user) -> pd.DataFrame:
    """Daily risk and 7-day user risk of one user by date, with the two alert levels as constant
    columns so a line chart draws them. No labels: this is the analyst's view."""
    rows = risk[risk["user"] == user].sort_values("date")
    if rows.empty:
        raise ValueError(f"user {user!r} has no rows")
    out = rows.set_index("date")[["daily_risk", "user_risk"]]
    out = out.rename(columns={"daily_risk": "Daily risk",
                              "user_risk": f"User risk ({WINDOW_DAYS}-day max)"})
    out[f"High ({HIGH:g})"] = HIGH
    out[f"Medium ({MEDIUM:g})"] = MEDIUM
    return out


def user_summary(risk: pd.DataFrame, user) -> dict:
    """Headline numbers of one user over the test period."""
    test = risk[(risk["user"] == user) & (risk["split"] == "test")]
    if test.empty:
        return {"active_days": 0, "peak_risk": float("nan"), "peak_date": None,
                "high_days": 0, "medium_days": 0}
    peak = test.loc[test["daily_risk"].idxmax()]
    return {"active_days": int(test["date"].nunique()), "peak_risk": float(peak["daily_risk"]),
            "peak_date": pd.Timestamp(peak["date"]),
            "high_days": int((test["daily_risk"] >= HIGH).sum()),
            "medium_days": int(((test["daily_risk"] >= MEDIUM) & (test["daily_risk"] < HIGH)).sum())}


# ---------------------------------------------------------------- part 3: reasons for one day
def user_days(risk: pd.DataFrame, user, split="test") -> pd.DataFrame:
    """The user's days in `split`, riskiest first (the day selector's choices). The index is the
    row's index in the feature table."""
    rows = risk[(risk["user"] == user) & (risk["split"] == split)]
    return rows.sort_values(["daily_risk", "date"], ascending=[False, True])[
        ["date", "daily_risk", "user_risk", "alert_level"]]


def day_reasons(df, X, detector, model, risk, user, date) -> dict:
    """The chosen user-day: its daily risk, user risk, alert level and up to 3 readable reasons
    (the features that contributed most to the model's score that day)."""
    day = pd.Timestamp(date).normalize()
    rows = risk[(risk["user"] == user) & (risk["date"] == day)]
    if rows.empty:
        raise ValueError(f"{user} has no activity on {day.date()}")
    row = rows.index[0]
    contrib = pipeline.contributions(detector, model, X.loc[[row]], df)
    reasons = pipeline.alert_reasons(contrib, df)[row]
    return {"user": user, "date": day, "daily_risk": float(risk.at[row, "daily_risk"]),
            "user_risk": float(risk.at[row, "user_risk"]),
            "alert_level": str(risk.at[row, "alert_level"]),
            "reasons": [r for r in reasons.split("; ") if r]}


# ---------------------------------------------------------------- the page
def main():
    import streamlit as st

    st.set_page_config(page_title="UEBA insider-threat dashboard", layout="wide")
    st.title("UEBA insider-threat dashboard")

    with st.sidebar:
        st.header("Settings")
        features_path = st.text_input("Feature table", default_features())
        model = st.selectbox("Model", MODELS, format_func={"iforest": "Isolation Forest",
                                                           "autoencoder": "Autoencoder"}.get,
                             key="model")
        top = st.slider("Users in the table", 5, 50, 20, step=5)
        mode = st.radio("Rank users", ("over the test period", "for one day"))
        retrain = st.checkbox("Retrain (ignore a saved model)", value=False)

    if not Path(features_path).exists():
        st.error(f"Feature table not found: {features_path}. Unzip the data drop in the repo "
                 f"root (TEAM_PLAN 2.5.12) or give another path.")
        st.stop()

    ranked = st.cache_data(ranked_users, show_spinner="Scoring every user-day...")
    inputs = st.cache_resource(load_inputs, show_spinner="Loading the model...")

    table, risk = ranked(features_path, model, top, None, retrain)
    test_days = risk.loc[risk["split"] == "test", "date"]
    date = None
    if mode == "for one day":
        date = st.sidebar.date_input("Day", test_days.max().date(), min_value=risk["date"].min().date(),
                                     max_value=risk["date"].max().date())
        table, risk = ranked(features_path, model, top, str(date), retrain)

    # part 1
    period = f"on {date}" if date else (f"over the test period ({test_days.min().date()} to "
                                        f"{test_days.max().date()})")
    st.subheader(f"1. Top {len(table)} users {period}")
    st.caption(f"Daily risk = percentile of the model's score among normal training days (0-100). "
               f"High: risk ≥ {HIGH:g}; Medium: risk ≥ {MEDIUM:g}. The reasons are for each user's "
               f"riskiest day in the period.")
    st.dataframe(display_table(table), hide_index=True, width="stretch")
    if table.empty:
        st.info("No user was active in that window.")
        st.stop()

    # part 2
    st.subheader("2. Risk timeline of one user")
    user = st.selectbox("User", table["user"].tolist(), key="user")
    summary = user_summary(risk, user)
    cols = st.columns(4)
    cols[0].metric("Peak daily risk (test)", f"{summary['peak_risk']:.1f}")
    cols[1].metric("High days", summary["high_days"])
    cols[2].metric("Medium days", summary["medium_days"])
    cols[3].metric("Active days", summary["active_days"])
    st.line_chart(timeline(risk, user), y_label="Risk (0-100)")

    # part 3
    st.subheader("3. Why was this day flagged?")
    days = user_days(risk, user)
    if days.empty:
        st.info(f"{user} has no activity in the test period.")
        st.stop()
    # one key per user: choosing another user starts again at that user's riskiest day
    day = st.selectbox("Day (riskiest first)", days["date"].tolist(), key=f"day_{user}",
                       format_func=lambda d: f"{pd.Timestamp(d).date()}  ·  daily risk "
                                             f"{days.set_index('date').at[d, 'daily_risk']:.1f}")
    df, X, detector = inputs(features_path, model)
    reasons = day_reasons(df, X, detector, model, risk, user, day)
    cols = st.columns(3)
    cols[0].metric("Daily risk", f"{reasons['daily_risk']:.1f}")
    cols[1].metric(f"User risk ({WINDOW_DAYS}-day max)", f"{reasons['user_risk']:.1f}")
    cols[2].metric("Alert level", reasons["alert_level"])
    if reasons["reasons"]:
        for i, reason in enumerate(reasons["reasons"], 1):
            st.markdown(f"{i}. {reason}")
    else:
        st.write("No feature stands out on this day.")


if __name__ == "__main__":
    main()
