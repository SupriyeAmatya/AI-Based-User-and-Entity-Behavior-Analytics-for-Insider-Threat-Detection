"""Risk scoring (owner: Arva; A7).

Usage:
    from src.risk_scoring import score_risk, rank_users
    risk = score_risk(scores)                    # scores = a TEAM_PLAN 5.2 score file
    table = rank_users(risk, "2011-03-14")       # analyst view for one day

- daily_risk (0-100): the percentile of each score within the scores of the normal training days
  (split == "train", label == 0). 99 means "more unusual than 99% of normal training days".
- user_risk: per user, the highest daily risk over the last 7 calendar days (the primary measure),
  and user_risk_decayed: risk x 0.5^(age_in_days / 3) summed over the user's past days.
- alert_level from user_risk: High >= HIGH, Medium >= MEDIUM, else Low.

Demo on Ayo's synthetic scores (the A7 "done when" check):
    python -m src.risk_scoring demo
"""
import sys

import numpy as np
import pandas as pd

# PROVISIONAL (A7, Arva decides and justifies them in IV-D): the card's suggested levels.
# High = top 1% of normal training behaviour, matching the TEAM_PLAN 5.6 alert budget.
HIGH = 99.0
MEDIUM = 95.0
WINDOW_DAYS = 7
HALF_LIFE_DAYS = 3.0


def to_risk(scores, reference_scores) -> np.ndarray:
    """Percentile (0-100) of each score among the reference scores (higher = more unusual)."""
    reference = np.sort(np.asarray(reference_scores, dtype=float))
    if reference.size == 0:
        raise ValueError("no reference scores to compare with")
    position = np.searchsorted(reference, np.asarray(scores, dtype=float), side="right")
    return 100.0 * position / reference.size


def alert_level(risk) -> np.ndarray:
    risk = np.asarray(risk, dtype=float)
    return np.select([risk >= HIGH, risk >= MEDIUM], ["High", "Medium"], default="Low")


def _window_max(frame: pd.DataFrame, window_days=WINDOW_DAYS) -> pd.Series:
    """Per user, the max daily_risk over the `window_days` calendar days ending on each row's date."""
    ordered = frame.sort_values(["user", "date"])
    rolled = (ordered.groupby("user", sort=False)
              .rolling(f"{window_days}D", on="date")["daily_risk"].max())
    return pd.Series(rolled.to_numpy(), index=ordered.index).reindex(frame.index)


def _decayed_sum(frame: pd.DataFrame, half_life_days=HALF_LIFE_DAYS) -> pd.Series:
    """Per user, sum of past daily risks weighted by 0.5^(age_in_days / half_life_days)."""
    out = pd.Series(0.0, index=frame.index)
    for _, rows in frame.sort_values(["user", "date"]).groupby("user", sort=False):
        days = rows["date"].to_numpy("datetime64[D]").astype("int64")
        risk = rows["daily_risk"].to_numpy(dtype=float)
        total, values = 0.0, np.empty(len(rows))
        for i in range(len(rows)):
            gap = days[i] - days[i - 1] if i else 0
            total = total * 0.5 ** (gap / half_life_days) + risk[i]
            values[i] = total
        out.loc[rows.index] = values
    return out


def score_risk(scores: pd.DataFrame, reference_scores=None) -> pd.DataFrame:
    """Add daily_risk, user_risk, user_risk_decayed and alert_level to a score file.

    The reference defaults to the scores of the normal training days, as in the A7 card.
    Rows keep their original order and index.
    """
    out = scores.copy()
    out["date"] = pd.to_datetime(out["date"])
    if reference_scores is None:
        reference_scores = out.loc[(out["split"] == "train") & (out["label"] == 0), "score"]
    out["daily_risk"] = to_risk(out["score"], reference_scores)
    out["user_risk"] = _window_max(out)
    out["user_risk_decayed"] = _decayed_sum(out)
    out["alert_level"] = alert_level(out["user_risk"])
    return out


def rank_users(risk: pd.DataFrame, date, top=None) -> pd.DataFrame:
    """Users ranked by user risk on `date`: the max daily risk over the 7 days ending that day.

    Users with no activity in that window are left out. This is the table an analyst would see,
    so it holds no labels.
    """
    day = pd.Timestamp(date).normalize()
    window = risk[(risk["date"] > day - pd.Timedelta(days=WINDOW_DAYS)) & (risk["date"] <= day)]
    table = (window.groupby("user")
             .agg(user_risk=("daily_risk", "max"), active_days=("date", "nunique"),
                  last_active=("date", "max"))
             .sort_values(["user_risk", "user"], ascending=[False, True])
             .reset_index())
    table["alert_level"] = alert_level(table["user_risk"])
    table.insert(0, "rank", np.arange(1, len(table) + 1))
    return table.head(top) if top else table


def demo():
    """A7 check: risk scores on Ayo's synthetic score file, and the ranked table for one test day."""
    from src.evaluate import make_synthetic_scores

    risk = score_risk(make_synthetic_scores())
    normal, bad = risk[risk["label"] == 0], risk[risk["label"] == 1]
    print(f"mean daily risk: normal {normal['daily_risk'].mean():.1f}, malicious {bad['daily_risk'].mean():.1f}")
    print("alert levels over all user-days:", risk["alert_level"].value_counts().to_dict())
    day = bad.loc[bad["split"] == "test", "date"].max()
    print(f"\nTop 10 users on {day.date()} (window: the {WINDOW_DAYS} days up to that day):")
    print(rank_users(risk, day, top=10).to_string(index=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["demo"]:
        demo()
    else:
        print(__doc__)
