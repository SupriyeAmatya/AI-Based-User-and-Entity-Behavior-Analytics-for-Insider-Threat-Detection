# Supriye: Data & Features Lead, Paper Integrator (v2, from Thu Nov 5)

Team rules, contracts and the shared schedule: [TEAM_PLAN.md](TEAM_PLAN.md). Tick progress in [PROGRESS.md](PROGRESS.md) §4.
**[H]** = human-only (TEAM_PLAN 2.6): do it yourself; an AI agent must not do it or tick it.

---

## 1. Executive Summary

### 1.1 Your role
- **Data owner:** CERT r4.2, labels, the train/val/test split, and the PROVISIONAL decisions in `src/config.py`.
- **Feature owner:** feature tables v0 and v1, the baselines, the feature dictionary, and the ablation (T7).
- **Paper integrator:** you write III, IV-A, IV-B, I, VII and the Abstract, merge Related Work, assemble the paper and submit.
- **Repo owner:** collaborators, branch protection, milestone tags, the final archive.

### 1.2 Files you own
- **Code:** `src/config.py`, `src/data_loader.py`, `src/labels.py`, `src/features.py`, `src/baseline.py`, `src/ablation.py` (new in S22), `src/lanl_features.py` (stretch).
- **Tests:** `tests/test_labels.py`, `test_features.py`, `test_baseline.py`, `test_pipeline_mini.py`, `test_v0_smoke.py`, `test_ablation.py` (new).
- **Notebooks:** `notebooks/01_eda.ipynb`, `notebooks/02_feature_engineering.ipynb`.
- **Docs:** `docs/feature_dictionary.md`, `README.md`, `requirements.txt`, `.gitignore`, `Tasks/`, `Guide/`, `paper/` assembly.

