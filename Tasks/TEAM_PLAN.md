# Team Plan: UEBA for Insider Threat Detection (v2, from Thu Nov 5)

| Person | Role | Task file | Task IDs |
|---|---|---|---|
| **Supriye** (`SupriyeAmatya`, repo owner) | Data & features lead, paper integrator | [Supriye.md](Supriye.md) | `S*` |
| **Arva** (`arjasa1103`) | Unsupervised models, risk scoring, prototype | [Arva.md](Arva.md) | `A*` |
| **Ayo** (`Bizzlefresh`) | Supervised models, evaluation, explainability | [Ayo.md](Ayo.md) | `Y*` |

Progress is tracked in [PROGRESS.md](PROGRESS.md). This file replaces the Oct 28 plan. Task IDs are kept, so finished work and old PRs still match.

**Old section numbers** (code comments, `CLAUDE.md`, the Guide and old PRs cite them):

| Old reference | Now |
|---|---|
| TEAM_PLAN 5.1–5.8 (contracts) | 2.5.1–2.5.8 (same numbers) |
| 5.9 Git rules | 3.9 |
| 5.10 Feature freeze | 2.5.9 |
| §3 Milestones | 1.5 |
| §6 Dataset facts, §8 Models | 2.7 |
| §7 Literature | 3.14 |
| §9 Tools | 2.2 |
| §10 Metrics, 10.2 Reporting protocol | 5.4 |
| §11 Paper plan | 3.12–3.13 |
| §12 Human-only work | 2.6 |
| §13 Risks | 4 |
| §14 Git workflow (14.6 reviewers, 14.7 tags) | 3.9 (3.10 reviewers; tags in 3.9 step 8) |

---

## 1. Executive Summary

### 1.1 Why
- **The assignment:** build and evaluate an AI/ML UEBA prototype that learns normal behavior per user and flags insider-threat activity, then write an IEEE-style research paper about it.
- **The research question:** *How effectively can AI/ML models detect anomalous user behavior associated with insider threats or compromised accounts, and which behavioral features and models provide the most reliable detection?*
- **The deadline:** **submit Fri Nov 20, 2026**. Be submission-ready on **Thu Nov 19**; Friday is a buffer.

### 1.2 What we build
- **Data:** CERT Insider Threat r4.2 (1,000 users, Jan 2 2010 – May 17 2011, 32.8M log rows). 70 insiders in 3 scenarios (30 / 30 / 10). 984 malicious user-days out of 330,268 (**0.298%**).
- **Unit of analysis:** one row per **user-day** with at least one logon.
- **Features (v1):** 73 model inputs:
  - **41 `f_*` behavior counts** across logon, time, USB, file, email, web and personality context;
  - **14 `z_user_*`** deviations from the user's own previous 30 active days;
  - **14 `z_peer_*`** deviations from same-role peers that day;
  - **4 `new_*`** first-time flags.
- **Models:** Isolation Forest, autoencoder and One-Class SVM (unsupervised, Arva); Random Forest and XGBoost (supervised, Ayo).
- **Risk scoring:** 0–100 daily risk, 7-day user risk, alert levels, and 3 readable reasons per alert (`src/pipeline.py`).
- **Evaluation:** test split only, at two operating points (best-F1 on val, top-1% alert budget), per scenario, plus leave-one-scenario-out (LOSO) for unseen behavior.
- **Paper:** IEEE conference format, ~8 pages, 8 tables (T1–T8) and 8 figures (F1–F8).

