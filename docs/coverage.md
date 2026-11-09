# UEBA assignment coverage

> **Snapshot from Sun Nov 8, 2026, evening** (repo at `2710789`). This file does not update itself. [`Tasks/PROGRESS.md`](../Tasks/PROGRESS.md) is still the tracker of record.

It maps each requirement in the CSCI 561 assignment brief to how it's measured, the deliverable, the proof that it's met, and where it stands. It's built from the brief, `Tasks/TEAM_PLAN.md`, `Tasks/PROGRESS.md` and the code on `main`. Tests weren't re-run for this snapshot. Work still on a branch is mentioned where it matters but doesn't count as met.

**12 days left to Fri Nov 20 · 5 of 25 requirements fully met**

## Where the requirements stand

| Status | Count | Meaning |
|---|---:|---|
| Gap | 2 | The current plan can’t fully meet it. |
| Overdue | 0 | Past its due date, with nothing on main. |
| Partial | 12 | Some of it exists; the rest is still due. |
| Not started | 6 | Nothing yet, and not due yet. |
| Done | 5 | Met, with proof in the repo or the paper. |

A requirement counts as met only when its proof exists. For most of them that includes paper text, so only 5 are fully met so far.

## Schedule

Milestones from TEAM_PLAN 1.5. Of the five due before today, two are done (`evaluate.py` and the split dates); M0, M1 and the `explain.py` check are still open. M2 is due today.

