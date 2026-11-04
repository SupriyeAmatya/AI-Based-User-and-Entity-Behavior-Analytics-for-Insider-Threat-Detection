"""Ground-truth labels, insider timeline and split check (owner: Supriye; tasks S6 and S8).

Run from the repo root after the S4 conversion:
    python -m src.labels

It writes
    data/processed/labels.parquet          one row per malicious user-day (user, day, scenario, n_events)
    results/tables/insider_timeline.csv    malicious user-days per month x scenario (for S8)
    results/tables/split_check.csv         malicious user-days and insiders per split x scenario
and prints the label checks (S6 step 4), the default 60/15/25 split proposal, and whether the
split currently in src/config.py has malicious days from every scenario in every split.
Choosing the final split stays with Supriye (S8, human-only).
"""
import csv

import pandas as pd

from src.config import ANSWERS_DIR, PROCESSED_DIR, TABLES_DIR, TRAIN_END, VAL_END
from src.data_loader import DATE_FORMAT, load_insiders, read_manifest

SPLITS = ["train", "val", "test"]


def answer_records(insiders: pd.DataFrame) -> pd.DataFrame:
    """Every malicious log record from the per-insider answer files.

    Each line is a copy of the original record, prefixed with its log type:
    type, id, date, user, pc, ...
    """
    rows = []
    for ins in insiders.itertuples():
        path = ANSWERS_DIR / f"r4.2-{ins.scenario}" / ins.details
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            for rec in csv.reader(f):
                if rec:
                    rows.append({"insider": ins.user, "scenario": ins.scenario, "type": rec[0],
                                 "id": rec[1], "date": rec[2], "user": rec[3].strip()})
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT)
    df["day"] = df["date"].dt.normalize()
    return df


def build_labels():
    """Return (labels, records, checks). labels has one row per malicious user-day."""
    insiders = load_insiders()
    records = answer_records(insiders)
    span = records.merge(insiders[["user", "start", "end"]], left_on="insider", right_on="user",
                         suffixes=("", "_ins"))
    outside = span[(span["date"] < span["start"]) | (span["date"] > span["end"])]
    checks = {
        "insiders_per_scenario_csv": insiders.groupby("scenario")["user"].nunique().to_dict(),
        "insiders_per_scenario_answers": records.groupby("scenario")["insider"].nunique().to_dict(),
        "records": len(records),
        "records_by_type": records["type"].value_counts().to_dict(),
        "records_user_not_insider": int((records["user"] != records["insider"]).sum()),
        "records_outside_start_end": len(outside),
    }
    labels = (records.groupby(["user", "day", "scenario"]).size()
              .rename("n_events").reset_index())
    checks["malicious_user_days"] = len(labels)
    return labels, records, checks


def insider_timeline(labels: pd.DataFrame) -> pd.DataFrame:
    """Malicious user-days per month x scenario (S6 step 5)."""
    t = labels.assign(month=labels["day"].dt.to_period("M"))
    table = t.pivot_table(index="month", columns="scenario", values="user", aggfunc="count",
                          fill_value=0)
    table.columns = [f"scenario_{c}" for c in table.columns]
    return table


def assign_split(dates, train_end=TRAIN_END, val_end=VAL_END) -> pd.Series:
    """train if date <= train_end, val if date <= val_end, else test (TEAM_PLAN 5.3)."""
    dates = pd.to_datetime(pd.Series(dates)).dt.normalize()  # compare calendar days, not times
    split = pd.Series("test", index=dates.index)
    split[dates <= pd.Timestamp(val_end)] = "val"
    split[dates <= pd.Timestamp(train_end)] = "train"
    return split


def propose_split(first_day, last_day, fractions=(0.60, 0.15)):
    """Month boundaries for the plan's default rule: first ~60% of months train, next ~15% val."""
    months = pd.period_range(pd.Timestamp(first_day), pd.Timestamp(last_day), freq="M")
    n_train = round(len(months) * fractions[0])
    n_val = max(1, round(len(months) * fractions[1]))
    train_end = months[n_train - 1].to_timestamp(how="end").normalize()
    val_end = months[n_train + n_val - 1].to_timestamp(how="end").normalize()
    return str(train_end.date()), str(val_end.date()), len(months)


def check_split(labels, train_end=TRAIN_END, val_end=VAL_END, real_insiders=None) -> pd.DataFrame:
    """Malicious user-days and accounts per split x scenario. Every cell must be > 0 (S8 step 2).

    The labels also hold the supervisor accounts hijacked in scenario 3, so `days_s*` and
    `accounts_s*` count every labeled account. Pass `real_insiders` (answers/insiders.csv) to add
    `insider_days_s*` and `insiders_s*`, which count the real insiders only.
    """
    t = labels.assign(split=assign_split(labels["day"], train_end, val_end).to_numpy())

    def per_cell(rows, value, func, prefix):
        table = rows.pivot_table(index="split", columns="scenario", values=value, aggfunc=func,
                                 fill_value=0).reindex(index=SPLITS, columns=[1, 2, 3], fill_value=0)
        table.columns = [f"{prefix}_s{c}" for c in table.columns]
        return table

    parts = [per_cell(t, "day", "count", "days"), per_cell(t, "user", "nunique", "accounts")]
    if real_insiders is not None:
        real = t[t["user"].isin(real_insiders)]
        parts += [per_cell(real, "day", "count", "insider_days"),
                  per_cell(real, "user", "nunique", "insiders")]
    return pd.concat(parts, axis=1)


def split_is_valid(table: pd.DataFrame) -> bool:
    """Every split has malicious days from every scenario; judged on real insiders when known."""
    days = table.filter(like="insider_days_s")
    if days.empty:
        days = table.filter(regex=r"^days_s")
    return bool((days > 0).all().all())


def main():
    labels, _, checks = build_labels()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    labels.to_parquet(PROCESSED_DIR / "labels.parquet", index=False)
    timeline = insider_timeline(labels)
    timeline.to_csv(TABLES_DIR / "insider_timeline.csv")

    print("S6 label checks:")
    for k, v in checks.items():
        print(f"  {k}: {v}")
    print("\nMalicious user-days per month x scenario:")
    print(timeline.to_string())

    real = set(load_insiders()["user"])
    hijacked = sorted(set(labels["user"]) - real)
    print(f"\nAccounts with malicious days that are not insiders (hijacked in scenario 3): {hijacked}")

    logon = read_manifest()["logon"]
    train_end, val_end, n_months = propose_split(logon["date_min"], logon["date_max"])
    print(f"\nData covers {n_months} months. Default 60/15/25 rule -> "
          f"TRAIN_END={train_end}, VAL_END={val_end}")
    print(check_split(labels, train_end, val_end, real).to_string())

    table = check_split(labels, real_insiders=real)
    table.to_csv(TABLES_DIR / "split_check.csv")
    print(f"\nSplit in src/config.py (TRAIN_END={TRAIN_END}, VAL_END={VAL_END}): "
          f"{'OK, every split has every scenario' if split_is_valid(table) else 'NOT VALID'}")
    print(table.to_string())


if __name__ == "__main__":
    main()
