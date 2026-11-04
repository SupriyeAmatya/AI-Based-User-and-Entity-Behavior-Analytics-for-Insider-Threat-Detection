# UEBA assignment coverage

> **Snapshot from Wed Nov 4, 2026** (repo at `a63ba46`). This file does not update itself. [`Tasks/PROGRESS.md`](../Tasks/PROGRESS.md) is still the tracker of record.

It maps each requirement in the CSCI 561 assignment brief to how it's measured, the deliverable, the proof that it's met, and where it stands. It's built from the brief, `Tasks/TEAM_PLAN.md`, `Tasks/PROGRESS.md` and the code on `main`. Tests weren't re-run for this snapshot.

**16 days left to Fri Nov 20 · 0 of 25 requirements fully met**

## Where the requirements stand

| Status | Count | Meaning |
|---|---:|---|
| Gap | 2 | The current plan can’t fully meet it. |
| Overdue | 2 | Past its due date, with nothing on main. |
| Partial | 10 | Some of it exists; the rest is still due. |
| Not started | 11 | Nothing yet, and not due yet. |
| Done | 0 | Met, with proof in the repo or the paper. |

A requirement counts as met only when its proof exists. For most of them that includes paper text, so nothing is fully met yet.

## Schedule

Milestones from TEAM_PLAN §3. Three of the four due so far are still open.

| Date | Milestone | State | Note |
|---|---|---|---|
| Sat, Oct 31 | **M0** Setup complete | Open, past due | Data upload and teammates’ installs not confirmed. |
| Sun, Nov 1 | evaluate.py ready | Done | Merged Nov 3. |
| Mon, Nov 2 | Split dates final | Open, past due |  |
| Tue, Nov 3 | **M1** Feature table v0 | Open, past due | Built; waiting on confirmed values and teammates. |
| Fri, Nov 6 | explain.py ready | Upcoming |  |
| Sun, Nov 8 | **M2** Feature table v1 | Upcoming |  |
| Tue, Nov 10 | Unsupervised scores | Upcoming |  |
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
| Review at least 5 recent papers from IEEE, Springer, Elsevier or ACM | 5 or more papers, each recent and from one of those publishers, covering UEBA, insider threat, behavioral anomaly, compromised accounts and AI/ML | `paper/lit_notes/<ID>.md` per paper, table T1 | 5+ note files; T1 lists venue and year | **Gap**<br>No notes in the repo and 4 readings past due. Only 3 planned papers are from 2022–2026. | Everyone · S-LIT, A-LIT, Y-LIT |
| Choose a suitable dataset | Named and justified, with ground-truth labels | CERT r4.2 + answers; paper §III Dataset | Checksums match; `dataset_files.csv` | **Partial**<br>Data done. §III due Nov 10. | Supriye · S1, S23 |
| Preprocess the data | Every log loads, removed rows are counted, and the date-based split has every scenario in every split | `data_loader.py`, `labels.py` | `cleaning_report.csv`, `split_check.csv`, tests | **Partial**<br>Code done. Split dates and after-hours window still PROVISIONAL; supervisor-account labeling undecided. | Supriye · S4–S8 |

### Behavioral features

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Login patterns | Logon counts, first and last logon, PCs used, logons on unusual PCs | `f_logon_*` columns in v1 | Feature dictionary T3 | **Partial**<br>v0 has logon, logoff and after-hours logon counts. Due Nov 4. | Supriye · S10 |
| Authentication failures | Failed logins per user-day | LANL features, or a stated limitation | LANL feature columns, or Limitations text | **Gap**<br>CERT has no failed logins. LANL is a stretch goal, decided at the Nov 9 stand-up. | Supriye · S24 |
| File and resource access | File copies to removable media, USB connects | `f_file_*`, `f_usb_*` | Feature dictionary T3 | **Partial**<br>`f_file_copy` and `f_usb_connect` in v0. Due Nov 5. | Supriye · S12, S13 |
| Application usage | Web categories (job, leak, cloud, hacking), email volume, external email | `f_web_*`, `f_email_*` | Feature dictionary T3 | **Partial**<br>Email counts in v0, no web features yet. CERT has no application logs, so web and email stand in. Due Nov 5–6. | Supriye · S14, S15 |
| Activity times | After-hours and weekend activity, work duration | `f_afterhours_*`, `f_weekend`, `f_work_duration` | T3, with the reason for the chosen hours | **Partial**<br>One after-hours count in v0; the window isn’t decided. Due Nov 4. | Supriye · S11 |
| Changes from normal behavior | Deviation from the user’s own past 30 days and from same-role peers; novelty flags | `z_user_*`, `z_peer_*`, `new_*` | T3, figure F3 | **Not started**<br>Due Nov 7–8. | Supriye · S17, S18 |

