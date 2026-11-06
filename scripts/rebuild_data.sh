#!/usr/bin/env bash
# S20b (owner: Supriye): rebuild everything that depends on the decisions in src/config.py
# (split dates, working hours, web keyword lists, email rule, labels). Run with the project
# environment active, after changing a value (it works from any folder):
#
#   bash scripts/rebuild_data.sh
#
# Steps: labels -> feature table v0 -> v1 (the web-log cache rebuilds itself if the working hours
# changed) -> notebooks 01 and 02 re-executed in place -> all tests -> a final check that the split
# covers every scenario and every v1 validation check passed (exit 1 otherwise). Then build the data
# drop with `python scripts/data_drop.py make`. Takes about 5 minutes; set PYTHON=... to use
# another interpreter.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
export PYTHONIOENCODING=utf-8   # some outputs print non-ASCII symbols; Windows consoles need this

step() { printf '\n== %s\n' "$1"; }

step "labels (S6, S8 split check)"
"$PY" -m src.labels
step "feature table v0 (S9)"
"$PY" -m src.features v0
step "feature table v1 (S10-S18)"
"$PY" -m src.features v1
step "notebooks 01 and 02 (Restart & Run All)"
"$PY" -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 \
    notebooks/01_eda.ipynb notebooks/02_feature_engineering.ipynb
step "tests"
"$PY" -m pytest tests -q
step "final check: split and v1 validation"
"$PY" - <<'PYEOF'
import sys

import pandas as pd

from src.config import TABLES_DIR
from src.labels import split_is_valid

problems = []
if not split_is_valid(pd.read_csv(TABLES_DIR / "split_check.csv", index_col=0)):
    problems.append("split_check.csv: a split has no malicious days for some scenario (NOT VALID)")
checks = pd.read_csv(TABLES_DIR / "v1_validation_checks.csv")
bad = checks[checks["result"].str.contains("FAIL|MISMATCH")]
problems += [f"v1_validation_checks.csv: {row.check} -> {row.result}" for row in bad.itertuples()]
if problems:
    print("STOP, do not build the data drop:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("split covers every scenario in every split; every v1 validation check passed")
PYEOF

printf '\nDone. Commit the changed tables, figures and notebooks, then run: python scripts/data_drop.py make\n'
