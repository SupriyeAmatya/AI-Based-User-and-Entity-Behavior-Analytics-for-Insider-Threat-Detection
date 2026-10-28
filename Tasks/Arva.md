# Arva — Unsupervised Models, Risk Scoring & Prototype Lead

**Your stream in one sentence:** build the unsupervised detectors that learn "normal" behavior without labels, turn their output into a 0–100 **risk score** with reasons, package everything into the end-to-end **UEBA prototype**, and explain the detected anomalies in the case studies.

**Deadline: Fri Nov 20, 2026. Target: submission-ready Thu Nov 19.**

Before starting, read [TEAM_PLAN.md](TEAM_PLAN.md) fully, especially **Section 5 (Team Rules)**: 5.2 (score files), 5.4 (training data), 5.5 (preprocessing), 5.6 (thresholds) and 5.7 (reproducibility) apply directly to your code.

---

## 1. Your Responsibilities

1. **Isolation Forest**, trained on normal user-days only.
2. **Autoencoder**, trained on normal user-days only; its reconstruction error is the anomaly score.
3. *(Optional)* One-Class SVM.
4. A **contamination variant** of both models (trained on all training rows), to show the effect of unlabeled bad days.
5. Hyperparameter tuning on the validation split.
6. **Risk scoring**: 0–100 risk, per-user aggregation over time, alert levels, top-3 reasons per alert.
7. **Detection time (a)**: training time and inference time per 1,000 user-days.
8. **End-to-end prototype** (`pipeline.py`), plus an optional Streamlit dashboard.
9. **Anomaly investigation**: 3–4 detected cases explained in detail.
10. Paper: IV-C (unsupervised models), IV-D (risk scoring & prototype), VI-B (case studies), VIII (conclusion & future work), and your Related Work paragraphs.

## 2. Hand-offs

| You give | To | Due |
|---|---|---|
| `src/synthetic.py` (synthetic feature table in TEAM_PLAN 5.1 format) | Ayo | Thu Oct 29 |
| Final score files: `iforest`, `autoencoder` (+ `ocsvm`, `iforest_contam`, `autoencoder_contam`) | Ayo | Tue Nov 10 |
| Tuned settings committed in `models_unsupervised.py` (for the ablation) | Supriye | Tue Nov 10 |
| Timing numbers + per-scenario results + alert volume | Ayo | Wed Nov 11 (M3) |
| Related Work paragraphs (L4, L5, L10a) | Supriye | Fri Nov 13 |
| IV-C (unsupervised), IV-D, VI-B | Supriye | Sun Nov 15 |
| VIII. Conclusion & Future Work | Supriye | Mon Nov 16 (M4) |

| You need | From | Due |
|---|---|---|
| `evaluate.py` | Ayo | Sun Nov 1 |
| Split dates | Supriye | Mon Nov 2 |
| Feature table v0 + `get_model_matrix()` | Supriye | Tue Nov 3 (M1) |
| `explain.py` (SHAP helper) | Ayo | Fri Nov 6 |
| Feature table v1 | Supriye | Sun Nov 8 (M2) |

## 3. Files You Own & Your Git Branches

**Files you own:** `src/synthetic.py`, `src/models_unsupervised.py`, `src/risk_scoring.py`, `src/pipeline.py`, `app/dashboard.py` (optional), `notebooks/03a_unsupervised_models.ipynb`, `notebooks/05_anomaly_investigation.ipynb`. Also the "Run the prototype" section of `README.md` (A23 only; README belongs to Supriye).

