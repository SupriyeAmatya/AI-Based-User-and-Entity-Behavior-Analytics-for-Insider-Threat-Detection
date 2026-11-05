# UEBA assignment coverage

> **Snapshot from Thu Nov 5, 2026** (repo at `c7f38cf`). This file does not update itself. [`Tasks/PROGRESS.md`](../Tasks/PROGRESS.md) is still the tracker of record.

It maps each requirement in the CSCI 561 assignment brief to how it's measured, the deliverable, the proof that it's met, and where it stands. It's built from the brief, `Tasks/TEAM_PLAN.md`, `Tasks/PROGRESS.md` and the code on `main`. Tests weren't re-run for this snapshot.

**15 days left to Fri Nov 20 · 3 of 25 requirements fully met**

## Where the requirements stand

| Status | Count | Meaning |
|---|---:|---|
| Gap | 2 | The current plan can’t fully meet it. |
| Overdue | 0 | Past its due date, with nothing on main. |
| Partial | 14 | Some of it exists; the rest is still due. |
| Not started | 6 | Nothing yet, and not due yet. |
| Done | 3 | Met, with proof in the repo or the paper. |

A requirement counts as met only when its proof exists. For most of them that includes paper text, so only 3 are fully met so far.

## Schedule

Milestones from TEAM_PLAN §3. Three of the four due so far are still open.

| Date | Milestone | State | Note |
|---|---|---|---|
| Sat, Oct 31 | **M0** Setup complete | Open, past due | Data isn’t on the shared drive, and Ayo’s install isn’t confirmed. |
| Sun, Nov 1 | evaluate.py ready | Done | Merged Nov 3. |
| Mon, Nov 2 | Split dates final | Open, past due | Still PROVISIONAL. |
| Tue, Nov 3 | **M1** Feature table v0 | Open, past due | Built and used by every model; waits on the confirmed values and the drive upload. |
| Fri, Nov 6 | explain.py ready | Upcoming | Code merged Nov 5; Arva still has to confirm it for the case studies. |
| Sun, Nov 8 | **M2** Feature table v1 | Upcoming | Built and documented Nov 5; drive upload, walkthrough and loading by Arva and Ayo remain. |
| Tue, Nov 10 | Unsupervised scores | Upcoming | v0 scores done; the v1 run is due Nov 9–10. |
| Wed, Nov 11 | **M3** All score files | Upcoming |  |
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
| Review at least 5 recent papers from IEEE, Springer, Elsevier or ACM | 5 or more papers, each recent and from one of those publishers, covering UEBA, insider threat, behavioral anomaly, compromised accounts and AI/ML | `paper/lit_notes/<ID>.md` per paper, table T1 | 5+ note files; T1 lists venue and year | **Gap**<br>`paper/lit_notes/` is still empty, with 4 readings past due. Only 3 planned papers are from 2022–2026. | Everyone · S-LIT, A-LIT, Y-LIT |
| Choose a suitable dataset | Named and justified, with ground-truth labels | CERT r4.2 + answers; paper §III Dataset | Checksums match; `dataset_files.csv` | **Partial**<br>Data done. §III due Nov 10. | Supriye · S1, S23 |
| Preprocess the data | Every log loads, removed rows are counted, and the date-based split has every scenario in every split | `data_loader.py`, `labels.py` | `cleaning_report.csv`, `split_check.csv`, tests | **Partial**<br>Code done. Split dates and after-hours window still PROVISIONAL; hijacked-account labeling undecided (S6). | Supriye · S4–S8 |

