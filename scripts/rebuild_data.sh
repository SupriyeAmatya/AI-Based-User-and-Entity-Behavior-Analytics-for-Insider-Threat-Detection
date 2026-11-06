#!/usr/bin/env bash
# S20b (owner: Supriye): rebuild everything that depends on the decisions in src/config.py
# (split dates, working hours, web keyword lists, email rule, labels). Run from the repo root with
# the project environment active, after changing a value:
#
#   bash scripts/rebuild_data.sh
#
# Steps: labels -> feature table v0 -> v1 (the web-log cache rebuilds itself if the working hours
# changed) -> notebooks 01 and 02 re-executed in place -> all tests. Then build the data drop with
# `python scripts/data_drop.py make`. Takes about 5 minutes; set PYTHON=... to use another interpreter.
set -euo pipefail
PY=${PYTHON:-python}
export PYTHONIOENCODING=utf-8   # some outputs print non-ASCII symbols; Windows consoles need this

step() { printf '\n== %s\n' "$1"; }

step "labels (S6, S8 split check)"
$PY -m src.labels
step "feature table v0 (S9)"
$PY -m src.features v0
step "feature table v1 (S10-S18)"
$PY -m src.features v1
step "notebooks 01 and 02 (Restart & Run All)"
$PY -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 \
    notebooks/01_eda.ipynb notebooks/02_feature_engineering.ipynb
step "tests"
$PY -m pytest tests -q

printf '\nDone. Check results/tables/split_check.csv and v1_validation_checks.csv, commit the changed\n'
printf 'tables, figures and notebooks, then run: python scripts/data_drop.py make\n'
