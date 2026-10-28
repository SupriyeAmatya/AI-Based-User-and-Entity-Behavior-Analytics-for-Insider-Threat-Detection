# Project Guide — AI-Based UEBA for Insider Threat Detection

A step-by-step plan for completing Topic 7, from research to final paper. Each phase lists **what to do**, **how to do it**, and **what to produce**. Tick the checkboxes as you go.

---

## Phase 0 — Understand the Requirements

The assignment is graded on two deliverables:

1. **A working UEBA prototype** that:
   1. establishes normal user behavior,
   2. extracts behavioral features from activity data,
   3. applies and compares at least two AI/ML models,
   4. assigns a risk/anomaly score to suspicious behavior,
   5. investigates examples of detected anomalies,
   6. compares model performance and analyzes FPs, FNs and limitations.
2. **A scientific research paper** covering dataset, feature engineering, models, experiments, results, limitations, and an analysis of selected anomalies explaining *why* they were flagged.

Keep the research question in front of you the whole time — every experiment should help answer it:

> *How effectively can AI/ML models detect anomalous user behavior associated with insider threats or compromised accounts, and which behavioral features and models provide the most reliable detection?*

---

## Phase 1 — Background Study & Literature Review

### What to learn

| Concept | Key points |
|---|---|
| **Insider threat** | Malicious insiders (data theft, sabotage, fraud), negligent insiders, and compromised insiders |
| **Compromised account** | Legitimate credentials used by an attacker; behavior suddenly differs from the real owner |
| **Behavioral anomaly** | A deviation from a user's own history (*individual baseline*) or from similar users (*peer group*) |
| **UEBA** | Profiles users *and* entities (hosts, devices, servers), scores risk, prioritizes alerts for analysts |
| **Class imbalance** | Malicious events are often < 0.1% of data — drives metric choice and model design |

### Literature review (≥ 5 papers from IEEE Xplore, Springer, Elsevier, or ACM DL)

Starting points (verify each citation yourself, then look for 2022–2026 papers that cite them):

- Glasser & Lindauer, "Bridging the Gap: A Pragmatic Approach to Generating Insider Threat Data," *IEEE Security and Privacy Workshops*, 2013. — origin of the CERT dataset.
- Liu, De Vel, Han, Zhang & Xiang, "Detecting and Preventing Cyber Insider Threats: A Survey," *IEEE Communications Surveys & Tutorials*, 2018.
- Le, Zincir-Heywood & Heywood, "Analyzing Data Granularity Levels for Insider Threat Detection Using Machine Learning," *IEEE Transactions on Network and Service Management*, 2020.
- Yuan & Wu, "Deep Learning for Insider Threat Detection: Review, Challenges and Opportunities," *Computers & Security* (Elsevier), 2021.
- Liu et al., "Log2vec: A Heterogeneous Graph Embedding Based Approach for Detecting Cyber Threats within Enterprise," *ACM CCS*, 2019.
- Kent, "Comprehensive, Multi-Source Cyber-Security Events," Los Alamos National Laboratory, 2015. — origin of the LANL dataset.

Search terms: `insider threat detection machine learning`, `UEBA anomaly detection`, `CERT insider threat dataset`, `compromised account detection authentication logs`, `autoencoder insider threat`, `LSTM user behavior anomaly`.

### For each paper, record

| Field | Notes |
|---|---|
| Citation | Authors, title, venue, year |
| Dataset | CERT version / LANL / other |
| Features | What behavioral features were used |
| Models | Which algorithms |
| Results | Key metrics |
| Limitations | What they couldn't do — this is where *your* project can add value |

