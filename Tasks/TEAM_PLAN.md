# Team Plan — Work Split, Rules & Shared Reference

| Person | Role | Personal plan |
|---|---|---|
| **Supriye** | Data & Feature Engineering Lead + Paper Integrator | [Supriye.md](Supriye.md) |
| **Arva** | Unsupervised Models, Risk Scoring & Prototype Lead | [Arva.md](Arva.md) |
| **Ayo** | Supervised Models, Evaluation & Explainability Lead | [Ayo.md](Ayo.md) |

> **Deadline: Friday, November 20, 2026.** That is just over three weeks from the start (Wed Oct 28). Aim to be **submission-ready on Thursday, November 19**, so Friday is only a buffer.
>
> Because the schedule is tight, **optional items are cut first** if anyone falls behind: One-Class SVM, dashboard, LANL extension, the second recent paper each. LSTM is not planned; it goes in Future Work.

---

## 1. How to Use These Files

1. **Before the kickoff meeting (Thu Oct 29):** everyone reads this whole file once, then their own plan.
2. Every task has an **ID**: `S` = Supriye, `A` = Arva, `Y` = Ayo (e.g. `S9`, `A21`, `Y14`).
3. Each personal file has:
   - a **day-by-day timeline** (date → task ID → short description), and
   - **task cards** with the goal, numbered steps, and a **"Done when"** checklist. A task is only finished when every "Done when" item is true.
4. Tick tasks off in your own file and push the change, so the team can see progress.
5. If you are going to miss a hand-off date, tell the team **as soon as you know**, not on the day.

---

## 2. How the Three Streams Run in Parallel

Models need features, and evaluation needs model scores. To avoid waiting on each other:

