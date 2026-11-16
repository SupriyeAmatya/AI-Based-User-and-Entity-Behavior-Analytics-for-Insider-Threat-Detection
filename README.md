# AI-Based User and Entity Behavior Analytics (UEBA) for Insider Threat Detection

## Overview

This project builds and evaluates an AI/ML-based **User and Entity Behavior Analytics (UEBA)** prototype that learns what "normal" behavior looks like for each user and device, then flags significant deviations that may indicate:

- a **malicious insider** (e.g., data theft before leaving the company),
- a **compromised account** (e.g., an attacker using stolen credentials), or
- **unauthorized activity** (e.g., access to unusual resources at unusual times).

Each user-day (or user-session) gets an **anomaly/risk score**. Suspicious cases are investigated and explained using the behavioral features that contributed most to the score.

## Research Question

> *How effectively can AI/ML models detect anomalous user behavior associated with insider threats or compromised accounts, and which behavioral features and models provide the most reliable detection?*

## Objectives

1. Study insider threats, compromised accounts, behavioral anomalies, and UEBA approaches.
2. Select and preprocess a user-activity / insider-threat dataset.
3. Engineer behavioral features (login patterns, authentication failures, file/resource access, application/web usage, activity times, deviation from baseline).
4. Build a per-user (and peer-group) **baseline of normal behavior**.
5. Develop and compare **at least two** AI/ML models.
6. Assign a **risk/anomaly score** to suspicious behavior.
7. Analyze false positives, false negatives, and feature importance.
8. Evaluate detection of **previously unseen** anomalous behavior.

## Dataset

| Dataset | Description | Labels | Use in this project |
|---|---|---|---|
| **CERT Insider Threat Dataset (r4.2)** — *primary* | Synthetic enterprise logs: logon, device (USB), file, email, HTTP, LDAP, psychometric | Malicious insiders listed per scenario | Insider-threat detection |
| **LANL Comprehensive Cyber Security Events** — *stretch goal* | Real (de-identified) authentication, process, flow, DNS logs | Red-team compromise events | Compromised-account detection, authentication failures |