### Behavioral features

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Login patterns | Logon counts, first and last logon, PCs used, logons on unusual PCs | `f_logon_*` and related columns in v1 | Feature dictionary T3 | **Done**<br>In v1 (PR #17): logon and logoff counts, first-logon and last-logoff hour, PCs used, logons on other PCs. Documented in `docs/feature_dictionary.md`. | Supriye · S10 |
| Authentication failures | Failed logins per user-day | LANL features, or a stated limitation | LANL feature columns, or Limitations text | **Gap**<br>CERT has no failed logins. LANL is a stretch goal, decided at the Nov 9 stand-up. | Supriye · S24 |
| File and resource access | File copies to removable media, USB connects | `f_file_*`, `f_usb_*` | Feature dictionary T3 | **Done**<br>In v1: file copies by type and after hours; USB connects, after-hours connects, PCs and minutes connected. | Supriye · S12, S13 |
| Application usage | Web categories (job, leak, cloud, hacking), email volume, external email | `f_http_*`, `f_email_*` | Feature dictionary T3 | **Partial**<br>In v1: 8 web and 8 email features. The web keyword lists and the email-count rule are still PROVISIONAL (S14, S15). CERT has no application logs, so web and email stand in. | Supriye · S14, S15 |
| Activity times | After-hours and weekend activity, work duration | `f_afterhours_*`, `f_weekend`, `f_work_duration` | T3, with the reason for the chosen hours | **Partial**<br>In v1: after-hours counts and ratio, weekend flag, work duration. Built on the PROVISIONAL 07:00–19:00 window, and the reason isn’t written yet (S11). | Supriye · S11 |
| Changes from normal behavior | Deviation from the user’s own past 30 days and from same-role peers; novelty flags | `z_user_*`, `z_peer_*`, `new_*` | T3, figure F3 | **Done**<br>In v1 (PR #18): 14 `z_user_*`, 14 `z_peer_*` and 4 `new_*` columns, and figure F3. | Supriye · S17, S18 |

### Normal behavior, models and risk score

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Establish normal behavior | Per-user and peer baselines; unsupervised models train on normal training days only | `src/baseline.py`, paper §IV-B | Figure F3: one user’s baseline next to a day that deviates | **Partial**<br>`baseline.py` and F3 are merged, and every unsupervised model trains on normal training days only. §IV-B due Nov 12. | Supriye, Arva · S17, A5 |
| Develop and compare at least 2 models | 2 or more score files in the agreed format; 5 are built (IF, AE, OCSVM, RF, XGB) | `models_unsupervised.py`, `models_supervised.py`, `results/scores/*.parquet` | Comparison table T5 from `compare_files()` | **Partial**<br>All five are on `main` and have scored v0. Best val PR-AUC so far: IF 0.063, AE 0.122, RF 0.273, XGB 0.324. Final v1 scores due Nov 10, T5 due Nov 12. | Arva, Ayo · A4–A6, A9–A10, A13, Y7–Y9 |
| Justify the models chosen | A reason for each model; hyperparameters listed | Paper §IV-C, table T4 | Paper text | **Partial**<br>T4 drafts exist for both model families. The reasons are still only in TEAM_PLAN §8, and the autoencoder architecture and tuning grids are Arva’s open calls. §IV-C due Nov 15. | Arva, Ayo · A14, A22, Y13, Y21 |
| Assign a risk score to suspicious behavior | 0–100 daily risk (percentile of normal training scores), 7-day user risk, alert levels, top-3 reasons per alert | `src/risk_scoring.py` | Ranked user table; F8 risk timeline for one insider | **Partial**<br>`risk_scoring.py` and `pipeline.py` are merged; the ranked table gives 3 reasons per user (`top_risky_users.csv`). Alert levels still PROVISIONAL (Arva). F8 due Nov 12. | Arva · A7, A11–A12, A18 |

### Evaluation

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Accuracy, precision, recall, F1, FPR, FNR, ROC-AUC, confusion matrix | Each on the test split at the best-F1 and top-1% thresholds, overall and per scenario | `evaluate.py`; T5, F4, F5 | Hand-checked unit test; v0 smoke test | **Partial**<br>Code done and run on v0 scores. Test-split tables and figures (T5, F4, F5) due Nov 12. | Ayo · Y3–Y6, Y17 |
| Detection time | Train time and inference time per 1,000 user-days; days from an insider’s first malicious day to their first alert | Table T8 | Timing log; `detection_delay()` | **Partial**<br>Delay is built, and every model now logs its fit time and scoring time per 1,000 user-days. T8 due Nov 12. | Arva, Ayo · A17, Y15, Y17 |
| Explain why precision and recall matter on imbalanced data | A paragraph with our base rate: 0.298% malicious, so always answering “normal” scores 99.70% accuracy with 0 recall | Paper §V | `class_imbalance.csv` | **Partial**<br>Number ready and quoted in TEAM_PLAN §10.2. Paper text due Nov 16. | Ayo · Y22 |
| Detect previously unseen anomalous behavior | Leave-one-scenario-out: PR-AUC, ROC-AUC and recall at top 1% on the held-out scenario | `run_loso()`, `<model>_loso_s<1–3>` score files | Table T6 | **Partial**<br>`run_loso()` and `loso_table()` are merged and run on v0. Results (T6) due Nov 11; Ayo still has to justify the design. | Ayo · Y12, Y16 |

### Analysis

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Analyze false positives and false negatives | Top false positives grouped by root cause; each missed test insider explained | Paper §VI-C | Case tables | **Not started**<br>Due Nov 14. | Ayo · Y20 |
| Find the features that drive detection | SHAP for RF and XGB, per-feature reconstruction error for the autoencoder, feature-group ablation | `explain.py`, `feature_importance.csv` | F6 SHAP plot, T7 ablation table | **Partial**<br>`explain.py` (SHAP) and the autoencoder’s `feature_errors()` are merged, with SHAP plots on v0. F6, `feature_importance.csv` and the T7 ablation due Nov 11–13. | Ayo, Arva, Supriye · Y11, Y18, A8, S22 |
| Investigate detected anomalies | 2–4 case studies, each saying why the system flagged it | `notebooks/05_anomaly_investigation.ipynb`, paper §VI-B | F7 explanation plots and written cases | **Not started**<br>Due Nov 13–14. The pipeline’s alert reasons are a starting point; the case narratives are human-only. | Arva · A19 |

### Prototype and paper

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| UEBA prototype | One command goes from features to ranked alerts with reasons, and it runs from a fresh clone | `src/pipeline.py`, README “Run the prototype” | Fresh-clone run; top-20 users with precision@20 | **Partial**<br>`src/pipeline.py` prints the top users with 3 reasons each, on v0 and v1. Precision@20 due Nov 12; README section and fresh-clone test due Nov 16–17. | Arva · A11, A18, A23, A24 |
| Research paper | Every planned section drafted (dataset, features, models, experiments, results, limitations) with all 16 figures and tables | IEEE-format PDF | The PDF | **Not started**<br>`paper/` has only an empty `lit_notes/`, and Overleaf isn’t set up. F1, F3 and the two T4 drafts exist. Sections due Nov 16. | Everyone · M4, M5 |
| Limitations | Covers the missing failed logins, label-filtered training, synthetic data and the thin test set | Paper §VII | Section text | **Not started**<br>Due Nov 13. | Supriye · S27 |
| Answer the research question | How well the models detect (PR-AUC, LOSO) and which features and models are most reliable (SHAP, ablation, T5) | Paper §VIII Conclusion | A conclusion backed by numbers | **Not started**<br>Human-only. Agreed at the Nov 14 results walkthrough. | Everyone · S28, A23 |

## What's missing

### Can't be fully met by the current plan

- **Authentication failures.** CERT's logon log has no failed logins. Either do the LANL extension (S24) or state the gap in Methodology and Limitations. The plan defaults to the second; the team decides at the Nov 9 stand-up.
- **Application usage.** CERT r4.2 has no application or process logs. Web browsing (8 `f_http_*` features) and email stand in, and the paper has to say so. The web keyword lists are still PROVISIONAL (S15).
- **"Recent" papers.** The plan counts 11+ papers, but only L9a, L10a and L11a are from 2022–2026. L7 is from 2021 and the rest from 2013–2020. If the instructor reads "recent" as the last five years, that's 3 or 4. Either make L9b, L10b and L11b required, or confirm the meaning with the instructor.
- **Compromised accounts.** Without LANL, the only compromised-account evidence is scenario 3, where the system administrator logs in as their supervisor. Since Nov 4 the two supervisor accounts (FAW0032, FBA0348) no longer count as insiders, but their 20 days are still labeled malicious: half of scenario 3's labeled days. Whether they stay that way is Supriye's open S6 decision.

### Still to do

- **Arva:** read and be able to explain the Claude-written `models_unsupervised.py`, `risk_scoring.py` and `pipeline.py`; decide the autoencoder architecture, tuning grids and alert levels. Next: retrain and tune on v1 (Nov 9), final scores (Nov 10), per-scenario results, alert volume and timing (Nov 11), the F2 diagram, and the case studies (Nov 13–14).
- **Ayo:** no commits yet. Read and be able to explain `models_supervised.py`, `explain.py` and the LOSO code; pick the imbalance set-up and justify the LOSO design. Next: retrain on v1 (Nov 9), final scores (Nov 10), LOSO results T6 (Nov 11), and T5, F4, F5 and T8 (Nov 12).
- **Supriye:** the human-only decisions (after-hours window, split dates, web keyword lists, email-count rule, hijacked-account labels), EDA observations, the label hand-check and leakage check 4; upload v1 to the drive; the v1 walkthrough (Nov 9) and the T7 ablation (Nov 11).
- **Not started anywhere:** notebooks 04–05, figures F2 and F8, the case studies, and any paper text.

### Blockers and loose ends

- The data isn't on the shared drive yet (S4, S20): no Parquet, v0 or v1. Until it is, Arva and Ayo can only work on real data by rebuilding it themselves (4.8 GB download, about 8 GB free disk).
- Four values are still PROVISIONAL: the after-hours window, the split dates, the web keyword lists and the email-count rule. Every score so far uses them, so they need deciding before the final v1 runs on Nov 9–10.
- None of PRs #1–#26 has a GitHub review, so the post-merge reviews in PROGRESS §9 are all open. Most Week 0–1 code in every lane was written by Claude at Supriye's request, so each owner still has to read it and be able to explain it (TEAM_PLAN §12).
- Scenario 3 is thinner than first reported: the test split has 1 real insider (JLM0364) with 2 days, plus 2 days on the hijacked account FBA0348. Its per-scenario and LOSO results rest on very few rows, so say so in Limitations.
- Branch protection on `main` is still off, so the PR rule holds by agreement only. Overleaf and Zotero aren't set up, and there are no milestone tags yet.

### Already covered

- CERT r4.2 downloaded, checksum-verified, converted to Parquet and cleaned: 32.8M rows, none removed.
- Labels, insider timeline and split check; every split has malicious days from every scenario. The counts now agree: 70 insiders (30/30/10), 72 accounts with malicious days, 984 malicious user-days.
- Feature table v1: 1,000 users, 330,268 user-days, 73 model inputs (41 `f_*`, 14 `z_user_*`, 14 `z_peer_*`, 4 `new_*`), with [`docs/feature_dictionary.md`](feature_dictionary.md); leakage checks 1, 2, 3 and 5 pass.
- All five models (Isolation Forest, autoencoder, One-Class SVM, Random Forest, XGBoost) with tuning workflows, run on v0; the contamination variant, the imbalance experiment and the LOSO code.
- `explain.py` (SHAP), the autoencoder's per-feature error, and the prototype `pipeline.py` with 3 reasons per alert.
- `evaluate.py` computes every metric the assignment lists plus PR-AUC, detection delay and user-level recall, and every model logs its fit and scoring time.
