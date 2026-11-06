"""Project-wide paths and settings (owner: Supriye).

The judgement-call values (working hours, split dates, scenario-3 labels, the email rule and the
web keyword lists) were decided by Supriye on Fri Nov 6 (S8; TEAM_PLAN 2.6 keeps such decisions for
a person). To change one later: edit it here, run `bash scripts/rebuild_data.sh`, and rebuild the
data drop with `python scripts/data_drop.py make`.
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
# Decided by Supriye, Fri Nov 6 (S8/S11): working hours 07:00-19:00. Events with hour <
# WORK_START_HOUR or hour >= WORK_END_HOUR count as "after hours". Data behind it: 61% of normal
# logons start between 07:00 and 09:00; 6.7% of normal logons vs 15.4% of logons on malicious days
# fall outside this window. The reason is written in docs/feature_dictionary.md (Supriye).
WORK_START_HOUR = 7
WORK_END_HOUR = 19

# Decided by Supriye, Fri Nov 6 (S8): temporal split boundaries (TEAM_PLAN 2.5.3), the plan's
# default rule (first ~60% of months = train, next ~15% = val, rest = test). Every split has every
# scenario; scenario 3 has 2 real-insider days in test (stated in III/VII, LOSO covers it).
# A user-day goes to train if date <= TRAIN_END, to val if date <= VAL_END, otherwise to test.
TRAIN_END = "2010-10-31"
VAL_END = "2011-01-31"

# Decided by Supriye, Fri Nov 6 (S6): scenario-3 labels. The 20 malicious days the sysadmin spent
# logged in as their supervisor stay labeled on the supervisor accounts FAW0032 and FBA0348
# (compromised-account view); those two accounts are not insiders (`insider` = 0).
# src/labels.py implements this; there is no switch.

# Company email domain (S14 step 1). Found in the data, not a judgement call: see the
# recipient-domain table in notebooks/01_eda.ipynb.
COMPANY_DOMAIN = "dtaa.com"

# ---------------------------------------------------------------- feature table v0 (S9)
V0_N_INSIDERS = 20
V0_N_NORMAL = 80

# ---------------------------------------------------------------- feature table v1 (S10-S16)
# Decided by Supriye, Fri Nov 6 (S14): every email the user sends counts as "sent", including
# personal webmail from the work PC (37.6% of emails). True = count both; False = work address only.
EMAIL_COUNT_PERSONAL = True

# Decided by Supriye, Fri Nov 6 (S15): web keyword lists. A domain is in a category when it equals
# an entry or is a sub-domain of one. Built from data/processed/http_domain_counts.csv (every domain
# in the http log with its visit count). The log has only 475 domains, so every one was read.
# Left out on purpose:
# linkedin.com (visited by nearly everyone), the defense-contractor sites raytheon.com,
# lockheedmartin.com, northropgrumman.com, boeing.com, harris.com (competitors, not job boards),
# freelance sites (elance, odesk, freelancer, fiverr), torrent indexes and download.cnet.com.
HTTP_CATEGORIES = {
    "job": ["careerbuilder.com", "monster.com", "simplyhired.com", "indeed.com", "job-hunt.org",
            "jobhuntersbible.com", "taleo.net"],
    "leak": ["wikileaks.org"],
    "cloud": ["mediafire.com", "yousendit.com", "dropbox.com", "megaupload.com", "filesonic.com",
              "fileserve.com", "4shared.com", "filestube.com"],
    "hack": ["refog.com", "blackhatworld.com", "dailykeylogger.com", "wellresearchedreviews.com",
             "relytec.com", "actualkeylogger.com", "keylogpc.com", "softactivity.com",
             "webwatchernow.com", "spectorsoft.com", "actionalert.com", "best-spy-soft.com"],
}