### 1.3 Where we stand (Thu Nov 5, `main` at `8060fc3`)
- **Weeks 0–1 code is done and merged** (PRs #1–#28). 83/83 tests pass. Most of it was written by Claude at Supriye's request, so **each owner must still read it and be able to explain every line** (2.6).
- **Feature table v1 exists** locally: 330,268 user-days, 73 inputs. Leakage checks 1, 2, 3 and 5 pass.
- **All 5 models run on v0** (100-user sample). Best val PR-AUC so far: IF 0.063, AE 0.122, RF 0.273, XGB 0.324.
- **No v1 model results yet.** No final score files, T5–T8, F4–F8, case studies or paper text exist yet.
- **Open human items:**
  - **Decisions:** the PROVISIONAL values;
  - **Reviews:** all of them (none of #1–#28 has one);
  - **Setup:** the data drop, Overleaf/Zotero and branch protection;
  - **Literature:** all notes (`paper/lit_notes/` is empty).
  - **Ayo:** no commits yet.

### 1.4 How the work flows from here

```
Thu Nov 5 – Sun Nov 8   CATCH-UP   decisions, reviews, ONE data drop, reading, code read-throughs → M2 (v1 frozen)
Mon Nov 9 – Wed Nov 11  MODELS     tune on v1 → final score files → LOSO, ablation, extra results → M3
Thu Nov 12 – Sat Nov 14 ANALYSIS   comparison, SHAP, FP/FN, case studies, prototype on v1 → results walkthrough
Sun Nov 15 – Wed Nov 18 PAPER      sections → M4 → full draft → M5 (code freeze Wed)
Thu Nov 19 – Fri Nov 20 FINISH     read-through, fresh-clone test, tag, archive → SUBMIT
```

### 1.5 Milestones

| ID | Due | Milestone | Owner | Done when | State (Nov 5) |
|---|---|---|---|---|---|
| M0 | Sat Oct 31 | **Setup complete** | Supriye | Everyone cloned and installed; Parquet data on the drive | Open (drive, Ayo) |
| — | Sun Nov 1 | `evaluate.py` ready | Ayo | Merged and tested | Done Nov 3 |
| — | Mon Nov 2 | Split dates final | Supriye | Dates written into 2.5.3 | Open (PROVISIONAL) |
| M1 | Tue Nov 3 | **Feature table v0** | Supriye | v0 + `get_model_matrix()` load in Arva's and Ayo's code | Open (confirmations) |
| — | Fri Nov 6 | `explain.py` ready | Ayo | Merged; Arva confirms it for the case studies | Code merged |
| M2 | Sun Nov 8 | **Feature table v1 frozen** | Supriye | v1 + dictionary on the drive; decisions final; both teammates load it | Built, not shared |
| — | Tue Nov 10 | Tuned models + scores | Arva, Ayo | Tuned defaults committed; final score files on the drive | — |
| M3 | Wed Nov 11 | **All score files final** | Arva, Ayo | All score files incl. LOSO + timing; `evaluate.py` runs on each | — |
| — | Sat Nov 14 | Analysis done | All | T5–T8, F4–F8, FP/FN, case studies; walkthrough held | — |
| M4 | Mon Nov 16 | **All paper sections drafted** | All | Every section in 3.12 is full text in Overleaf | — |
| M5 | Wed Nov 18 18:00 | **Full paper draft** | Supriye | One merged PDF circulated | — |
| — | Thu Nov 19 | Submission-ready | All | Fresh-clone test passes; `final-submission` tag | — |
| — | Fri Nov 20 | **Submitted** | All | Paper + code submitted | — |

---

## 2. Prerequisites / Required Tools

### 2.1 Access
- **GitHub:** collaborator access to `SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection` (all three have it, checked Nov 4).
- **Shared drive:** read access to one file, `ueba_data_v1.zip` (~360 MB, the only data that moves between laptops; 2.5.12). **Supriye uploads it once, by Sat Nov 7.**
- **Overleaf:** the team project on the IEEE conference template (Supriye creates it and invites both).
- **Zotero:** the shared group library (Supriye creates it), exporting IEEE style.
- **StFX library login:** for paywalled papers.
- **LANL data** *(only if S24 is agreed)*: each downloader accepts the terms at `csr.lanl.gov/data/cyber1/` personally.

### 2.2 Software
| Tool | Version / note | Used for |
|---|---|---|
| **Python** | 3.13 | Everything |
| **Virtual environment** | At a short path **outside** the repo, e.g. `%USERPROFILE%\.venvs\ueba` (Windows path-length limit) | Installing `requirements.txt` |
| **Packages** | Pinned in `requirements.txt`: pandas, numpy, pyarrow, scikit-learn, xgboost, imbalanced-learn, torch (CPU), shap, matplotlib, seaborn, jupyter, pytest, streamlit, psutil | Code, notebooks, tests |
| **Git + GitHub CLI (optional)** | Any recent | Branches, PRs |
| **Jupyter** | From `requirements.txt` | Notebooks 01–05 |
| **draw.io or PowerPoint** | Any | Figure F2 (Arva) |

### 2.3 One-time setup (each person)
1. **Clone** the repo: `git clone https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection.git`
2. **Create** the environment outside the repo: `python -m venv %USERPROFILE%\.venvs\ueba` (macOS/Linux: `python3 -m venv ~/.venvs/ueba`).
3. **Activate** it: `%USERPROFILE%\.venvs\ueba\Scripts\activate` (macOS/Linux: `source ~/.venvs/ueba/bin/activate`).
4. **Install** packages: `pip install -r requirements.txt`.
5. **Unzip** `ueba_data_v1.zip` into the repo root (it creates `data/processed/` and `data/parquet/`) and run `python scripts/data_drop.py verify`. Or rebuild everything yourself (2.5.11).
6. **Run** `python -m pytest tests` from the repo root. Expect every test to pass (without `data/`, the 2 v0 smoke tests skip).
7. **Set** your Git identity: `git config user.name "Your Name"` and `git config user.email "you@example.com"`.

### 2.4 Hardware
- **Disk:** ≥ 8 GB free to rebuild the data (4.8 GB archive + 1.2 GB Parquet).
- **RAM:** 16 GB is comfortable. The web log (28.4M rows) is always read in batches.
- **CPU time:** tuning on v1 takes about an hour per model family on a 24-thread laptop. Run it in the background.

### 2.5 Team contracts (every step must follow them; change only with the whole team)
#### 2.5.1 Feature table (Supriye)
- **Paths:** `data/processed/features_v0.parquet` (100-user sample), `features_v1.parquet` (all users).
- **Rows:** one per user-day with ≥ 1 logon. Days without a logon are dropped (17 activity days, 2 malicious days in v1).
- **Metadata columns (never model inputs):** `user, date, split, label, scenario, insider, role, department`.
- **Model inputs:** only columns starting with `f_`, `z_user_`, `z_peer_` or `new_`.
- **Definitions:** every column is in [docs/feature_dictionary.md](../docs/feature_dictionary.md).

#### 2.5.2 Score files (Arva, Ayo)
- **Path:** `results/scores/<model>.parquet`. Model stems: `iforest`, `autoencoder`, `ocsvm`, `random_forest`, `xgboost`, `iforest_contam`, `autoencoder_contam`, `<model>_loso_s<1|2|3>`.
- **Columns:** `user, date, split, label, scenario, score`. Higher `score` = more suspicious.
- **Coverage:** score **every** row (train, val, test). LOSO files hold only their test rows.

#### 2.5.3 Split rule (PROVISIONAL until Supriye decides)
- **By date, never shuffled.** `train` ≤ `TRAIN_END`, `val` ≤ `VAL_END`, else `test`.
- **Current values:** `TRAIN_END = 2010-10-31`, `VAL_END = 2011-01-31` (the 60/15/25 month rule).
- **Requirement:** every split has malicious days from every scenario (`python -m src.labels` checks it).
- **Known weakness:** scenario 3 in test is 1 real insider (`JLM0364`) with 2 days, plus 2 days on the hijacked account `FBA0348`.
- **Final values:** `train` = ______, `val` = ______, `test` = ______ *(Supriye fills in by Fri Nov 6)*.

#### 2.5.4 Training-data rule
- **Unsupervised models** train on `split == "train"` and `label == 0`; the `_contam` variants train on all train rows.
- **Supervised models** train on all `split == "train"` rows.
- **Tuning** uses `val` only. **Test** is used once, for the final numbers.

#### 2.5.5 Preprocessing rule
- **Every model** builds inputs with `get_model_matrix(df, split=..., columns=...)`: it applies `log1p` to `f_*` counts (not `NOT_COUNTS`) and fills NaN/inf with 0.
- **Every model** fits `StandardScaler` on training rows only, inside a scikit-learn (or imblearn) `Pipeline`.

#### 2.5.6 Threshold rule
- **Best-F1:** the threshold maximizing F1 on `val`, applied unchanged to `test`.
- **Top-1% budget:** flag the top 1% of `test` user-days.
- **Both** are computed by `src/evaluate.py` (`evaluate_file`, `compare_files`).

#### 2.5.7 Reproducibility rule
- **Seed** 42 everywhere (`RANDOM_STATE` in `src/config.py`).
- **Paths** come from `src/config.py`; no hard-coded `data/...` or `C:\Users\...`.
- **Notebooks** run top to bottom after Restart & Run All before merge.

#### 2.5.8 Code ownership (edit only your own files; otherwise open an Issue)
| Owner | Files |
|---|---|
| **Supriye** | `src/config.py`, `data_loader.py`, `labels.py`, `features.py`, `baseline.py`, `src/ablation.py` (new, S22), `src/lanl_features.py` (stretch); `tests/test_labels.py`, `test_features.py`, `test_baseline.py`, `test_pipeline_mini.py`, `test_v0_smoke.py`; notebooks `01`, `02`; `docs/feature_dictionary.md`; `README.md`, `requirements.txt`, `.gitignore`, `Tasks/`, `Guide/`, `paper/` assembly |
| **Arva** | `src/synthetic.py`, `models_unsupervised.py`, `risk_scoring.py`, `pipeline.py`, `app/dashboard.py`; their tests; notebooks `03a`, `05`; `docs/coverage.md`; `CLAUDE.md` |
| **Ayo** | `src/models_supervised.py`, `evaluate.py`, `explain.py`; their tests; notebooks `03b`, `04` |
| **Exception** | Arva adds the README "Run the prototype" section (A23) through a PR that Supriye reviews |

#### 2.5.9 Feature-table freeze
- **Freeze:** after Sun Nov 8.
- **Exception:** a result-changing bug reported as a GitHub Issue, fixed as `features_v1_1.parquet` by **Tue Nov 10 12:00**.

#### 2.5.10 Data rule
- **Git:** code, notebooks, small CSV tables (`results/tables/`), figures, notes. Every result table moves this way.
- **Shared drive:** only `ueba_data_v1.zip` (and `features_v1_1.parquet` if S21 needs it, or `lanl_features.parquet` if S24 happens).
- **Never shared:** raw archives, `http.parquet`, `results/scores/`, `models/`. Each laptop regenerates them (2.5.12).
- **Overleaf:** the paper.

#### 2.5.11 Rebuilding the data (if the drive copy is missing)
1. **Run** `bash scripts/download_cert.sh` (4.8 GB, resumable, checksum-verified).
2. **Run** `python -m src.data_loader convert` (~10 min).
3. **Run** `python -m src.labels`.
4. **Run** `python -m src.features v0` and `python -m src.features v1` (~2 min; the first v1 run makes a 30-second pass over the web log).

#### 2.5.12 Minimal-transfer rule (send code, not data)
- **One data drop, once:** after the decisions are final, Supriye uploads `ueba_data_v1.zip` (~360 MB):
  - **`data/processed/`:** `labels.parquet`, `features_v0.parquet`, `features_v1.parquet` (35 MB), `http_user_day_domain.parquet` (18 MB), `http_domain_counts.csv`;
  - **`data/parquet/`:** `logon`, `device`, `file`, `email` + `manifest.json` (~325 MB);
  - **`data/CHECKSUMS.txt`:** SHA-256 of every file, plus **`data/DROP_INFO.txt`** (commit and decisions). Built with `python scripts/data_drop.py make`, checked with `verify`.
- **Left out on purpose:** `http.parquet` (907 MB; the 18 MB web cache replaces it) and the 4.5 GB raw archive. Only Supriye needs those.
- **Tuned settings travel as code:** the merged module defaults (A16, Y15), never as parameter files or trained models.
- **Score files are rebuilt, not sent:**
  - **Rebuild commands:** `python -m src.models_unsupervised final` and `python -m src.models_supervised final` regenerate them from `features_v1.parquet` with seed 42, in minutes, with no grid search.
  - **Self-contained experiments:** LOSO, the ablation and SHAP retrain on their own.
- **One results machine:** the paper's comparison numbers (T5, T6, T8, F4–F6) come from Ayo's laptop (notebook 04), so small CPU differences in the AE cannot make two versions of a table.
- **Trained models (`models/`) are never shared:** `pipeline.py` retrains when one is missing (`--retrain`).
- **A second drop is allowed only for** `features_v1_1.parquet` (S21) or `lanl_features.parquet` (S24).

### 2.6 Human-only work (no AI agents)
**Check the course's AI-use policy first; if it is stricter, it wins.** These stay 100% human:

- **Reading papers** and writing literature notes and Related Work.
- **Writing the paper:** ideas, structure, sentences, conclusions.
- **Interpreting results** and answering the research question.
- **Explaining flagged anomalies** (case-study narratives and verdicts, FP/FN root causes).
- **Checking every citation:** it exists, the details are right, and it says what we claim.
- **Design decisions and their reasons:** granularity, after-hours, split dates, keyword lists, labeling, thresholds, alert levels, AE architecture, imbalance set-up, LOSO design.
- **Understanding every line of submitted code:** each owner explains their own code without notes.
- **Presenting the demo** and your own parts.

AI agents may write code (as in Weeks 0–1), but **the owner reviews it, runs it and can explain it** before it counts as done. Agents must leave every human-only box unticked.

### 2.7 Dataset and model facts

#### 2.7.1 CERT r4.2 files (columns verified Nov 3)
| File | Columns |
|---|---|
| `logon.csv` | `id, date, user, pc, activity` (Logon / Logoff); **no failed logins** |
| `device.csv` | `id, date, user, pc, activity` (Connect / Disconnect) |
| `file.csv` | `id, date, user, pc, filename, content` (copies to removable media; only doc/pdf/txt/jpg/zip/exe) |
| `email.csv` | `id, date, user, pc, to, cc, bcc, from, size, attachments, content` |
| `http.csv` | `id, date, user, pc, url, content` (28.4M rows, 475 domains) |
| `psychometric.csv` | `employee_name, user_id, O, C, E, A, N` |
| `LDAP/YYYY-MM.csv` | `employee_name, user_id, email, role, business_unit, functional_unit, department, team, supervisor` |
| `answers/insiders.csv` + `answers/r4.2-<s>/…` | One row per insider; one file per insider listing their malicious records |

`content` is dropped from email and http during conversion. The company domain is `dtaa.com`. 14 senior staff have no LDAP department (their functional unit is used).

#### 2.7.2 Insider scenarios
- **Scenario 1 (30 insiders):** someone who never worked after hours or used USB starts doing both and uploads data to `wikileaks.org`, then leaves.
- **Scenario 2 (30 insiders):** someone browses job sites and contacts a competitor, then copies data to USB at a much higher rate before leaving.
- **Scenario 3 (10 insiders):** a disgruntled sysadmin plants a keylogger via USB, logs in **as the supervisor** and sends an alarming mass email. 20 malicious days sit on the hijacked accounts `FAW0032`/`FBA0348` (decision S6).

#### 2.7.3 Models
| Model | Type | Owner | Trains on | Score (higher = more suspicious) | Required? |
|---|---|---|---|---|---|
| Isolation Forest | Unsupervised | Arva | train, label 0 | `-decision_function(X)` | Yes |
| Autoencoder (dense, PyTorch) | Unsupervised | Arva | train, label 0 | mean squared reconstruction error | Yes |
| One-Class SVM | Unsupervised | Arva | ≤ 20k train rows, label 0 | `-decision_function(X)` | Optional |
| `_contam` variants | Unsupervised | Arva | all train rows | same | Yes (contamination effect) |
| Random Forest | Supervised | Ayo | all train rows | `predict_proba(X)[:, 1]` | Yes |
| XGBoost | Supervised | Ayo | all train rows (early stopping on val) | `predict_proba(X)[:, 1]` | Yes |
| LSTM | Sequence | — | — | — | Not planned (future work, cite L5) |

- **Why both families:** unsupervised models match real deployments (labels are rare, attacks change); supervised models show the best case with labels. LOSO compares them on unseen attacks.

---

## 3. Step-by-Step Instructions

### 3.1 Daily routine (everyone)
1. **Pull** `main` every morning: `git checkout main`, then `git pull origin main`.
2. **Start** each task on its own branch from the fresh `main`: `git checkout -b <name>/<TaskID>-<short-description>`.
3. **Run** code from the repo root as modules: `python -m src.<module>`.
4. **Run** `python -m pytest tests` before every push.
5. **Check** `git status` before committing. Never commit data, score files or models.
6. **Commit** with the task ID first: `git commit -m "A15: tune on v1"`.
7. **Push** every evening: `git push -u origin <branch>`.
8. **Tick** the matching line in [PROGRESS.md](PROGRESS.md) on the same branch.
9. **Post** hand-offs in the group chat with the file path and commit or PR link.

### 3.2 Catch-up block: Thu Nov 5 – Sun Nov 8
1. **Supriye: decide** the 5 PROVISIONAL values (split dates, after-hours window, web keyword lists, email-count rule, hijacked-account labels) by **Fri Nov 6**, and write them into `src/config.py` and 2.5.3.
2. **Supriye: rebuild** labels, v0 and v1 if any value changed (Supriye.md S20b), then upload the **single** data drop `ueba_data_v1.zip` by **Sat Nov 7** (2.5.12).
3. **Everyone: read** the Claude-written code in your own lane until you can explain it (your file, step 1).
4. **Everyone: review** the merged PRs assigned to you in [PROGRESS.md §7](PROGRESS.md) and open new PRs for any fixes.
5. **Ayo: clone, install and run** the tests (Y1). This is overdue.
6. **Arva and Ayo: fix** the tuning-notebook log reset before running on v1 (Arva.md A15 step 1, Ayo.md Y14 step 1).
7. **Everyone: catch up** on literature notes (your LIT tasks).
8. **Supriye: freeze** v1 on **Sun Nov 8** (M2), then tag `m2-features-v1`.

### 3.3 Models block: Mon Nov 9 – Wed Nov 11
1. **Hold** the Mon stand-up with the 30-min v1 walkthrough. Decide whether the LANL stretch (S24) happens; the default is no.
2. **Arva and Ayo: tune** on v1 (A15, Y14) on Mon.
3. **Supriye: run** the bug-fix window until **Tue Nov 10 12:00** (S21); release `features_v1_1.parquet` only if a result-changing bug is reported.
4. **Arva and Ayo: merge** the tuned settings as code defaults plus a one-line `final` command that rebuilds their score files (A16, Y15) on Tue. **No score files are sent**: anyone runs `python -m src.models_unsupervised final` and `python -m src.models_supervised final`.
5. **Supriye: run** the feature-group ablation (S22) on Wed, after both tuned-defaults PRs merge.
6. **Arva: send** per-scenario recall, contamination effect, alert volume and timing (A17) on Wed.
7. **Ayo: run** LOSO and build T6 (Y16) on Wed → **M3**; Supriye tags `m3-all-scores`.

### 3.4 Analysis block: Thu Nov 12 – Sat Nov 14
1. **Ayo: build** T5, F4, F5, the detection-delay table and T8 (Y17) on Thu.
2. **Arva: run** the prototype on v1, record precision@20 and draw F8 (A18) on Thu.
3. **Ayo: run** the SHAP analysis (F6, `feature_importance.csv`, Y18) on Fri.
4. **Arva: build** the 4 case studies with F7 (A19) on Fri–Sat.
5. **Supriye: send** the data-processing time for T8 to Ayo on Fri.
6. **Everyone: post** your Related Work paragraphs in Overleaf by Fri night.
7. **Ayo: build** the FP/FN tables and causes (Y20) on Sat.
8. **Hold** the results walkthrough (45 min) on Sat. Agree on the answer to the research question; Supriye tags `analysis-done`.

### 3.5 Paper block: Sun Nov 15 – Wed Nov 18
1. **Write** your sections in Overleaf (3.12) by **Mon Nov 16** → M4.
2. **Supriye: integrate** and write the Abstract on Tue.
3. **Ayo: verify** every number against `results/tables/` on Tue (Y23).
4. **Arva: test** a fresh clone and rehearse the demo on Tue (A24).
5. **Freeze** code on **Wed Nov 18**: bug fixes only from here.
6. **Supriye: circulate** the full PDF by **Wed 18:00** → M5.

### 3.6 Finish: Thu Nov 19 – Fri Nov 20
1. **Hold** the final read-through (60 min) on Thu; fix everything assigned the same day.
2. **Supriye: merge** the last PRs, run the fresh-clone test, tag `final-submission` and build the code archive (S34).
3. **Supriye: submit** the paper and code on Fri, and post the confirmation in chat (S35).

### 3.7 Hand-off calendar (from Nov 5)

| Due | What | From → To |
|---|---|---|
| Fri Nov 6 | Final PROVISIONAL values in `src/config.py` + 2.5.3 | Supriye → all |
| Sat Nov 7 | **The only data drop:** `ueba_data_v1.zip` (labels, v0, v1, web cache, 4 small logs; ~360 MB) | Supriye → Arva, Ayo |
| Sun Nov 8 | v1 frozen + `docs/feature_dictionary.md` | Supriye → Arva, Ayo |
| Tue Nov 10 12:00 | `features_v1_1.parquet` *(only if needed; 35 MB, the only allowed second drop)* | Supriye → Arva, Ayo |
| Tue Nov 10 | Merged PR: tuned `models_unsupervised.py` defaults + `python -m src.models_unsupervised final` (rebuilds `iforest`, `autoencoder`, `*_contam`, `ocsvm`) | Arva → Ayo, Supriye (via Git) |
| Tue Nov 10 | Merged PR: tuned `models_supervised.py` defaults + `python -m src.models_supervised final` (rebuilds `random_forest`, `xgboost`) + `timing_supervised.csv` | Ayo → Supriye, Arva (via Git) |
| Wed Nov 11 | Merged PR with `results/tables/unsupervised_extra.csv` | Arva → Ayo (via Git) |
| Wed Nov 11 | Merged PR with `results/tables/loso.csv` (T6) | Ayo → team (via Git) |
| Wed Nov 11 | Merged PR with `results/tables/ablation.csv` (T7) | Supriye → Ayo (via Git) |
| Thu Nov 12 | T5, F4, F5 | Ayo → team |
| Fri Nov 13 | Merged PR with `data_processing_time.csv` (for T8; part of S22) | Supriye → Ayo (via Git) |
| Fri Nov 13 | Related Work paragraphs | Arva, Ayo → Supriye |
| Sun Nov 15 | IV-C, IV-D, V, VI-B drafts | Arva, Ayo → Supriye |
| Mon Nov 16 | VI-A, VI-C, VIII drafts + README "Run the prototype" | Arva, Ayo → Supriye |
| Wed Nov 18 18:00 | Full paper PDF | Supriye → Arva, Ayo |

### 3.8 Meetings
| Meeting | When | Length | Agenda |
|---|---|---|---|
| **Stand-up** | Every Mon, Wed, Fri | 15 min | Finished / next / blocked |
| **Catch-up check** | Fri Nov 6 (stand-up) | 15 min | Decisions final? Drive upload date? Reviews done? |
| **v1 walkthrough** | Mon Nov 9 | 30 min | Supriye explains the feature groups and dictionary; decide S24 |
| **Results walkthrough** | Sat Nov 14 | 45 min | T5, T6, T7, F4, FP/FN, case studies; agree on the answer |
| **Final read-through** | Thu Nov 19 | 60 min | Page-by-page fixes |

### 3.9 Git workflow
1. **Branch** names follow `<name>/<TaskID>-<short-description>`, e.g. `arva/A15-final-models`.
2. **Open** every PR into `main` with: tasks, what changed, how to test, and who it's a hand-off for.
3. **Assign** the reviewer from 3.10. The reviewer runs the "how to test" step and approves or requests changes within **12 h** (**3 h** for hand-offs).
4. **Merge** with **Squash and merge**, then **Delete branch**, then `git branch -D <branch>` locally.
5. **Retarget** stacked PRs before merging their base: open the child PR and set its base to `main` first. GitHub **closes** a child PR when its base branch is deleted (this happened to #18).
6. **Resolve** conflicts by keeping both sides' lines in `README.md` and `PROGRESS.md`. Never resolve a whole file with "ours". For a conflict in someone else's file or a notebook, run `git merge --abort` and ask the owner.
7. **Never** push to `main`, force-push `main`, or delete someone else's branch.
8. **Tag** milestones (Supriye): `git tag -a <tag> -m "<message>"`, then `git push origin <tag>`.

### 3.10 Reviewer map
| Author's branch kind | Reviewer |
|---|---|
| Supriye: data, features, baselines, LANL | Arva |
| Supriye: ablation, final README | Ayo |
| Arva: unsupervised models, tuning, results, case studies | Ayo |
| Arva: risk scoring, pipeline, final models, dashboard, README run section, fixes | Supriye |
| Ayo: `evaluate.py`, `explain.py`, LOSO, comparison, SHAP, FP/FN | Arva |
| Ayo: supervised models, final tuned models, verification | Supriye |
| Anyone: `<name>/notes`, tracker updates | Any teammate |

### 3.11 Branch calendar (remaining)
| Merge by | Branch | Tasks | Reviewer |
|---|---|---|---|
| Fri Nov 6 | `supriye/S8-decisions` | Final PROVISIONAL values (+ rebuild if changed) | Arva |
| Sun Nov 8 | review-fix branches as needed | Fixes from post-merge reviews | File owner's reviewer |
| Tue Nov 10 12:00 | `supriye/S21-v1-fixes` *(only if needed)* | S21 | Arva |
| Tue Nov 10 | `arva/A15-final-models` | A15, A16 | Supriye |
| Tue Nov 10 | `ayo/Y14-final-models` | Y14, Y15 | Supriye |
| Wed Nov 11 | `supriye/S22-ablation` | S22 (+ T8 data time) | Ayo |
| Wed Nov 11 | `arva/A17-results` | A17 | Ayo |
| Wed Nov 11 | `ayo/Y16-loso-results` | Y16 | Arva |
| Wed Nov 11 | `supriye/S24-lanl` *(stretch)* | S24 | Arva |
| Thu Nov 12 | `ayo/Y17-comparison` | Y17 | Arva |
| Fri Nov 13 | `supriye/notes`, `arva/notes`, `ayo/notes` | LIT notes, section notes, F2 | Any teammate |
| Sat Nov 14 | `arva/A18-prototype-cases` | A18, A19 | Ayo |
| Sat Nov 14 | `ayo/Y18-shap-fpfn` | Y18, Y20 | Arva |
| Sat Nov 14 | `arva/A21-dashboard` *(optional)* | A21 | Supriye |
| Mon Nov 16 | `arva/A23-readme-run` | A23 | Supriye |
| Tue Nov 17 | `arva/A24-fresh-clone-fixes`, `ayo/Y23-verify` | A24, Y23 | Supriye |
| Wed Nov 18 | **Code freeze** | Bug fixes only | — |
| Thu Nov 19 | `arva/A26-final-fixes`, `ayo/Y25-final-fixes` *(if needed)* | A26, Y25 | Supriye |
| Thu Nov 19 | `supriye/S33-final` | S33, S34 | Ayo |

### 3.12 Paper sections
| Section | Writer | Length | Draft due |
|---|---|---|---|
| Abstract | Supriye | ~200 words | Tue Nov 17 |
| I. Introduction | Supriye | 0.75 p | Fri Nov 13 |
| II. Related Work + T1 | All write; Supriye merges | 1 p | Paragraphs Fri Nov 13; merged Sat Nov 14 |
| III. Dataset | Supriye | 0.75 p | Tue Nov 10 |
| IV-A Preprocessing & Features | Supriye | 0.75 p | Thu Nov 12 |
| IV-B Establishing Normal Behavior | Supriye | 0.5 p | Thu Nov 12 |
| IV-C Models: unsupervised / supervised | Arva / Ayo | 0.5 p each | Sun Nov 15 |
| IV-D Risk Scoring & Prototype | Arva | 0.5 p | Sun Nov 15 |
| V. Experiments & Results | Ayo | 1.25 p | Sun Nov 15 |
| VI-A Feature Importance | Ayo | 0.5 p | Mon Nov 16 |
| VI-B Anomaly Case Studies | Arva | 0.75 p | Sun Nov 15 |
| VI-C FP / FN Analysis | Ayo | 0.5 p | Mon Nov 16 |
| VII. Limitations & Ethics | Supriye | 0.5 p | Fri Nov 13 |
| VIII. Conclusion & Future Work | Arva | 0.25 p | Mon Nov 16 |

### 3.13 Figures and tables
| # | Content | Owner | Source | State (Nov 5) |
|---|---|---|---|---|
| T1 | Literature comparison | Supriye | Lit notes | — |
| T2 | Dataset summary + class imbalance | Supriye | `class_imbalance.csv`, `dataset_files.csv` | Data ready |
| T3 | Feature dictionary (condensed) | Supriye | `docs/feature_dictionary.md` | Data ready |
| T4 | Hyperparameters | Arva, Ayo | `T4_hyperparameters_*.csv` | v0 drafts |
| T5 | Model comparison, both thresholds | Ayo | `model_comparison.csv` | — |
| T6 | LOSO results | Ayo | `loso.csv` | — |
| T7 | Feature-group ablation | Supriye | `ablation.csv` | — |
| T8 | Timing + detection delay | Ayo | `T8_timing.csv` | — |
| F1 | Hourly activity, insider vs. normal | Supriye | `F1_insider_vs_normal.*` | Done |
| F2 | UEBA pipeline diagram | Arva | draw.io | — |
| F3 | One user's baseline vs. deviating days | Supriye | `F3_user_baseline.*` | Done |
| F4 | ROC + PR curves | Ayo | `F4_*` | — |
| F5 | Confusion matrices | Ayo | `F5_*` | — |
| F6 | SHAP summary (XGBoost) | Ayo | `F6_*` | v0 version only |
| F7 | Case-study explanations | Arva | `F7_*` | — |
| F8 | Risk timeline, one insider | Arva | `F8_*` | — |

### 3.14 Literature (≥ 5 recent papers from IEEE, Springer, Elsevier or ACM)
| ID | Paper | Reader |
|---|---|---|
| L1 | Glasser & Lindauer, "Bridging the Gap…", IEEE S&P Workshops (2013) | Supriye |
| L2 | Le, Zincir-Heywood & Heywood, "Analyzing Data Granularity Levels…", IEEE TNSM (2020) | Supriye |
| L3 | Homoliak et al., "Insight into Insiders and IT…", ACM Computing Surveys (2019) | Supriye |
| L4 | Tuor et al., "Deep Learning for Unsupervised Insider Threat Detection…", AAAI Workshops (2017) | Arva |
| L5 | Lu & Wong, "Insider Threat Detection with LSTM", ACM ACSW (2019) | Arva |
| L6 | Liu, De Vel, Han, Zhang & Xiang, "Detecting and Preventing Cyber Insider Threats: A Survey", IEEE COMST (2018) | Ayo |
| L7 | Yuan & Wu, "Deep Learning for Insider Threat Detection: Review…", Computers & Security (2021) | Ayo |
| L8 | Liu et al., "Log2vec…", ACM CCS (2019) | Ayo |
| L9a / L10a / L11a | One **2022–2026** paper each: features/UEBA (Supriye), unsupervised/AE (Arva), supervised/XAI (Ayo) | Each |
| L9b / L10b / L11b | **Strongly recommended:** "recent" may mean the last 5 years, which only L9a–L11a (+ L7) meet | Each |

- **Method citations:**
  - **Arva:** Liu, Ting & Zhou (IF, 2008), Schölkopf et al. (OCSVM, 2001) and Chandola et al. (2009).
  - **Ayo:** Breiman (2001), Chen & Guestrin (2016), Lundberg & Lee (2017) and Saito & Rehmsmeier (2015).
  - **Supriye:** Lindauer (CERT, KiltHub), plus Kent (LANL, 2015) if S24 is done.
- **Finding papers:** use Google Scholar "Cited by" on L2 or L7 with "Since 2022", or IEEE Xplore / ACM DL / ScienceDirect / SpringerLink. Post the title in chat before reading.
- **Note template** (`paper/lit_notes/<ID>.md`): citation (IEEE), problem, dataset, granularity, features, models, metrics + key numbers, strengths, limitations, relation to our project.

---

## 4. Edge Cases & Troubleshooting

### 4.1 Environment
- **`pip install` fails on a long path (Windows):** create the venv outside the repo at a short path (2.3).
- **`UnicodeEncodeError` printing "σ" or "→" on Windows:** set `PYTHONIOENCODING=utf-8` before running, e.g. `set PYTHONIOENCODING=utf-8` and then `python src/pipeline.py`.
- **`ModuleNotFoundError: src`:** run from the repo root as `python -m src.<module>`. `python src/pipeline.py` also works.
- **Tests skip `test_v0_smoke`:** `data/processed/features_v0.parquet` is missing; copy `data/` from the drive.

### 4.2 Data
- **The conversion stops after `file.csv`:** the archive is multi-stream bz2. Use `python -m src.data_loader convert`, which handles it; never `tarfile.open(..., "r|bz2")`.
- **Out of memory on the web log:** always pass `columns=` / `users=` to `load_http`, or use `iter_http_batches()`. The S15 cache (`data/processed/http_user_day_domain.parquet`) avoids re-reading it.
- **Counts that look inconsistent:** 70 insiders vs. 72 accounts (2 hijacked supervisor accounts); 986 labeled malicious user-days vs. 984 in the feature table (2 days with no logon). Both are expected.
- **Web features:** v1 has **7** `f_http_*` columns (count, domains, after-hours, job, leak, cloud, hack), not 8.
- **Checksums don't match after unzipping** (`python scripts/data_drop.py verify` lists `CHANGED`/`MISSING`): re-download the zip once; if it still fails, ask Supriye to re-upload. Never send single files around.
- **The working hours changed but the after-hours web counts didn't:** fixed. The web-log cache records the window it was built with and rebuilds itself (S20b, Nov 5).
- **A teammate's score file differs slightly from yours:** this is expected for the AE on another CPU. Use the results machine's tables (2.5.12) for the paper.
- **Someone asks for a score file or model:** send the command instead (`python -m src.models_*  final`, `python src/pipeline.py --retrain`).

### 4.3 Models and results
- **Tuning notebooks wipe the v0 log:** `03a`/`03b` call `log_path.unlink()` at the start. Before running on v1, change them to drop only the current dataset's rows (A15, Y14 step 1).
- **Tuning log columns get misaligned:** `tune_supervised()` appends with `mode="a"`. If you add a log column, rewrite the file with `pd.concat([old, new])`, not an append.
- **Supervised scores near 1.0 on v1:** an unsaved Nov 5 run gave RF/XGB val PR-AUC ≈ 0.95–0.99 with all 73 inputs. Without the 5 psychometric columns it was still 0.99; with only the raw `f_*` counts it was 0.51 val / 0.38 test. So the baselines drive it. **Re-run, then sanity-check** (ablation S22, SHAP Y18) before claiming it in the paper.
- **Isolation Forest weak on v1:** the same unsaved run gave IF val PR-AUC ≈ 0.014. Report it honestly, and check the tuned AE and the per-scenario numbers.
- **One-Class SVM below random on v0** (ROC-AUC 0.26): the implementation was checked. It's optional, so Arva decides whether to keep, tune or drop it.
- **XGBoost stops at iteration 0 on synthetic data:** val has 24 positives, so val PR-AUC is noisy. On real data it trains 81–221 trees.
- **Scenario 3 is thin in test:** 4 malicious days. Say so in V and VII, and lean on LOSO.

### 4.4 Git
- **A stacked child PR closed itself:** its base branch was deleted. Push the base branch back, reopen the PR, set its base to `main`, then delete the base again.
- **Conflict in `README.md` / `PROGRESS.md`:** keep both sides line by line (3.9 step 6).
- **Squash-merged branch won't delete locally:** use `git branch -D <branch>`.
- **`main` broke after a merge:** tell the team, find the PR on GitHub and click **Revert**; never force-push.
- **Worktree with folder links (junctions):** remove the links before deleting the worktree, or the delete follows them into the real `data/`.

### 4.5 People and time
- **A hand-off will be late:** say so in chat as soon as you know, with the new time.
- **Running behind at M3:** drop optional items first (One-Class SVM, dashboard, LANL, second recent paper). Never drop the 2 + 2 models, LOSO, FP/FN or the case studies.
- **A teammate is unavailable:** the other two split their open tasks by priority; all code and notes are on GitHub.
- **A PR waits > 3 h on a hand-off:** ping the reviewer; after that, the third person reviews.

---

## 5. Success Metrics / Definitions

### 5.1 Definition of done
- **A task** is done when every "Done when" item in its card is true and its PR is merged.
- **A hand-off** is delivered when its PR is merged and announced (data: uploaded and announced).
- **A milestone** is done when its "Done when" column (1.5) is true; Supriye then ticks it in PROGRESS and tags `main`.

### 5.2 Assignment requirements → proof
| Requirement | Proof that it is met |
|---|---|
| Study insider threats, compromised accounts, anomalies, UEBA | §I + §II with checked citations |
| ≥ 5 recent papers (IEEE/Springer/Elsevier/ACM) | ≥ 5 notes in `paper/lit_notes/`, T1 with venue + year |
| Suitable dataset, preprocessed | §III; `cleaning_report.csv`, `split_check.csv` |
| Login patterns | `f_logon_*` family in v1 + T3 |
| Authentication failures | LANL features (S24) **or** the gap stated in §III and §VII |
| File / resource access | `f_file_*`, `f_usb_*` + T3 |
| Application usage | `f_http_*`, `f_email_*` + the stand-in stated in §III |
| Activity times | `f_afterhours_*`, `f_weekend`, `f_work_duration` + reason for the hours |
| Deviation from baseline | `z_user_*`, `z_peer_*`, `new_*` + F3 |
| ≥ 2 models compared | 5 score files + T5 |
| Risk score | `pipeline.py` output, alert levels, F8 |
| Precision, recall, F1, FPR, FNR, accuracy, ROC-AUC, PR-AUC, confusion matrix | T5, F4, F5 |
| Detection time | T8 (compute time + delay) |
| Precision/recall vs. accuracy paragraph | §V with 0.298% / 99.70% numbers |
| Unseen behavior | T6 (LOSO) |
| FP / FN analysis | §VI-C + `fp_fn_causes.csv` |
| Feature importance | F6, `feature_importance.csv`, T7 |
| Anomaly explanations | Notebook 05 + §VI-B + F7 |
| Prototype | `python src/pipeline.py` from a fresh clone + README section |
| Paper | IEEE PDF within the page limit, all T1–T8 and F1–F8 referenced |

### 5.3 Quality gates
- **Tests:** `python -m pytest tests` passes on `main` after every merge (83 today; the count only grows).
- **Notebooks:** 01–05 run top to bottom; their outputs match `results/tables/`.
- **Reproducibility:** a fresh clone + `pip install -r requirements.txt` + `ueba_data_v1.zip` runs both `final` commands, the pipeline and `04_evaluation.ipynb`.
- **Transfers:** exactly one data drop (two if S21 or S24 happens); no score file, model or partial table was ever sent by chat or drive.
- **Numbers:** every number in the paper traces to a CSV in `results/tables/` (Y23).
- **Ownership:** each person can explain their code line by line (2.6).

### 5.4 Evaluation metrics and reporting protocol
TP = malicious user-day flagged, FP = normal flagged, TN = normal not flagged, FN = malicious not flagged. All are computed by `src/evaluate.py`.

| Metric | Formula / meaning | Note |
|---|---|---|
| Accuracy | (TP + TN) / all | Reported but **misleading**: "always normal" scores 99.70% |
| Precision | TP / (TP + FP) | Share of alerts that are real |
| Recall (TPR) | TP / (TP + FN) | Share of threats caught |
| F1 | 2PR / (P + R) | Balance of the two |
| FPR | FP / (FP + TN) | Analyst alert fatigue |
| FNR | FN / (FN + TP) | Missed threats |
| ROC-AUC | Area under TPR vs. FPR | Threshold-free |
| **PR-AUC** | Average precision | **Primary metric** under 0.298% positives |
| Confusion matrix | TP / FP / TN / FN | At each operating point (F5) |
| Detection time (a) | Fit time; inference time per 1,000 user-days (3-run mean) | T8 |
| Detection time (b) | Days from an insider's first malicious test day to the first alert | T8 |
| User-level recall | Test insiders flagged on ≥ 1 malicious day / all test insiders | T5 |

**Reporting protocol (every model, `test` split only):**
1. **Report** all metrics at the **best-F1** threshold (from val) and the **top-1%** budget.
2. **Report** ROC-AUC and PR-AUC.
3. **Report** the same per scenario (1, 2, 3).
4. **Report** the unseen-scenario (LOSO) results (T6).
5. **Include** the precision/recall paragraph in §V: 984 of 330,268 user-days (0.298%) are malicious, so always answering "normal" scores 99.70% accuracy with 0% recall (`class_imbalance.csv`).
