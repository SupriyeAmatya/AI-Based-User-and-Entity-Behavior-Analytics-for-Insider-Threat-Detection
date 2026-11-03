"""Project-wide paths and settings (owner: Supriye).

Every value marked PROVISIONAL is a placeholder for a decision that TEAM_PLAN Section 12
reserves for a person. Change the value here, re-run the scripts, and nothing else needs
editing. Search this file for "PROVISIONAL" to find them all.
"""
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
CERT_ARCHIVE = RAW_DIR / "r4.2.tar.bz2"
ANSWERS_ARCHIVE = RAW_DIR / "answers.tar.bz2"
CERT_SMALL_DIR = RAW_DIR / "r4.2"          # LDAP/, psychometric.csv, readme (extracted)
ANSWERS_DIR = RAW_DIR / "answers"           # insiders.csv + per-insider answer files
PARQUET_DIR = ROOT / "data" / "parquet"     # one Parquet file per big log (S4)
PROCESSED_DIR = ROOT / "data" / "processed" # labels, feature tables
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
SCORES_DIR = RESULTS_DIR / "scores"

LOGS = ["logon", "device", "file", "email", "http"]   # the big CSVs converted to Parquet

# ---------------------------------------------------------------- reproducibility (TEAM_PLAN 5.7)
RANDOM_STATE = 42

# ---------------------------------------------------------------- decisions
# PROVISIONAL (S11, human-only): working hours. Events with hour < WORK_START_HOUR or
# hour >= WORK_END_HOUR count as "after hours". Values are the example from the S11 task card;
# Supriye decides the real ones from the hour-of-day plot in notebooks/01_eda.ipynb.
WORK_START_HOUR = 7
WORK_END_HOUR = 19

# PROVISIONAL (S8, human-only): temporal split boundaries (TEAM_PLAN 5.3).
# Computed with the plan's default rule (first ~60% of months = train, next ~15% = val, rest = test)
# by src/labels.py; Supriye confirms or moves them, then writes them into TEAM_PLAN 5.3.
# A user-day goes to train if date <= TRAIN_END, to val if date <= VAL_END, otherwise to test.
TRAIN_END = "2010-10-31"
VAL_END = "2011-01-31"

# Company email domain (S14 step 1). Found in the data, not a judgement call: see the
# recipient-domain table in notebooks/01_eda.ipynb.
COMPANY_DOMAIN = "dtaa.com"

# ---------------------------------------------------------------- feature table v0 (S9)
V0_N_INSIDERS = 20
V0_N_NORMAL = 80
