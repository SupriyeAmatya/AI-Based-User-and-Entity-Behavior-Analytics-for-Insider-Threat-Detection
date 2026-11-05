"""Per-user and peer-group baselines, novelty flags (owner: Supriye; tasks S17-S19).

This is the "behavior analytics" part of UEBA: each user-day is compared with the same user's
own past (z_user_*), with colleagues in the same role on the same day (z_peer_*), and flagged when
something happens for the first time (new_*). `python -m src.features v1` calls add_baselines()
after building the behavior features; the result is data/processed/features_v1.parquet.

    z_user_x = (x - mean of the previous 30 active days) / (std of those days + 1)
    z_peer_x = (x - mean of the peer group that day)    / (std of the group that day + 1)

The `+ 1` keeps users with an almost constant history from producing huge z values.
"""
import numpy as np
import pandas as pd

from src.config import FIGURES_DIR

KEY = ["user", "date"]
# S17 step 1: the ~15 features that get a baseline.
KEY_FEATURES = [
    "f_logon_count", "f_first_logon_hour", "f_work_duration", "f_afterhours_events",
    "f_usb_connect", "f_file_copy", "f_email_external", "f_email_recipients", "f_http_count",
    "f_http_job", "f_http_leak", "f_http_cloud", "f_http_hack", "f_logon_other_pc",
]
WINDOW = 30          # previous active days in the per-user baseline
MIN_PERIODS = 10     # fewer past days than this = cold start (S17 step 3)
PEER_MIN_USERS = 5   # a role with fewer users that day falls back to the department (S18 step 2)


def _short(col):
    return col[2:]  # f_usb_connect -> usb_connect


def user_baselines(df: pd.DataFrame, cols=KEY_FEATURES, window=WINDOW,
                   min_periods=MIN_PERIODS) -> pd.DataFrame:
    """z_user_* for every row of `df`, aligned with its index (S17 step 2).

    The rolling window is shifted by one row per user, so today's value is never part of its own
    baseline. Malicious days stay in the history (S17 step 4): nobody knows which days are bad.
    Rows with fewer than `min_periods` past days are NaN (cold start).
    """
    d = df.sort_values(KEY)
    past = d.groupby("user", sort=False)[cols].shift(1)
    roll = past.groupby(d["user"], sort=False).rolling(window, min_periods=min_periods)
    mean = roll.mean().reset_index(level=0, drop=True)
    std = roll.std().reset_index(level=0, drop=True)
    z = (d[cols] - mean[cols]) / (std[cols] + 1)
    z.columns = [f"z_user_{_short(c)}" for c in cols]
    return z.reindex(df.index)


def peer_groups(df: pd.DataFrame, min_users=PEER_MIN_USERS) -> pd.Series:
    """Peer group of each row: its role, or its department when fewer than `min_users` users
    have that role on that date (S18 step 2)."""
    role_size = df.groupby(["date", "role"])["user"].transform("nunique")
    return df["role"].astype(str).where(role_size >= min_users,
                                        "dept:" + df["department"].astype(str))


def peer_baselines(df: pd.DataFrame, cols=KEY_FEATURES, min_users=PEER_MIN_USERS) -> pd.DataFrame:
    """z_peer_* for every row: compared with the peer group on the same date (S18 step 1).

    The group includes the user. A group of one has no std, so its z is NaN (filled with 0 later).
    """
    group = [df["date"], peer_groups(df, min_users)]
    g = df.groupby(group)[cols]
    z = (df[cols] - g.transform("mean")) / (g.transform("std") + 1)
    z.columns = [f"z_peer_{_short(c)}" for c in cols]
    return z


def _first_time(df: pd.DataFrame, happened: pd.Series) -> pd.Series:
    """1 on the first day `happened` is true for a user, never on the user's first active day
    (nothing in the data is 'new' on the day a user's history starts)."""
    d = df.assign(_h=happened.astype(int)).sort_values(KEY)
    before = d.groupby("user", sort=False)["_h"].cumsum() - d["_h"]
    first_day = d.groupby("user", sort=False).cumcount() == 0
    return ((d["_h"] == 1) & (before == 0) & ~first_day).astype(int).reindex(df.index)


