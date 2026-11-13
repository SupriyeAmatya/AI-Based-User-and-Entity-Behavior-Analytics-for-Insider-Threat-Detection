# UEBA assignment coverage

> **Snapshot from Fri Nov 13, 2026** (repo at `0729548`). This file does not update itself. [`Tasks/PROGRESS.md`](../Tasks/PROGRESS.md) is still the tracker of record.

It maps each requirement in the CSCI 561 assignment brief to how it's measured, the deliverable, the proof that it's met, and where it stands. It's built from the brief, `Tasks/TEAM_PLAN.md`, `Tasks/PROGRESS.md` and the code on `main`. Tests weren't re-run for this snapshot. Work still on a branch is mentioned where it matters but doesn't count as met.

**7 days left to Fri Nov 20 · 10 of 25 requirements fully met**

## Where the requirements stand

| Status | Count | Meaning |
|---|---:|---|
| Gap | 2 | The current plan can’t fully meet it. |
| Overdue | 0 | Past its due date, with nothing on main. |
| Partial | 9 | Some of it exists; the rest is still due. |
| Not started | 4 | Nothing yet, and not due yet. |
| Done | 10 | Met, with proof in the repo or the paper. |

A requirement counts as met only when its proof exists. For most of them that includes paper text, so only 10 are fully met so far.

## Schedule

Milestones from TEAM_PLAN 1.5. Of the eight due by today, five are done (M0, `evaluate.py`, the split dates, M2 and the tuned models); M1, the `explain.py` check and M3 are still open.

