# Progress Tracker — Everyone's Tasks and Events

**Last updated:** Wed Nov 4, 2026 (cross-check of Tasks, Guide and docs against the repo) · **Submission:** Fri Nov 20, 2026 (ready by Thu Nov 19)

## How to use this file
- `[x]` = done: every "Done when" item of that task in the person's plan is true. `[ ]` = not done yet.
- Indented boxes under a task show partial progress.
- **(Claude)** = the work was done by Claude (AI) at Supriye's request. The owner must still read it, understand it and be able to explain it (TEAM_PLAN 12, rule 7), and review it before the PR is merged.
- **Status unknown** = the date has passed but nobody has recorded it here. The owner ticks it, or writes what's left.
- **Human-only** = TEAM_PLAN Section 12 or the person's "Do This Yourself" list keeps this for a person. Claude did not do these.
- Update your own section whenever you finish something, and commit it on the branch you're working on.

---

## 0. Snapshot

- **Behind plan:** M0 (Sat Oct 31) and `evaluate.py` (Sun Nov 1) were late. **All S1–S9 and Y3–Y6 code is merged into `main` (Tue Nov 3)**. M1 still needs v0 rebuilt with Supriye's confirmed values, plus Arva's and Ayo's confirmation (§9).
- **Done by Claude, at Supriye's request (Nov 2–3):**
  - **Data:** CERT r4.2 downloaded and checksum-verified, converted to Parquet (32.8M rows, 1.2 GB), labels built: 70 insiders, 984 malicious user-days out of 330,268 (0.298%).
  - **Notebook and tables:** EDA notebook run end to end; v0 table built (100 users, 31,175 user-days, 236 malicious, every split × scenario covered; rebuilt Nov 4 so all 20 insiders are real).
  - **Ayo's `evaluate.py`** (Y3–Y6).
  - **Tests:** 23/23 pass on `main` + this update (with the data present; without it the 2 v0 smoke tests skip).
- **Bugs found and fixed:**
  - **Before running** (self-review): duplicated `date` column, de-duplication on column subsets, nullable integers.
  - **On real data:** the archive is multi-stream bz2, which the first converter couldn't read; 14 senior staff have no department in LDAP.