### Your branches
How-to: [TEAM_PLAN §14](TEAM_PLAN.md#14-git-workflow--branching-pulling-and-pushing). A code hand-off counts as delivered only once its PR is **merged** and announced in chat. Commit (or `git stash`) before switching between branches.

| Branch | Tasks | Create on | Open PR | Merge by | Reviewer |
|---|---|---|---|---|---|
| `arva/notes` | A-LIT1–4 notes, A14 (F2 diagram, T4 draft, section notes) | Wed Oct 28 | Fri Nov 13 | Fri Nov 13 | Any teammate |
| `arva/A3-synthetic` | A3 | Thu Oct 29 (after `supriye/S2-setup` merges) | Thu Oct 29 (hand-off) | Thu Oct 29 | Ayo |
| `arva/A4-unsupervised-models` | A4, A5, A6, A8 | Fri Oct 30 | Mon Nov 2 | Mon Nov 2 | Ayo |
| `arva/A7-risk-scoring` | A7 | Sun Nov 1 | Sun Nov 1 | Sun Nov 1 | Supriye |
| `arva/A9-v0-tuning` | A9, A10 | Tue Nov 3 (after `supriye/S9-features-v0` merges) | Wed Nov 4 | Wed Nov 4 | Ayo |
| `arva/A11-pipeline` | A11, A12 | Thu Nov 5 | Fri Nov 6 | Fri Nov 6 | Supriye |
| `arva/A13-ocsvm` *(optional)* | A13 | Sat Nov 7 | Sat Nov 7 | Sat Nov 7 | Ayo |
| `arva/A15-final-models` | A15, A16 | Mon Nov 9 | Tue Nov 10 (hand-off) | Tue Nov 10 | Supriye |
| `arva/A17-results` | A17 | Wed Nov 11 | Wed Nov 11 (hand-off) | Wed Nov 11 | Ayo |
| `arva/A18-prototype-cases` | A18, A19 | Thu Nov 12 | Sat Nov 14 | Sat Nov 14 | Ayo |
| `arva/A21-dashboard` *(optional)* | A21 | Sat Nov 14 | Sat Nov 14 | Sat Nov 14 | Supriye |
| `arva/A23-readme-run` | A23 | Mon Nov 16 | Mon Nov 16 | Mon Nov 16 | Supriye |
| `arva/A24-fresh-clone-fixes` *(if needed)* | A24 | Tue Nov 17 | Tue Nov 17 | Tue Nov 17 | Supriye |
| `arva/A26-final-fixes` *(if needed)* | A26 | Thu Nov 19 | Thu Nov 19 | Thu Nov 19 | Supriye |

You also **review** Supriye's `S5`, `S6`, `S9`, `S10`, `S17`, `S21`, `S24` branches and Ayo's `Y3`, `Y11`, `Y12`, `Y16`, `Y17`, `Y18` branches; see the calendar in [TEAM_PLAN 14.8](TEAM_PLAN.md#148-branch-calendar--everyones-branches-in-one-view). Supriye's `S9` (Tue Nov 3) and `S17` (Sun Nov 8) are the data hand-offs your own work depends on, so review those within 3 hours.

### When to pull `main`
Every morning, plus right after these merges. If you're on a branch, run `git pull origin main` on it.

| When | After merge of | Why you need it |
|---|---|---|
| Thu Oct 29 | `supriye/S2-setup` | Folder structure, `.gitignore`, `requirements.txt` → run `pip install -r requirements.txt` |
| Sun Nov 1 | `ayo/Y3-evaluate` | `evaluate.py` (for A9, A10) |
| Tue Nov 3 | `supriye/S9-features-v0` | `get_model_matrix()`; also download `features_v0.parquet` from the drive |
| Fri Nov 6 | `ayo/Y11-explain` | `explain.py` (for A12, A19) |
| Sun Nov 8 / Mon Nov 9 morning | `supriye/S17-baselines-v1` | v1 code; also download `features_v1.parquet` |
| Tue Nov 10, 12:00 | `supriye/S21-v1-fixes` (if any) | v1.1 fixes; also download `features_v1_1.parquet` |
| Wed Nov 11 | `supriye/S24-lanl` (stretch only) | LANL feature code for A18 step 4 |

### Shared drive, not Git
Upload these and post the link in chat:
- Score files `results/scores/iforest.parquet`, `autoencoder.parquet`, `iforest_contam.parquet`, `autoencoder_contam.parquet` (+ `ocsvm.parquet`) → by Tue Nov 10.
- Trained models in `models/`, only if a teammate asks. Otherwise `pipeline.py` retrains when the files are missing.

The small CSV tables (`results/tables/`) and figures (`results/figures/`) **are** committed through Git.

---

## 4. Day-by-Day Timeline

| Date | Task | What |
|---|---|---|
| **Week 0** | | |
| Wed Oct 28 | A1, A-LIT1 | Environment; read the Isolation Forest paper, skim Chandola et al. |
| Thu Oct 29 | A2, A3 | Kickoff; synthetic data generator → share with Ayo |
| Fri Oct 30 | A4, A5 | Module skeleton; Isolation Forest |
| Sat Oct 31 | A6 | Autoencoder |
| Sun Nov 1 | A7 | Risk scoring module |
| **Week 1** | | |
| Mon Nov 2 | A8, A-LIT2 | Per-feature reconstruction error + contamination variant; read L4 |
| Tue Nov 3 | A9 | First run on real data (v0) |
| Wed Nov 4 | A10 | Tuning workflow on v0 |
| Thu Nov 5 | A11 | Prototype pipeline (`pipeline.py`) |
| Fri Nov 6 | A12, A-LIT3 | Alert reasons (top-3); read L5 |
| Sat Nov 7 | A13, A-LIT4 | One-Class SVM (optional); read L10a |
| Sun Nov 8 | A14 | Pipeline diagram (F2), hyperparameter table draft (T4), section notes |
| **Week 2** | | |
| Mon Nov 9 | A15 | v1 walkthrough; retrain and tune on v1 |
| Tue Nov 10 | A16 | Final scores → Ayo; tuned settings → Supriye |
| Wed Nov 11 | A17 | Per-scenario results, alert volume, timing → **M3** |
| Thu Nov 12 | A18 | Prototype on v1: top-20 users, risk timeline (F8) |
| Fri Nov 13 | A19, A20 | Case studies part 1; your Related Work paragraphs |
| Sat Nov 14 | A19, A21 | Finish case studies; results walkthrough; dashboard (optional) |
| Sun Nov 15 | A22 | Write IV-C (unsupervised), IV-D, VI-B |
| **Week 3** | | |
| Mon Nov 16 | A23 | Write VIII; README run instructions → **M4** |
| Tue Nov 17 | A24 | Demo rehearsal; fresh-clone test of the pipeline |
| Wed Nov 18 | A25 | Review the full draft (comments by Thu morning) |
| Thu Nov 19 | A26 | Final read-through; last fixes → **submission-ready** |
| Fri Nov 20 | — | **Submit** |

---

## 5. Task Cards

### A1 · Wed Oct 28 · Environment
1. Accept the GitHub invite from Supriye. Clone the repo and set your Git name and email, exactly as in TEAM_PLAN 14.1.
2. Create a virtual environment inside the cloned folder (`.venv`). Install the packages listed in Supriye's S2 step 5 now; once `supriye/S2-setup` merges (Thu Oct 29), pull `main` and run `pip install -r requirements.txt` so your versions match the team's.
3. Check that `import torch, sklearn, shap` works. The CPU build of PyTorch is enough; no GPU is needed.
4. Create your `arva/notes` branch for literature notes (`git checkout -b arva/notes`).
5. Read TEAM_PLAN.md fully before the kickoff, especially Sections 5 and 14.

**Done when:** the repo is cloned, the imports work, and you have read TEAM_PLAN.md.

### A2 · Thu Oct 29 · Kickoff
Agree on: the score-file format (TEAM_PLAN 5.2), **"higher score = more suspicious"**, PyTorch vs. Keras, and the model names. Bring questions about anything unclear in this file.

### A3 · Thu Oct 29 · Synthetic data generator (`src/synthetic.py`)
**Goal:** let you and Ayo build and test code before real data exists.
1. Write `make_synthetic_features(n_users=50, n_days=300, seed=42)`, returning a DataFrame in **exactly** the TEAM_PLAN 5.1 format.
2. Normal behavior: for each user, draw a personal rate per feature, then draw daily counts from a Poisson distribution with that rate (`f_logon_count`, `f_usb_connect`, `f_file_copy`, `f_email_external`, `f_http_count`, …). Add `z_user_*` columns computed the simple way (value minus the user's mean, divided by the user's std + 1).
3. Anomalies: mark ~0.5% of rows `label = 1` and give them a random `scenario` of 1–3. Multiply 2–3 of their features by 3–10× (e.g. scenario 1: USB + after-hours; scenario 2: file copies + job sites; scenario 3: email recipients).
4. `split` by date: first 60% of days `train`, next 15% `val`, last 25% `test`. Give each user a `role` from 3 made-up roles.
5. Push and tell Ayo it's ready.

**Done when:** `make_synthetic_features()` returns the right columns, and Ayo can load it.

### A4 · Fri Oct 30 · Module skeleton (`src/models_unsupervised.py`)
1. Write one common interface for every unsupervised model:
   ```python
   class UnsupervisedDetector:
       def fit(self, X_train_normal): ...   # X = output of get_model_matrix()
       def score(self, X): ...              # returns an array, higher = more suspicious
   ```
2. Write `train_and_score(df, model_name, params) -> DataFrame` that:
   - selects training rows by TEAM_PLAN 5.4 (`split == "train"` and `label == 0`),
   - fits the model,
   - scores **every** row,
   - returns `user, date, split, label, scenario, score`, and
   - saves to `results/scores/<model_name>.parquet`.
3. Until Supriye's `get_model_matrix()` exists (Tue Nov 3), use a simple stand-in that selects `f_*`/`z_*` columns and applies `log1p` to `f_*`.

**Done when:** `train_and_score()` runs end to end on synthetic data with a dummy model.

### A5 · Fri Oct 30 · Isolation Forest
1. Build `Pipeline([("scaler", StandardScaler()), ("model", IsolationForest(n_estimators=200, max_samples="auto", contamination="auto", random_state=42))])`.
2. Score = `-pipeline.decision_function(X)`, so that higher means more anomalous.
3. Test on synthetic data with `sklearn.metrics.roc_auc_score(label, score)`; it should be well above 0.5 (often > 0.9 on synthetic data).

**Done when:** Isolation Forest scores are saved for synthetic data, and the ROC-AUC is printed.

### A6 · Sat Oct 31 · Autoencoder
1. Architecture (PyTorch): input *n* → 64 → 32 → **16 (bottleneck)** → 32 → 64 → *n*, ReLU activations, linear output layer.
2. Inputs: the same `StandardScaler`-scaled matrix (fit on training normal rows only).
3. Training: MSE loss, Adam (learning rate 1e-3), batch size 256, up to 50 epochs, **early stopping** on the validation normal rows (patience 5). Set `torch.manual_seed(42)` and `np.random.seed(42)`.
4. Score = mean squared reconstruction error per row.
5. Plot the training and validation loss curves; save the figure.
6. Test on synthetic data: anomalies should have clearly higher error than normal rows (plot both histograms).

**Done when:** the AE trains without errors, the loss curves look sensible (decreasing, then flat), and anomalies separate on synthetic data.

### A7 · Sun Nov 1 · Risk scoring (`src/risk_scoring.py`)
1. **Daily risk (0–100):** `to_risk(scores, reference_scores)` = the percentile of each score within the **training normal** scores. Example: risk 99 means "more unusual than 99% of normal training days".
2. **User risk over time:** for each user, the rolling **7-day maximum** of daily risk (primary). Also compute an exponentially decayed sum (`risk × 0.5^(age_in_days / 3)`) as a secondary option.
3. **Alert levels** (your decision; justify it in IV-D). Suggested:
   - **High** ≥ 99 (top 1%, matching the TEAM_PLAN 5.6 alert budget)
   - **Medium** 95–99
   - **Low** < 95
4. `rank_users(df, date)` returns users sorted by user risk on a given date, with their alert level.

**Done when:** the functions work on synthetic scores, and a ranked user table prints.

### A8 · Mon Nov 2 · Per-feature reconstruction error + contamination variant
1. In the AE class add `feature_errors(X)`, which returns the squared error **per feature** (same shape as X). This is how you explain AE alerts later.
2. Add a `train_on="normal" | "all"` option to `train_and_score()`. With `"all"`, train on every `split == "train"` row, including malicious ones, and save as `<model>_contam`.
3. Read **L4** (A-LIT2).

**Done when:** `feature_errors()` returns the right shape, and the `_contam` option works on synthetic data.

### A9 · Tue Nov 3 · First run on real data (v0)
1. Switch to Supriye's `get_model_matrix()`.
2. Run Isolation Forest and the AE on `features_v0.parquet`.
3. Run Ayo's `evaluate.py` on the `val` split. Record ROC-AUC, PR-AUC and recall at top-1% in a **tuning log** (a table in `03a_unsupervised_models.ipynb`).
4. Report anything strange in the data to Supriye through a GitHub Issue.

**Done when:** both models have scored v0, and the first validation numbers are in the tuning log.

### A10 · Wed Nov 4 · Tuning workflow
Build the tuning loop now on v0, so that on Mon Nov 9 you only re-run it on v1.
1. **Isolation Forest grid:** `n_estimators` {100, 200, 500} × `max_samples` {256, 1024, "auto"} × `max_features` {0.5, 1.0}.
2. **Autoencoder grid:** bottleneck {8, 16} × hidden layers {(64, 32), (128, 64)} × dropout {0, 0.1} × learning rate {1e-3, 1e-4}.
3. Choose by **validation PR-AUC** (never by test results, and never by accuracy).
4. Every run adds one row to the tuning log: parameters, val ROC-AUC, val PR-AUC, training time.

**Done when:** one function call runs a whole grid and fills the tuning log.

### A11 · Thu Nov 5 · Prototype pipeline (`src/pipeline.py`)
**Goal:** one command that shows the full UEBA flow.
1. Command-line interface:
   ```
   python src/pipeline.py --features data/processed/features_v1.parquet --model iforest --top 20
   ```
2. Steps inside:
   1. load features
   2. `get_model_matrix()`
   3. load the saved trained model from `models/` (train it if it's missing)
   4. score the `test` period
   5. daily risk → user risk → alert levels
   6. top-N table
   7. save `results/tables/top_risky_users.csv` and print it
3. Save trained models with `joblib.dump` (Isolation Forest) and `torch.save` (AE) in `models/`. Add `models/` to `.gitignore` if the files are large.
4. Test with `features_v0.parquet`.

**Done when:** the command runs from the repo root on v0 and prints a ranked table.

### A12 · Fri Nov 6 · Alert reasons
1. For every alert row, find the **top-3 contributing features**:
   - Isolation Forest: the three largest `|z_user_*|` values (or SHAP values via Ayo's `explain.py`, ready today).
   - Autoencoder: the three largest per-feature errors from `feature_errors()`.
2. Turn them into readable text, e.g. *"USB connects 6.2σ above own baseline; 37 files copied; first-ever leak-site visit"*.
3. Add a `reasons` column to the top-N table in `pipeline.py`.
4. Read **L5** (A-LIT3).

**Done when:** each alert in the pipeline output has 3 readable reasons.

### A13 · Sat Nov 7 · One-Class SVM (optional) + reading
1. *(Optional)* `OneClassSVM(kernel="rbf", nu=0.01, gamma="scale")` inside the same scaler pipeline. Train on a random **20,000-row sample** of training normal rows, because it scales poorly. Score = `-decision_function(X)`.
2. Read **L10a** (A-LIT4); find it first using TEAM_PLAN 7.3 and post the title in chat.

**Done when:** OCSVM scores v0 (or is explicitly skipped), and the L10a notes are written.

### A14 · Sun Nov 8 · Diagram, table and notes for the paper
1. Draw the **UEBA pipeline diagram (F2)**: raw logs → features → baselines → models → risk score → ranked alerts + reasons. Draw.io or PowerPoint, exported as PDF/PNG.
2. Start the **hyperparameter table (T4)** for your models.
3. Write bullet notes for IV-C and IV-D: decisions made and why. Drafting on Nov 15 will then be fast.

**Done when:** F2 is saved in `results/figures/`, and the notes are in `paper/notes_arva.md`.

### A15 · Mon Nov 9 · Retrain and tune on v1
1. Attend the v1 walkthrough at stand-up.
2. Run the A10 grids on `features_v1.parquet`; pick the best settings by validation PR-AUC.
3. Train the `_contam` variants with the same best settings.

**Done when:** the best settings for Isolation Forest and the AE are chosen and recorded in the tuning log and T4.

### A16 · Tue Nov 10 · Final scores
1. If Supriye releases `features_v1_1.parquet` at 12:00, use it; otherwise use v1.
2. Produce the final score files for **all rows**: `iforest`, `autoencoder`, `iforest_contam`, `autoencoder_contam` (+ `ocsvm`).
3. Commit the tuned settings as the defaults in `models_unsupervised.py`, so Supriye can run the ablation tomorrow.
4. Share the score files and post the commit in chat.

**Done when:** Ayo confirms that `evaluate.py` runs on all your score files.

### A17 · Wed Nov 11 · Per-scenario results, alert volume, timing → M3
1. **Per scenario:** with `evaluate.py`, compute recall for scenarios 1, 2 and 3 separately on `test` (best-F1 threshold and top-1%). Unsupervised models never see labels, so **every scenario is "unseen"** for them. This is the key comparison with Ayo's leave-one-scenario-out results.
2. **Contamination effect:** compare `iforest` vs. `iforest_contam` and `autoencoder` vs. `autoencoder_contam` (PR-AUC).
3. **Alert volume:** average number of alerts per day at each threshold. Would an analyst cope with that many?
4. **Timing:** use `time.perf_counter()` around `fit` and `score`. Report training time and **inference time per 1,000 user-days**, averaged over 3 runs. Note your CPU and RAM.
5. Send everything to Ayo (`results/tables/unsupervised_extra.csv`).

**Done when:** the four results are in the CSV, and Ayo has it. → **M3**

### A18 · Thu Nov 12 · Prototype on v1
1. Run `pipeline.py` on v1 for the test period, for both models.
2. Record how many of the top 20 users are real insiders (**precision@20**).
3. **Figure F8:** for one insider, plot daily risk and 7-day user risk over time, shading the malicious days, with the High-alert threshold as a line.
4. *(Only if the LANL stretch was agreed)* Run Isolation Forest and the AE on `lanl_features.parquet` with the same code; save `iforest_lanl` and `autoencoder_lanl` for Ayo.

**Done when:** `top_risky_users.csv` and F8 are saved.

### A19 · Fri Nov 13 – Sat Nov 14 · Anomaly case studies (`notebooks/05_anomaly_investigation.ipynb`)
**Goal:** the assignment requires explaining **why** the system flagged selected activities.
1. **Pick 4 cases** from the test period:
   - 1 true positive from **each scenario** (3 cases)
   - 1 **false positive**: the highest-scoring normal user-day

   If a scenario has no true positive, use a missed (false-negative) day from that scenario instead, and tell Ayo, who covers FP/FN analysis overall.
2. For **each** case, build:
   1. **Context:** user, role, date, daily risk, user risk, alert level.
   2. **Baseline vs. flagged day:** a table of the top 5 features: value that day, the user's 30-day mean, `z_user`, `z_peer`.
   3. **Model explanation:** SHAP waterfall for Isolation Forest (Ayo's `explain.py`) and the per-feature error bar chart for the AE. This becomes figure **F7**.
   4. **Raw evidence:** load the raw Parquet logs for that user and day and list the actual events, e.g. *"23:14 USB connect on PC-1234; 37 `.doc` files copied; visit to wikileaks.org"*.
   5. **Narrative (yourself, no AI):** 4–6 sentences explaining why this is suspicious and how it matches (or doesn't match) the scenario.
   6. **Analyst verdict:** would a security analyst escalate this? Why?
3. **Sat:** present 2 cases at the results walkthrough.

**Done when:** all 4 cases have all 6 parts in the notebook, and the F7 figures are saved.

### A20 · Fri Nov 13 · Related Work paragraphs
Write one paragraph each for **L4, L5, L10a** in Overleaf (II. Related Work), from your notes. Say how each relates to our approach (e.g. L4 also uses unsupervised deep learning on CERT).

**Done when:** the paragraphs are in Overleaf by Fri night.

### A21 · Sat Nov 14 · Dashboard (optional)
Only if A19 is finished. A Streamlit app (`app/dashboard.py`, run with `streamlit run app/dashboard.py`) with:
1. the ranked user table
2. a user selector showing the risk timeline (like F8)
3. the top-3 reasons for the selected day

Skip it without hesitation if time is short; `pipeline.py` already satisfies the prototype requirement.

### A22 · Sun Nov 15 · Paper sections IV-C (unsupervised), IV-D, VI-B
Write in Overleaf, in your own words:
- **IV-C Unsupervised Models (~0.5 page):**
  - why unsupervised (labels are rare; attacks change)
  - how Isolation Forest works (cite Liu, Ting & Zhou), with its score
  - the AE architecture and the reconstruction-error score
  - training on normal days only (TEAM_PLAN 5.4) and the contamination variant
  - optional OCSVM (cite Schölkopf et al.)
  - hyperparameters (T4)
- **IV-D Risk Scoring & UEBA Prototype (~0.5 page):** pipeline (F2), percentile risk, 7-day user risk, alert levels and why, how the reasons are produced, precision@20.
- **VI-B Anomaly Case Studies (~0.75 page):** the 2–3 strongest cases from A19 with F7 (and F8). Each case: what happened, why it was flagged, the analyst verdict.

**Done when:** all three are full paragraphs, with every figure and table referenced.

### A23 · Mon Nov 16 · VIII. Conclusion & Future Work + README → M4
1. **Conclusion (~0.25 page):** answer the research question in 2–3 sentences, using the answer agreed at the walkthrough. Then summarize the main findings.
2. **Future work:** sequence models such as LSTM (cite L5), graph-based detection (cite L8), streaming / real-time scoring, authentication-failure data (LANL), an analyst-feedback loop to reduce false positives.
3. Add a **"Run the prototype"** section to [README.md](../README.md) with the exact commands.

**Done when:** VIII is in Overleaf and the README section is pushed. → **M4**

### A24 · Tue Nov 17 · Demo rehearsal + fresh-clone test
1. Clone the repo into a new folder, install, and run `pipeline.py`. Fix anything that only worked on your machine (paths, missing packages).
2. Write a 3-minute demo script: run the pipeline → show the top-20 → open one case study → explain its reasons.
3. Rehearse it once with a timer.

**Done when:** the pipeline runs from a fresh clone, and the demo fits in 3 minutes.

### A25 · Wed Nov 18 · Review the full draft
Read the whole PDF that Supriye circulates (by 18:00). Comment in Overleaf by Thu morning: technical errors, numbers that don't match, unclear sentences. Check your own sections most carefully.

### A26 · Thu Nov 19 · Final read-through → submission-ready
Attend the final meeting; fix everything assigned to you the same day.

### A-LIT · Literature reading
| Task | Date | Papers |
|---|---|---|
| A-LIT1 | Wed Oct 28 | Liu, Ting & Zhou, "Isolation Forest" (2008); skim Chandola et al. (2009) |
| A-LIT2 | Mon Nov 2 | **L4** — Tuor et al. (2017) |
| A-LIT3 | Fri Nov 6 | **L5** — Lu & Wong (2019) |
| A-LIT4 | Sat Nov 7 | **L10a** — one 2022–2026 paper on unsupervised / autoencoder insider-threat detection (TEAM_PLAN 7.3). L10b only if time allows |

For each: fill in the note template (TEAM_PLAN 7.4) as `paper/lit_notes/<ID>.md` and add it to Zotero.

---

## 6. Do This Yourself — No AI Agents

On top of the [team-wide list](TEAM_PLAN.md#12-human-only-work-no-ai-agents):

- [ ] **Read L4, L5, L10a and the method papers**, and write their notes and Related Work paragraphs in your own words.
- [ ] **Choose the Autoencoder architecture and the tuning grids**, and write why.
- [ ] **Choose the alert levels and thresholds** and justify them (alert volume vs. recall).
- [ ] **Select the case-study anomalies** and **write each "why was this flagged?" narrative and analyst verdict** by examining the data yourself.
- [ ] **Interpret** the contamination and per-scenario results.
- [ ] **Write** IV-C (unsupervised), IV-D, VI-B and VIII.
- [ ] **Draw** the pipeline diagram (F2).
- [ ] **Run and present the demo**, and explain `models_unsupervised.py`, `risk_scoring.py` and `pipeline.py` line by line if asked.

---

## 7. Your Literature

| ID | Paper | What to extract |
|---|---|---|
| L4 | Tuor et al., AAAI Workshops (2017) | Their unsupervised deep model on CERT; how they score anomalies; results for T1 |
| L5 | Lu & Wong, ACM ACSW (2019) | How LSTM models user activity sequences (for Future Work) |
| L10a (L10b optional) | 2022–2026 paper on unsupervised / autoencoder insider-threat detection (you find it) | Recent architectures and results to compare |
| — | Liu, Ting & Zhou, IEEE ICDM (2008) | How Isolation Forest works; cite in IV-C |
| — | Schölkopf et al., Neural Computation (2001) | One-Class SVM citation (if used) |
| — | Chandola, Banerjee & Kumar, ACM Computing Surveys (2009) | Definitions of anomaly types for IV-C |

## 8. Your Models

| Model | Library | Trained on | Anomaly score | Key settings to tune |
|---|---|---|---|---|
| **Isolation Forest** | `sklearn.ensemble.IsolationForest` | Train split, label 0 | `-decision_function(X)` | `n_estimators`, `max_samples`, `max_features` |
| **Autoencoder** | PyTorch | Train split, label 0 | Mean squared reconstruction error | Layer sizes, bottleneck, dropout, learning rate |
| One-Class SVM *(optional)* | `sklearn.svm.OneClassSVM` | 20k-row sample of train, label 0 | `-decision_function(X)` | `nu`, `gamma` |
| `_contam` variants | Same as above | All train rows | Same | Same settings as the best normal-only model |

## 9. Your Tools
Python, Pandas, NumPy, **Scikit-learn**, **PyTorch**, SHAP (through Ayo's `explain.py`), Matplotlib, Jupyter, joblib, **Streamlit** (optional), draw.io (diagram), Git/GitHub.

## 10. Your Evaluation Responsibilities
| What | Where reported |
|---|---|
| Validation tuning log (PR-AUC-based) | T4 / notebook |
| Per-scenario recall of unsupervised models (= unseen behavior) | V (via Ayo), table T6 |
| Contamination effect | V / VII |
| Alert volume per day; precision@20 | IV-D / V |
| **Detection time (a):** training and inference time per 1,000 user-days | Table T8 (via Ayo) |
| Explanations of flagged anomalies | VI-B |