| Date | Milestone | State | Note |
|---|---|---|---|
| Sat, Oct 31 | **M0** Setup complete | Done | Tagged `m0-setup` Nov 10. |
| Sun, Nov 1 | evaluate.py ready | Done | Merged Nov 3. |
| Mon, Nov 2 | Split dates final | Done | Decided Nov 6 (#36); reason in TEAM_PLAN 2.5.3. |
| Tue, Nov 3 | **M1** Feature table v0 | Open, past due | Built and used by every model; Arva’s and Ayo’s v0 confirmations aren’t ticked. |
| Fri, Nov 6 | explain.py ready | Open, past due | Code merged Nov 5; Arva still has to confirm it for the case studies. |
| Sun, Nov 8 | **M2** Feature table v1 | Done | Tagged `m2-features-v1` Nov 8 (#45). |
| Tue, Nov 10 | Tuned models + `final` commands | Done | Supervised (#41) and unsupervised (#50) tuned defaults merged. |
| Wed, Nov 11 | **M3** All score files | Open, past due | `m3-all-scores` is tagged (#56); the box waits for `unsupervised_extra.csv`, which is in open PR #57. |
| Sat, Nov 14 | Analysis done | Upcoming | T5–T8, F4–F6 and the FP/FN tables are merged; F7 and F8 are in #57 and #58. Walkthrough on Sat. |
| Mon, Nov 16 | **M4** All sections drafted | Upcoming | No section is drafted yet, and Overleaf isn’t set up. |
| Wed, Nov 18 | **M5** Full paper draft | Upcoming |  |
| Thu, Nov 19 | Submission-ready | Upcoming |  |
| Fri, Nov 20 | Submit | Upcoming |  |

## Requirements

Owner and task IDs refer to the task cards in `Tasks/`.

### Research and data

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Study insider threats, compromised accounts, behavioral anomalies and UEBA | All four topics covered and cited in the background | Paper §I Introduction and §II Related Work | Section text with citations | **Not started**<br>§I and the Related Work paragraphs are due today (Nov 13). Overleaf isn’t set up yet (S2-rest). | Everyone · S25–S26, A20, Y19 |
| Review at least 5 recent papers from IEEE, Springer, Elsevier or ACM | 5 or more papers, each recent and from one of those publishers, covering UEBA, insider threat, behavioral anomaly, compromised accounts and AI/ML | `paper/lit_notes/<ID>.md` per paper, table T1 | 5+ note files; T1 lists venue and year | **Gap**<br>`paper/lit_notes/` is still empty, and neither `arva/notes` nor `ayo/notes` is on GitHub. Every reading is past due (Arva Nov 7, Ayo Nov 8, Supriye Nov 12). Only 3 planned papers are from 2022–2026. | Everyone · S-LIT, A-LIT, Y-LIT |
| Choose a suitable dataset | Named and justified, with ground-truth labels | CERT r4.2 + answers; paper §III Dataset | Checksums match; `dataset_files.csv` | **Partial**<br>Data done. §III was due Nov 10 (S23a) and isn’t ticked. | Supriye · S1, S23a |
| Preprocess the data | Every log loads, removed rows are counted, and the date-based split has every scenario in every split | `data_loader.py`, `labels.py` | `cleaning_report.csv`, `split_check.csv`, tests | **Done**<br>Code and checks done. The split dates and the scenario-3 labels were decided Nov 6 (#36), with the reasons in TEAM_PLAN 2.5.3 and the feature dictionary (#37, #38). | Supriye · S4–S8 |

### Behavioral features

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Login patterns | Logon counts, first and last logon, PCs used, logons on unusual PCs | `f_logon_*` and related columns in v1 | Feature dictionary T3 | **Done**<br>In v1 (PR #17): logon and logoff counts, first-logon and last-logoff hour, PCs used, logons on other PCs. Documented in `docs/feature_dictionary.md`. | Supriye · S10 |
| Authentication failures | Failed logins per user-day | LANL features, or a stated limitation | LANL feature columns, or Limitations text | **Gap**<br>CERT has no failed logins. LANL is a stretch goal, decided at today’s v1 walkthrough. | Supriye · S24 |
| File and resource access | File copies to removable media, USB connects | `f_file_*`, `f_usb_*` | Feature dictionary T3 | **Done**<br>In v1: file copies by type and after hours; USB connects, after-hours connects, PCs and minutes connected. | Supriye · S12, S13 |
| Application usage | Web categories (job, leak, cloud, hacking, competitor), email volume, external email | `f_http_*`, `f_email_*` | Feature dictionary T3, and the stand-in stated in §III | **Partial**<br>In v1: 8 web and 8 email features. The keyword lists and the email-count rule were decided Nov 6 (#36), and a `competitor` web category was added (#38). CERT has no application logs, so web and email stand in, and §III (due Nov 10) has to say so. | Supriye · S14, S15 |
| Activity times | After-hours and weekend activity, work duration | `f_afterhours_*`, `f_weekend`, `f_work_duration` | T3, with the reason for the chosen hours | **Done**<br>In v1: after-hours counts and ratio, weekend flag, work duration. The 07:00–19:00 window was decided Nov 6 (#36), and its reason is in the feature dictionary (#37, #38). | Supriye · S11 |
| Changes from normal behavior | Deviation from the user’s own past 30 days and from same-role peers; novelty flags | `z_user_*`, `z_peer_*`, `new_*` | T3, figure F3 | **Done**<br>In v1 (PR #18, extended by #38): 15 `z_user_*`, 15 `z_peer_*` and 4 `new_*` columns, and figure F3. | Supriye · S17, S18 |

### Normal behavior, models and risk score

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Establish normal behavior | Per-user and peer baselines; unsupervised models train on normal training days only | `src/baseline.py`, paper §IV-B | Figure F3: one user’s baseline next to a day that deviates | **Partial**<br>`baseline.py` and F3 are merged, and every unsupervised model trains on normal training days only. §IV-B was due Nov 12 (S23b) and isn’t ticked. | Supriye, Arva · S17, S23b, A5 |
| Develop and compare at least 2 models | 2 or more score files in the agreed format; 5 are built (IF, AE, OCSVM, RF, XGB) | `models_unsupervised.py`, `models_supervised.py`, `results/scores/*.parquet` | Comparison table T5 from `compare_files()` | **Done**<br>All five are tuned on v1 and compared on the test split at both operating points in T5 (`model_comparison.csv`, #48, re-run with the tuned unsupervised defaults in #52). The README shows T5 (#54). | Arva, Ayo · A4–A6, A9–A10, A13, A15–A16, Y7–Y9, Y14–Y15 |
| Justify the models chosen | A reason for each model; hyperparameters listed | Paper §IV-C, table T4 | Paper text | **Partial**<br>T4 has the v1-tuned values for both families (#41, #50). The reasons are still only in TEAM_PLAN 2.7.3; Arva’s DEC-A reasons are open, and Ayo’s imbalance set-up is recorded in #41. §IV-C due Nov 15. | Arva, Ayo · A14, A22, DEC-A, Y13, Y21, DEC-Y |
| Assign a risk score to suspicious behavior | 0–100 daily risk (percentile of normal training scores), 7-day user risk, alert levels, top-3 reasons per alert | `src/risk_scoring.py` | Ranked user table; F8 risk timeline for one insider | **Partial**<br>`risk_scoring.py` and `pipeline.py` are merged. The v1 ranked tables, precision@20 and F8 are in open PR #57. Alert levels still PROVISIONAL (DEC-A, due Nov 8). §IV-D due Nov 15. | Arva · A7, A11–A12, A18 |

### Evaluation

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Accuracy, precision, recall, F1, FPR, FNR, ROC-AUC, confusion matrix | Each on the test split at the best-F1 and top-1% thresholds, overall and per scenario | `evaluate.py`; T5, F4, F5 | Hand-checked unit test; v0 smoke test | **Done**<br>T5, the per-scenario table, F4 and F5 are on `main` from the test split at both operating points (#48, #52). §V due Nov 15. | Ayo · Y3–Y6, Y17 |
| Detection time | Train time and inference time per 1,000 user-days; data-processing time; days from an insider’s first malicious day to their first alert | Table T8 | Timing tables; `detection_delay()` | **Done**<br>T8 (`T8_timing.csv`) has every model’s fit and inference time (3-run means on the results machine), the detection delay, and the data-processing time (#48, #52). | Arva, Ayo, Supriye · A17, Y15, Y17, S22 |
| Explain why precision and recall matter on imbalanced data | A paragraph with our base rate: 0.298% malicious, so always answering “normal” scores 99.70% accuracy with 0 recall | Paper §V | `class_imbalance.csv` | **Partial**<br>Number ready and quoted in TEAM_PLAN 5.4. Paper text due Nov 16. | Ayo · Y22 |
| Detect previously unseen anomalous behavior | Leave-one-scenario-out: PR-AUC, ROC-AUC and recall at top 1% on the held-out scenario | `run_loso()`, `<model>_loso_s<1–3>` score files | Table T6 | **Done**<br>T6 (`loso.csv`, `loso_pr_auc.csv`) is on `main` (#46, re-run in #52). Ayo’s written LOSO justification (DEC-Y) is still open. | Ayo · Y12, Y16, DEC-Y |

### Analysis

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| Analyze false positives and false negatives | Top false positives grouped by root cause; each missed test insider explained | Paper §VI-C | Case tables | **Partial**<br>The FP/FN tables are on `main` (`fp_breakdown.csv`, `fp_top10.csv`, `fn_by_insider.csv`, #55). The causes (`fp_fn_causes.csv`) are marked as drafts for Ayo to check [H]. §VI-C due Nov 16. | Ayo · Y20 |
| Find the features that drive detection | SHAP for RF and XGB, per-feature reconstruction error for the autoencoder, feature-group ablation | `explain.py`, `feature_importance.csv` | F6 SHAP plot, T7 ablation table | **Done**<br>F6 and `feature_importance.csv` (with per-scenario importance) are on `main` (#53), and so is the T7 ablation (`ablation.csv`, #51). Interpreting them is human-only. | Ayo, Arva, Supriye · Y11, Y18, A8, S22 |
| Investigate detected anomalies | 2–4 case studies, each saying why the system flagged it | `notebooks/05_anomaly_investigation.ipynb`, paper §VI-B | F7 explanation plots and written cases | **Partial**<br>Notebook 05 with 4 cases, their raw evidence and the F7 figures is in open PR #58. The narratives and verdicts are Arva’s [H]; 2 cases go to the Sat Nov 14 walkthrough. | Arva · A19 |

### Prototype and paper

| Goal | How it's measured | Deliverable | Proof | Status | Owner · tasks |
|---|---|---|---|---|---|
| UEBA prototype | One command goes from features to ranked alerts with reasons, and it runs from a fresh clone | `src/pipeline.py`, README “Run the prototype” | Fresh-clone run; top-20 users with precision@20 | **Partial**<br>`src/pipeline.py` ranks users with 3 reasons each. The v1 outputs and precision@20 are in open PR #57, and the README “Run the prototype” section in #59. The fresh-clone test is due Nov 17. | Arva · A11, A18, A23, A24 |
| Research paper | Every planned section drafted (dataset, features, models, experiments, results, limitations) with all 16 figures and tables | IEEE-format PDF | The PDF | **Not started**<br>No section is drafted, and Overleaf isn’t set up (S2-rest); all sections are due Mon Nov 16 (M4). On file: F1 and F3–F6, T2–T8 data; F7 and F8 are in open PRs; F2 isn’t drawn. | Everyone · M4, M5 |
| Limitations | Covers the missing failed logins, label-filtered training, synthetic data and the thin test set | Paper §VII | Section text | **Not started**<br>Due today (Nov 13). | Supriye · S27 |
| Answer the research question | How well the models detect (PR-AUC, LOSO) and which features and models are most reliable (SHAP, ablation, T5) | Paper §VIII Conclusion | A conclusion backed by numbers | **Not started**<br>Human-only. Agreed at the Sat Nov 14 results walkthrough; Arva writes §VIII by Nov 16. | Everyone · S28, A23 |

## What's missing

### Can't be fully met by the current plan

- **Authentication failures.** CERT's logon log has no failed logins. S24 (LANL) wasn't agreed, so the gap has to be stated in §III and §VII.
- **Application usage.** CERT r4.2 has no application or process logs. Web browsing (8 `f_http_*` features, including the `competitor` category added Nov 6) and email stand in, and §III has to say so.
- **"Recent" papers.** The plan counts 11+ papers, but only L9a, L10a and L11a are from 2022–2026. L7 is from 2021 and the rest from 2013–2020. If the instructor reads "recent" as the last five years, that's 3 or 4. Plan v2 marks L9b, L10b and L11b as strongly recommended (TEAM_PLAN 3.14). Making them required, or confirming the meaning with the instructor, would close the gap.
- **Compromised accounts.** Without LANL, the only compromised-account evidence is scenario 3, where the system administrator logs in as their supervisor. On Nov 6 Supriye decided to keep those 20 days labeled malicious on the supervisor accounts, `FAW0032` (16 days) and `FBA0348` (4), which don't count as insiders (S6, #36, #38).

### Still to do (for M4, Mon Nov 16)

- **Arva:**
  - **Code in review:**
    - #57 (A17 `unsupervised_extra.csv`, A18 v1 outputs and F8) and #58 (A19 notebook 05, F7), both written by Claude at Supriye's request, in Arva's files;
    - #59 (A23 README run section).
  - **Overdue [H]:**
    - DEC-A (autoencoder architecture and grid reasons, alert levels, OCSVM, F8 model);
    - REV-A (13 merged PRs plus #31);
    - A-LIT1–4;
    - F2 and the IV-C/IV-D notes (A14-rest);
    - confirming `explain.py`.
  - **Due today:** A20 Related Work paragraphs (L4, L5, L10a).
  - **Next [H]:**
    - A19 narratives and verdicts, and 2 cases at the Sat Nov 14 walkthrough;
    - A22 IV-C, IV-D and VI-B (Sun Nov 15);
    - A23 VIII (Mon Nov 16).
  - **After M4:** A24 fresh-clone test and demo (Tue Nov 17). A21 dashboard is optional.
- **Ayo:**
  - **Merged:** T5–T8, F4–F6, LOSO, SHAP and the FP/FN tables (#46, #48, #52, #53, #55).
  - **Open [H]:** checking the Claude-drafted readings and causes (Y16-H, Y18-H, Y20-H), the LOSO justification (DEC-Y), Y-LIT1–4 and `ayo/notes`, REV-Y.
  - **Due today:** Y19 Related Work paragraphs.
  - **Next [H]:** Y21 IV-C (supervised) and V (Sun Nov 15); Y22 VI-A, VI-C and the P/R paragraph (Mon Nov 16).
- **Supriye:**
  - **Merged:** the T7 ablation (#51) and the README results table (#54). `m3-all-scores` is tagged (#56 records it).
  - **Open:**
    - Overleaf and Zotero (S2-rest), which every section needs;
    - the course rules (S3-rest);
    - the hand-checks (S6-H, S19-H) and EDA observations (S7-H);
    - interpreting the ablation (S22-H);
    - REV-S.
  - **Overdue [H]:** S-LIT1–3 (Nov 12), III. Dataset (Nov 10), IV-A and IV-B (Nov 12).
  - **Due today [H]:** I. Introduction, Related Work paragraphs, VII. Limitations.
  - **Next:** the results walkthrough and merging II (Sat Nov 14), then assembling M4 (Nov 15–16).
- **Not started anywhere:** F2, Overleaf, and any paper text.

### Blockers and loose ends

- **No paper yet.** M4 (Mon Nov 16) needs every section drafted in Overleaf. Overleaf isn't set up, and no section is ticked. All the writing is human-only (TEAM_PLAN 2.6).
- **No literature notes.** Nothing is in `paper/lit_notes/`, and II, T1 and the ≥ 5 recent papers depend on them.
- **DEC-A is still open.** `HIGH`/`MEDIUM` are PROVISIONAL, and they drive `top_risky_users*.csv`, F8 and IV-D.
- **Course rules unconfirmed (S3-rest).** The page limit and the AI-use policy aren't confirmed, and much of the code and several readings were drafted by Claude.
- **Alert reasons in #57.** `src/pipeline.py` `PHRASES` has no wording for `http_competitor`, so reasons read "http competitor 3.7σ above own baseline".
- **Old PRs are unreviewed.** None of #1–#38 has an approving review (#29 has a comment from Arva), so the post-merge reviews in PROGRESS §3.7 are all open. Every PR since #39 was approved before merging.
- **Scenario 3 is thin.** The test split has 1 real insider (`JLM0364`) with 2 days, plus 2 days on the hijacked account `FBA0348`. Its per-scenario and LOSO results rest on very few rows, so say so in Limitations.

### Already covered

- **Data:** CERT r4.2 downloaded, checksum-verified, converted to Parquet and cleaned: 32.8M rows, none removed. The one data drop is on the shared drive (Nov 8).
- **Labels and split:** labels, insider timeline and split check; every split has malicious days from every scenario. The counts are 70 insiders (30/30/10), 72 accounts with malicious days, 984 malicious user-days.
- **Decisions:** all five data decisions are final with written reasons (#36–#38).
- **Feature table v1, frozen:** 1,000 users, 330,268 user-days, 76 model inputs (42 `f_*`, 15 `z_user_*`, 15 `z_peer_*`, 4 `new_*`), with [`docs/feature_dictionary.md`](feature_dictionary.md). Leakage checks 1, 2, 3 and 5 pass. No bug fix was needed (S21).
- **Models:** all five tuned on v1, with tuned defaults and `final` commands (#41, #50). T4 covers both families.
- **Results:**
  - T5, the per-scenario and delay tables, F4, F5 and T8 (#48, #52);
  - T6 LOSO (#46);
  - F6 and feature importance (#53);
  - T7 ablation (#51);
  - FP/FN tables (#55);
  - the README results table, generated from T5 (#54).
- **Milestone tags:** `m0-setup`, `m2-features-v1` and `m3-all-scores`.
- **Explanations and prototype:** `explain.py` (SHAP), the autoencoder's per-feature error, and `pipeline.py` with 3 reasons per alert. `precision_at_k()`, the F8 user rule and the risk-timeline plot (#35).
- **Evaluation:** `evaluate.py` computes every metric the assignment lists, plus PR-AUC, detection delay and user-level recall.