- **Environment:** on this laptop the project path is too long for Jupyter's install (Windows 260-character limit), so the environment lives at `%USERPROFILE%\.venvs\ueba`; the README explains it.
- **Review of `main`, Wed Nov 4 (Claude, at Supriye's request).** Fixed in [PR #11](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/11) (merged):
  - **v0 sampled both hijacked supervisor accounts as scenario-3 insiders**, so 2 of the 6 "insiders" were victims and 20 of 252 malicious rows were theirs. The sampler and the `insider` column now use only `answers/insiders.csv`. A new unit test fails on the old code.
  - **`class_imbalance.csv` said 72 insiders.** It now gives 70 insiders (30/30/10) and, separately, 72 accounts with malicious days. This resolves the "two counts disagree" point in `docs/coverage.md`; the 986 vs 984 gap is the 2 malicious days with no logon.
  - **`requirements.txt` pinned the Windows-only `pywinpty`,** which would break `pip install` on macOS/Linux; it's now marked `sys_platform == "win32"`.
  - **`scripts/download_cert.sh` used `sha256sum`,** which macOS lacks; it now falls back to `shasum -a 256`.
  - **No bugs in `evaluate.py`.** One note for Ayo (his file, not edited): `detection_delay()` counts from an insider's first malicious day *in test*, so a campaign that started in val looks faster to detect. Say so in §V or add the first-ever day.
  - **Process:** `docs/coverage.md` (Arva) went straight to `main` without a PR (TEAM_PLAN 5.9); PR #9 (Arva's `CLAUDE.md`) was merged without a review.
- **Cross-check of the docs, Wed Nov 4 evening (Claude).** Every number quoted in `Tasks/`, `Guide/` and `docs/` was recomputed from the data. All matched except one:
  - **Scenario 3 is thinner than reported.** "Scenario 3 in test: 2 insiders, 4 days" counted *accounts*. The truth: **1 real insider (`JLM0364`) with 2 days**, plus 2 days on the hijacked supervisor account `FBA0348`. Across all splits, **20 of scenario 3's 40 labeled days are on the two hijacked accounts**. `split_check.csv` now reports real insiders and accounts separately; a new test covers it.
  - Stale facts updated in the plans: disk space, conversion time, merged PRs, collaborators, branch-protection note, the real base rate in TEAM_PLAN 10.2, the README folder tree, and the ticked setup/EDA steps in the guide.
- **Overdue as of Wed Nov 4:**
  - **Arva:** A4–A10 (unsupervised models, risk score, first v0 run, tuning), due Oct 30 – Nov 4. A3 is done: [PR #10](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/10) merged Nov 4 (`src/synthetic.py`, 5 tests). Follow-up rename `f_http_job_site` → `f_http_job` done on branch `arva/A3-http-job-rename`.
  - **Ayo:** Y7–Y9 (supervised models, first v0 run, tuning), due Nov 2–4. Ayo has no commits yet.
  - **Literature:** `paper/lit_notes/` is empty; S-LIT, A-LIT1–2 and Y-LIT1–2 were due Oct 28 – Nov 2.
  - **Supriye:** the human-only decisions above; S10 and S11 are due today.
- **Waiting on Supriye (human-only, Section 4 → "Decisions"):** after-hours hours, split dates, web keyword lists, EDA observations, label hand-check, and two new labeling questions (see S6, S14).
- **Waiting on Ayo:** read `evaluate.py` (now on `main`), do the Y3 paper hand-check, and do the post-merge reviews assigned in §9.
- **Waiting on Arva:** A4–A10 (A3 is merged); v0 + `get_model_matrix()` + `evaluate.py` + `synthetic.py` are all on `main`, ready for A4–A9. Also the post-merge reviews in §9 and the `f_http_job` rename.
- **GitHub:** PRs #1–#11 are merged and every task branch is deleted; only `main` remains. **No PR had a GitHub review**, so the reviews in §9 are still open and are done after the merge. All three are collaborators (`SupriyeAmatya`; `arjasa1103` = Arva; `Bizzlefresh`). **Branch protection on `main` is off**, and the repo is **public**, which makes protection free: Supriye can turn it on in Settings → Branches. Being public also means anyone can read the course work, so check the course rules. No milestone tags yet.
- **Everyone now:** `git checkout main`, then `git pull origin main`. New branches start from `main`; no more stacking.

---

## 1. Milestones

- [ ] **Kickoff done** (Thu Oct 29): Section 5 rules agreed and written into TEAM_PLAN. *Status unknown*
- [ ] **M0 Setup complete** (Sat Oct 31)
  - [ ] Repo cloned by all 3 *(Arva, Ayo: status unknown)*
  - [ ] Everyone's environment installs from `requirements.txt`
  - [ ] CERT r4.2 Parquet files on the shared drive
- [x] **`evaluate.py` ready** (Sun Nov 1, Ayo): merged to `main`, tested on synthetic scores. *Done Tue Nov 3 (PR #3, reached `main` via #7); Ayo's own review still open (§9)*
- [ ] **Split dates final** (Mon Nov 2, Supriye): boundaries written into TEAM_PLAN 5.3
- [ ] **M1 Feature table v0** (Tue Nov 3, Supriye): `features_v0.parquet` + `get_model_matrix()` load in Arva's and Ayo's code
- [ ] **`explain.py` ready** (Fri Nov 6, Ayo)
- [ ] **M2 Feature table v1** (Sun Nov 8, Supriye): v1 + feature dictionary shared, leakage checks passed
- [ ] **Unsupervised scores + tuned model code** (Tue Nov 10, Arva & Ayo)
- [ ] **M3 All score files final** (Wed Nov 11, Arva & Ayo)
- [ ] **Analysis done** (Sat Nov 14, all)
- [ ] **M4 All paper sections drafted** (Mon Nov 16, all)
- [ ] **M5 Full paper draft** circulated by 18:00 (Wed Nov 18, Supriye)
- [ ] **Code freeze** (Wed Nov 18): only bug fixes merged after this
- [ ] **Submission-ready** (Thu Nov 19, all): final fixes applied; code runs from a fresh clone
- [ ] **Submitted** (Fri Nov 20, all)

## 2. Meetings and stand-ups

- [ ] Kickoff, 60 min (Thu Oct 29) *Status unknown*
- [ ] Stand-up Mon Nov 2
- [ ] Stand-up Wed Nov 4
- [ ] Stand-up Fri Nov 6
- [ ] Stand-up + **features v1 walkthrough** (Mon Nov 9). Also decide whether the LANL stretch (S24) happens
- [ ] Stand-up Wed Nov 11
- [ ] Stand-up Fri Nov 13
- [ ] **Results walkthrough**, 45 min (Sat Nov 14): agree on the answer to the research question
- [ ] Stand-up Mon Nov 16
- [ ] Stand-up Wed Nov 18
- [ ] **Final read-through**, 60 min (Thu Nov 19)

## 3. Hand-offs

| ✓ | Due | What | From → To |
|---|---|---|---|
| [ ] | Thu Oct 29 | GitHub invites, `requirements.txt`, Overleaf + Zotero invites | Supriye → Arva, Ayo |
| [x] | Thu Oct 29 | `src/synthetic.py` *(merged Nov 4, PR #10)* | Arva → Ayo |
| [ ] | Sat Oct 31 | CERT Parquet files on the shared drive | Supriye → Arva, Ayo |
| [x] | Sun Nov 1 | `src/evaluate.py` merged *(Nov 3)* | Ayo → Arva, Supriye |
| [ ] | Mon Nov 2 | Final split dates (TEAM_PLAN 5.3) | Supriye → Arva, Ayo |
| [ ] | Tue Nov 3 | `features_v0.parquet` (drive) + `get_model_matrix()` (merged) | Supriye → Arva, Ayo |
| [ ] | Fri Nov 6 | `src/explain.py` merged | Ayo → Arva |
| [ ] | Sun Nov 8 | `features_v1.parquet` + feature dictionary | Supriye → Arva, Ayo |
| [ ] | Tue Nov 10, 12:00 | `features_v1_1.parquet` *(only if needed)* | Supriye → Arva, Ayo |
| [ ] | Tue Nov 10 | Unsupervised score files (drive) + tuned `models_unsupervised.py` | Arva → Ayo, Supriye |
| [ ] | Tue Nov 10 | `random_forest` / `xgboost` score files + tuned `models_supervised.py` | Ayo → team, Supriye |
| [ ] | Wed Nov 11 | Per-scenario results, alert volume, timings (`unsupervised_extra.csv`) | Arva → Ayo |
| [ ] | Wed Nov 11 | LOSO score files + table T6 | Ayo → team |
| [ ] | Thu Nov 12 | Comparison table T5 + figures F4, F5 | Ayo → team |
| [ ] | Fri Nov 13 | Data-processing time (for T8) | Supriye → Ayo |
| [ ] | Fri Nov 13 | Related Work paragraphs | Arva, Ayo → Supriye |
| [ ] | Sun Nov 15 | IV-C, IV-D, V, VI-B | Arva, Ayo → Supriye |
| [ ] | Mon Nov 16 | VI-A, VI-C, VIII | Arva, Ayo → Supriye |
| [ ] | Wed Nov 18, 18:00 | Full paper draft PDF | Supriye → Arva, Ayo |

---

## 4. Supriye

### Week 0
- [x] **S1** (Wed Oct 28) Download CERT r4.2 **(Claude, done Nov 3)**
  - [x] Resumable parallel download script `scripts/download_cert.sh`
  - [x] `r4.2.tar.bz2` (4.82 GB) and `answers.tar.bz2` downloaded; both SHA-256 checksums match
- [ ] **S2** (Wed Oct 28 – Thu Oct 29) Repository, environment and writing tools
  - [x] Folder structure, `.gitignore` (TEAM_PLAN 14.1), `src/config.py` committed on `supriye/S2-setup` **(Claude)**
  - [x] Environment built (Python 3.13, at `%USERPROFILE%\.venvs\ueba`, because the repo path is too long for Windows) and `requirements.txt` pinned on `supriye/S2-setup` **(Claude)**
  - [x] Both teammates added as collaborators (`arjasa1103`, `Bizzlefresh`; checked Nov 4)
  - [ ] Branch protection on `main` (GitHub Settings → Branches, Supriye; free because the repo is public)
  - [ ] Overleaf project (IEEE template) + Zotero group library created; invites sent
  - [ ] PR merged (reviewer Ayo); Arva and Ayo cloned and installed `requirements.txt`
- [ ] **S3** (Thu Oct 29) Run the kickoff meeting. *Status unknown*
  - [ ] Page limit, AI-use policy, PyTorch vs. Keras and submission contents confirmed
  - [ ] Section 5 decisions written into TEAM_PLAN and pushed
- [ ] **S4** (Fri Oct 30) Convert CSVs to Parquet
  - [x] Streaming converter `python -m src.data_loader convert` on `supriye/S5-data-loader` **(Claude)**
  - [x] Run on the real archive: 5 logs, 32,770,222 rows, Jan 2 2010 – May 17 2011 (`data/parquet/manifest.json`, `results/tables/dataset_files.csv`) **(Claude)**
  - [ ] `data/` (raw answers, parquet, processed) uploaded to the shared drive (Supriye)
- [ ] **S5** (Sat Oct 31) Data loaders and cleaning → M0
  - [x] Loaders `load_logon()` … `load_insiders()`, `iter_http_batches()`, cleaning report **(Claude)**
  - [x] Cleaning report produced: no duplicates or missing keys in any log (`results/tables/cleaning_report.csv`) **(Claude)**
  - [ ] PRs for S2 and S5 merged (reviewers Ayo, Arva) → tag `m0-setup` (Section 9)

### Week 1
- [ ] **S6** (Sun Nov 1) Ground-truth labels + insider timeline
  - [x] `python -m src.labels`: labels, insider timeline and the step-4 checks, on `supriye/S6-labels-eda` **(Claude)**
  - [x] Run: 70 insiders (30/30/10), matching `insiders.csv`; 7,323 malicious records; all inside each insider's start–end; 986 malicious user-days **(Claude)**
  - [ ] **Human-only:** hand-check 3 insiders against `data/raw/answers/` (Supriye)
  - [ ] **Decision (Supriye):** 50 scenario-3 records happen on the *supervisor's* account (the sysadmin logs in as them), so 20 malicious days are labeled on accounts `FAW0032` and `FBA0348`. Since Nov 4 (PR #11) they don't count as insiders, but those 20 days are still labeled malicious, which is half of scenario 3's labeled days. Keep this (compromised-account view) or move those days to the insider?
- [ ] **S7** (Sun Nov 1 – Mon Nov 2) EDA notebook `notebooks/01_eda.ipynb`
  - [x] Notebook `notebooks/01_eda.ipynb` with items 1–6 written **(Claude)**
  - [x] Run top to bottom (10/10 cells, no errors); 4 figures incl. F1 in `results/figures/`, 7 tables in `results/tables/` **(Claude)**
  - [ ] **Human-only:** Observation cells written (Supriye)
- [ ] **S8** (Sun Nov 1 – Mon Nov 2) Decide the train/val/test split
  - [x] Default 60/15/25 proposal + split check (`results/tables/split_check.csv`) **(Claude)**
  - [x] The plan's default (train ≤ 2010-10-31, val ≤ 2011-01-31) passes: every split has every scenario. Thinnest cell: scenario 3 in test, only **1 real insider (`JLM0364`) with 2 days**; 2 more days are on the hijacked account `FBA0348` (corrected Nov 4; `split_check.csv` now shows insiders and accounts separately) **(Claude)**
  - [ ] **Human-only:** Supriye decides `TRAIN_END` / `VAL_END` in `src/config.py` (now PROVISIONAL: 2010-10-31 / 2011-01-31)
  - [ ] Final dates written into TEAM_PLAN 5.3 and announced
- [ ] **S9** (Tue Nov 3) Feature table v0 + `get_model_matrix()` → M1
  - [x] `python -m src.features v0` + `get_model_matrix()` + tests, on `supriye/S9-features-v0` **(Claude)**
  - [x] `features_v0.parquet` built with the PROVISIONAL values: 100 users (20 insiders, 7/7/6 per scenario), 31,175 user-days, 236 malicious, every split × scenario covered (test has only 2 scenario-3 rows); all 20 insiders are real insiders (rebuilt Nov 4); smoke tests pass with `evaluate.py` **(Claude)**
  - [ ] Rebuilt once Supriye confirms after-hours + split, then uploaded to the drive
  - [ ] PRs merged (reviewer Arva) → tag `m1-features-v0`; Arva and Ayo confirm it loads in their code
- [ ] **S10** (Wed Nov 4) Login features
- [ ] **S11** (Wed Nov 4) Activity-time features. **Human-only:** decide after hours from the EDA hour plot and write the reason in the feature dictionary
- [ ] **S12** (Thu Nov 5) USB device features
- [ ] **S13** (Thu Nov 5) File features
- [ ] **S14** (Fri Nov 6) Email features. **Decision (Supriye):** only 62.4% of emails come from the user's own `dtaa.com` address; the rest look like personal webmail sent from the work PC. Count all of them as "sent", or only work-address ones?
- [ ] **S15** (Thu Nov 5 – Fri Nov 6) Web-usage features. **Human-only:** build the job / leak / cloud / hack keyword lists from `results/tables/top100_web_domains.csv`
- [ ] **S16** (Sat Nov 7) Organizational context (no "days until leaving" feature). Note: 14 senior staff have no LDAP department; `ldap_context()` uses their functional unit instead (already in v0)
- [ ] **S17** (Sat Nov 7) Per-user baselines `z_user_*` + figure F3
- [ ] **S18** (Sun Nov 8) Peer-group baselines `z_peer_*` + novelty flags `new_*`
- [ ] **S19** (Sun Nov 8) Validation and leakage checks (5 checks; check 4 is a hand check, human-only)
- [ ] **S20** (Sun Nov 8 – Mon Nov 9) Feature table v1 + feature dictionary + walkthrough → M2

### Week 2
- [ ] **S21** (Tue Nov 10) Bug-fix window until 12:00
- [ ] **S22** (Wed Nov 11) Feature-group ablation → table T7. **Human-only:** interpret the results
- [ ] **S23** (Tue Nov 10 + Thu Nov 12) Write III. Dataset, IV-A, IV-B. **Human-only**
- [ ] **S24** *(stretch, only if agreed Mon Nov 9)* LANL authentication features
- [ ] **S25** (Fri Nov 13) Related Work paragraphs for L1, L2, L3, L9a. **Human-only**
- [ ] **S26** (Fri Nov 13) Write I. Introduction. **Human-only**
- [ ] **S27** (Fri Nov 13) Write VII. Limitations & Ethics. **Human-only**
- [ ] **S28** (Sat Nov 14) Results walkthrough; merge Related Work + table T1. **Human-only**
- [ ] **S29** (Sun Nov 15 – Mon Nov 16) Assemble the paper → M4

### Week 3
- [ ] **S30** (Tue Nov 17) Abstract + integration. **Human-only**
- [ ] **S31** (Wed Nov 18) Editing pass. **Human-only**
- [ ] **S32** (Wed Nov 18) Circulate the full draft by 18:00 → M5
- [ ] **S33** (Thu Nov 19) Final read-through + README results
- [ ] **S34** (Thu Nov 19) Fresh-clone test, `final-submission` tag, code archive
- [ ] **S35** (Fri Nov 20) Submit

### Literature (all human-only)
- [ ] **S-LIT1** (Mon Nov 9) L1 Glasser & Lindauer, L2 Le et al.: notes in `paper/lit_notes/` + Zotero
- [ ] **S-LIT2** (Wed Nov 11) L3 Homoliak et al.
- [ ] **S-LIT3** (Thu Nov 12) L9a, one 2022–2026 paper (L9b optional)

---

## 5. Arva

### Week 0
- [ ] **A1** (Wed Oct 28) Environment, clone, `arva/notes` branch. *Status unknown*
- [ ] **A2** (Thu Oct 29) Kickoff. *Status unknown*
- [ ] **A3** (Thu Oct 29) Synthetic data generator `src/synthetic.py`
  - [x] Merged Nov 4 ([PR #10](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/10), Arva): 50 users × 300 days, TEAM_PLAN 5.1 format, 5 tests pass
  - [ ] Ayo confirms he can load it (the card's "Done when")
  - [x] Renamed `f_http_job_site` to `f_http_job` to match the real feature (S15); a new test checks every synthetic feature name against the planned v1 names **(Claude, branch `arva/A3-http-job-rename`)**
- [ ] **A4** (Fri Oct 30) Module skeleton `src/models_unsupervised.py`. *Status unknown — not in the repo yet*
- [ ] **A5** (Fri Oct 30) Isolation Forest. *Status unknown*
- [ ] **A6** (Sat Oct 31) Autoencoder. *Status unknown*
- [ ] **A7** (Sun Nov 1) Risk scoring `src/risk_scoring.py`. *Status unknown*

### Week 1
- [ ] **A8** (Mon Nov 2) Per-feature reconstruction error + contamination variant
- [ ] **A9** (Tue Nov 3) First run on real data (v0); tuning log started
- [ ] **A10** (Wed Nov 4) Tuning workflow (IF and AE grids, chosen by val PR-AUC)
- [ ] **A11** (Thu Nov 5) Prototype pipeline `src/pipeline.py`
- [ ] **A12** (Fri Nov 6) Alert reasons (top-3 per alert)
- [ ] **A13** *(optional)* (Sat Nov 7) One-Class SVM
- [ ] **A14** (Sun Nov 8) Pipeline diagram F2, hyperparameter table T4 draft, section notes. **Human-only:** draw F2

### Week 2
- [ ] **A15** (Mon Nov 9) Retrain and tune on v1
- [ ] **A16** (Tue Nov 10) Final scores + tuned settings committed
- [ ] **A17** (Wed Nov 11) Per-scenario results, contamination effect, alert volume, timing → M3
- [ ] **A18** (Thu Nov 12) Prototype on v1: top-20 users, precision@20, figure F8
- [ ] **A19** (Fri Nov 13 – Sat Nov 14) Four anomaly case studies + F7. **Human-only:** narratives and analyst verdicts
- [ ] **A20** (Fri Nov 13) Related Work paragraphs L4, L5, L10a. **Human-only**
- [ ] **A21** *(optional)* (Sat Nov 14) Streamlit dashboard
- [ ] **A22** (Sun Nov 15) Write IV-C (unsupervised), IV-D, VI-B. **Human-only**

### Week 3
- [ ] **A23** (Mon Nov 16) Write VIII + README "Run the prototype" section → M4
- [ ] **A24** (Tue Nov 17) Demo rehearsal + fresh-clone test
- [ ] **A25** (Wed Nov 18) Review the full draft
- [ ] **A26** (Thu Nov 19) Final read-through + last fixes

### Literature (all human-only)
- [ ] **A-LIT1** (Wed Oct 28) Isolation Forest paper; skim Chandola et al. *Status unknown*
- [ ] **A-LIT2** (Mon Nov 2) L4 Tuor et al.
- [ ] **A-LIT3** (Fri Nov 6) L5 Lu & Wong
- [ ] **A-LIT4** (Sat Nov 7) L10a, one 2022–2026 paper (L10b optional)

---

## 6. Ayo

### Week 0
- [ ] **Y1** (Wed Oct 28) Environment, clone, `ayo/notes` branch. *Status unknown*
- [ ] **Y2** (Thu Oct 29) Kickoff: lead the threshold and reporting discussion. *Status unknown*
- [ ] **Y3** (Thu Oct 29) Synthetic scores + core metrics
  - [x] `make_synthetic_scores()`, `threshold_metrics()`, `ranking_metrics()` + tests on `ayo/Y3-evaluate` **(Claude)**
  - [ ] **Human-only:** Ayo's own 10-row hand check on paper
- [x] **Y4** (Fri Oct 30) Thresholds + `evaluate_file()` + `compare_files()`: code + tests pass on synthetic scores **(Claude)**
- [x] **Y5** (Sat Oct 31) ROC, PR, confusion and score-distribution plots: all 4 render on synthetic scores **(Claude)**
- [ ] **Y6** (Sun Nov 1) Detection delay + user-level recall → share `evaluate.py`
  - [x] Code + tests (6/6 pass); also verified on the real v0 table **(Claude)**
  - [ ] Ayo reads and understands all of `evaluate.py`; PR opened (base `supriye/S2-setup`, reviewer Arva) and merged
  - [ ] Arva and Supriye confirm they can import and run it

### Week 1
- [ ] **Y7** (Mon Nov 2) Random Forest + XGBoost `src/models_supervised.py`
- [ ] **Y8** (Tue Nov 3) First run on real data (v0); tuning log started
- [ ] **Y9** (Wed Nov 4) Tuning workflow (RF and XGB grids)
- [ ] **Y10** (Thu Nov 5) Imbalance experiment → `results/tables/imbalance.csv`
- [ ] **Y11** (Fri Nov 6) `src/explain.py` (SHAP) → Arva
- [ ] **Y12** (Sat Nov 7) Leave-one-scenario-out (LOSO) code. **Human-only:** design and justify the experiment
- [ ] **Y13** (Sun Nov 8) Hyperparameter table T4 draft + section notes

### Week 2
- [ ] **Y14** (Mon Nov 9) Retrain and tune on v1
- [ ] **Y15** (Tue Nov 10) Final RF/XGB scores + timing; tuned settings committed
- [ ] **Y16** (Wed Nov 11) Run LOSO → table T6 → M3
- [ ] **Y17** (Thu Nov 12) Master comparison T5, F4, F5, detection delay, T8
- [ ] **Y18** (Fri Nov 13) SHAP analysis → F6 + `feature_importance.csv`. **Human-only:** interpret it
- [ ] **Y19** (Fri Nov 13) Related Work paragraphs L6, L7, L8, L11a. **Human-only**
- [ ] **Y20** (Sat Nov 14) FP/FN analysis + present at the results walkthrough. **Human-only:** root causes
- [ ] **Y21** (Sun Nov 15) Write IV-C (supervised) + V. **Human-only**

### Week 3
- [ ] **Y22** (Mon Nov 16) Write VI-A, VI-C, precision/recall paragraph → M4. **Human-only**
- [ ] **Y23** (Tue Nov 17) Re-run evaluation, verify every number, polish figures
- [ ] **Y24** (Wed Nov 18) Review the full draft
- [ ] **Y25** (Thu Nov 19) Final read-through + last fixes

### Literature (all human-only)
- [ ] **Y-LIT1** (Wed Oct 28) Saito & Rehmsmeier (PR vs. ROC). *Status unknown*
- [ ] **Y-LIT2** (Sun Nov 1) L6 Liu et al. survey. *Status unknown*
- [ ] **Y-LIT3** (Sat Nov 7) L7 Yuan & Wu
- [ ] **Y-LIT4** (Sun Nov 8) L8 Log2vec + L11a (L11b optional)

---

## 7. Branches and pull requests (TEAM_PLAN 14.8)

Tick when the PR is **merged** into `main`.

**Nov 3:** PRs #3–#6 were merged into `supriye/S2-setup` after #1 had already merged it into `main` (the base branch wasn't deleted, so GitHub didn't move them). PR #7 then brought them into `main`. **Lesson:** delete a branch as soon as it's merged.

- [x] `supriye/S2-setup`: merged into `main` Nov 3 (PR #1), branch deleted. Review by Ayo still open (§9). `.gitignore`, folders, `src/config.py`, `scripts/download_cert.sh`, `requirements.txt`
- [x] `supriye/plan-updates`: merged into `main` Nov 3 (PR #2), branch deleted. Review by any teammate still open (§9). `Tasks/PROGRESS.md` and the updated plans
- [x] `ayo/Y3-evaluate`: merged into `main` Nov 3 (PR #3 → #7), branch deleted. Review by Arva still open (§9). `src/evaluate.py`, `tests/test_evaluate.py`
- [x] `supriye/S5-data-loader`: merged into `main` Nov 3 (PR #4 → #7), branch deleted. Review by Arva still open (§9). `src/data_loader.py`
- [x] `supriye/S6-labels-eda`: merged into `main` Nov 3 (PR #5 → #7), branch deleted. Review by Arva still open (§9). `src/labels.py`, `tests/test_labels.py`, `notebooks/01_eda.ipynb` (executed), `results/tables/*.csv`, `results/figures/*`
- [x] `supriye/S9-features-v0`: merged into `main` Nov 3 (PR #6 → #7), branch deleted. Review by Arva still open (§9). `src/features.py`, `tests/test_features.py`, `tests/test_v0_smoke.py`, `tests/test_pipeline_mini.py`
- [x] `arva/A3-synthetic`: merged into `main` Nov 4 (PR #10), branch deleted. Review by Ayo still open (§9).
- [ ] `arva/A4-unsupervised-models` (reviewer Ayo, Mon Nov 2)
- [ ] `arva/A7-risk-scoring` (reviewer Supriye, Sun Nov 1)
- [ ] `arva/A9-v0-tuning` (reviewer Ayo, Wed Nov 4)
- [ ] `ayo/Y7-supervised-models` (reviewer Supriye, Thu Nov 5)
- [ ] `ayo/Y11-explain` (reviewer Arva, Fri Nov 6)
- [ ] `arva/A11-pipeline` (reviewer Supriye, Fri Nov 6)
- [ ] `supriye/S10-behavior-features` (reviewer Arva, Sat Nov 7)
- [ ] `ayo/Y12-loso` (reviewer Arva, Sat Nov 7)
- [ ] `arva/A13-ocsvm` *(optional)* (reviewer Ayo, Sat Nov 7)
- [ ] `supriye/S17-baselines-v1` (reviewer Arva, Sun Nov 8)
- [ ] `supriye/S21-v1-fixes` *(only if needed)* (reviewer Arva, Tue Nov 10, 12:00)
- [ ] `arva/A15-final-models` (reviewer Supriye, Tue Nov 10)
- [ ] `ayo/Y14-final-models` (reviewer Supriye, Tue Nov 10)
- [ ] `supriye/S22-ablation` (reviewer Ayo, Wed Nov 11)
- [ ] `supriye/S24-lanl` *(stretch)* (reviewer Arva, Wed Nov 11)
- [ ] `arva/A17-results` (reviewer Ayo, Wed Nov 11)
- [ ] `ayo/Y16-loso-results` (reviewer Arva, Wed Nov 11)
- [ ] `ayo/Y17-comparison` (reviewer Arva, Thu Nov 12)
- [ ] `supriye/notes`, `arva/notes`, `ayo/notes` (any reviewer, Fri Nov 13)
- [ ] `arva/A18-prototype-cases` (reviewer Ayo, Sat Nov 14)
- [ ] `ayo/Y18-shap-fpfn` (reviewer Arva, Sat Nov 14)
- [ ] `arva/A21-dashboard` *(optional)* (reviewer Supriye, Sat Nov 14)
- [ ] `arva/A23-readme-run` (reviewer Supriye, Mon Nov 16)
- [ ] `arva/A24-fresh-clone-fixes` *(if needed)* (reviewer Supriye, Tue Nov 17)
- [ ] `ayo/Y23-verify` (reviewer Supriye, Tue Nov 17)
- [ ] `arva/A26-final-fixes`, `ayo/Y25-final-fixes` *(if needed)* (reviewer Supriye, Thu Nov 19)
- [ ] `supriye/S33-final` (reviewer Ayo, Thu Nov 19)

## 8. Milestone tags (Supriye, TEAM_PLAN 14.7)

- [ ] `m0-setup` (Sat Oct 31)
- [ ] `m1-features-v0` (Tue Nov 3)
- [ ] `m2-features-v1` (Sun Nov 8)
- [ ] `m3-all-scores` (Wed Nov 11)
- [ ] `analysis-done` (Sat Nov 14)
- [ ] `final-submission` (Thu Nov 19)

## 9. Review and merge checkpoints (PRs opened Tue Nov 3)

**Status Tue Nov 3:** all PRs below are **merged into `main`** (by `SupriyeAmatya`; #7 by Claude at Supriye's request), with **no GitHub review recorded**. The review items are still required. Do them now on `main`; anything that needs changing goes into a new PR from a new branch. Claude-written code also needs the **owner's** own read-through (TEAM_PLAN 12, rule 7).

For future PRs: Squash and merge, **delete the branch right after merging**, and post "merged" in chat.

Reviewer GitHub accounts: only `Bizzlefresh` is a collaborator so far. Supriye invites the third teammate, so future PRs can request reviews on GitHub.

### Checkpoint 1: setup and plans (target Tue Nov 3)
- [x] **[PR #1](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/1)** `supriye/S2-setup` → `main` (S1, S2), reviewer **Ayo**
  - [ ] Supriye has read `src/config.py` and `scripts/download_cert.sh` and can explain them
  - [ ] Ayo: fresh `pip install -r requirements.txt` works on his machine
  - [x] Merged into `main` Tue Nov 3
  - [ ] Reviewer approval: **none recorded on GitHub** (merged directly). Review it on `main` now; fixes go in a new PR
- [x] **[PR #2](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/2)** `supriye/plan-updates` → `main` (plans + this tracker), reviewer **any teammate**
  - [ ] Each person has read their own `Tasks/<Name>.md` §3 and PROGRESS.md §0
  - [x] Merged into `main` Tue Nov 3
  - [ ] Reviewer approval: **none recorded on GitHub** (merged directly). Review it on `main` now; fixes go in a new PR
- [ ] Everyone: `git checkout main` + `git pull origin main`

### Checkpoint 2: evaluation code and data loaders (target Tue Nov 3)
- [x] **[PR #3](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/3)** `ayo/Y3-evaluate` (S2 → `main` after checkpoint 1) (Y3–Y6), reviewer **Arva**
  - [ ] Ayo has read every function in `evaluate.py` and can explain it
  - [ ] **Human-only:** Ayo's Y3 paper hand-check matches `threshold_metrics()`
  - [ ] Arva: `python -m pytest tests/test_evaluate.py` passes (6 tests)
  - [x] Merged (into `supriye/S2-setup`, then `main` via PR #7) → milestone "`evaluate.py` ready" ticked in §1
  - [ ] Reviewer approval: **none recorded on GitHub** (merged directly). Review it on `main` now; fixes go in a new PR
- [x] **[PR #4](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/4)** `supriye/S5-data-loader` (S2 → `main`) (S4, S5), reviewer **Arva**
  - [ ] Supriye has read `data_loader.py` and can explain it
  - [ ] Arva: tests pass; loads a table with `load_logon(users=[...])` from the shared-drive Parquet
  - [x] Merged (into `supriye/S2-setup`, then `main` via PR #7)
  - [ ] Reviewer approval: **none recorded on GitHub** (merged directly). Review it on `main` now; fixes go in a new PR
- [ ] `data/` (Parquet + answers) uploaded to the shared drive and the link posted
- [ ] Supriye tags **`m0-setup`** (TEAM_PLAN 14.7)

### Checkpoint 3: labels, EDA and split (target Tue Nov 3 – Wed Nov 4)
- [x] **[PR #5](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/5)** `supriye/S6-labels-eda` (S5 → `main`) (S6–S8), reviewer **Arva**
  - [ ] Supriye has read `labels.py` and the notebook code and can explain them
  - [ ] **Human-only (Supriye):** Observation cells written; split dates confirmed and copied into TEAM_PLAN 5.3; 3 insiders hand-checked; hijacked-account labeling decided
  - [ ] Notebook re-run (Restart & Run All) if any decision changed a value
  - [x] Merged (into `supriye/S2-setup`, then `main` via PR #7)
  - [ ] Reviewer approval: **none recorded on GitHub** (merged directly). Review it on `main` now; fixes go in a new PR
  - [ ] Milestone "Split dates final" ticked in §1 (after Supriye's decision)

### Checkpoint 4: feature table v0 = M1 (target Wed Nov 4)
- [x] **[PR #6](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/6)** `supriye/S9-features-v0` (S6 → `main`) (S9), reviewer **Arva**
  - [ ] Supriye has read `features.py` and the tests and can explain them
  - [ ] v0 rebuilt with the confirmed after-hours and split values (`python -m src.features v0`), uploaded to the drive
  - [ ] Arva: `get_model_matrix()` works in Arva's code; Ayo: the same in Ayo's code
  - [x] Merged (into `supriye/S2-setup`, then `main` via PR #7)
  - [ ] Reviewer approval: **none recorded on GitHub** (merged directly). Review it on `main` now; fixes go in a new PR
- [ ] Supriye tags **`m1-features-v0`**; milestone M1 ticked in §1
- [ ] Everyone pulls `main`. From here on, new branches start from `main` (no more stacking)

### Later PRs (Nov 3–4)
- [x] **[PR #8](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/8)** `supriye/tracker-merged` (tracker): merged Nov 3, no review
- [x] **[PR #9](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/9)** `arva/docs-claude-md` (`CLAUDE.md`, Arva): merged Nov 4, no review
- [x] **[PR #10](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/10)** `arva/A3-synthetic` (A3, Arva): merged Nov 4, no review. Reviewer **Ayo**: run `python -m pytest tests/test_synthetic.py`, confirm `make_synthetic_features()` loads in Y7
- [x] **[PR #11](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/11)** `supriye/review-fixes` (review fixes, Supriye): merged Nov 4, no review. Reviewer **Arva**
- [ ] `docs/coverage.md` (Arva) was pushed straight to `main` without a PR; a teammate should still read it

### Catch-up merge
- [x] **[PR #7](https://github.com/SupriyeAmatya/AI-Based-User-and-Entity-Behavior-Analytics-for-Insider-Threat-Detection/pull/7)** `supriye/S2-setup` → `main`: brought #3–#6 into `main`. Squash-merged by Claude at Supriye's request, Tue Nov 3. 16/16 tests pass on `main`; `supriye/S2-setup` deleted afterwards
