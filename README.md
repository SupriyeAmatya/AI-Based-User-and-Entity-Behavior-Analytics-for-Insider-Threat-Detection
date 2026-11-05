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
│   └── feature_dictionary.md # (S20, to come) every feature, its definition and why it matters
├── requirements.txt          # Python dependencies (pinned, Python 3.13)
├── scripts/
│   └── download_cert.sh      # Download CERT r4.2 + answers (resumable, checksum-verified)
├── data/                     # Not committed; share through the team drive
│   ├── raw/                  # CERT archives, extracted LDAP/psychometric files and answers
│   ├── parquet/              # The five logs as Parquet + manifest.json
│   └── processed/            # labels.parquet, features_v0.parquet, features_v1.parquet
├── notebooks/
│   ├── 01_eda.ipynb          # Done (S7)
│   ├── 02_feature_engineering.ipynb
│   ├── 03a_unsupervised_models.ipynb
│   ├── 03b_supervised_models.ipynb   # Done on v0 (Y8–Y10): tuning log, imbalance
│   ├── 04_evaluation.ipynb
│   └── 05_anomaly_investigation.ipynb
├── src/
│   ├── config.py             # Paths, seed, PROVISIONAL decisions        (done)
│   ├── data_loader.py        # Convert the archive; load and clean logs   (done)
│   ├── labels.py             # Ground-truth labels, split check           (done)
│   ├── features.py           # Feature table + get_model_matrix()         (v0 done)
│   ├── synthetic.py          # Synthetic feature table for testing        (done)
│   ├── evaluate.py           # Metrics, plots, detection delay            (done)
│   ├── baseline.py           # Per-user / peer-group baselines
│   ├── models_unsupervised.py# Isolation Forest, Autoencoder, One-Class SVM
│   ├── models_supervised.py  # Random Forest, XGBoost (+ tuning, imbalance) (done)
│   ├── risk_scoring.py       # Convert model output to a 0–100 risk score
│   ├── explain.py            # SHAP explanations                         (done)
│   └── pipeline.py           # End-to-end UEBA prototype
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

## Results

*To be completed after experiments.* Summary table of models vs. Precision / Recall / F1 / FPR / FNR / ROC-AUC / PR-AUC / detection time will go here.

## Deliverables

- [ ] Working UEBA prototype (code + notebooks)
- [ ] Research paper: dataset, feature engineering, models, experiments, results, limitations
- [ ] Analysis of selected detected anomalies with explanations
- [ ] Literature review (≥ 5 recent papers)

## Tools

Python, Pandas, NumPy, PyArrow, Scikit-learn, XGBoost, imbalanced-learn, PyTorch, SHAP, Matplotlib/Seaborn, Jupyter Notebook, Streamlit (optional).
