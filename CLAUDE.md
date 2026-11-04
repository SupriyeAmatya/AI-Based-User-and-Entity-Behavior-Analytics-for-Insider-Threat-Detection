# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A three-person course project (CSCI 561): a UEBA (User and Entity Behavior Analytics) prototype that scores CERT r4.2 **user-days** for insider-threat risk and compares unsupervised models (Isolation Forest, Autoencoder, optional One-Class SVM) against supervised ones (Random Forest, XGBoost). Deadline: Fri Nov 20, 2026. The README tree lists modules that don't exist yet (`baseline.py`, `models_*.py`, `risk_scoring.py`, `explain.py`, `pipeline.py`, `app/dashboard.py`). Planning lives in `Tasks/` and is the source of truth for contracts and who owns what:
- `Tasks/TEAM_PLAN.md`: shared rules (§5), dataset facts (§6), reporting protocol (§10.2), human-only work (§12), git workflow (§14)
- `Tasks/<Name>.md`: per-person task cards with IDs (`S*` Supriye, `A*` Arva, `Y*` Ayo)
- `Tasks/PROGRESS.md`: tracker. Mark work Claude did with **(Claude)**.

## Commands

Python 3.13, in a venv kept outside the repo (`python3 -m venv ~/.venvs/ueba && source ~/.venvs/ueba/bin/activate && pip install -r requirements.txt`). Run everything from the repo root as modules (`python -m src.<module>`) so `src.` imports resolve.

```bash
python -m pytest tests                                                    # all tests
python -m pytest tests/test_evaluate.py::test_threshold_metrics_hand_example  # one test
```

No linter or formatter is configured.

Data pipeline (raw data is not in Git; copy `data/` from the team's shared drive, or rebuild it):
```bash
bash scripts/download_cert.sh       # CERT r4.2 (4.8 GB) + answers into data/raw/, resumable, checksum-verified
python -m src.data_loader convert   # one streaming pass -> data/parquet/<log>.parquet + manifest.json
python -m src.labels                # -> data/processed/labels.parquet, results/tables/{insider_timeline,split_check}.csv
python -m src.features v0           # -> data/processed/features_v0.parquet (100-user sample)
```

## Architecture

Linear pipeline. Each stage writes files the next stage reads, and the file formats are fixed team contracts (TEAM_PLAN §5).

1. **`src/config.py`**: every path, `RANDOM_STATE = 42`, and the judgement-call values marked `PROVISIONAL` (after-hours window, split dates `TRAIN_END`/`VAL_END`). Modules import from here; never hard-code `data/...` paths. A PROVISIONAL value is a human decision (TEAM_PLAN §12). Don't change it on your own.
2. **`src/data_loader.py`**: converts the archive to Parquet without unpacking it. The archive is multi-stream bz2, so it is read with `bz2.open` + `tarfile` mode `"r|"`; `tarfile`'s own `"r|bz2"` stops after the first stream. `content` is dropped from email/http. The `load_<log>(columns=, users=)` loaders push a user filter down to Parquet, then clean (strip, drop rows with no key, dedupe on the full record including `id`) and add `day` (midnight) and `hour` (decimal). `http` is ~28M rows: always pass `columns`/`users`, or use `iter_http_batches()`.
3. **`src/labels.py`**: malicious user-days come from the per-insider answer files, and `assign_split()` splits **by date**, never randomly. Every split must contain malicious days from all 3 scenarios (`check_split` / `split_is_valid`).
4. **`src/features.py`**: one row per user-day. `META_COLUMNS` come first, then feature columns. Only columns prefixed `f_`, `z_user_`, `z_peer_` or `new_` are model inputs. `insider`, `role`, `department` etc. must never reach a model. **Every model builds its inputs with `get_model_matrix(df, split=...)`**: it applies `log1p` to `f_*` counts (except those in `NOT_COUNTS`) and fills NaN/inf with 0. Each model then fits `StandardScaler` on train rows only, inside a sklearn `Pipeline`.
5. **Models** (to come) write `results/scores/<model>.parquet` with columns `user, date, split, label, scenario, score`, where higher score = more suspicious. Score **every** split. The file stem is the model name: `iforest`, `autoencoder`, `ocsvm`, `random_forest`, `xgboost`, plus the variants `*_contam` and `<model>_loso_s<1|2|3>`. Unsupervised models train on `split=="train" & label==0`. Supervised models train on all train rows. Tune on val; use test once.
6. **`src/evaluate.py`**: `evaluate_file` / `compare_files` report on **test only**, at two operating points: `best_f1` (threshold picked on val, then applied to test) and `top_1pct` (top 1% of test user-days). They also give per-scenario metrics, detection delay and user-level recall. `MODEL_COLORS` fixes one color per model across all paper figures. `make_synthetic_scores()` generates data in the score-file format for testing.

Outputs: figures go to `results/figures/` as PNG and PDF (300 dpi). Tables go to `results/tables/` as CSV. `data/`, `results/scores/`, `models/` and `*.parquet` are gitignored.

## Tests

- `tests/test_pipeline_mini.py` builds a fake r4.2 archive in `tmp_path` and runs convert → labels → features v0 with no real data. Modules import config constants by name (`from src.config import X`), so the fixture monkeypatches the constant **in the consuming module** (`data_loader.PARQUET_DIR`, `labels.PROCESSED_DIR`, `features.V0_N_INSIDERS`, ...), not in `src.config`. New modules that read config constants need the same treatment in tests.
- `tests/test_v0_smoke.py` is skipped unless `data/processed/features_v0.parquet` exists.

## Team rules that constrain changes

- **Code ownership (TEAM_PLAN §5.8):** each `src/` file has one owner. Only edit files owned by the teammate you're working for. For anyone else's file, open a GitHub Issue for its owner. Supriye owns config/data_loader/labels/features/baseline plus README, requirements and `Tasks/`. Arva owns synthetic/models_unsupervised/risk_scoring/pipeline/dashboard. Ayo owns models_supervised/evaluate/explain. Notebooks have owners too, and their merge conflicts are painful.
- **Human-only (TEAM_PLAN §12):** don't write the paper, literature notes or Related Work. Don't interpret results, explain flagged anomalies, or make design decisions (granularity, after-hours window, split dates, thresholds, model choice). Code may be written by Claude, but the owner has to be able to explain every line.
- **Git:** no direct pushes to `main`; every change goes through a PR with one reviewer (TEAM_PLAN §14.6). Branch names follow `<name>/<TaskID>-<short-description>`, e.g. `arva/A6-autoencoder`, starting from the latest `main`. Commit messages start with the task ID, e.g. `A6: add autoencoder`. Never commit data, score files or trained models.
- **Reproducibility:** seed 42 everywhere (NumPy, sklearn, XGBoost, PyTorch). Notebooks must run top to bottom after Restart & Run All before merge.
- **Feature-table freeze:** v1 (`features_v1.parquet`) is frozen after Nov 8. Only result-changing bug fixes are allowed after that, released as `features_v1_1.parquet` by Nov 10 noon.

## Dataset gotchas

- CERT `logon.csv` has **no failed logins**, so authentication-failure features can't come from CERT. The stand-in signal is logons on unusual PCs or at unusual times. LANL is a stretch goal.
- Base rate is about 0.3% malicious user-days (984 of 330,268; 70 insiders, 3 scenarios). That is why PR-AUC, precision and recall are the headline metrics, not accuracy.
- The company email domain is `dtaa.com`. 14 senior staff have no LDAP `department`; `ldap_context()` falls back to `functional_unit` and then `"(none)"`.
