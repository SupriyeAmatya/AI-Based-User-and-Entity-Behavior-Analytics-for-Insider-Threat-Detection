# AI-Based User and Entity Behavior Analytics (UEBA) for Insider Threat Detection

**Course:** CSCI 561 – Computer Network and Security
**Topic 7:** AI-Based User and Entity Behavior Analytics for Insider Threat Detection
**Team:** Supriye, Arva, Ayo — **Submission:** Friday, November 20, 2026

| Planning document | What it contains |
|---|---|
| [TEAM_PLAN.md](TEAM_PLAN.md) | Work split, milestones, team rules, literature, models, tools, metrics, paper plan |
| [Supriye.md](Supriye.md) / [Arva.md](Arva.md) / [Ayo.md](Ayo.md) | Each person's day-by-day tasks with step-by-step instructions |
| [PROJECT_GUIDE.md](PROJECT_GUIDE.md) | Background and methodology guide for the whole project |

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

CERT has no failed-login records, so authentication failures are only available through LANL; see [TEAM_PLAN.md §6](TEAM_PLAN.md#6-dataset-facts-everyone-should-know).

Raw data is **not** committed to this repository (it is several GB). See [TEAM_PLAN.md §6](TEAM_PLAN.md#6-dataset-facts-everyone-should-know) for download links and where to place the files.

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
├── PROJECT_GUIDE.md          # Step-by-step guide for completing the project
├── TEAM_PLAN.md              # Work split, milestones, file formats, literature/models/tools/metrics
├── Supriye.md                # Supriye's tasks and timeline (data, features, paper assembly)
├── Arva.md                   # Arva's tasks and timeline (unsupervised models, risk scoring, prototype)
├── Ayo.md                    # Ayo's tasks and timeline (supervised models, evaluation, explainability)
├── requirements.txt          # Python dependencies
├── data/
│   ├── raw/                  # Original CERT / LANL files (not committed)
│   └── processed/            # Cleaned data and feature tables
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03a_unsupervised_models.ipynb
│   ├── 03b_supervised_models.ipynb
│   ├── 04_evaluation.ipynb
│   └── 05_anomaly_investigation.ipynb
├── src/
│   ├── data_loader.py        # Load and clean raw logs
│   ├── features.py           # Behavioral feature extraction
│   ├── baseline.py           # Per-user / peer-group baselines
│   ├── models_unsupervised.py# Isolation Forest, Autoencoder, One-Class SVM
│   ├── models_supervised.py  # Random Forest, XGBoost
│   ├── risk_scoring.py       # Convert model output to a 0–100 risk score
│   ├── evaluate.py           # Metrics, plots, detection delay
│   ├── explain.py            # SHAP explanations
│   └── pipeline.py           # End-to-end UEBA prototype
├── app/
│   └── dashboard.py          # Optional Streamlit dashboard
├── results/
│   ├── scores/               # One score file per model
│   ├── figures/              # ROC/PR curves, confusion matrices, SHAP plots
│   └── tables/               # Metric tables for the paper
└── paper/                    # Research paper (IEEE format) and references
```

## Getting Started

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

(On macOS/Linux, activate with `source .venv/bin/activate` instead.)

```bash
pip install -r requirements.txt
```

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