### 1.3 Already done (code by Claude at your request; you must still read and explain it)
- **S1:** CERT r4.2 + answers downloaded and checksum-verified (`scripts/download_cert.sh`).
- **S2:** repo structure, `.gitignore`, `src/config.py`, pinned `requirements.txt`, both collaborators added.
- **S4–S5:** streaming Parquet converter (32.8M rows) and cleaning loaders (no duplicates or missing keys).
- **S6:** labels (70 insiders, 984 malicious user-days in the table) and the insider timeline.
- **S7:** EDA notebook with F1 and T2 data.
- **S8:** split proposal and the split check.
- **S9:** v0 table (100 users) + `get_model_matrix()`.
- **S10–S16:** 41 behavior features for all users (PR #17).
- **S17–S20:** `src/baseline.py` (`z_user_*`, `z_peer_*`, `new_*`), F3, leakage checks 1/2/3/5 and the feature dictionary (PR #18).
- **Tracker:** PROGRESS audit (#16), the Week 1 tracker (#26), and the web-count fix (#28).

### 1.4 What's left (in order)
1. **Catch-up (Nov 5–8):** your 5 decisions, the rebuild if needed, the hand-checks, the drive upload, setup leftovers, reviews, and the M2 freeze.
2. **Models block (Nov 9–11):** the v1 walkthrough, the bug-fix window, III. Dataset, the ablation T7 and the T8 data time.
3. **Analysis + paper (Nov 12–18):** IV-A/IV-B, literature, Intro, Limitations, Related Work + T1, assembly, Abstract, editing, M5.
4. **Finish (Nov 19–20):** README results, fresh-clone test, tag, archive, submit.

---

## 2. Prerequisites / Required Tools

- **Environment:** Python 3.13 venv at `%USERPROFILE%\.venvs\ueba` with `requirements.txt` installed (TEAM_PLAN 2.3).
- **Data on your laptop:** `data/raw/` (archives + extracted LDAP, psychometric, answers), `data/parquet/` (5 logs + `manifest.json`), `data/processed/` (`labels.parquet`, `features_v0.parquet`, `features_v1.parquet`, `http_user_day_domain.parquet`, `http_domain_counts.csv`).
- **GitHub admin rights:** you own the repo (settings, tags).
- **Shared drive:** write access, to upload the single `ueba_data_v1.zip` (TEAM_PLAN 2.5.12).
- **Overleaf + Zotero:** accounts to create the project and group library.
- **Arva's and Ayo's merged tuned-defaults PRs** (for S22): `arva/A15-final-models`, `ayo/Y14-final-models`. You need **no score files**: the ablation retrains each model on each feature set.

---

## 3. Step-by-Step Instructions

### Catch-up block: Thu Nov 5 – Sun Nov 8

#### S2-rest · Thu Nov 5 · Finish setup
1. **Turn on** branch protection: GitHub → **Settings → Branches → Add rule** for `main` → tick **Require a pull request before merging** with 1 approval.
2. **Create** the Overleaf project from the IEEE conference template and invite Arva and Ayo.
3. **Create** the Zotero group library (IEEE export style) and invite both.
4. **Post** both links in the group chat.

**Done when:** a direct push to `main` is rejected, and both teammates have joined Overleaf and Zotero.

#### S3-rest · Thu Nov 5 · Confirm the course rules
1. **Confirm** the page limit, the AI-use policy and the submission contents (PDF + code archive?) with the instructor or the brief.
2. **Write** the answers into TEAM_PLAN §1 and §2.6 on your next plan branch.

**Done when:** all three answers are in TEAM_PLAN.

#### S8 · Thu Nov 5 – Fri Nov 6 · Decide the PROVISIONAL values [H]
Branch: `supriye/S8-decisions` (reviewer Arva).
1. **Decide** the split dates from `results/tables/split_check.csv`. Keep 2010-10-31 / 2011-01-31, or move them so scenario 3 has more than 4 test days. Every cell of `insider_days_s*` must stay > 0.
2. **Decide** the after-hours window from the hour-of-day plot in `notebooks/01_eda.ipynb` (now 07:00–19:00), and write the reason under "Settings" in `docs/feature_dictionary.md`.
3. **Check** the web keyword lists in `src/config.py` `HTTP_CATEGORIES` against `data/processed/http_domain_counts.csv` (all 475 domains). Note what's left out and why: LinkedIn, the 5 defense-contractor sites, freelance sites, torrent indexes.
4. **Decide** the email rule: `EMAIL_COUNT_PERSONAL = True` counts webmail sent from the work PC too, and 37.6% of emails are such webmail.
5. **Decide** the hijacked-account labels: keep the 20 scenario-3 days on `FAW0032`/`FBA0348` (compromised-account view), or move them to the insider.
6. **Write** each value into `src/config.py` (remove the PROVISIONAL tag), the split dates into TEAM_PLAN 2.5.3, and the reasons into the feature dictionary.
7. **Post** the final values in chat.

**Done when:** no PROVISIONAL tag is left in `src/config.py`, and TEAM_PLAN 2.5.3 shows the dates.

#### S20b · Fri Nov 6 – Sat Nov 7 · Rebuild after the decisions (only if a value changed)
1. **Run** `python -m src.labels`.
2. **Run** `python -m src.features v0`, then `python -m src.features v1` (~2 min).
3. **Re-run** `notebooks/01_eda.ipynb` and `notebooks/02_feature_engineering.ipynb` with Restart & Run All.
4. **Run** `python -m pytest tests`.
5. **Commit** the regenerated tables and figures on `supriye/S8-decisions`, and note the changed numbers in the PR.

**Done when:** tests pass, both notebooks run clean, and `v1_validation_checks.csv` still shows PASS.

#### S6-H / S19-H · Fri Nov 6 · Hand-checks [H]
1. **Pick** one insider per scenario.
2. **Open** their answer file in `data/raw/answers/` and the raw logs for one malicious day.
3. **Count** 3–4 feature values by hand (logons, USB connects, file copies, emails) and compare them with `features_v1.parquet`.
4. **Write** the result in the Observation cell of `02_feature_engineering.ipynb` (S19 check 4).

**Done when:** the Observation cell says which values matched.

#### S7-H · Fri Nov 6 · EDA observations [H]
1. **Write** 2–3 sentences under each plot in `notebooks/01_eda.ipynb`.

**Done when:** no Observation cell in notebook 01 is empty.

#### S4-rest / S20-rest · Sat Nov 7 · The one data drop (TEAM_PLAN 2.5.12)
1. **Write** checksums: `sha256sum data/processed/* data/parquet/logon.parquet data/parquet/device.parquet data/parquet/file.parquet data/parquet/email.parquet data/parquet/manifest.json > data/CHECKSUMS.txt`.
2. **Zip** only those files plus `data/CHECKSUMS.txt` into `ueba_data_v1.zip` (~380 MB). Leave out `http.parquet` and `data/raw/`.
3. **Upload** the zip once to the shared drive, and post the link with the commit it matches.

**Done when:** Arva and Ayo confirm the checksums pass and `get_model_matrix(pd.read_parquet('data/processed/features_v1.parquet'), split='train')` works.

#### REV-S · Thu Nov 5 – Sun Nov 8 · Read your code and do your reviews
1. **Read** `data_loader.py`, `labels.py`, `features.py` and `baseline.py` until you can explain each function [H].
2. **Review** on `main` the PRs assigned to you: Arva's #9 (`CLAUDE.md`), #15 (A7), #21 (A11–A12) and #27 (coverage), and Ayo's #23 (Y7–Y10). Run each "How to test" step.
3. **Open** a GitHub Issue for the owner for anything that needs changing (TEAM_PLAN 2.5.8).
4. **Tick** each review in PROGRESS §7.

**Done when:** every review assigned to you in PROGRESS §7 is ticked.

#### S20-tag · Sun Nov 8 · Freeze v1 → M2
1. **Tag** `m0-setup` and `m1-features-v0` if their conditions are met (PROGRESS §8).
2. **Announce** the freeze (TEAM_PLAN 2.5.9).
3. **Tag** `m2-features-v1`: `git tag -a m2-features-v1 -m "M2: feature table v1"`, then `git push origin m2-features-v1`.

**Done when:** the tag is on GitHub and M2 is ticked in PROGRESS §1.

### Models block: Mon Nov 9 – Wed Nov 11

#### S20-walk · Mon Nov 9 · v1 walkthrough (30 min)
1. **Walk** Arva and Ayo through each feature group with `docs/feature_dictionary.md` and F3.
2. **Lead** the decision on the LANL stretch (S24). The default is to skip it and state the gap.

**Done when:** both teammates have asked their questions, and the S24 decision is in the chat.

#### S21 · Tue Nov 10 (until 12:00) · Bug-fix window
1. **Check** GitHub Issues for feature bugs (none were open on Nov 5).
2. **Fix** only result-changing bugs on `supriye/S21-v1-fixes`, rebuild as `features_v1_1.parquet`, upload that one 35 MB file (the only allowed second drop) and post what changed.
3. **Close** or explicitly postpone every feature issue at 12:00.

**Done when:** no feature issue is open without a decision.

#### S23a · Tue Nov 10 · III. Dataset [H]
1. **Write** in Overleaf: what CERT r4.2 is and how it was made (cite L1), the log types, the 3 scenarios, the preprocessing, the split dates, T2 (`class_imbalance.csv`), and the "no failed logins" gap.

**Done when:** III is full paragraphs, with T2 referenced.

#### S22 · Wed Nov 11 · Feature-group ablation → T7
Branch: `supriye/S22-ablation`, from `main` **after** `arva/A15-final-models` and `ayo/Y14-final-models` merge (reviewer Ayo).
1. **Create** `src/ablation.py` with:
   - **`feature_group(column)`** maps every model input to one of `logon, time, usb, file, email, http, context`. `z_user_*` and `z_peer_*` follow their feature; `new_usb_user` → usb, `new_pc` → logon, `new_leak_site` → http, `new_afterhours` → time.
   - **`feature_sets(columns)`** returns (a) raw `f_*`, (b) `f_*` + `z_user_*`, (c) full, and (d) full minus one group at a time.
   - **`run_ablation(df)`** retrains XGBoost (`train_and_score_supervised(..., columns=...)`) and Isolation Forest (`train_and_score(..., columns=...)`) with their **tuned defaults**, scores with `evaluate_df()`, and records test PR-AUC, ROC-AUC, recall at top 1%, recall at best-F1 and the change vs. full.
2. **Add** `data_processing_time()`: wall-clock time of `labels.build_labels()`, the web-log pass (`http_user_day_domains(refresh=True)`) and `build_v1()`, plus the ~10-min conversion. It writes `results/tables/data_processing_time.csv`.
3. **Add** `tests/test_ablation.py`: every v1 input has a group; the feature sets are correct; `run_ablation()` works on `make_synthetic_features()`.
4. **Run** `python -m src.ablation`, which writes `results/tables/ablation.csv` (T7).
5. **Run** `python -m src.ablation time`, which writes `data_processing_time.csv` (for T8).
6. **Write** 3–5 sentences on (a) vs. (b) vs. (c) and the biggest group drops in the PR and in your notes [H].
7. **Tag** `m3-all-scores` once `ayo/Y16-loso-results` is merged too.

**Done when:**
- **Table:** `ablation.csv` has 10 feature sets × 2 models;
- **Answer:** the (a)/(b)/(c) comparison says whether baselining helps;
- **Hand-off:** Ayo has the data-processing time.

#### S24 · Tue Nov 10 – Wed Nov 11 · LANL authentication features *(stretch, only if agreed Nov 9)*
1. **Accept** the LANL terms yourself and download `auth.txt.gz` + `redteam.txt.gz`.
2. **Stream** `auth.txt.gz` in chunks. Keep `src_user` starting with `U`; drop accounts ending in `$` and `ANONYMOUS`.
3. **Scope** to red-team users + 1,000 random others (`random_state=42`). Compute `day = time // 86400`.
4. **Build** `f_auth_count`, `f_auth_fail`, `f_auth_fail_ratio`, `f_auth_dst_hosts`, `f_auth_src_hosts`, `f_auth_new_dst`, `f_auth_ntlm`, `f_auth_network_logon`. Label = (user, day) in `redteam.txt`. Split by day so every split has red-team days.
5. **Save** `data/processed/lanl_features.parquet` in the 2.5.1 format.

**Done when:** the file is on the drive by Wed night.

### Analysis + paper block: Thu Nov 12 – Wed Nov 18

#### S-LIT1–3 · by Thu Nov 12 · Literature [H]
1. **Read** L1, L2 (S-LIT1), L3 (S-LIT2) and L9a, plus **L9b, strongly recommended** (S-LIT3; find it via TEAM_PLAN 3.14).
2. **Write** one `paper/lit_notes/<ID>.md` per paper with the TEAM_PLAN 3.14 template, and add each to Zotero.
3. **Merge** `supriye/notes` by Fri Nov 13 (any reviewer).

**Done when:** 4–5 note files are on `main`.

#### S23b · Thu Nov 12 · IV-A and IV-B [H]
1. **Write** IV-A: why user-day (cite L2), each feature group and its intuition, the after-hours definition, T3, and why there is no "days until leaving" feature.
2. **Write** IV-B: the rolling baseline formula, the `+1` in the denominator, peer groups and the department fallback, novelty flags, cold start, and F3.

**Done when:** both are full paragraphs, with T3 and F3 referenced.

#### S-T8 · Fri Nov 13 · Data-processing time for T8
1. **Point** Ayo to `results/tables/data_processing_time.csv` on `main` (merged with S22); nothing is sent separately.

**Done when:** Ayo confirms T8 includes it.

#### S25 · Fri Nov 13 · Related Work paragraphs [H]
1. **Write** one paragraph each for L1, L2, L3 and L9a in Overleaf II.

#### S26 · Fri Nov 13 · I. Introduction [H]
1. **Write** the problem, UEBA, the research question (quoted exactly), the contributions (bullets) and the outline sentence. Cite every statistic.

**Done when:** ~0.75 page, and every claim is cited.

#### S27 · Fri Nov 13 · VII. Limitations & Ethics [H]
1. **Cover** synthetic data, label-filtered training, few insiders per scenario (scenario 3: 4 test days), concept drift, threshold dependence, cold start, the missing failed logins, the provisional choices, and the privacy/ethics of monitoring (proportionality, transparency, false accusations, human in the loop).

**Done when:** each limitation states its effect on our results.

#### S28 · Sat Nov 14 · Results walkthrough + merge Related Work [H]
1. **Present** the ablation (T7) at the walkthrough, and write down the agreed answer to the research question.
2. **Order** Related Work by theme (surveys → features/granularity → unsupervised/deep → supervised/XAI) and add linking sentences.
3. **Build** T1 (paper, year, venue, dataset, models, best result, limitation).
4. **Close** with 2–3 sentences on the gap our project fills.
5. **Tag** `analysis-done` after `arva/A18-prototype-cases` and `ayo/Y18-shap-fpfn` merge.

**Done when:** II reads as one section, and T1 is complete.

#### S29 · Sun Nov 15 – Mon Nov 16 · Assemble → M4
1. **Check** on Sun that IV-C, IV-D, V and VI-B are in Overleaf and compile.
2. **Check** on Mon that VI-A, VI-C and VIII are in; chase anything missing.

**Done when:** every section in TEAM_PLAN 3.12 is a full draft → **M4**.

#### S30 · Tue Nov 17 · Abstract + integration [H]
1. **Write** the ~200-word Abstract: problem → approach → data → models → key numbers → main finding.
2. **Number** all figures and tables, and check that each is referenced.
3. **Export** Zotero in IEEE style, and check that there are no `??` references.

**Done when:** the PDF compiles within the page limit with no missing references.

#### S31 · Wed Nov 18 · Editing pass [H]
1. **Check** that terms are consistent (user-day, insider, anomaly score, risk score).
2. **Check** that every number matches `results/tables/`.
3. **Check** captions, readability, one voice, the page limit, and that the research question is answered explicitly.

**Done when:** every check passes.

#### S32 · Wed Nov 18 · Circulate → M5
1. **Export** the PDF by **18:00**, post it, and ask for comments by Thu morning.

### Finish: Thu Nov 19 – Fri Nov 20

#### S33 · Thu Nov 19 · Final read-through + README results
1. **Lead** the 60-min read-through, then assign and apply the fixes.
2. **Fill** the README **Results** section with the main comparison table (from `model_comparison.csv`) on `supriye/S33-final` (reviewer Ayo).

#### S34 · Thu Nov 19 · Fresh-clone test → submission-ready
1. **Merge** `supriye/S33-final` and any `*-final-fixes` PRs.
2. **Clone** into a new folder, create a new venv and run `pip install -r requirements.txt`.
3. **Unzip** `ueba_data_v1.zip` into the clone, run both `final` commands (`python -m src.models_unsupervised final`, `python -m src.models_supervised final`), then `python src/pipeline.py`, then Restart & Run All `notebooks/04_evaluation.ipynb`.
4. **Tag** `final-submission` and push the tag.
5. **Build** the archive: `git archive --format=zip -o submission-code.zip final-submission`.
6. **Export** the final PDF, and check both files against the course requirements.

**Done when:** the tag is pushed, and the zip and PDF are ready Thu night.

#### S35 · Fri Nov 20 · Submit
1. **Submit** the paper and code, and post a confirmation screenshot in chat.

---

## 4. Edge Cases & Troubleshooting

- **A decision changes the split:** rebuild labels, v0 and v1 (S20b) **before** Arva and Ayo tune on Mon Nov 9; tell them the new commit.
- **Scenario 3 has no test day after moving the split:** `python -m src.labels` prints "NOT VALID". Move `VAL_END` earlier until every `insider_days_s*` cell is > 0.
- **`build_v1` is slow or runs out of memory:** the first run makes one pass over the 28.4M-row web log (~30 s) and caches it. Later runs reuse `http_user_day_domain.parquet`. Pass `refresh=True` only after a keyword-list change.
- **Keyword lists changed:** delete nothing, and just re-run `python -m src.features v1`. Categories are applied from the cache.
- **A conflict in `PROGRESS.md` or `README.md` when merging:** keep both sides' lines; never take a whole file from one side.
- **Ablation numbers look too good:** supervised v1 runs reached val PR-AUC ≈ 0.99 in an unsaved Nov 5 test, while `f_*` alone gave 0.51 val / 0.38 test. Report (a) vs. (c) honestly and check against Ayo's SHAP (Y18).
- **The tuned defaults aren't merged by Wed:** run S22 with explicit params read from `results/tables/T4_hyperparameters_*.csv` (v1 rows, on the open PRs' branches), and note it in the PR. Don't ask for score files.
- **A teammate asks for raw logs or `http.parquet`:** point them to the web cache (`http_user_day_domain.parquet`) or the 4 small logs in the drop; send nothing else.
- **Overleaf compile errors near the deadline:** keep the last good PDF; fix one section at a time.

---

## 5. Success Metrics / Definitions

| Task | Verified by |
|---|---|
| S2-rest, S3-rest | Protection rule active; Overleaf/Zotero joined; course answers in TEAM_PLAN |
| S8 + S20b | No PROVISIONAL tags; tests pass; notebooks 01–02 re-run; checks PASS |
| Data drop | One `ueba_data_v1.zip`; both teammates' checksums pass and v1 loads |
| Reviews | Every review assigned to you ticked in PROGRESS §7 |
| M2 | `m2-features-v1` tag pushed |
| S21 | No undecided feature issue at Tue 12:00 |
| S22 | `ablation.csv` (20 rows) + `data_processing_time.csv` on `main`; tests pass |
| Literature | 4–5 notes in `paper/lit_notes/`, in Zotero |
| Paper | III, IV-A, IV-B, I, VII, Abstract, II + T1 drafted; M4 and M5 met |
| Submission | `final-submission` tag, zip and PDF submitted; confirmation posted |

**Your numbers in the paper:**
- **T2:** dataset size and imbalance, overall and per scenario (`class_imbalance.csv`).
- **T7:** the ablation (`ablation.csv`).
- **T8:** the data-processing time (`data_processing_time.csv`).
- **III:** the 0.298% base rate (984 / 330,268).