### Produce
- [ ] Literature summary table (goes into the paper's Related Work section)
- [ ] 1–2 paragraphs identifying the gap your project addresses

---

## Phase 2 — Dataset Selection & Setup

### Recommended: CERT Insider Threat Dataset r4.2

- **Download:** Carnegie Mellon University KiltHub — search "CERT Insider Threat Test Dataset".
- **Why r4.2:** ~1,000 users over ~17 months with ~70 malicious insiders, the most insiders of any release, so you have enough positive examples to evaluate on. (r5.2 / r6.2 are larger but have fewer insiders per user.)
- **Files:**

| File | Contents |
|---|---|
| `logon.csv` | Logon / logoff events per user and PC |
| `device.csv` | USB / removable drive connect & disconnect |
| `file.csv` | File copies to removable media |
| `email.csv` | Sender, recipients, size, attachments |
| `http.csv` | Websites visited (**very large** — read in chunks) |
| `psychometric.csv` | Big-Five (OCEAN) personality scores |
| `LDAP/` | Monthly employee roster: role, department, supervisor |
| `answers/` | Ground truth — which users are insiders, in which scenario, on which dates |

- **Insider scenarios in r4.2** (useful for the "unseen anomaly" experiment):
  1. User starts logging in after hours, uses a USB drive, uploads data to wikileaks.org, then leaves.
  2. User browses job sites and contacts a competitor; before leaving, copies data to USB at a much higher rate.
  3. Disgruntled sysadmin installs a keylogger, steals the supervisor's credentials, logs in as them, sends a mass email, then leaves.

> **Note:** CERT `logon.csv` contains **no failed logins**, so "authentication failures" can't come from CERT. Either use LANL (below), or state the gap in the paper and use logons on unusual PCs or at unusual times as the authentication-behavior signal.

### Stretch goal: LANL Cyber Security Dataset (for compromised accounts and auth failures)
- **Download:** `csr.lanl.gov/data/cyber1/` (accept the data-use terms yourself).
- Use `auth.txt` (authentication events, with a Success/Failure field) + `redteam.txt` (known compromise events).
- `auth.txt` has ~1 billion rows — work on a time window or a subset of users.

### Setup tasks
- [ ] Create the folder structure from `README.md`
- [ ] Place raw files in `data/raw/` (add `data/` to `.gitignore`)
- [ ] Create a virtual environment and `requirements.txt`:
  ```
  pandas
  numpy
  scikit-learn
  xgboost
  imbalanced-learn  # SMOTE (training set only)
  torch             # or tensorflow
  shap
  matplotlib
  seaborn
  jupyter
  pyarrow           # for fast parquet I/O
  ```

---

## Phase 3 — Exploratory Data Analysis (`notebooks/01_eda.ipynb`)

- [ ] Load each log file; check row counts, date ranges, missing values, duplicates
- [ ] Parse timestamps into `datetime`
- [ ] Plot activity by hour of day and day of week (shows "normal working hours")
- [ ] Count events per user — look for very active / very quiet users
- [ ] Load the `answers/` folder and mark malicious events / user-days
- [ ] Report the **class imbalance**: % of malicious user-days vs. normal
- [ ] Plot a timeline for 2–3 known insiders vs. a normal user (great figure for the paper)

**Tip:** Convert the big CSVs to Parquet once, then always load Parquet — it is much faster.

---

## Phase 4 — Feature Engineering (`src/features.py`)

### 4.1 Choose a granularity
Aggregate raw events into one row per **user-day** (recommended). Alternatives: user-week (smoother, fewer rows) or user-session (finer, harder). Justify your choice in the paper.

### 4.2 Raw behavioral features (per user-day)

| Category | Example features |
|---|---|
| **Login patterns** | # logons, # logoffs, first logon hour, last logoff hour, session duration, # distinct PCs, logons on a PC that isn't the user's usual PC |
| **Activity time** | # events after hours (e.g., before 8:00 / after 18:00), weekend activity flag |
| **Removable media** | # USB connects, # USB connects after hours, # files copied to removable media, # `.exe` / `.zip` / `.doc` files copied |
| **Email** | # emails sent, # external recipients, # attachments, total attachment size, # emails to non-company domains |
| **Web / application usage** | # HTTP requests, # visits to job-search sites, # visits to cloud-storage / leak sites (e.g., wikileaks, dropbox), # keylogger-related URLs |
| **Authentication** *(LANL)* | # auth failures, # distinct destination hosts, # first-time host accesses, ratio of failed/total, unusual auth type |
| **Context** *(LDAP / psychometric)* | Role, department (for peer groups), OCEAN scores (optional). **Don't** use "days until leaving the organization": it relies on future information, so it's data leakage |

### 4.3 Deviation-from-normal features (this is the "UEBA" part)
For each raw feature `x` on day `d`:

- **Individual baseline:** compare to the same user's previous N days (e.g., 30)
  - `z_user = (x_d − mean_user_last30) / (std_user_last30 + ε)`
- **Peer-group baseline:** compare to users with the same role/department on the same day
  - `z_peer = (x_d − mean_peers_d) / (std_peers_d + ε)`
- **Novelty flags:** first time ever using a USB drive, first time on this PC, first time on this domain

Use **only past data** to compute baselines — never future days (that is data leakage).

### Produce
- [ ] `data/processed/features_user_day.parquet`
- [ ] A feature dictionary table (name, description, category) for the paper

---

## Phase 5 — Establish Normal Behavior (`src/baseline.py`)

- [ ] Pick a **training period** (e.g., the first 6 months) and keep only days with **no** malicious activity — this is your "normal" reference
- [ ] Save per-user and per-peer-group baseline statistics (mean, std, percentiles)
- [ ] Visualize one user's baseline vs. a day that deviates (good for the paper)

---

## Phase 6 — Model Development (`src/models_unsupervised.py`, `src/models_supervised.py`)

Compare **at least two** models. A strong design compares one unsupervised and one supervised approach:

| Model | Type | Train on | Anomaly score |
|---|---|---|---|
| **Isolation Forest** | Unsupervised | Normal training days only | `-decision_function()` |
| **Autoencoder** | Unsupervised (deep) | Normal training days only | Reconstruction error (MSE) |
| **Random Forest / XGBoost** | Supervised | Labeled training days | Predicted probability of malicious |
| *(optional)* One-Class SVM | Unsupervised | Normal only (subsample — it scales poorly) | `-decision_function()` |
| *(future work)* LSTM | Sequence | Sequences of user-days | Prediction / reconstruction error |

**Justify your choice** in the paper: unsupervised models match the real world (labels are rare and attacks change), supervised models show the best-case performance when labels exist.

### Data splitting — avoid leakage
- [ ] **Temporal split:** train on earlier months, validate on the next months, test on the last months (never randomly shuffle across time). Each split must contain malicious days from every scenario. Exact rule: [TEAM_PLAN.md §5.3](TEAM_PLAN.md#53-data-split-rule-temporal)
- [ ] For the **unseen-anomaly** test, hold out all users of one scenario from training entirely (leave-one-scenario-out), so the model can't memorize those users
- [ ] Scale features with `StandardScaler` fit on **training data only**
- [ ] For supervised models, handle imbalance with `class_weight='balanced'` / `scale_pos_weight`, or SMOTE on the **training set only**
- [ ] Tune hyperparameters on a validation set, not the test set

---

## Phase 7 — Risk Scoring (`src/risk_scoring.py`)

- [ ] Normalize each model's raw score to **0–100** (e.g., percentile rank against training scores)
- [ ] Aggregate per user over time, e.g. a rolling 7-day max or exponentially decayed sum, so repeated suspicious days raise risk
- [ ] Define alert levels on the percentile scale: e.g., Low < 95, Medium 95–99, High ≥ 99 (top 1% of normal behavior)
- [ ] Choose an alert threshold — e.g., top 1% of scores, or the threshold giving a target recall
- [ ] Output a **ranked list of riskiest users** (what an analyst would see)

---

## Phase 8 — Evaluation (`src/evaluate.py`, `notebooks/04_evaluation.ipynb`)

### Metrics to report for every model

| Metric | Formula / meaning |
|---|---|
| Accuracy | (TP + TN) / all — **misleading on imbalanced data** |
| Precision | TP / (TP + FP) — "of the alerts, how many were real?" |
| Recall (TPR) | TP / (TP + FN) — "of the real threats, how many did we catch?" |
| F1-score | Harmonic mean of precision and recall |
| FPR | FP / (FP + TN) — drives analyst alert fatigue |
| FNR | FN / (FN + TP) — missed insiders |
| ROC-AUC | Threshold-independent ranking quality |
| **PR-AUC** | Better than ROC-AUC under heavy imbalance — include it |
| Confusion matrix | At your chosen threshold |
| Detection time | (a) Inference time per 1,000 user-days; (b) days between an insider's first malicious action and the first alert |

### Explain *why* precision/recall matter (required in the paper)
If 0.1% of user-days are malicious, predicting "normal" always gives **99.9% accuracy and 0% recall**. Security teams care about catching threats (recall) without flooding analysts with false alarms (precision / FPR). Show this with a concrete number from your data.

### Detecting previously unseen anomalies (required)
- [ ] **Leave-one-scenario-out:** train the supervised model on scenarios 1 & 2, test on scenario 3 (repeat for each). Compare with unsupervised models, which never see labels. Expect supervised models to drop sharply here — that is a key finding.
- [ ] **Temporal hold-out:** test on later months containing insiders not seen in training.
- [ ] *(optional)* **Cross-dataset:** apply the approach to LANL red-team events.

### Plots
- [ ] ROC and Precision-Recall curves (all models on one plot)
- [ ] Confusion matrices
- [ ] Score distributions: normal vs. malicious
- [ ] Bar chart comparing all metrics across models

---

## Phase 9 — Explainability & Error Analysis (`notebooks/05_anomaly_investigation.ipynb`)

### Feature importance
- [ ] Tree models: built-in importance + **SHAP** summary plot
- [ ] Autoencoder: per-feature reconstruction error (which features couldn't be reconstructed)
- [ ] Isolation Forest: SHAP (`TreeExplainer` supports it) or per-feature z-scores
- [ ] Answer: **which behavioral features contribute most to detection?** Do the models agree?

### Investigate detected anomalies (the paper must include these)
Pick **3–5 flagged cases** — mix of true positives and false positives. For each:
- [ ] Show the user's normal baseline vs. the flagged day
- [ ] List the top contributing features (SHAP waterfall or z-scores)
- [ ] Map it to the scenario story — e.g., "First-ever USB use at 11 pm, 40 files copied, wikileaks visit → matches Scenario 1"

### False positive analysis
- [ ] What do FP users have in common? (e.g., IT staff who legitimately work late, new employees with no baseline)
- [ ] How could they be reduced? (peer-group baselines, role-based allow-lists, longer baselines)

### False negative analysis
- [ ] Which insiders were missed and why? (e.g., malicious behavior too similar to normal, too short, or the user had always been "noisy")

---

## Phase 10 — The UEBA Prototype

Package the pipeline so it runs end-to-end:

```
raw logs → clean → features → baseline deviation → model scores → risk score → ranked alerts + explanations
```

- [ ] A single script or notebook that runs the full pipeline
- [ ] Output: CSV/table of top-N risky users with score, alert level, and top-3 reasons
- [ ] *(optional, nice for the demo)* A simple dashboard (Streamlit or a notebook with widgets) showing a user's risk timeline and explanations

---

## Phase 11 — Research Paper

Use **IEEE conference format** (two-column, ~6–10 pages; check with the instructor).

| Section | Content |
|---|---|
| **Abstract** | Problem, approach, dataset, best model, key numbers (≈ 200 words) |
| **I. Introduction** | Insider-threat problem, why UEBA, research question, contributions |
| **II. Background & Related Work** | Insider threats, compromised accounts, UEBA; literature table (≥ 5 papers) |
| **III. Dataset** | CERT (and LANL) description, scenarios, class imbalance, preprocessing |
| **IV. Methodology** | Granularity, feature engineering, baselines, models + justification, risk scoring, splits |
| **V. Experiments & Results** | Metric tables, ROC/PR curves, confusion matrices, detection time, unseen-scenario results |
| **VI. Discussion** | Feature importance, anomaly case studies, FP/FN analysis, answer to the research question |
| **VII. Limitations** | Synthetic data, label scarcity, concept drift, threshold choice, privacy/ethics of monitoring |
| **VIII. Conclusion & Future Work** | Summary, graph-based / LSTM / real-time streaming ideas |
| **References** | IEEE style |

---

## Timeline

**Submission: Fri Nov 20, 2026.** The phases above run **in parallel** across the three team members, not one after another. The dated plan is in [TEAM_PLAN.md](TEAM_PLAN.md) (milestones) and in [Supriye.md](Supriye.md), [Arva.md](Arva.md) and [Ayo.md](Ayo.md) (day-by-day tasks).

| Dates | Phases in progress |
|---|---|
| Oct 28 – Nov 1 | Phase 2 setup; Phase 3 EDA starts; model and evaluation code built on synthetic data |
| Nov 2 – Nov 8 | Phases 3–5 (features, baselines); Phases 6–8 code tested on the v0 sample; Phase 1 reading |
| Nov 9 – Nov 15 | Phases 6–10 on full data (tuning, final scores, evaluation, unseen scenarios, SHAP, FP/FN, case studies); Phase 11 writing starts |
| Nov 16 – Nov 20 | Phase 11: merge, edit, verify numbers, fresh-clone test, submit |

---

## Common Pitfalls

- **Reporting accuracy as the main metric** — always lead with precision, recall, F1, PR-AUC.
- **Data leakage** — random train/test splits across time, baselines that use future data, or scalers fit on the full dataset.
- **Running out of memory** on `http.csv` / `auth.txt` — use `pd.read_csv(..., chunksize=...)`, Parquet, or only the columns you need.
- **Evaluating only on seen scenarios** — the assignment explicitly asks about *unseen* anomalous behavior.
- **No explanations** — every flagged case in the paper needs a "why".
- **Ignoring the cold-start problem** — new users have no baseline; mention how you handle it (e.g., fall back to peer group).

---

## Final Checklist

- [ ] ≥ 5 papers reviewed and summarized
- [ ] Dataset preprocessed; class imbalance reported
- [ ] Behavioral features extracted (login, auth failures, file/resource access, app/web usage, time, deviation)
- [ ] Normal behavior baseline established
- [ ] ≥ 2 models trained and compared, with justification
- [ ] Risk/anomaly score assigned
- [ ] All required metrics reported, including FPR, FNR, ROC-AUC, detection time
- [ ] Precision/recall importance explained
- [ ] Unseen-anomaly experiment done
- [ ] Feature importance analyzed
- [ ] FP and FN cases analyzed
- [ ] 3–5 anomalies investigated with explanations
- [ ] Limitations discussed
- [ ] Prototype runs end-to-end
- [ ] Paper written in IEEE format
