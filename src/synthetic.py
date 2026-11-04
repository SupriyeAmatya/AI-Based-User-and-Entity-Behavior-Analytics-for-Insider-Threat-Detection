"""Synthetic feature table for building and testing models before real data exists (owner: Arva; A3).

Usage (from the repo root):
    from src.synthetic import make_synthetic_features
    df = make_synthetic_features()          # 50 users x 300 days, TEAM_PLAN 5.1 format

How the data is made:
- Normal days: each user gets a personal daily rate for every feature (the feature's base rate
  times a random factor between 0.5 and 1.5). Each day's count is drawn from a Poisson
  distribution with that rate.
- Malicious days: 9 insiders, one for each (scenario, split) pair, so train, val and test all
  contain every scenario (TEAM_PLAN 5.3). Each insider has one run of consecutive malicious days,
  together about `anomaly_rate` of all rows. On those days the scenario's features are drawn with
  the user's rate multiplied by a random factor between 3 and 10.
- z_user_* columns use the simple formula from the A3 card: (value - user's mean) / (user's std + 1),
  over all of that user's days. The real v1 table uses a past-30-day baseline instead.
- split by date: first 60% of days train, next 15% val, last 25% test.
"""
import numpy as np
import pandas as pd

from src.config import RANDOM_STATE
from src.features import META_COLUMNS

# Average daily count of each feature across users (made up, roughly office-like).
BASE_RATES = {
    "f_logon_count": 2.0,
    "f_afterhours_logon": 0.5,
    "f_usb_connect": 1.0,
    "f_file_copy": 5.0,
    "f_email_sent": 10.0,
    "f_email_external": 3.0,
    "f_email_recipients": 15.0,
    "f_http_count": 100.0,
    "f_http_job_site": 0.5,
}
# Features that are inflated on malicious days, per scenario (the examples in the A3 card).
SCENARIO_FEATURES = {
    1: ["f_afterhours_logon", "f_usb_connect"],   # after-hours USB use
    2: ["f_file_copy", "f_http_job_site"],        # job hunting + copying files
    3: ["f_email_external", "f_email_recipients"],  # emailing data out
}
ROLES = ["Engineer", "Salesperson", "ITAdmin"]
DEPARTMENTS = ["Research", "Sales", "Operations"]
SPLIT_FRACTIONS = (0.60, 0.15)  # train, val; test gets the rest


def make_synthetic_features(n_users=50, n_days=300, seed=RANDOM_STATE, anomaly_rate=0.005):
    """Return a user-day feature table in exactly the TEAM_PLAN 5.1 format.

    Columns: META_COLUMNS, then f_* counts, then z_user_* deviations. One row per user per day.
    """
    rng = np.random.default_rng(seed)
    users = [f"U{i:03d}" for i in range(n_users)]
    dates = pd.date_range("2010-01-04", periods=n_days, freq="D")
    df = pd.DataFrame([(u, d) for u in users for d in dates], columns=["user", "date"])
    user_idx = np.repeat(np.arange(n_users), n_days)
    day_idx = np.tile(np.arange(n_days), n_users)

    # split by date (TEAM_PLAN 5.3)
    n_train = int(n_days * SPLIT_FRACTIONS[0])
    n_val = int(n_days * SPLIT_FRACTIONS[1])
    df["split"] = np.where(day_idx < n_train, "train",
                           np.where(day_idx < n_train + n_val, "val", "test"))

    # malicious runs: insider i has scenario i % 3 + 1 in split i // 3
    df["label"], df["scenario"] = 0, 0
    windows = {"train": (0, n_train), "val": (n_train, n_train + n_val),
               "test": (n_train + n_val, n_days)}
    insiders = rng.choice(n_users, size=9, replace=False)
    run_length = max(1, round(anomaly_rate * n_users * n_days / len(insiders)))
    for i, u in enumerate(insiders):
        scenario, split = i % 3 + 1, ["train", "val", "test"][i // 3]
        lo, hi = windows[split]
        length = min(run_length, hi - lo)
        start = int(rng.integers(lo, hi - length + 1))
        run = (user_idx == u) & (day_idx >= start) & (day_idx < start + length)
        df.loc[run, ["label", "scenario"]] = [1, scenario]
    df["insider"] = df["user"].isin([users[u] for u in insiders]).astype(int)

    # role and department: one made-up value per user
    df["role"] = np.array(ROLES)[rng.integers(0, len(ROLES), n_users)][user_idx]
    df["department"] = np.array(DEPARTMENTS)[rng.integers(0, len(DEPARTMENTS), n_users)][user_idx]

    # f_* counts: Poisson around each user's personal rate, inflated on malicious days
    for col, base in BASE_RATES.items():
        user_rate = base * rng.uniform(0.5, 1.5, size=n_users)
        rate = user_rate[user_idx]
        for scenario, cols in SCENARIO_FEATURES.items():
            if col in cols:
                bad = (df["scenario"] == scenario).to_numpy()
                rate = np.where(bad, rate * rng.uniform(3, 10, size=len(df)), rate)
        df[col] = rng.poisson(rate).astype("int64")

    # z_user_*: deviation from the user's own mean, the simple way (A3 step 2)
    f_cols = list(BASE_RATES)
    by_user = df.groupby("user")[f_cols]
    z = (df[f_cols] - by_user.transform("mean")) / (by_user.transform("std") + 1)
    z.columns = ["z_user_" + c.removeprefix("f_") for c in f_cols]

    df = pd.concat([df, z], axis=1)
    return df[META_COLUMNS + f_cols + list(z.columns)]
