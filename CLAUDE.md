# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A three-person course project (CSCI 561): a UEBA (User and Entity Behavior Analytics) prototype that scores CERT r4.2 **user-days** for insider-threat risk and compares unsupervised models (Isolation Forest, Autoencoder, optional One-Class SVM) against supervised ones (Random Forest, XGBoost). Deadline: Fri Nov 20, 2026. Every module in the README tree exists except the optional `app/dashboard.py`. Planning lives in `Tasks/` (plan v2, rewritten Nov 5) and is the source of truth for contracts and who owns what:
- `Tasks/TEAM_PLAN.md`: team contracts (2.5), human-only work (2.6), dataset and model facts (2.7), git workflow and reviewer map (3.9, 3.10), reporting protocol (5.4)
- `Tasks/<Name>.md`: per-person task cards with IDs (`S*` Supriye, `A*` Arva, `Y*` Ayo)
- `Tasks/PROGRESS.md`: tracker. Mark work Claude did with **(Claude)**.

## Commands

Python 3.13, in a venv kept outside the repo (`python3 -m venv ~/.venvs/ueba && source ~/.venvs/ueba/bin/activate && pip install -r requirements.txt`). Run everything from the repo root as modules (`python -m src.<module>`) so `src.` imports resolve.

```bash
python -m pytest tests                                                    # all tests
python -m pytest tests/test_evaluate.py::test_threshold_metrics_hand_example  # one test
```

No linter or formatter is configured.

Data (not in Git). Arva and Ayo get it from the one data drop (TEAM_PLAN 2.5.12): unzip `ueba_data_v1.zip` from the shared drive in the repo root, then check it:
```bash
python scripts/data_drop.py verify  # checksums + the config decisions the drop was built with
```
Rebuilding from scratch (TEAM_PLAN 2.5.11; mainly Supriye, who also has `http.parquet` and the raw archive):
```bash
bash scripts/download_cert.sh       # CERT r4.2 (4.8 GB) + answers into data/raw/, resumable, checksum-verified
python -m src.data_loader convert   # one streaming pass -> data/parquet/<log>.parquet + manifest.json
python -m src.labels                # -> data/processed/labels.parquet, results/tables/{insider_timeline,split_check}.csv
python -m src.features v0           # -> data/processed/features_v0.parquet (100-user sample)
python -m src.features v1           # -> data/processed/features_v1.parquet (all users, 76 inputs)
bash scripts/rebuild_data.sh        # after a config decision changes: labels, v0, v1, notebooks 01-02, tests, final check
python scripts/data_drop.py make    # Supriye: -> data/ueba_data_v1.zip
```
Models and prototype:
```bash
python -m src.models_unsupervised demo     # synthetic data; also models_supervised / risk_scoring / explain demo
python -m src.models_unsupervised final    # -> results/scores/{iforest,autoencoder,iforest_contam,autoencoder_contam,ocsvm}.parquet
python -m src.pipeline --features data/processed/features_v1.parquet --model iforest --top 20
python -m src.ablation                     # T7 (run after the tuned defaults merge); `time` -> data_processing_time.csv
```

## Architecture

Linear pipeline. Each stage writes files the next stage reads, and the file formats are fixed team contracts (TEAM_PLAN 2.5).