def new_pc_days(logon: pd.DataFrame) -> pd.DataFrame:
    """(user, date) pairs on which the user logs on to a PC for the first time, from the raw
    logon log (needs `user`, `pc`, `activity`, `day`)."""
    lg = logon[logon["activity"] == "Logon"]
    first = lg.groupby(["user", "pc"])["day"].min().reset_index()
    return first.rename(columns={"day": "date"})[KEY].drop_duplicates()


def novelty_flags(df: pd.DataFrame, logon: pd.DataFrame = None) -> pd.DataFrame:
    """new_* flags from past days only (S18 step 3)."""
    flags = pd.DataFrame(index=df.index)
    flags["new_usb_user"] = _first_time(df, df["f_usb_connect"] > 0)
    if logon is not None:
        new_pc = new_pc_days(logon).assign(_new=1)
        hit = df[KEY].merge(new_pc, on=KEY, how="left")["_new"].fillna(0).to_numpy()
        first_day = df.sort_values(KEY).groupby("user").cumcount().reindex(df.index) == 0
        flags["new_pc"] = ((hit == 1) & ~first_day.to_numpy()).astype(int)
    flags["new_leak_site"] = _first_time(df, (df["f_http_leak"] + df["f_http_cloud"]) > 0)
    flags["new_afterhours"] = _first_time(df, df["f_afterhours_logon"] > 0)
    return flags


def add_baselines(df: pd.DataFrame, logon: pd.DataFrame = None, cols=KEY_FEATURES) -> pd.DataFrame:
    """Append z_user_*, z_peer_*, new_* to a v1 behavior table. Cold-start z_user values come
    from z_peer, then 0 (S17 step 3); z_peer NaNs (groups of one) become 0."""
    z_user = user_baselines(df, cols)
    z_peer = peer_baselines(df, cols).fillna(0.0)
    z_user = z_user.fillna(z_peer.set_axis(z_user.columns, axis=1))
    return pd.concat([df, z_user, z_peer, novelty_flags(df, logon)], axis=1)


def leakage_check(df: pd.DataFrame, cols=KEY_FEATURES) -> float:
    """S19 check 3: drop the last month, recompute z_user, and return the largest change in any
    earlier row. 0 means no baseline looks into the future."""
    last_month = df["date"].max().to_period("M").to_timestamp()
    full = user_baselines(df, cols)
    cut = df[df["date"] < last_month]
    again = user_baselines(cut, cols)
    diff = (full.loc[cut.index] - again).abs().to_numpy()
    both_nan = np.isnan(full.loc[cut.index].to_numpy()) & np.isnan(again.to_numpy())
    return float(np.nanmax(np.where(both_nan, 0.0, diff))) if diff.size else 0.0


def plot_user_baseline(df: pd.DataFrame, user: str, col: str, path_stem="F3_user_baseline",
                       window=WINDOW, min_periods=MIN_PERIODS):
    """Figure F3 (S17 step 5): one user's feature with its rolling mean +- 2 std band (previous
    `window` active days) and the malicious days marked. Saved as PNG and PDF (300 dpi)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    u = df[df["user"] == user].sort_values("date")
    past = u[col].shift(1).rolling(window, min_periods=min_periods)
    mean, std = past.mean(), past.std()
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.plot(u["date"], u[col], lw=0.8, color="#4c72b0", label=col)
    ax.plot(u["date"], mean, lw=1.2, color="#333333", label=f"mean of previous {window} days")
    ax.fill_between(u["date"], mean - 2 * std, mean + 2 * std, color="#999999", alpha=0.3,
                    label="mean ± 2 std")
    bad = u[u["label"] == 1]
    ax.scatter(bad["date"], bad[col], color="#c44e52", s=18, zorder=3, label="malicious day")
    ax.set_xlabel("date")
    ax.set_ylabel(col)
    ax.set_title(f"Per-user baseline: {user}")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES_DIR / f"{path_stem}.{ext}", dpi=300)
    plt.close(fig)
    return fig