### Normal behavior, models and risk score

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Establish normal behavior | Per-user and peer baselines; unsupervised models train on normal training days only | `src/baseline.py`, paper §IV-B | Figure F3: one user’s baseline next to a day that deviates | **Not started**<br>Due Nov 7–8. | Supriye, Arva · S17, A5 |
| Develop and compare at least 2 models | 2 or more score files in the agreed format; 4 are planned (IF, AE, RF, XGB) | `models_unsupervised.py`, `models_supervised.py`, `results/scores/*.parquet` | Comparison table T5 from `compare_files()` | **Overdue**<br>No model code on main. A4–A6, A9, Y7 and Y8 are past due. | Arva, Ayo · A4–A6, Y7 |
| Justify the models chosen | A reason for each model; hyperparameters listed | Paper §IV-C, table T4 | Paper text | **Partial**<br>Reasons exist only in TEAM_PLAN §8. Due Nov 15. | Arva, Ayo · A22, Y21 |
| Assign a risk score to suspicious behavior | 0–100 daily risk (percentile of normal training scores), 7-day user risk, alert levels, top-3 reasons per alert | `src/risk_scoring.py` | Ranked user table; F8 risk timeline for one insider | **Overdue**<br>A7 was due Nov 1. | Arva · A7, A12 |

### Evaluation

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Accuracy, precision, recall, F1, FPR, FNR, ROC-AUC, confusion matrix | Each on the test split at the best-F1 and top-1% thresholds, overall and per scenario | `evaluate.py`; T5, F4, F5 | Hand-checked unit test; v0 smoke test | **Partial**<br>Code done. No model scores to run it on yet. | Ayo · Y3–Y6, Y17 |
| Detection time | Train time and inference time per 1,000 user-days; days from an insider’s first malicious day to their first alert | Table T8 | Timing log; `detection_delay()` | **Partial**<br>Delay is built; compute timing isn’t. | Arva, Ayo · A17, Y15, Y17 |
| Explain why precision and recall matter on imbalanced data | A paragraph with our base rate: 0.298% malicious, so always answering “normal” scores 99.70% accuracy with 0 recall | Paper §V | `class_imbalance.csv` | **Partial**<br>Number ready; README has a draft. Paper text due Nov 16. | Ayo · Y22 |
| Detect previously unseen anomalous behavior | Leave-one-scenario-out: PR-AUC, ROC-AUC and recall at top 1% on the held-out scenario | `run_loso()`, `<model>_loso_s<1–3>` score files | Table T6 | **Not started**<br>Code due Nov 7, results Nov 11. | Ayo · Y12, Y16 |

### Analysis

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Analyze false positives and false negatives | Top false positives grouped by root cause; each missed test insider explained | Paper §VI-C | Case tables | **Not started**<br>Due Nov 14. | Ayo · Y20 |
| Find the features that drive detection | SHAP for RF and XGB, per-feature reconstruction error for the autoencoder, feature-group ablation | `explain.py`, `feature_importance.csv` | F6 SHAP plot, T7 ablation table | **Not started**<br>`explain.py` due Nov 6. | Ayo, Arva, Supriye · Y11, Y18, A8, S22 |
| Investigate detected anomalies | 2–4 case studies, each saying why the system flagged it | `notebooks/05_anomaly_investigation.ipynb`, paper §VI-B | F7 explanation plots and written cases | **Not started**<br>Due Nov 13–14. | Arva · A19 |