1. **`src/config.py`**: every path, `RANDOM_STATE = 42`, and the judgement-call values Supriye decided on Nov 6 (S8): working hours 07:00–19:00, split dates `TRAIN_END`/`VAL_END`, scenario-3 labels, the email-count rule and the web keyword lists `HTTP_CATEGORIES` (with a `competitor` category since #38). Modules import from here; never hard-code `data/...` paths. These are human decisions (TEAM_PLAN 2.6). Don't change one on your own; a change means `bash scripts/rebuild_data.sh` and a new data drop. The values still marked `PROVISIONAL` are Arva's: the detector defaults in `models_unsupervised.py` (A16) and `HIGH`/`MEDIUM` in `risk_scoring.py` (DEC-A).
2. **`src/data_loader.py`**: converts the archive to Parquet without unpacking it. The archive is multi-stream bz2, so it is read with `bz2.open` + `tarfile` mode `"r|"`; `tarfile`'s own `"r|bz2"` stops after the first stream. `content` is dropped from email/http. The `load_<log>(columns=, users=)` loaders push a user filter down to Parquet, then clean (strip, drop rows with no key, dedupe on the full record including `id`) and add `day` (midnight) and `hour` (decimal). `http` is ~28M rows: always pass `columns`/`users`, or use `iter_http_batches()`. The data drop leaves `http.parquet` out; v1 uses the cached `http_user_day_domain.parquet` instead, which records the working hours it was built with and rebuilds itself (this needs `http.parquet`) when they change.
3. **`src/labels.py`**: malicious user-days come from the per-insider answer files, and `assign_split()` splits **by date**, never randomly. Every split must contain malicious days from all 3 scenarios (`check_split` / `split_is_valid`).
4. **`src/features.py`** + **`src/baseline.py`**: one row per user-day. `META_COLUMNS` come first, then feature columns. Only columns prefixed `f_`, `z_user_`, `z_peer_` or `new_` are model inputs (v1: 42 + 15 + 15 + 4 = 76). `insider`, `role`, `department` etc. must never reach a model. `baseline.py` adds the `z_user_*` (user's previous 30 active days), `z_peer_*` (same-role peers that day) and `new_*` columns. **Every model builds its inputs with `get_model_matrix(df, split=...)`**: it applies `log1p` to `f_*` counts (except those in `NOT_COUNTS`) and fills NaN/inf with 0. Each model then fits `StandardScaler` on train rows only, inside a sklearn `Pipeline`.
5. **Models** write `results/scores/<model>.parquet` with columns `user, date, split, label, scenario, score`, where higher score = more suspicious. Score **every** split. The file stem is the model name: `iforest`, `autoencoder`, `ocsvm`, `random_forest`, `xgboost`, plus the variants `*_contam` and `<model>_loso_s<1|2|3>`. `models_unsupervised.py` (Arva) trains on `split=="train" & label==0`; `models_supervised.py` (Ayo, incl. LOSO) trains on all train rows. Tune on val; use test once. Tuning appends to `results/tables/tuning_log_*.csv`; in `models_unsupervised.py`, `clear_log(dataset)` resets one dataset's rows only, so never delete the whole log. Score files are rebuilt with the `final` commands on each laptop, never shared.
6. **`src/evaluate.py`**: `evaluate_file` / `compare_files` report on **test only**, at two operating points: `best_f1` (threshold picked on val, then applied to test) and `top_1pct` (top 1% of test user-days). They also give per-scenario metrics, detection delay and user-level recall. `MODEL_COLORS` fixes one color per model across all paper figures. `make_synthetic_scores()` generates data in the score-file format for testing.
7. **`src/risk_scoring.py`** + **`src/pipeline.py`**: daily risk is the percentile of a score among the normal training days' scores (0–100); user risk is the 7-day maximum; alert levels come from `HIGH`/`MEDIUM`. `pipeline.py` goes from a feature table to ranked users with 3 readable reasons each (`PHRASES` maps features to wording). `precision_at_k()`, `f8_user()` and `plot_risk_timeline()` produce the A18 outputs.
8. **`src/explain.py`** (SHAP for RF/XGB) and **`src/ablation.py`** (feature-group ablation, T7, and data-processing time for T8).

Outputs: figures go to `results/figures/` as PNG and PDF (300 dpi). Tables go to `results/tables/` as CSV. `data/`, `results/scores/`, `models/` and `*.parquet` are gitignored.

## Tests

- `tests/test_pipeline_mini.py` builds a fake r4.2 archive in `tmp_path` and runs convert → labels → features v0 with no real data. Modules import config constants by name (`from src.config import X`), so the fixture monkeypatches the constant **in the consuming module** (`data_loader.PARQUET_DIR`, `labels.PROCESSED_DIR`, `features.V0_N_INSIDERS`, ...), not in `src.config`. New modules that read config constants need the same treatment in tests.
- `tests/test_v0_smoke.py` is skipped unless `data/processed/features_v0.parquet` exists.
- macOS: xgboost and PyTorch each load their own OpenMP runtime. `models_unsupervised.py` calls `torch.set_num_threads(1)`, which stops the deadlock when the autoencoder runs after XGBoost. Training the autoencoder *before* XGBoost in one process can still crash (`OMP: Error #179`); set `OMP_NUM_THREADS=1` for that.

## Team rules that constrain changes

- **Code ownership (TEAM_PLAN 2.5.8):** each file has one owner. Only edit files owned by the teammate you're working for. For anyone else's file, open a GitHub Issue for its owner.
  - **Supriye:** `config`, `data_loader`, `labels`, `features`, `baseline`, `ablation`, their tests, notebooks 01–02, `docs/feature_dictionary.md`, README, requirements, `Tasks/`, `Guide/`.
  - **Arva:** `synthetic`, `models_unsupervised`, `risk_scoring`, `pipeline`, `app/dashboard.py`, their tests, notebooks 03a and 05, `docs/coverage.md`, `CLAUDE.md`.
  - **Ayo:** `models_supervised`, `evaluate`, `explain`, their tests, notebooks 03b and 04.
- **Human-only (TEAM_PLAN 2.6):** don't write the paper, literature notes or Related Work. Don't interpret results, explain flagged anomalies, or make design decisions or write their reasons (granularity, after-hours, split dates, keyword lists, labeling, thresholds, alert levels, AE architecture, imbalance set-up, LOSO design). Code may be written by Claude, but the owner has to be able to explain every line.
- **Git (TEAM_PLAN 3.9):** `main` has branch protection (since Nov 6; per #39 one approving review per PR, admins included), so every change goes through a reviewed PR. Branch names follow `<name>/<TaskID>-<short-description>`, e.g. `arva/A15-final-models`, starting from the latest `main`. Commit messages start with the task ID, e.g. `A6: add autoencoder`. PRs are squash-merged. Retarget a stacked PR to `main` before its base merges, and update a stacked branch by rebasing onto `main`, not by merging `main` into it: a merge resolution dropped A17's code from #34. Never commit data, score files or trained models; the repo is public.
- **Reproducibility:** seed 42 everywhere (NumPy, sklearn, XGBoost, PyTorch). Notebooks must run top to bottom after Restart & Run All before merge.
- **Feature-table freeze (TEAM_PLAN 2.5.9):** v1 (`features_v1.parquet`) is frozen after Sun Nov 8. Only result-changing bug fixes, reported as an Issue, are allowed after that, released as `features_v1_1.parquet` by Tue Nov 10 12:00.
- **Data (TEAM_PLAN 2.5.10–2.5.12):** one data drop, once. Tuned settings travel as merged module defaults; score files and models are regenerated on each laptop, never sent.

## Dataset gotchas

- CERT `logon.csv` has **no failed logins**, so authentication-failure features can't come from CERT. The stand-in signal is logons on unusual PCs or at unusual times. LANL is a stretch goal.
- Base rate is about 0.3% malicious user-days (984 of 330,268; 70 insiders, 3 scenarios). That is why PR-AUC, precision and recall are the headline metrics, not accuracy.
- Scenario 3's 20 hijacked-account days stay labeled malicious on the supervisor accounts `FAW0032` (16) and `FBA0348` (4), which have `insider` = 0 (S6). The test split holds only 1 real scenario-3 insider (`JLM0364`, 2 days) plus 2 days on `FBA0348`.
- The company email domain is `dtaa.com`. 14 senior staff have no LDAP `department`; `ldap_context()` falls back to `functional_unit` and then `"(none)"`.