CERT has no failed-login records, so authentication failures are only available through LANL; see [TEAM_PLAN.md §6](Tasks/TEAM_PLAN.md#6-dataset-facts-everyone-should-know).

Raw data is **not** committed to this repository (it is several GB). See [TEAM_PLAN.md §6](Tasks/TEAM_PLAN.md#6-dataset-facts-everyone-should-know) for download links and where to place the files.

## Models

| Model | Type | Why |
|---|---|---|
| Isolation Forest | Unsupervised | Fast, scalable baseline for anomalies; needs no labels |
| Autoencoder | Unsupervised (deep) | Learns normal behavior; reconstruction error = anomaly score |
| Random Forest / XGBoost | Supervised | Upper-bound comparison; gives feature importance |
| *(optional)* One-Class SVM | Unsupervised | Extra comparison if time allows |

## Evaluation Metrics

Accuracy, Precision, Recall, F1-score, False Positive Rate (FPR), False Negative Rate (FNR), ROC-AUC, **PR-AUC**, Confusion Matrix, and detection time.

Because malicious activity is a tiny fraction of the data, **accuracy is misleading** — a model that labels everything "normal" can score above 99%. Precision (how many alerts are real) and recall (how many threats are caught) are the metrics that matter for a security team.

## Project Structure

```
.
├── README.md                 # This file
├── CLAUDE.md                 # Guidance for Claude Code sessions in this repo
├── Guide/
│   └── PROJECT_GUIDE.md      # Step-by-step guide for completing the project
├── Tasks/
│   ├── TEAM_PLAN.md          # Work split, milestones, file formats, literature/models/tools/metrics
│   ├── PROGRESS.md           # Progress tracker: every task, meeting, hand-off and PR
│   ├── Supriye.md            # Supriye's tasks and timeline (data, features, paper assembly)
│   ├── Arva.md               # Arva's tasks and timeline (unsupervised models, risk scoring, prototype)
│   └── Ayo.md                # Ayo's tasks and timeline (supervised models, evaluation, explainability)
├── docs/
│   ├── coverage.md           # Assignment requirements vs. status (dated snapshot)
│   └── feature_dictionary.md # Every v1 column: definition, unit, why it matters (S20)
├── requirements.txt          # Python dependencies (pinned, Python 3.13)
├── scripts/
│   ├── download_cert.sh      # Download CERT r4.2 + answers (resumable, checksum-verified)
│   ├── rebuild_data.sh       # Labels, v0, v1, notebooks 01-02, tests, final check (S20b)
│   ├── data_drop.py          # Build / verify the one data drop ueba_data_v1.zip (S4/S20)
│   └── readme_results.py     # Writes the Results table below from model_comparison.csv (S33)
├── data/                     # Not committed; share through the team drive
│   ├── raw/                  # CERT archives, extracted LDAP/psychometric files and answers
│   ├── parquet/              # The five logs as Parquet + manifest.json
│   └── processed/            # labels.parquet, features_v0.parquet, features_v1.parquet
├── notebooks/
│   ├── 01_eda.ipynb          # Done (S7)
│   ├── 02_feature_engineering.ipynb  # Done (S17–S19): F3 + validation checks
│   ├── 03a_unsupervised_models.ipynb # Done on v0 (A9–A10): tuning log
│   ├── 03b_supervised_models.ipynb   # Done on v0 (Y8–Y10): tuning log, imbalance
│   ├── 04_evaluation.ipynb
│   └── 05_anomaly_investigation.ipynb
├── src/
│   ├── config.py             # Paths, seed, the S8 decisions (final Nov 6) (done)
│   ├── data_loader.py        # Convert the archive; load and clean logs   (done)
│   ├── labels.py             # Ground-truth labels, split check           (done)
│   ├── features.py           # Feature tables v0/v1 + get_model_matrix()  (done)
│   ├── synthetic.py          # Synthetic feature table for testing        (done)
│   ├── evaluate.py           # Metrics, plots, detection delay            (done)
│   ├── baseline.py           # Per-user / peer-group baselines, new_* flags (done)
│   ├── ablation.py           # Feature-group ablation (T7) + data time (T8) (code done)
│   ├── models_unsupervised.py# Isolation Forest, Autoencoder (+ tuning)    (done)
│   ├── models_supervised.py  # Random Forest, XGBoost (+ tuning, imbalance) (done)
│   ├── risk_scoring.py       # Convert model output to a 0–100 risk score (done)
│   ├── explain.py            # SHAP explanations                         (done)
│   └── pipeline.py           # End-to-end UEBA prototype                 (done)
├── tests/                    # pytest: python -m pytest tests
├── app/
│   └── dashboard.py          # Optional Streamlit dashboard
├── results/
│   ├── scores/               # One score file per model (not committed)
│   ├── figures/              # ROC/PR curves, confusion matrices, SHAP plots
│   └── tables/               # Metric tables for the paper
└── paper/                    # Research paper (IEEE format) and references
```

## Getting Started

Use **Python 3.13**. On Windows, create the environment at a short path **outside** the project folder. If the project's folder path is long, Jupyter's install fails on the 260-character Windows path limit.

```bash
python -m venv %USERPROFILE%\.venvs\ueba
```

```bash
%USERPROFILE%\.venvs\ueba\Scripts\activate
```

(On macOS/Linux: `python3 -m venv ~/.venvs/ueba`, then `source ~/.venvs/ueba/bin/activate`.)

```bash
pip install -r requirements.txt
```

Run everything from the repo root with that environment active, e.g. `python -m pytest tests`.

**Data (not in Git):** `bash scripts/download_cert.sh` downloads CERT r4.2 (4.8 GB, resumable), and `python -m src.data_loader convert` converts it to Parquet. Or copy `data/` from the team's shared drive.

```bash
jupyter notebook
```

Then run the notebooks in order (`01` → `05`).

## Run the prototype

The prototype goes from the frozen feature table to a ranked list of the riskiest users in the test period, each with the three features that made their riskiest day stand out. Set up the environment as in Getting Started first.

1. **Get the data.** Unzip `ueba_data_v1.zip` from the team drive in the repo root, then check it:

   ```bash
   python scripts/data_drop.py verify
   ```

2. **Run the pipeline** (Isolation Forest, top 20 users of the test period):

   ```bash
   python src/pipeline.py
   ```

   The first run trains the model and saves it in `models/`; later runs load it. The table is printed and saved to `results/tables/top_risky_users.csv`. A saved model is reused whenever its feature columns match, so after the detector defaults change (as with the tuning in #50), run once with `--retrain` or delete `models/`.

3. **Options:**
   - `--model autoencoder` (or `ocsvm`) ranks with another detector;
   - `--date 2011-03-22` ranks users by their risk over the 7 days ending that day, instead of the whole test period;
   - `--top 50` lists more users, and `--retrain` ignores a saved model;
   - `--features data/processed/features_v0.parquet` runs on the 100-user sample.

**Reading the table** (one row per user):
- `peak_date`, `peak_risk`: the user's riskiest day and its daily risk. Daily risk (0–100) is the percentile of that day's score among the normal training days.
- `high_days`, `medium_days`: test days at the High level, and at Medium but below High (levels in `src/risk_scoring.py`).
- `active_days`: test days with activity. `first_alert`: the first day at Medium or above.
- `alert_level`: High, Medium or Low, from `peak_risk`.
- `reasons`: the three features that contributed most on `peak_date`, e.g. "24 files copied; 9 USB connects; 1 after-hours logons".
- With `--date`, the table has `user_risk` (the highest daily risk in the 7 days ending that day), `active_days` (days with activity in that window), `last_active`, `alert_level` (from `user_risk`) and `reasons` (for the riskiest day in the window) instead.

The table holds no labels, as an analyst would see it. To rebuild every score file for the evaluation (not needed for the pipeline):

```bash
python -m src.models_unsupervised final   # iforest, autoencoder, the two _contam variants, ocsvm
python -m src.models_supervised final     # random_forest, xgboost
python -m src.evaluate report             # T5 and the other result tables
```

## Results

Model comparison on the **test** split (Feb 1 – May 17, 2011: 65,007 user-days, 170 malicious, on 15 accounts: 14 insiders and the hijacked supervisor account `FBA0348`), from `results/tables/model_comparison.csv` (T5). The numbers come from the results machine (TEAM_PLAN 2.5.12); rebuild them with the two `final` commands and `python -m src.evaluate report`.

- **Operating points:** *best-F1* uses the threshold that maximises F1 on the validation split, applied unchanged to test; *top 1%* flags the 1% highest-scoring test user-days (651).
- **Columns:** FPR and FNR are the false-positive and false-negative rates; *user recall* is the share of those 15 accounts flagged on at least one malicious day; *median delay* is the days from an account's first malicious test day to its first alert.
- **"All train rows":** the `_contam` variants train on every train row, malicious ones included; the other unsupervised models train on normal rows only.
- **More results:** per scenario `model_per_scenario.csv`, unseen scenarios `loso.csv` (T6), feature groups `ablation.csv` (T7), timing `T8_timing.csv` (T8), feature importance `feature_importance.csv` (F6).

<!-- results:start (generated by scripts/readme_results.py from model_comparison.csv) -->
| Model | Operating point | Precision | Recall | F1 | FPR | FNR | ROC-AUC | PR-AUC | User recall | Median delay (days) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Isolation Forest | best-F1 | 0.012 | 0.524 | 0.023 | 0.1159 | 0.476 | 0.879 | 0.012 | 0.933 | 0.0 |
| Isolation Forest | top 1% | 0.014 | 0.053 | 0.022 | 0.0099 | 0.947 | 0.879 | 0.012 | 0.267 | 2.0 |
| Autoencoder | best-F1 | 0.072 | 0.165 | 0.100 | 0.0056 | 0.835 | 0.916 | 0.093 | 0.667 | 0.0 |
| Autoencoder | top 1% | 0.048 | 0.182 | 0.076 | 0.0096 | 0.818 | 0.916 | 0.093 | 0.733 | 0.0 |
| One-Class SVM | best-F1 | 0.818 | 0.053 | 0.099 | 0.0000 | 0.947 | 0.741 | 0.057 | 0.400 | 0.0 |
| One-Class SVM | top 1% | 0.038 | 0.147 | 0.061 | 0.0097 | 0.853 | 0.741 | 0.057 | 0.667 | 0.0 |
| Isolation Forest, all train rows | best-F1 | 0.011 | 0.712 | 0.021 | 0.1712 | 0.288 | 0.861 | 0.010 | 1.000 | 0.0 |
| Isolation Forest, all train rows | top 1% | 0.014 | 0.053 | 0.022 | 0.0099 | 0.947 | 0.861 | 0.010 | 0.200 | 3.0 |
| Autoencoder, all train rows | best-F1 | 0.102 | 0.059 | 0.075 | 0.0014 | 0.941 | 0.902 | 0.041 | 0.467 | 0.0 |
| Autoencoder, all train rows | top 1% | 0.034 | 0.129 | 0.054 | 0.0097 | 0.871 | 0.902 | 0.041 | 0.733 | 0.0 |
| Random Forest | best-F1 | 0.937 | 0.876 | 0.906 | 0.0002 | 0.124 | 1.000 | 0.966 | 0.933 | 0.0 |
| Random Forest | top 1% | 0.261 | 1.000 | 0.414 | 0.0074 | 0.000 | 1.000 | 0.966 | 1.000 | 0.0 |
| XGBoost | best-F1 | 0.964 | 0.959 | 0.962 | 0.0001 | 0.041 | 1.000 | 0.988 | 1.000 | 0.0 |
| XGBoost | top 1% | 0.260 | 0.994 | 0.412 | 0.0074 | 0.006 | 1.000 | 0.988 | 1.000 | 0.0 |
<!-- results:end -->

## Deliverables

- [ ] Working UEBA prototype (code + notebooks)
- [ ] Research paper: dataset, feature engineering, models, experiments, results, limitations
- [ ] Analysis of selected detected anomalies with explanations
- [ ] Literature review (≥ 5 recent papers)

## Tools

Python, Pandas, NumPy, PyArrow, Scikit-learn, XGBoost, imbalanced-learn, PyTorch, SHAP, Matplotlib/Seaborn, Jupyter Notebook, Streamlit (optional).