### Prototype and paper

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| UEBA prototype | One command goes from features to ranked alerts with reasons, and it runs from a fresh clone | `src/pipeline.py`, README “Run the prototype” | Fresh-clone run; top-20 users with precision@20 | **Not started**<br>Pipeline due Nov 5. | Arva · A11, A18, A23, A24 |
| Research paper | Every planned section drafted (dataset, features, models, experiments, results, limitations) with all 16 figures and tables | IEEE-format PDF | The PDF | **Not started**<br>`paper/` is empty and Overleaf isn’t set up. Only F1 and T2 exist. Sections due Nov 16. | Everyone · M4, M5 |
| Limitations | Covers the missing failed logins, label-filtered training, synthetic data and the thin test set | Paper §VII | Section text | **Not started**<br>Due Nov 13. | Supriye · S27 |
| Answer the research question | How well the models detect (PR-AUC, LOSO) and which features and models are most reliable (SHAP, ablation, T5) | Paper §VIII Conclusion | A conclusion backed by numbers | **Not started**<br>Human-only. Agreed at the Nov 14 results walkthrough. | Everyone · S28, A23 |

## What's missing

### Can't be fully met by the current plan

- **Authentication failures.** CERT's logon log has no failed logins. Either do the LANL extension (S24) or state the gap in Methodology and Limitations. The plan defaults to the second; the team decides at the Nov 9 stand-up.
- **Application usage.** CERT r4.2 has no application or process logs. Web browsing and email stand in, and the paper has to say so. No web features exist yet (S15 needs Supriye's keyword lists).
- **"Recent" papers.** The plan counts 11+ papers, but only L9a, L10a and L11a are from 2022–2026. L7 is from 2021 and the rest from 2013–2020. If the instructor reads "recent" as the last five years, that's 3 or 4. Either make L9b, L10b and L11b required, or confirm the meaning with the instructor.
- **Compromised accounts.** Without LANL, the only compromised-account evidence is scenario 3, where the system administrator logs in as their supervisor: 20 malicious days on accounts FAW0032 and FBA0348. Whether those days count that way is Supriye's open S6 decision.

### Still to build

- **Arva, overdue:** `synthetic.py`, `models_unsupervised.py` (Isolation Forest, autoencoder, contamination variant, per-feature error), `risk_scoring.py`, and the first run on v0. Next: `pipeline.py` (Nov 5) and alert reasons (Nov 6).
- **Ayo, overdue:** `models_supervised.py` and the first run on v0. Next: `explain.py` (Nov 6) and the LOSO code (Nov 7).
- **Supriye:** the v1 features (S10–S18), `baseline.py`, leakage checks and the feature dictionary, all due Nov 8.
- **Not started anywhere:** measuring train and inference time for "detection time" (planned in A17 and Y15), and notebooks 02–05.

### Blockers and loose ends

- The data isn't on the shared drive yet (S4). Until it is, Arva and Ayo have to run `scripts/download_cert.sh` (4.8 GB) to work on real data.
- Reviews of PRs #1–#7 are still open. Arva has #3–#6; Ayo has #1.
- The after-hours window and the split dates are still PROVISIONAL, so v0 has to be rebuilt once Supriye decides them.
- Two counts disagree and need one answer before the paper. `class_imbalance.csv` says 72 insiders because it counts the two supervisor accounts; the tracker says 70. The labels have 986 malicious user-days and the feature table keeps 984, probably because 2 of those days have no logon.
- Scenario 3 has 2 insiders and 4 malicious days in the test split, so its per-scenario and LOSO results rest on 4 rows. Say so in Limitations, or Supriye moves the split.
- The tracker doesn't show Overleaf or Zotero as set up yet, and one teammate still needs a GitHub invite.

### Already covered

- CERT r4.2 downloaded, checksum-verified, converted to Parquet and cleaned: 32.8M rows, none removed.
- Labels, insider timeline and split check. Every split has malicious days from every scenario.
- The EDA notebook runs end to end and produced figure F1 and table T2. Its observation cells are still to write.
- Feature table v0 (100 users, 31,278 user-days, 252 malicious) and `get_model_matrix()`.
- `evaluate.py` computes every metric the assignment lists except compute time, plus PR-AUC, detection delay and user-level recall.
- `requirements.txt` has the assignment's tools: scikit-learn, PyTorch, Jupyter and Matplotlib.