| Date | Milestone | State | Note |
|---|---|---|---|
| Sat, Oct 31 | **M0** Setup complete | Open, past due | The data drop isn’t ticked as uploaded, and Ayo’s Y1 isn’t ticked, though Ayo has tuned on v1 (#41). |
| Sun, Nov 1 | evaluate.py ready | Done | Merged Nov 3. |
| Mon, Nov 2 | Split dates final | Done | Decided Nov 6 (#36); reason in TEAM_PLAN 2.5.3. |
| Tue, Nov 3 | **M1** Feature table v0 | Open, past due | Built and used by every model; Arva’s and Ayo’s confirmations remain. |
| Fri, Nov 6 | explain.py ready | Open, past due | Code merged Nov 5; Arva still has to confirm it for the case studies, which needs the data. |
| Sun, Nov 8 | **M2** Feature table v1 | Due today | Decisions final (#36–#38) and S20b done (#40); v1 grew to 76 inputs on Nov 6. The data drop, Arva loading v1, and the tag remain. |
| Tue, Nov 10 | Tuned models + `final` commands | Upcoming | Supervised half merged (#41). The unsupervised `final` command is merged (#33), but its tuned defaults wait for the data. |
| Wed, Nov 11 | **M3** All score files | Upcoming | Needs A17’s code re-applied first (in progress). |
| Sat, Nov 14 | Analysis done | Upcoming |  |
| Mon, Nov 16 | **M4** All sections drafted | Upcoming |  |
| Wed, Nov 18 | **M5** Full paper draft | Upcoming |  |
| Thu, Nov 19 | Submission-ready | Upcoming |  |
| Fri, Nov 20 | Submit | Upcoming |  |

## Requirements

Owner and task IDs refer to the task cards in `Tasks/`.

### Research and data

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Study insider threats, compromised accounts, behavioral anomalies and UEBA | All four topics covered and cited in the background | Paper §I Introduction and §II Related Work | Section text with citations | **Not started**<br>Due Nov 13. | Everyone · S25–S26, A20, Y19 |
| Review at least 5 recent papers from IEEE, Springer, Elsevier or ACM | 5 or more papers, each recent and from one of those publishers, covering UEBA, insider threat, behavioral anomaly, compromised accounts and AI/ML | `paper/lit_notes/<ID>.md` per paper, table T1 | 5+ note files; T1 lists venue and year | **Gap**<br>`paper/lit_notes/` is still empty, and neither `arva/notes` nor `ayo/notes` is on GitHub. Arva’s notes were due Nov 7, Ayo’s are due today, Supriye’s Nov 12. Only 3 planned papers are from 2022–2026. | Everyone · S-LIT, A-LIT, Y-LIT |
| Choose a suitable dataset | Named and justified, with ground-truth labels | CERT r4.2 + answers; paper §III Dataset | Checksums match; `dataset_files.csv` | **Partial**<br>Data done. §III due Nov 10. | Supriye · S1, S23a |
| Preprocess the data | Every log loads, removed rows are counted, and the date-based split has every scenario in every split | `data_loader.py`, `labels.py` | `cleaning_report.csv`, `split_check.csv`, tests | **Done**<br>Code and checks done. The split dates and the scenario-3 labels were decided Nov 6 (#36), with the reasons in TEAM_PLAN 2.5.3 and the feature dictionary (#37, #38). | Supriye · S4–S8 |

### Behavioral features

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Login patterns | Logon counts, first and last logon, PCs used, logons on unusual PCs | `f_logon_*` and related columns in v1 | Feature dictionary T3 | **Done**<br>In v1 (PR #17): logon and logoff counts, first-logon and last-logoff hour, PCs used, logons on other PCs. Documented in `docs/feature_dictionary.md`. | Supriye · S10 |
| Authentication failures | Failed logins per user-day | LANL features, or a stated limitation | LANL feature columns, or Limitations text | **Gap**<br>CERT has no failed logins. LANL is a stretch goal, decided at the Nov 9 v1 walkthrough. | Supriye · S24 |
| File and resource access | File copies to removable media, USB connects | `f_file_*`, `f_usb_*` | Feature dictionary T3 | **Done**<br>In v1: file copies by type and after hours; USB connects, after-hours connects, PCs and minutes connected. | Supriye · S12, S13 |
| Application usage | Web categories (job, leak, cloud, hacking, competitor), email volume, external email | `f_http_*`, `f_email_*` | Feature dictionary T3, and the stand-in stated in §III | **Partial**<br>In v1: 8 web and 8 email features. The keyword lists and the email-count rule were decided Nov 6 (#36), and a `competitor` web category was added (#38). CERT has no application logs, so web and email stand in, and §III (due Nov 10) has to say so. | Supriye · S14, S15 |
| Activity times | After-hours and weekend activity, work duration | `f_afterhours_*`, `f_weekend`, `f_work_duration` | T3, with the reason for the chosen hours | **Done**<br>In v1: after-hours counts and ratio, weekend flag, work duration. The 07:00–19:00 window was decided Nov 6 (#36), and its reason is in the feature dictionary (#37, #38). | Supriye · S11 |
| Changes from normal behavior | Deviation from the user’s own past 30 days and from same-role peers; novelty flags | `z_user_*`, `z_peer_*`, `new_*` | T3, figure F3 | **Done**<br>In v1 (PR #18, extended by #38): 15 `z_user_*`, 15 `z_peer_*` and 4 `new_*` columns, and figure F3. | Supriye · S17, S18 |

### Normal behavior, models and risk score

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Establish normal behavior | Per-user and peer baselines; unsupervised models train on normal training days only | `src/baseline.py`, paper §IV-B | Figure F3: one user’s baseline next to a day that deviates | **Partial**<br>`baseline.py` and F3 are merged, and every unsupervised model trains on normal training days only. §IV-B due Nov 12. | Supriye, Arva · S17, S23b, A5 |
| Develop and compare at least 2 models | 2 or more score files in the agreed format; 5 are built (IF, AE, OCSVM, RF, XGB) | `models_unsupervised.py`, `models_supervised.py`, `results/scores/*.parquet` | Comparison table T5 from `compare_files()` | **Partial**<br>All five are on `main` and have scored v0 (best val PR-AUC: IF 0.063, AE 0.122, RF 0.273, XGB 0.324). The supervised models are tuned on v1, with their tuned defaults and `final` command merged (#41). The unsupervised `final` command is merged (#33), but their v1 tuning waits for the data. Final v1 scores due Nov 10, T5 due Nov 12. | Arva, Ayo · A4–A6, A9–A10, A13, A15–A16, Y7–Y9, Y14–Y15 |
| Justify the models chosen | A reason for each model; hyperparameters listed | Paper §IV-C, table T4 | Paper text | **Partial**<br>The supervised T4 shows the v1-tuned values (#41); the unsupervised one is still the v0 draft. The reasons are still only in TEAM_PLAN 2.7.3. Ayo’s imbalance set-up is in the code (`FINAL_SETUP`, #41), but its written reason isn’t on `main`. Arva’s autoencoder architecture and grids (DEC-A) are due today. §IV-C due Nov 15. | Arva, Ayo · A14, A22, DEC-A, Y13, Y21, DEC-Y |
| Assign a risk score to suspicious behavior | 0–100 daily risk (percentile of normal training scores), 7-day user risk, alert levels, top-3 reasons per alert | `src/risk_scoring.py` | Ranked user table; F8 risk timeline for one insider | **Partial**<br>`risk_scoring.py` and `pipeline.py` are merged; the ranked table gives 3 reasons per user. The precision@k, F8-user and risk-timeline code is merged (#35). Alert levels still PROVISIONAL (DEC-A, due today). F8 and precision@20 due Nov 12. | Arva · A7, A11–A12, A18 |

### Evaluation

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Accuracy, precision, recall, F1, FPR, FNR, ROC-AUC, confusion matrix | Each on the test split at the best-F1 and top-1% thresholds, overall and per scenario | `evaluate.py`; T5, F4, F5 | Hand-checked unit test; v0 smoke test | **Partial**<br>Code done and run on v0 scores. Test-split tables and figures (T5, F4, F5) due Nov 12. | Ayo · Y3–Y6, Y17 |
| Detection time | Train time and inference time per 1,000 user-days; data-processing time; days from an insider’s first malicious day to their first alert | Table T8 | Timing tables; `detection_delay()` | **Partial**<br>Delay is built. Data-processing time (`data_processing_time.csv`, #32) and supervised fit and inference time (`timing_supervised.csv`, #41) are measured. Arva’s `timing()` was in #34 but was lost when that branch was merged with `main`; it is being re-applied. T8 due Nov 12. | Arva, Ayo, Supriye · A17, Y15, Y17, S22 |
| Explain why precision and recall matter on imbalanced data | A paragraph with our base rate: 0.298% malicious, so always answering “normal” scores 99.70% accuracy with 0 recall | Paper §V | `class_imbalance.csv` | **Partial**<br>Number ready and quoted in TEAM_PLAN 5.4. Paper text due Nov 16. | Ayo · Y22 |
| Detect previously unseen anomalous behavior | Leave-one-scenario-out: PR-AUC, ROC-AUC and recall at top 1% on the held-out scenario | `run_loso()`, `<model>_loso_s<1–3>` score files | Table T6 | **Partial**<br>`run_loso()` and `loso_table()` are merged and run on v0. Results (T6) due Nov 11; Ayo’s LOSO justification (DEC-Y) is due today. | Ayo · Y12, Y16, DEC-Y |

### Analysis

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Analyze false positives and false negatives | Top false positives grouped by root cause; each missed test insider explained | Paper §VI-C | Case tables | **Not started**<br>Due Nov 14. | Ayo · Y20 |
| Find the features that drive detection | SHAP for RF and XGB, per-feature reconstruction error for the autoencoder, feature-group ablation | `explain.py`, `feature_importance.csv` | F6 SHAP plot, T7 ablation table | **Partial**<br>`explain.py` (SHAP), the autoencoder’s `feature_errors()` and the ablation code (`src/ablation.py`, #32) are merged, with SHAP plots on v0. The T7 run waits for Arva’s tuned defaults (Ayo’s merged in #41); F6, `feature_importance.csv` and T7 due Nov 11–13. | Ayo, Arva, Supriye · Y11, Y18, A8, S22 |
| Investigate detected anomalies | 2–4 case studies, each saying why the system flagged it | `notebooks/05_anomaly_investigation.ipynb`, paper §VI-B | F7 explanation plots and written cases | **Not started**<br>Due Nov 13–14. The pipeline’s alert reasons are a starting point; the case narratives are human-only. | Arva · A19 |

### Prototype and paper

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| UEBA prototype | One command goes from features to ranked alerts with reasons, and it runs from a fresh clone | `src/pipeline.py`, README “Run the prototype” | Fresh-clone run; top-20 users with precision@20 | **Partial**<br>`src/pipeline.py` prints the top users with 3 reasons each, on v0 and v1. `precision_at_k()` is merged (#35); the v1 run and precision@20 are due Nov 12, the README section and fresh-clone test Nov 16–17. | Arva · A11, A18, A23, A24 |
| Research paper | Every planned section drafted (dataset, features, models, experiments, results, limitations) with all 16 figures and tables | IEEE-format PDF | The PDF | **Not started**<br>`paper/` has only an empty `lit_notes/`, and Overleaf isn’t set up (S2-rest). F1, T2 (`class_imbalance.csv`), F3, T3 (`docs/feature_dictionary.md`) and the two T4 drafts exist. Sections due Nov 16. | Everyone · M4, M5 |
| Limitations | Covers the missing failed logins, label-filtered training, synthetic data and the thin test set | Paper §VII | Section text | **Not started**<br>Due Nov 13. | Supriye · S27 |
| Answer the research question | How well the models detect (PR-AUC, LOSO) and which features and models are most reliable (SHAP, ablation, T5) | Paper §VIII Conclusion | A conclusion backed by numbers | **Not started**<br>Human-only. Agreed at the Nov 14 results walkthrough; Arva writes §VIII. | Everyone · S28, A23 |

## What's missing

### Can't be fully met by the current plan

- **Authentication failures.** CERT's logon log has no failed logins. Either do the LANL extension (S24) or state the gap in Methodology and Limitations. The plan defaults to the second; the team decides at the Nov 9 v1 walkthrough.
- **Application usage.** CERT r4.2 has no application or process logs. Web browsing (8 `f_http_*` features, including the `competitor` category added Nov 6) and email stand in, and §III has to say so.
- **"Recent" papers.** The plan counts 11+ papers, but only L9a, L10a and L11a are from 2022–2026. L7 is from 2021 and the rest from 2013–2020. If the instructor reads "recent" as the last five years, that's 3 or 4. Plan v2 marks L9b, L10b and L11b as strongly recommended (TEAM_PLAN 3.14). Making them required, or confirming the meaning with the instructor, would close the gap.
- **Compromised accounts.** Without LANL, the only compromised-account evidence is scenario 3, where the system administrator logs in as their supervisor. On Nov 6 Supriye decided to keep those 20 days labeled malicious on the supervisor accounts, `FAW0032` (16 days) and `FBA0348` (4), which don't count as insiders (S6, #36, #38).

### Still to do

- **Arva:**
  - **Due today (Nov 8):** the DEC-A decisions (autoencoder architecture and grids, alert levels, keep or drop OCSVM) and the REV-A reviews (13 merged PRs, plus #31, which names Arva as reviewer).
  - **Already overdue:** the A-LIT1–4 notes (due Nov 7) and `arva/notes`.
  - **Open requests:** confirming `explain.py` once the data arrives. (The #40 review is posted.)
  - **Fixes:** re-apply the A17 code lost from #34 (in progress), and add a `pipeline.py` phrase for `http_competitor` (#38).
  - **Next:** A15 on the 76-input v1 (Nov 9), tuned defaults and final scores (Nov 10), A17 results (Nov 11), the A18 run (Nov 12), case studies (Nov 13–14), F2 (by Nov 13).
- **Ayo:**
  - **Merged today:** #41 (Y14/Y15: v1 tuning, tuned defaults with RF + SMOTE and XGBoost + class weights, the supervised `final` command, `timing_supervised.csv`). The tracker hasn't ticked them yet.
  - **Due today:** Y-LIT1–4 and DEC-Y's written reasons (imbalance set-up, LOSO design). Y1 and REV-Y are still unticked.
  - **Next:** LOSO results T6 (Nov 11); T5, F4, F5 and T8 (Nov 12).
- **Supriye:**
  - **Open:**
    - the data drop, rebuilt after #38;
    - the v1 freeze and milestone tags (Nov 8);
    - the hand-checks (S6-H, S19-H) and EDA observations (S7-H);
    - Overleaf and Zotero;
    - REV-S and S3-rest (course rules).
  - **Next:** the v1 walkthrough (Nov 9) and the T7 ablation run (Nov 11).
- **Not started anywhere:** notebooks 04–05, figures F2, F7 and F8 (the F8 code exists), the case studies, and any paper text.

### Blockers and loose ends

- **No data drop yet.** The tracker doesn't show it as uploaded. The tooling is merged (`scripts/data_drop.py`, `scripts/rebuild_data.sh`, #31), and the zip has to be rebuilt after #38 changed v1. Arva can't start A15 until it arrives.
- **A17's code is missing from `main`.** `results_extra()`, `timing()`, `alerts_per_day()` and their tests were in #34. The "Merge branch 'main'" commit on that branch kept only three import lines. `unsupervised_extra.csv` (Nov 11) and the unsupervised half of T8 depend on them. A PR to re-apply them is being prepared.
- **Old PRs are unreviewed.** Since Nov 7 `main` requires one approval (#39), and #39–#42 were approved. None of #1–#38 has an approving review (#29 has a comment from Arva), so the post-merge reviews in PROGRESS §3.7 are all open.
- **Scenario 3 is thin.** The test split has 1 real insider (`JLM0364`) with 2 days, plus 2 days on the hijacked account `FBA0348`. Its per-scenario and LOSO results rest on very few rows, so say so in Limitations.
- **Setup gaps.** Overleaf and Zotero aren't set up, and there are no milestone tags yet. The repository is public (that's what allowed branch protection), so nothing private belongs in it.

### Already covered

- **Data:** CERT r4.2 downloaded, checksum-verified, converted to Parquet and cleaned: 32.8M rows, none removed.
- **Labels and split:** labels, insider timeline and split check; every split has malicious days from every scenario. The counts agree: 70 insiders (30/30/10), 72 accounts with malicious days, 984 malicious user-days.
- **Decisions:** all five data decisions are final with written reasons (#36–#38): working hours, split dates, scenario-3 labels, email rule, web keyword lists.
- **Feature table v1:** 1,000 users, 330,268 user-days, 76 model inputs (42 `f_*`, 15 `z_user_*`, 15 `z_peer_*`, 4 `new_*`), with [`docs/feature_dictionary.md`](feature_dictionary.md). Leakage checks 1, 2, 3 and 5 pass.
- **Data tooling:** rebuild and data-drop scripts with checksums (#31). The web-log cache now rebuilds when the working hours change. Tests check the rebuild's outputs (#40).
- **Models:** all five (Isolation Forest, autoencoder, One-Class SVM, Random Forest, XGBoost) with tuning workflows, run on v0, plus the contamination variant, the imbalance experiment and the LOSO code. The unsupervised tuning log keeps every dataset's rows, the `final` command writes the five unsupervised score files, and the macOS test hang is fixed (#33). The supervised models are tuned on v1, with tuned defaults, a `final` command and measured timing (#41).
- **Explanations and prototype:** `explain.py` (SHAP), the autoencoder's per-feature error, and `pipeline.py` with 3 reasons per alert. `precision_at_k()`, the F8 user rule and the risk-timeline plot (#35).
- **Ablation and timing:** `src/ablation.py` with the 10 feature sets (#32), and the measured data-processing time (~138 s from Parquet logs to v1, `data_processing_time.csv`).
- **Evaluation:** `evaluate.py` computes every metric the assignment lists, plus PR-AUC, detection delay and user-level recall.