1. **Kickoff (Thu Oct 29):** agree on the rules in [Section 5](#5-team-rules-agree-at-kickoff). They fix the file formats, so code written separately will fit together.
2. **Oct 29 – Nov 2:** Arva and Ayo write and test their code on **synthetic data** in the agreed format while Supriye prepares the real data.
3. **Tue Nov 3:** Supriye ships a small **v0 feature table** (real data, 100 users, basic features) so everyone switches to real data early.
4. **Sun Nov 8:** Supriye ships the full **v1 feature table**. Arva and Ayo re-run their already-working code on it on Mon Nov 9.
5. **Tue Nov 10 → Wed Nov 11:** all model scores flow to Ayo for the team-wide comparison.
6. **Nov 12 – Nov 16:** analysis and paper writing. **Nov 17 – Nov 19:** merge, edit, final checks. **Fri Nov 20:** submit.

```
Week:     0 (Oct 28–Nov 1)      1 (Nov 2–8)               2 (Nov 9–15)               3 (Nov 16–20)
Supriye   setup, data, labels → EDA, features, baselines → ablation, paper sections → merge, edit, SUBMIT
                                  │ v0 Nov 3   │ v1 Nov 8
Arva      IF + AE (synthetic) → risk score, AE on v0,    → tune on v1, final scores, → paper sections,
                                prototype                  case studies               demo, SUBMIT
                                                             │ scores Nov 10
Ayo       evaluate.py         → RF + XGB, LOSO, SHAP     → tune on v1, compare all,  → paper sections,
             │ Nov 1                                       FP/FN analysis             verify, SUBMIT
                                                             │ all scores Nov 11
```

---

## 3. Milestones

| ID | Date | Milestone | Owner | Done when |
|---|---|---|---|---|
| — | Thu Oct 29 | Kickoff done | All | Section 5 rules agreed and written in this file |
| M0 | Sat Oct 31 | **Setup complete** | Supriye (all) | Repo cloned by all 3; everyone's environment installs from `requirements.txt`; CERT r4.2 Parquet files on the shared drive |
| — | Sun Nov 1 | `evaluate.py` ready | Ayo | Merged to `main`; tested on synthetic scores |
| — | Mon Nov 2 | Split dates final | Supriye | Train/val/test boundaries written in Section 5.3 |
| M1 | Tue Nov 3 | **Feature table v0** | Supriye | `data/processed/features_v0.parquet` + `get_model_matrix()` shared; loads without errors in Arva's and Ayo's code |
| — | Fri Nov 6 | `explain.py` ready | Ayo | SHAP helper merged to `main` |
| M2 | Sun Nov 8 | **Feature table v1** | Supriye | `features_v1.parquet` + feature dictionary shared; leakage checks passed |
| — | Tue Nov 10 | Unsupervised scores + tuned model code | Arva (scores), Arva & Ayo (code) | `iforest`, `autoencoder` (+ `ocsvm`) score files in `results/scores/`; tuned settings committed so Supriye can run the ablation |
| M3 | Wed Nov 11 | **All score files final** | Arva, Ayo | All model score files incl. leave-one-scenario-out runs + timing numbers pushed; `evaluate.py` runs on every one |
| — | Sat Nov 14 | Analysis done | All | Comparison table, SHAP, ablation, FP/FN and case studies finished; results walkthrough held |
| M4 | Mon Nov 16 | **All paper sections drafted** | All | Every section in Section 11 is in Overleaf as a full draft (not bullet points) |
| M5 | Wed Nov 18 | **Full paper draft** | Supriye | One merged PDF circulated by 18:00; all figures and references in place |
| — | Thu Nov 19 | **Submission-ready** | All | Final fixes applied; code runs from a fresh clone |
| — | Fri Nov 20 | **Submission** | All | Paper and code submitted |

---

## 4. Meetings & Communication

| Meeting | When | Length | Agenda |
|---|---|---|---|
| Kickoff | Thu Oct 29 | 60 min | Walk through this file; agree on Section 5; confirm page limit and AI-use policy |
| Stand-up | Every Mon, Wed & Fri | 15 min | Each person: what I finished / what's next / what's blocking me |
| Features v1 walkthrough | Mon Nov 9 (with stand-up) | 30 min | Supriye explains every feature group and the feature dictionary |
| Results walkthrough | Sat Nov 14 | 45 min | Ayo presents the comparison table; Arva presents case studies; Supriye presents the ablation; agree on the answer to the research question |
| Final read-through | Thu Nov 19 | 60 min | Go through the paper page by page; assign and apply last fixes |

- Use **one group chat** for quick questions and **GitHub Issues** for bugs in someone else's code (assign the owner).
- Post every hand-off in the chat with the file path and Git commit, e.g. *"features_v1 pushed, commit a1b2c3d"*.

---

## 5. Team Rules (agree at kickoff)

These rules keep separately written code compatible and the results comparable. **Do not change a rule without telling the whole team.**

### 5.1 Feature table (produced by Supriye)
Path: `data/processed/features_v0.parquet` (sample) and `data/processed/features_v1.parquet` (full). One row = one **user-day**.

| Column | Type | Meaning |
|---|---|---|
| `user` | str | CERT user ID (e.g. `AAM0658`) |
| `date` | date | Calendar day |
| `split` | str | `train` / `val` / `test` (see 5.3) |
| `label` | int | 1 = at least one malicious event that day, 0 = normal |
| `scenario` | int | 0 = normal user-day; 1 / 2 / 3 = CERT insider scenario |
| `insider` | int | 1 if this user is an insider (any day), else 0 — for analysis only, **never a model input** |
| `role`, `department` | str | From LDAP for that month (peer groups and analysis only) |
| `f_*` | float | Raw behavioral features, **unscaled** (e.g. `f_logon_count`) |
| `z_user_*` | float | Deviation from the user's own past-30-day baseline (v1 only) |
| `z_peer_*` | float | Deviation from same-role peers on that day (v1 only) |
| `new_*` | int | Novelty flags, 0/1 (v1 only) |

**Model inputs are only the `f_*`, `z_user_*`, `z_peer_*` and `new_*` columns.** Never feed `user`, `date`, `split`, `label`, `scenario`, `insider`, `role` or `department` to a model.

### 5.2 Score files (produced by Arva and Ayo)
Path: `results/scores/<model>.parquet`, where `<model>` is one of `iforest`, `autoencoder`, `ocsvm`, `random_forest`, `xgboost`. Variants: contamination runs `iforest_contam` / `autoencoder_contam` (TEAM_PLAN 5.4); leave-one-scenario-out runs `<model>_loso_s<1|2|3>`.

| Column | Type | Meaning |
|---|---|---|
| `user`, `date` | — | Same keys as the feature table |
| `split`, `label`, `scenario` | — | Copied from the feature table |
| `score` | float | Raw model output, **higher = more suspicious** |

Score **every** row (train, val and test), not just test. Thresholds are chosen on `val` and reported on `test`.

### 5.3 Data split rule (temporal)
- CERT r4.2 covers roughly Jan 2010 – May 2011. Rows are split **by date**, never randomly shuffled.
- **Proposed default:** first ~60% of months = `train`, next ~15% = `val`, last ~25% = `test`.
- Supriye checks how the insiders are spread over time (task `S6`) and posts the **final boundary dates here by Mon Nov 2**. Each split must contain malicious days from **every** scenario. If a scenario has none in one split, move the boundary.
- Final boundaries (fill in on Nov 2): `train` = ______ to ______, `val` = ______ to ______, `test` = ______ to ______.

### 5.4 Training-data rule
- **Unsupervised models** (Isolation Forest, Autoencoder, One-Class SVM) train on `split == "train"` **and** `label == 0` only. Using labels to remove known-bad days is a simplification; it goes in the Limitations section. Arva also runs a variant trained on **all** train rows to show how much contamination hurts.
- **Supervised models** (Random Forest, XGBoost) train on all `split == "train"` rows.
- **Hyperparameters** are tuned on `val`. The `test` split is used **once**, for the final numbers.

### 5.5 Preprocessing rule
All models call the same helper so inputs are identical:
```python
from src.features import get_model_matrix
X_train, y_train, feature_names = get_model_matrix(df, split="train")
```
- `get_model_matrix()` (written by Supriye) selects the model-input columns, applies `log1p` to count features (`f_*`) and fills missing values with 0.
- Each model then fits `StandardScaler` on the **training rows only** and applies it to val/test (use a scikit-learn `Pipeline`).

### 5.6 Threshold rule
Every model is reported at **two** operating points so the comparison is fair:
1. **Best-F1 threshold:** the score threshold that maximizes F1 on `val`, applied unchanged to `test`.
2. **Fixed alert budget:** flag the top **1%** of `test` user-days (simulates "an analyst can review ~1% of activity").

ROC-AUC and PR-AUC need no threshold.

### 5.7 Reproducibility rule
- `random_state=42` / `seed=42` everywhere (NumPy, scikit-learn, XGBoost, PyTorch).
- Pin versions: after setup, Supriye runs `pip freeze > requirements.txt` and commits it.
- Every notebook must run **top to bottom** after "Restart & Run All" before it is merged.
- No hard-coded personal paths (`C:\Users\...`); use paths relative to the repo root.

### 5.8 Code ownership
| File | Owner |
|---|---|
| `src/data_loader.py`, `src/features.py`, `src/baseline.py`, `src/lanl_features.py` | Supriye |
| `src/synthetic.py`, `src/models_unsupervised.py`, `src/risk_scoring.py`, `src/pipeline.py`, `app/dashboard.py` | Arva |
| `src/models_supervised.py`, `src/evaluate.py`, `src/explain.py` | Ayo |
| `README.md`, `requirements.txt`, `paper/` (assembly) | Supriye |

Need a change in someone else's file? Open a GitHub Issue and assign the owner. Don't edit it directly.

### 5.9 Git workflow
1. `main` must always run. Never push broken code to `main`.
2. Work on a personal branch: `supriye/<topic>`, `arva/<topic>`, `ayo/<topic>`.
3. Merge through a **pull request**; one teammate skims it before merging.
4. **Never commit data** (`data/` and `results/scores/` are in `.gitignore`). Share large files through the team's shared drive and post the link in chat.
5. Commit small and often, with clear messages, e.g. `Add USB features to features.py`.

### 5.10 Feature-table freeze rule
After v1 (Sun Nov 8) the feature table is **frozen**. Only bugs that change results are fixed, released as `features_v1_1.parquet` **no later than Tue Nov 10, 12:00**, and announced in chat. After that, no feature changes.

---

## 6. Dataset Facts Everyone Should Know

### CERT Insider Threat Test Dataset r4.2 (primary)
- **Where:** Carnegie Mellon University KiltHub, "Insider Threat Test Dataset" (search the title on `kilthub.cmu.edu`). Download **`r4.2.tar.bz2`** and **`answers.tar.bz2`**.
- **Size:** several GB unpacked; `http.csv` is by far the largest. Recommended: ≥ 16 GB RAM, ≥ 40 GB free disk.
- **Scale:** ~1,000 users, ~17 months, ~70 malicious insiders across 3 scenarios (verify the exact counts in `answers/insiders.csv`).

| File | Typical columns (verify in the dataset readme) |
|---|---|
| `logon.csv` | `id, date, user, pc, activity` (Logon / Logoff) |
| `device.csv` | `id, date, user, pc, activity` (Connect / Disconnect) |
| `file.csv` | `id, date, user, pc, filename, content` (file copies to removable media) |
| `email.csv` | `id, date, user, pc, to, cc, bcc, from, size, attachments, content` |
| `http.csv` | `id, date, user, pc, url, content` |
| `psychometric.csv` | `employee_name, user_id, O, C, E, A, N` |
| `LDAP/YYYY-MM.csv` | `employee_name, user_id, email, role, business_unit, functional_unit, department, team, supervisor` |
| `answers/insiders.csv` | `dataset, scenario, details, user, start, end` |
| `answers/r4.2-<scenario>/…` | One file per insider listing their malicious log records |

**Scenarios in r4.2:**
1. A user who never worked after hours or used USB drives starts logging in after hours, using a USB drive and uploading data to `wikileaks.org`, then leaves the organization.
2. A user starts browsing job websites and contacting a competitor; before leaving, they copy data to USB drives at a much higher rate than before.
3. A disgruntled system administrator downloads a keylogger, uses a USB drive to put it on the supervisor's machine, then logs in as the supervisor to send an alarming mass email, and leaves.

**Important gap:** CERT `logon.csv` has **no failed logins**, so "authentication failures" (named in the assignment) cannot come from CERT. With the Nov 20 deadline, the default plan is to **state this gap clearly in Methodology and Limitations**, and use logon behavior on unusual PCs and at unusual times as the authentication signal. The LANL extension below is a **stretch goal**. At the Mon Nov 9 stand-up the team decides whether there is time for it.

### LANL Comprehensive Cyber-Security Events (stretch goal)
- **Where:** `csr.lanl.gov/data/cyber1/`. Each person who downloads it must read and accept the data-use terms themselves.
- **Files used:** `auth.txt.gz` (~1 billion authentication events with a **Success/Failure** field) and `redteam.txt.gz` (~750 known compromise events = labels).
- **Scope for this project:** a subset of the data (see task `S24`). This adds the authentication-failure and compromised-account angle that CERT lacks.

---

## 7. Literature

The assignment requires **≥ 5 recent papers** on UEBA / insider-threat / anomaly detection from **IEEE Xplore, Springer, Elsevier or ACM DL**. Our plan: 8 assigned topical papers + **1 paper from 2022–2026 per person** (a second one only if time allows) = 11+ papers. That covers both "≥ 5" and "recent".

### 7.1 Assigned topical papers (the literature review)
| ID | Paper | Venue | Topic | Reviewer |
|---|---|---|---|---|
| L1 | Glasser & Lindauer, "Bridging the Gap: A Pragmatic Approach to Generating Insider Threat Data" (2013) | IEEE Security & Privacy Workshops | How the CERT data was made | Supriye |
| L2 | Le, Zincir-Heywood & Heywood, "Analyzing Data Granularity Levels for Insider Threat Detection Using Machine Learning" (2020) | IEEE Trans. on Network and Service Management | Features & granularity on CERT | Supriye |
| L3 | Homoliak et al., "Insight into Insiders and IT: A Survey of Insider Threat Taxonomies, Analysis, Modeling, and Countermeasures" (2019) | ACM Computing Surveys | Insider-threat taxonomy | Supriye |
| L4 | Tuor et al., "Deep Learning for Unsupervised Insider Threat Detection in Structured Cybersecurity Data Streams" (2017) | AAAI Workshops | Unsupervised deep learning on CERT | Arva |
| L5 | Lu & Wong, "Insider Threat Detection with Long Short-Term Memory" (2019) | ACM ACSW | Sequence models | Arva |
| L6 | Liu, De Vel, Han, Zhang & Xiang, "Detecting and Preventing Cyber Insider Threats: A Survey" (2018) | IEEE Communications Surveys & Tutorials | Survey of approaches | Ayo |
| L7 | Yuan & Wu, "Deep Learning for Insider Threat Detection: Review, Challenges and Opportunities" (2021) | Computers & Security (Elsevier) | Survey; evaluation challenges | Ayo |
| L8 | Liu et al., "Log2vec: A Heterogeneous Graph Embedding Based Approach for Detecting Cyber Threats within Enterprise" (2019) | ACM CCS | Strong CERT result to compare | Ayo |
| L9a (L9b optional) | 2022–2026 paper(s): **insider-threat features / UEBA / compromised accounts** | IEEE / Springer / Elsevier / ACM | — | Supriye |
| L10a (L10b optional) | 2022–2026 paper(s): **unsupervised / autoencoder / sequence anomaly detection for insider threats** | IEEE / Springer / Elsevier / ACM | — | Arva |
| L11a (L11b optional) | 2022–2026 paper(s): **supervised / explainable (XAI) insider-threat detection** | IEEE / Springer / Elsevier / ACM | — | Ayo |

### 7.2 Method & supporting references (cite where used)
| Reference | Used for | Owner |
|---|---|---|
| Liu, Ting & Zhou, "Isolation Forest," IEEE ICDM (2008) | Isolation Forest | Arva |
| Schölkopf et al., "Estimating the Support of a High-Dimensional Distribution," Neural Computation (2001) | One-Class SVM | Arva |
| Chandola, Banerjee & Kumar, "Anomaly Detection: A Survey," ACM Computing Surveys (2009) | Anomaly-detection background | Arva |
| Breiman, "Random Forests," Machine Learning (Springer) (2001) | Random Forest | Ayo |
| Chen & Guestrin, "XGBoost: A Scalable Tree Boosting System," ACM KDD (2016) | XGBoost | Ayo |
| Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions," NeurIPS (2017) | SHAP | Ayo |
| Saito & Rehmsmeier, "The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets," PLoS ONE (2015) | Why PR matters | Ayo |
| Lindauer, "Insider Threat Test Dataset," Carnegie Mellon University (KiltHub) | CERT dataset citation | Supriye |
| Kent, "Comprehensive, Multi-Source Cyber-Security Events," Los Alamos National Laboratory (2015) | LANL dataset citation | Supriye |

### 7.3 How to find your 2022–2026 papers
1. Open L2 or L7 in **Google Scholar** → click **"Cited by"** → set **"Since 2022"**.
2. Or search IEEE Xplore / ACM DL / ScienceDirect / SpringerLink with: `insider threat detection`, `UEBA`, `user behavior anomaly detection`, `CERT insider threat dataset`, `compromised account detection`, `explainable insider threat`.
3. Keep a paper only if: (a) its publisher is IEEE, Springer, Elsevier or ACM, (b) it's from 2022–2026, (c) it runs experiments (preferably on CERT or LANL).
4. Access full text through the **StFX library** login if a paywall appears.
5. Post the title in chat before reading it so nobody picks the same paper.

### 7.4 Note template (one file per paper: `paper/lit_notes/<ID>.md`)
```
Citation (IEEE style):
Problem addressed:
Dataset (CERT version / LANL / other):
Granularity (event / session / day / week):
Features used:
Models used:
Evaluation metrics + key results (numbers):
Strengths:
Limitations / gaps:
How it relates to our project (1–2 sentences):
```
Add each paper to the shared **Zotero** group library as you read it.

---

## 8. Models

| Model | Type | Owner | Required? | Anomaly score |
|---|---|---|---|---|
| Isolation Forest | Unsupervised | Arva | **Required** | `-decision_function(X)` |
| Autoencoder (dense) | Unsupervised, deep | Arva | **Required** | Mean squared reconstruction error |
| Random Forest | Supervised | Ayo | **Required** | `predict_proba(X)[:, 1]` |
| XGBoost | Supervised | Ayo | **Required** | `predict_proba(X)[:, 1]` |
| One-Class SVM | Unsupervised | Arva | Optional | `-decision_function(X)` |
| LSTM | Sequence | — | **Not planned** (Future Work; cite L5) | — |

**Justification for the paper:** unsupervised models match real deployments, where labels are rare and attacks change. Supervised models show the best case when labels exist. Comparing both, especially on **unseen scenarios**, answers the research question.

---

## 9. Tools

| Tool | Purpose | Who |
|---|---|---|
| Python 3.11 | Language | All |
| Pandas, NumPy, PyArrow | Data processing, Parquet I/O | All |
| Scikit-learn | Isolation Forest, One-Class SVM, Random Forest, scaling, metrics | All |
| XGBoost | Gradient-boosted trees | Ayo |
| imbalanced-learn | SMOTE (training set only) | Ayo |
| PyTorch (CPU build) | Autoencoder. TensorFlow/Keras is fine if the team prefers; decide at kickoff | Arva |
| SHAP | Feature-level explanations | Ayo, Arva |
| Matplotlib, Seaborn | Figures | All |
| Jupyter Notebook | Experiments and analysis | All |
| Streamlit *(optional)* | Prototype dashboard | Arva |
| Git + GitHub | Version control, pull requests, issues | All |
| Overleaf (IEEE conference template) | Writing the paper together | All |
| Zotero (shared group library) | References, exported in IEEE style | All |

---

## 10. Evaluation Metrics

### 10.1 Definitions
TP = malicious user-day flagged, FP = normal user-day flagged, TN = normal not flagged, FN = malicious not flagged.

| Metric | Formula | What it tells us | Computed by |
|---|---|---|---|
| Accuracy | (TP + TN) / (TP + TN + FP + FN) | Reported but **misleading** under imbalance | `evaluate.py` |
| Precision | TP / (TP + FP) | Share of alerts that are real threats | `evaluate.py` |
| Recall (TPR) | TP / (TP + FN) | Share of real threats caught | `evaluate.py` |
| F1-score | 2 · P · R / (P + R) | Balance of precision and recall | `evaluate.py` |
| False Positive Rate | FP / (FP + TN) | Alert fatigue for analysts | `evaluate.py` |
| False Negative Rate | FN / (FN + TP) = 1 − Recall | Missed malicious activity | `evaluate.py` |
| ROC-AUC | Area under TPR vs. FPR curve | Threshold-free ranking quality | `evaluate.py` |
| **PR-AUC** (average precision) | Area under precision vs. recall curve | Ranking quality under heavy imbalance (**primary metric**) | `evaluate.py` |
| Confusion matrix | TP / FP / TN / FN counts | Error breakdown at a threshold | `evaluate.py` |
| Detection time (a): compute | Train time; inference time per 1,000 user-days | Can it run in practice? | Arva (unsupervised), Ayo (supervised) |
| Detection time (b): delay | Days from an insider's first malicious day to their first alert | How fast an insider is caught | `evaluate.py` |
| User-level recall | Insiders flagged on ≥ 1 malicious day / all test insiders | Did we catch the *person*? | `evaluate.py` |

### 10.2 Reporting protocol
For **every** model, report on the `test` split:
1. All metrics above at the **best-F1 threshold** and at the **top-1% alert budget** (Section 5.6).
2. ROC-AUC and PR-AUC.
3. The same metrics **per scenario** (1, 2, 3).
4. The **unseen-scenario** (leave-one-scenario-out) results — see [Ayo.md](Ayo.md), tasks `Y12` and `Y16`.

Why precision/recall matter (this paragraph must be in the paper): if ~0.1% of user-days are malicious, a model that always says "normal" scores **~99.9% accuracy with 0% recall**, so accuracy hides the failure completely. Use the real percentage from our data.

---

## 11. Paper Plan (IEEE conference format, ~8 pages — confirm the page limit with the instructor)

| Section | Writer | Target length | Draft due |
|---|---|---|---|
| Abstract | Supriye | ~200 words | Tue Nov 17 |
| I. Introduction | Supriye | 0.75 page | Fri Nov 13 |
| II. Related Work (+ comparison table) | Everyone writes their papers' paragraphs; Supriye merges | 1 page | Paragraphs by Fri Nov 13; merged Sat Nov 14 |
| III. Dataset | Supriye | 0.75 page | Tue Nov 10 |
| IV-A Preprocessing & Feature Engineering | Supriye | 0.75 page | Thu Nov 12 |
| IV-B Establishing Normal Behavior | Supriye | 0.5 page | Thu Nov 12 |
| IV-C Models — unsupervised / supervised | Arva / Ayo | 0.5 page each | Sun Nov 15 |
| IV-D Risk Scoring & UEBA Prototype | Arva | 0.5 page | Sun Nov 15 |
| V. Experiments & Results | Ayo | 1.25 pages | Sun Nov 15 |
| VI-A Feature Importance | Ayo | 0.5 page | Mon Nov 16 |
| VI-B Anomaly Case Studies | Arva | 0.75 page | Sun Nov 15 |
| VI-C False Positive / False Negative Analysis | Ayo | 0.5 page | Mon Nov 16 |
| VII. Limitations & Ethics | Supriye | 0.5 page | Fri Nov 13 |
| VIII. Conclusion & Future Work | Arva | 0.25 page | Mon Nov 16 |

### Figures & tables
| # | Figure / table | Owner |
|---|---|---|
| T1 | Literature comparison table | Supriye |
| T2 | Dataset summary & class imbalance | Supriye |
| T3 | Feature dictionary (condensed) | Supriye |
| T4 | Hyperparameters of all models | Arva, Ayo |
| T5 | Main model comparison (all metrics, both thresholds) | Ayo |
| T6 | Unseen-scenario (LOSO) results | Ayo |
| T7 | Feature-group ablation | Supriye |
| T8 | Timing / detection delay | Ayo (with Arva's timings) |
| F1 | Hourly activity: normal user vs. insider | Supriye |
| F2 | UEBA pipeline diagram | Arva |
| F3 | One user's baseline vs. a deviating day | Supriye |
| F4 | ROC and PR curves, all models | Ayo |
| F5 | Confusion matrices | Ayo |
| F6 | SHAP summary plot | Ayo |
| F7 | Case-study explanation plots (2–3) | Arva |
| F8 | Risk-score timeline for one insider | Arva |

---

## 12. Human-Only Work (no AI agents)

**First, check the course's AI-use policy at the kickoff and follow it.** If it's stricter than this list, the policy wins.

As a team, these stay **100% human**:
1. **Reading papers** and writing the literature notes and Related Work in your own words.
2. **Writing the paper.** The ideas, structure, sentences and conclusions are ours.
3. **Interpreting results**: what the numbers mean, and the answer to the research question.
4. **Explaining flagged anomalies**: why each case looks suspicious.
5. **Checking every citation**: it exists, the details are correct, and it says what we claim.
6. **Design decisions and their justification**: granularity, after-hours definition, split dates, thresholds, model choice.
7. **Understanding every line of submitted code.** Each person must be able to explain their own code without notes.
8. **Presenting / demoing** our own parts.

Each personal file lists extra human-only tasks for that role.

*If the policy allows it*, AI tools may be used for things like looking up library syntax, explaining an error message, or checking grammar. Whoever uses them stays responsible for verifying the output.

---

## 13. Risks & Fallback Plans

| Risk | Early sign | Fallback |
|---|---|---|
| CERT download is slow or fails | Not finished by Thu Oct 29 | Retry on campus network; download in parts; tell team immediately |
| `http.csv` too big for RAM | Memory errors | Read with `chunksize=1_000_000` and `usecols`; aggregate per chunk; keep only user-day counts |
| v1 features late | Not ready Sun Nov 8 | Arva and Ayo keep tuning on v0; Supriye ships v1 without `z_peer_*` first and adds them as v1.1 by Tue Nov 10, 12:00 |
| Paper writing squeezed at the end | Sections still bullet points on Sun Nov 15 | Write notes for your sections as you work (hyperparameters, decisions, numbers) so drafting is fast |
| Autoencoder won't train well | Validation loss flat or no separation | Smaller network, more epochs, check scaling; keep Isolation Forest + One-Class SVM as the unsupervised pair |
| A scenario has too few test insiders | Fewer than ~3 insiders in test | Report per-scenario results with that caveat; rely on LOSO for that scenario |
| Teammate unavailable (illness etc.) | Missed stand-up and hand-off | Their code and notes are on GitHub; the other two split the remaining tasks by priority (required > optional) |
| Running behind overall | M3 (Wed Nov 11) missed | Drop optional items first: One-Class SVM, dashboard, LANL extension, second recent paper. Never drop: 2 unsupervised + 2 supervised models, the LOSO experiment, FP/FN analysis, case studies |
