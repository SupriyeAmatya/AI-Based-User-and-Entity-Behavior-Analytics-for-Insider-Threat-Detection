# Ayo — Supervised Models, Evaluation & Explainability Lead

**Your stream in one sentence:** build the supervised detectors, own the **evaluation code that every model is measured with**, run the **unseen-anomaly experiment**, and explain the results: which features matter most, and why false positives and false negatives happen.

**Deadline: Fri Nov 20, 2026. Target: submission-ready Thu Nov 19.**

Before starting, read [TEAM_PLAN.md](TEAM_PLAN.md) fully, especially **Section 5 (Team Rules)** and **Section 10 (Evaluation Metrics)**. You own the evaluation rules: 5.6 (thresholds) and 10.2 (reporting protocol).

---

## 1. Your Responsibilities

1. **`evaluate.py`**: every required metric and plot, used by the whole team. This is due first (Sun Nov 1) because everyone needs it.
2. **Random Forest** and **XGBoost**, with class-imbalance handling.
3. **Imbalance experiment**: no weighting vs. class weights vs. SMOTE (training set only).
4. **Unseen-anomaly experiment**: leave-one-scenario-out (LOSO), i.e. train on two scenarios and test on the third.
5. **Detection time (b)**: days from an insider's first malicious action to the first alert; plus timing for your models.
6. **Model comparison** across all models (yours + Arva's).
7. **Explainability**: SHAP (`explain.py`) for global and per-scenario feature importance.
8. **False positive / false negative analysis**.
9. Paper: IV-C (supervised models), V (Experiments & Results), VI-A (Feature Importance), VI-C (FP/FN Analysis), the precision/recall paragraph, and your Related Work paragraphs.

## 2. Hand-offs

| You give | To | Due |
|---|---|---|
| `evaluate.py` (works on any score file) | Arva, Supriye | Sun Nov 1 |
| `explain.py` (SHAP helper) | Arva | Fri Nov 6 |
| Final score files `random_forest`, `xgboost` + tuned settings committed (for the ablation) | Supriye, team | Tue Nov 10 |
| LOSO score files + table T6 | Team | Wed Nov 11 (M3) |
| Comparison table T5 + figures F4, F5 | Team | Thu Nov 12 (presented Sat Nov 14) |
| Related Work paragraphs (L6, L7, L8, L11a) | Supriye | Fri Nov 13 |
| IV-C (supervised) + V | Supriye | Sun Nov 15 |
| VI-A + VI-C + precision/recall paragraph | Supriye | Mon Nov 16 (M4) |

| You need | From | Due |
|---|---|---|
| `src/synthetic.py` | Arva | Thu Oct 29 |
| Split dates | Supriye | Mon Nov 2 |
| Feature table v0 + `get_model_matrix()` | Supriye | Tue Nov 3 (M1) |
| Feature table v1 | Supriye | Sun Nov 8 (M2) |
| Unsupervised score files | Arva | Tue Nov 10 |
| Per-scenario results, alert volume, timings | Arva | Wed Nov 11 |
| Data-processing time | Supriye | Fri Nov 13 |

## 3. Files You Own & Your Git Branches

**Files you own:** `src/models_supervised.py`, `src/evaluate.py`, `src/explain.py`, `notebooks/03b_supervised_models.ipynb`, `notebooks/04_evaluation.ipynb`

### Your branches
How-to: [TEAM_PLAN §14](TEAM_PLAN.md#14-git-workflow--branching-pulling-and-pushing). A code hand-off counts as delivered only once its PR is **merged** and announced in chat. Commit (or `git stash`) before switching between branches.

| Branch | Tasks | Create on | Open PR | Merge by | Reviewer |
|---|---|---|---|---|---|
| `ayo/notes` | Y-LIT1–4 notes, Y13 (T4 draft, section notes) | Wed Oct 28 | Fri Nov 13 | Fri Nov 13 | Any teammate |
| `ayo/Y3-evaluate` | Y3, Y4, Y5, Y6 | Thu Oct 29 | Sun Nov 1 (hand-off) | Sun Nov 1 | Arva |
| `ayo/Y7-supervised-models` | Y7, Y8, Y9, Y10 | Mon Nov 2 | Thu Nov 5 | Thu Nov 5 | Supriye |
| `ayo/Y11-explain` | Y11 | Fri Nov 6 | Fri Nov 6 (hand-off) | Fri Nov 6 | Arva |
| `ayo/Y12-loso` | Y12 | Sat Nov 7 | Sat Nov 7 | Sat Nov 7 | Arva |
| `ayo/Y14-final-models` | Y14, Y15 | Mon Nov 9 | Tue Nov 10 (hand-off) | Tue Nov 10 | Supriye |
| `ayo/Y16-loso-results` | Y16 | Wed Nov 11 | Wed Nov 11 | Wed Nov 11 | Arva |
| `ayo/Y17-comparison` | Y17 | Thu Nov 12 | Thu Nov 12 | Thu Nov 12 | Arva |
| `ayo/Y18-shap-fpfn` | Y18, Y20 | Fri Nov 13 | Sat Nov 14 | Sat Nov 14 | Arva |
| `ayo/Y23-verify` | Y23 | Tue Nov 17 | Tue Nov 17 | Tue Nov 17 | Supriye |
| `ayo/Y25-final-fixes` *(if needed)* | Y25 | Thu Nov 19 | Thu Nov 19 | Thu Nov 19 | Supriye |

You also **review** Supriye's `S2-setup` (Thu Oct 29), `S22-ablation` (Wed Nov 11) and `S33-final` (Thu Nov 19), and most of Arva's model branches. See the calendar in [TEAM_PLAN 14.8](TEAM_PLAN.md#148-branch-calendar--everyones-branches-in-one-view).

### When to pull `main`
Every morning, plus right after these merges. If you're on a branch, run `git pull origin main` on it.

| When | After merge of | Why you need it |
|---|---|---|
| Thu Oct 29 | `supriye/S2-setup`, `arva/A3-synthetic` | `requirements.txt` → `pip install -r requirements.txt`; synthetic features for Y7 |
| Tue Nov 3 | `supriye/S9-features-v0` | `get_model_matrix()` (pull it into `ayo/Y7-supervised-models`); download `features_v0.parquet` from the drive |
| Sun Nov 8 / Mon Nov 9 morning | `supriye/S17-baselines-v1` | v1 code; download `features_v1.parquet` |
| Tue Nov 10 | `supriye/S21-v1-fixes` (if any), `arva/A15-final-models` | v1.1 fixes; Arva's final model code. Also download Arva's score files from the drive |
| Wed Nov 11 | `arva/A17-results` | Arva's per-scenario results, alert volume and timings (for Y17) |

### Shared drive, not Git
Upload the score files `results/scores/random_forest.parquet`, `xgboost.parquet` and the `*_loso_s*.parquet` files, and post the link in chat. The tables in `results/tables/` and figures in `results/figures/` **are** committed through Git.

---

## 4. Day-by-Day Timeline

| Date | Task | What |
|---|---|---|
| **Week 0** | | |
| Wed Oct 28 | Y1, Y-LIT1 | Environment; read Saito & Rehmsmeier (PR vs. ROC) |
| Thu Oct 29 | Y2, Y3 | Kickoff; synthetic scores + core metric functions |
| Fri Oct 30 | Y4 | Threshold selection + `evaluate_file()` |
| Sat Oct 31 | Y5 | Plots |
| Sun Nov 1 | Y6, Y-LIT2 | Detection delay + user-level recall; **share `evaluate.py`**; read L6 |
| **Week 1** | | |
| Mon Nov 2 | Y7 | Random Forest + XGBoost modules (on synthetic data) |
| Tue Nov 3 | Y8 | First run on real data (v0) |
| Wed Nov 4 | Y9 | Tuning workflow |
| Thu Nov 5 | Y10 | Imbalance experiment |
| Fri Nov 6 | Y11 | `explain.py` → share with Arva |
| Sat Nov 7 | Y12, Y-LIT3 | Leave-one-scenario-out (LOSO) code; read L7 |
| Sun Nov 8 | Y13, Y-LIT4 | Hyperparameter table draft + section notes; read L8 and L11a |
| **Week 2** | | |
| Mon Nov 9 | Y14 | v1 walkthrough; retrain and tune on v1 |
| Tue Nov 10 | Y15 | Final RF/XGB scores + timing; tuned settings → Supriye |
| Wed Nov 11 | Y16 | Run LOSO; unseen-scenario table T6 → **M3** |
| Thu Nov 12 | Y17 | Master comparison (T5, F4, F5), detection delay |
| Fri Nov 13 | Y18, Y19 | SHAP analysis (F6); your Related Work paragraphs |
| Sat Nov 14 | Y20 | False positive / false negative analysis; present at results walkthrough |
| Sun Nov 15 | Y21 | Write IV-C (supervised) + V |
| **Week 3** | | |
| Mon Nov 16 | Y22 | Write VI-A, VI-C, precision/recall paragraph → **M4** |
| Tue Nov 17 | Y23 | Re-run evaluation; verify every number; polish figures |
| Wed Nov 18 | Y24 | Review the full draft (comments by Thu morning) |
| Thu Nov 19 | Y25 | Final read-through; last fixes → **submission-ready** |
| Fri Nov 20 | — | **Submit** |

---

## 5. Task Cards

### Y1 · Wed Oct 28 · Environment
1. Accept the GitHub invite from Supriye. Clone the repo and set your Git name and email, exactly as in TEAM_PLAN 14.1.
2. Create a virtual environment inside the cloned folder (`.venv`). Install the packages listed in Supriye's S2 step 5 now; once `supriye/S2-setup` merges (Thu Oct 29), pull `main` and run `pip install -r requirements.txt` so your versions match the team's.
3. Check that `import sklearn, xgboost, imblearn, shap` works.
4. Create your `ayo/notes` branch for literature notes (`git checkout -b ayo/notes`).
5. Read TEAM_PLAN.md fully before the kickoff, especially Sections 5, 10, 11 and 14.

**Done when:** the repo is cloned, the imports work, and you have read TEAM_PLAN.md.

### Y2 · Thu Oct 29 · Kickoff
Lead the discussion of TEAM_PLAN **5.6 (thresholds)** and **10.2 (reporting protocol)**, so everyone agrees how models will be compared before any code is written.

### Y3 · Thu Oct 29 · Synthetic scores + core metrics (`src/evaluate.py`)
1. **Synthetic score file:** 10,000 rows in TEAM_PLAN 5.2 format, ~0.5% `label = 1` with random `scenario` 1–3, split 60/15/25 by date. `score = normal noise + 1.5 × label` (so positives score higher but overlap). Use `seed=42`.
2. Write:
   ```python
   def threshold_metrics(y_true, scores, threshold) -> dict:
       # accuracy, precision, recall, f1, fpr, fnr, tp, fp, tn, fn
   def ranking_metrics(y_true, scores) -> dict:
       # roc_auc (roc_auc_score), pr_auc (average_precision_score), positive_rate
   ```
   Use `zero_division=0` so there are no crashes when a model flags nothing.
3. **Test by hand:** make a 10-row example, compute TP/FP/TN/FN on paper, and check that the function gives the same numbers.

**Done when:** both functions pass your hand-computed example.

### Y4 · Fri Oct 30 · Threshold selection + `evaluate_file()`
1. Implement the two operating points from TEAM_PLAN 5.6:
   - `threshold_best_f1(val_df)`: use `precision_recall_curve` on the **val** rows and pick the threshold with the highest F1.
   - `threshold_top_k(test_df, k=0.01)`: `np.quantile(test_scores, 1 - k)`, i.e. flag the top 1%.
2. Write `evaluate_file(path) -> dict` that loads a score file and returns, for the **test** split:
   - `threshold_metrics` at both thresholds
   - `ranking_metrics`
   - **per-scenario** results: for each scenario *s*, use test rows with `scenario in {0, s}` and report recall at both thresholds plus PR-AUC
3. Write `compare_files(list_of_paths) -> DataFrame`: one row per model × operating point (this becomes table T5).

**Done when:** `evaluate_file()` and `compare_files()` run on the synthetic score file.

### Y5 · Sat Oct 31 · Plots
In `evaluate.py`, add:
1. `plot_roc(paths)` and `plot_pr(paths)`: all models on one figure. On the PR plot, draw the **positive-rate baseline** as a dashed line (a random model's PR-AUC).
2. `plot_confusion(path, threshold_type)`.
3. `plot_score_distribution(path)`: histograms of normal vs. malicious scores, log-scale y axis.
4. Use a **fixed color per model** (one dict at the top of the file), so figures look consistent across the paper.
5. Save figures to `results/figures/` as PNG (300 dpi) and PDF.

**Done when:** all 4 plots render for the synthetic file.

### Y6 · Sun Nov 1 · Detection delay + user-level recall → share `evaluate.py`
1. **Detection delay**, for each insider with malicious days in `test`:
   - `d0` = their first malicious day
   - `d1` = their first flagged day on or after `d0` (score ≥ threshold)
   - delay = `(d1 − d0)` in days; if there is no `d1`, the insider is "missed"
   - report the median and mean delay plus the number missed, at both thresholds
2. **User-level recall** = insiders with ≥ 1 flagged malicious day ÷ all test insiders.
3. Add both to `evaluate_file()`.
4. Write docstrings and a usage example at the top of the file, push to `main`, and post in chat:
   ```python
   from src.evaluate import evaluate_file, compare_files
   results = evaluate_file("results/scores/iforest.parquet")
   ```
5. Read **L6** (Y-LIT2).

**Done when:** Arva and Supriye confirm they can import and run it.

### Y7 · Mon Nov 2 · Random Forest + XGBoost (`src/models_supervised.py`)
1. Write `train_and_score_supervised(df, model_name, params)`, with the same inputs and outputs as Arva's `train_and_score()`:
   - trains on **all** `split == "train"` rows (TEAM_PLAN 5.4)
   - scores **every** row
   - saves `results/scores/<model_name>.parquet`
2. **Random Forest:** `RandomForestClassifier(n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=42)`; score = `predict_proba(X)[:, 1]`.
3. **XGBoost:** `XGBClassifier(n_estimators=1000, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, scale_pos_weight=n_neg/n_pos, eval_metric="aucpr", early_stopping_rounds=50, random_state=42)`, fitted with `eval_set=[(X_val, y_val)]`.
4. Tree models don't need scaling, but keep the `StandardScaler` step for consistency with TEAM_PLAN 5.5. It doesn't change the results.
5. Test on Arva's synthetic features.

**Done when:** both models produce score files for synthetic data, and `evaluate_file()` runs on them.

### Y8 · Tue Nov 3 · First run on real data (v0)
1. Switch to Supriye's `get_model_matrix()`; run RF and XGB on `features_v0.parquet`.
2. Evaluate on `val`; start a **tuning log** table in `03b_supervised_models.ipynb`.
3. Report data problems to Supriye through GitHub Issues.

**Done when:** v0 scores exist, and the first validation numbers are logged.

### Y9 · Wed Nov 4 · Tuning workflow
Build it on v0 now, so that on Mon Nov 9 you only re-run it on v1.
1. **RF grid:** `n_estimators` {200, 500} × `max_depth` {None, 10, 20} × `min_samples_leaf` {1, 5} × `max_features` {"sqrt", 0.5}.
2. **XGB grid:** `max_depth` {3, 6} × `learning_rate` {0.05, 0.1} × `subsample` {0.8, 1.0} × `min_child_weight` {1, 5}; the number of trees comes from early stopping.
3. Select by **validation PR-AUC**. Never look at test results while tuning.
4. Each run adds a row to the tuning log (parameters, val PR-AUC, val ROC-AUC, training time).

**Done when:** one call runs a whole grid and fills the log.

### Y10 · Thu Nov 5 · Imbalance experiment
1. For XGBoost (and RF if time), compare three set-ups:
   - (a) no weighting
   - (b) class weights (`class_weight="balanced"` / `scale_pos_weight`)
   - (c) **SMOTE on the training set only**, using `imblearn.pipeline.Pipeline([("smote", SMOTE(sampling_strategy=0.1, random_state=42)), ("model", ...)])` so that oversampling happens only during `fit`
2. Never apply SMOTE to val or test data.
3. Record val PR-AUC and recall at top-1% for each set-up; pick the best one for the final models.

**Done when:** the 3-row (or 6-row) table is saved as `results/tables/imbalance.csv`.

### Y11 · Fri Nov 6 · `explain.py` (SHAP) → share with Arva
1. `get_shap_values(fitted_pipeline, X)`: pull the model out of the pipeline, apply the scaler to X, and use `shap.TreeExplainer`. It works for **Random Forest, XGBoost and Isolation Forest**. For RF classifiers, keep the values for class 1.
2. To keep it fast, explain a **sample**: all positive rows in `test` + 5,000 random negatives (`random_state=42`).
3. `plot_summary(shap_values, X)`: beeswarm plot (global importance).
4. `plot_waterfall(shap_values, X, row)`: explanation of one user-day.
5. `top_features(shap_values, feature_names, k=10)`: mean |SHAP| ranking.
6. Push, and post a usage example for Arva (case studies, A19).

**Done when:** all functions work on the v0 XGBoost and Isolation Forest, and Arva has confirmed.

### Y12 · Sat Nov 7 · Leave-one-scenario-out (LOSO) code — the "unseen anomaly" experiment
**Goal:** test whether a supervised model can detect an attack **type it has never seen**.
1. Write `run_loso(df, model_name, params, held_out)` for `held_out` in {1, 2, 3}:
   - **Training rows:** `split == "train"`, **excluding every row of the held-out scenario's insider users** (both their malicious and their normal days, so the model never sees those people).
   - **Test rows:** `split == "test"` with `scenario in {0, held_out}`. Leave out the other scenarios' malicious days, so the test measures only the unseen attack.
   - Report **PR-AUC, ROC-AUC and recall at top-1%**. No validation threshold is needed, which keeps it simple and fair.
   - Save as `<model>_loso_s<held_out>.parquet`.
2. Write `loso_table(...)`: for each held-out scenario, put RF and XGB (LOSO) next to **Isolation Forest and AE evaluated on the same test rows**. Unsupervised models never use labels, so for them every scenario is unseen.
3. Test it on synthetic data.
4. Read **L7** (Y-LIT3).

**Done when:** `run_loso()` and `loso_table()` work on synthetic data.

### Y13 · Sun Nov 8 · Notes for the paper + reading
1. Start the **hyperparameter table T4** for RF and XGB.
2. Write bullet notes for IV-C (supervised) and V in `paper/notes_ayo.md`: set-up decisions and why.
3. Read **L8** and **L11a** (Y-LIT4); find L11a first using TEAM_PLAN 7.3 and post the title in chat.

**Done when:** the notes file exists, and the L8/L11a notes are written.

### Y14 · Mon Nov 9 · Retrain and tune on v1
1. Attend the v1 walkthrough at stand-up.
2. Run the Y9 grids on `features_v1.parquet` with the imbalance set-up chosen in Y10.
3. Record the best settings in the tuning log and T4.

**Done when:** the best RF and XGB settings are chosen by validation PR-AUC.

### Y15 · Tue Nov 10 · Final scores + timing
1. If Supriye releases `features_v1_1.parquet` at 12:00, use it.
2. Produce the final `random_forest.parquet` and `xgboost.parquet` for **all rows**.
3. **Timing:** training time, and inference time per 1,000 user-days, averaged over 3 runs with `time.perf_counter()`. Note your CPU and RAM.
4. Commit the tuned settings as the defaults in `models_supervised.py`, so Supriye can run the ablation tomorrow.
5. Check that Arva's unsupervised score files also load in `evaluate_file()`.

**Done when:** all score files available today run through `evaluate_file()` without errors.

### Y16 · Wed Nov 11 · Run LOSO → M3
1. Run `run_loso()` for RF and XGB × 3 held-out scenarios (6 runs).
2. Build **table T6** with `loso_table()`, including Isolation Forest and the AE on the same test subsets.
3. Write 3–4 sentences on what you see. For example, does the supervised PR-AUC drop sharply on the unseen scenario while the unsupervised models stay steady?

**Done when:** T6 is saved as `results/tables/loso.csv`, and all score files are final. → **M3**

### Y17 · Thu Nov 12 · Master comparison
1. `compare_files()` on **all** models: `iforest`, `autoencoder`, (`ocsvm`), `random_forest`, `xgboost`, plus the `_contam` variants. Save `results/tables/model_comparison.csv` (**T5**).
2. **F4:** combined ROC and PR curves (all main models). **F5:** confusion matrices at the best-F1 threshold (one panel per model).
3. Detection delay and user-level recall per model, added to T5 or a separate table.
4. **T8 (timing):** your timings + Arva's (A17) + Supriye's data-processing time (arrives Fri; add it then).
5. Prepare 3–4 slides or a notebook section for the Sat walkthrough.

**Done when:** T5, F4 and F5 are saved, and T8 is complete except Supriye's number.

### Y18 · Fri Nov 13 · SHAP analysis (feature importance)
1. **Global importance:** SHAP summary plots for XGBoost (**F6**, the paper figure), RF and Isolation Forest.
2. **Top-10 features per model**: do the models agree? Count the overlap between their top-10 lists.
3. **Per scenario:** mean |SHAP| over the malicious rows of each scenario. Which features drive scenario 1 vs. 2 vs. 3?
4. Compare with Supriye's ablation (T7): do SHAP and the ablation point to the same feature groups?
5. Save `results/tables/feature_importance.csv`.

**Done when:** F6 and the table are saved, and you have written notes on agreement and per-scenario drivers.

### Y19 · Fri Nov 13 · Related Work paragraphs
Write one paragraph each for **L6, L7, L8, L11a** in Overleaf (II. Related Work), from your notes. For L8 (Log2vec), note its reported CERT results for comparison in T1.

**Done when:** the paragraphs are in Overleaf by Fri night.

### Y20 · Sat Nov 14 · False positive / false negative analysis + walkthrough
Use the **best supervised model** and the **best unsupervised model** (by test PR-AUC), at the best-F1 threshold.

1. **False positives:**
   - Count FPs by `role`, `department`, weekday, and top users.
   - For the 10 highest-scoring FPs, look at their SHAP values or top `z_*` features.
   - Group them into causes, e.g. *IT staff who legitimately work after hours*, *new users with no baseline (cold start)*, *one-off legitimate bulk email*.
   - For each cause, propose a fix (peer-group baselines, role-aware thresholds, longer baselines, analyst feedback).
2. **False negatives:**
   - Count missed malicious days per scenario.
   - For each missed insider, compare their malicious-day features with their own baseline. Why was the score low? Typical reasons: activity too subtle, too short, or the user was already "noisy".
   - Propose a fix for each cause.
3. Save a table of causes with counts (`results/tables/fp_fn_causes.csv`) and coordinate with Arva so the case studies and this analysis don't contradict each other.
4. **Walkthrough:** present T5, T6, F4 and the FP/FN findings; agree with the team on the answer to the research question.

**Done when:** the causes table exists, each cause has a proposed fix, and the walkthrough is done.

### Y21 · Sun Nov 15 · Paper sections IV-C (supervised) + V
Write in Overleaf, in your own words:
- **IV-C Supervised Models (~0.5 page):**
  - why supervised as a comparison (best case with labels)
  - RF (cite Breiman) and XGBoost (cite Chen & Guestrin)
  - imbalance handling and the result of Y10
  - tuning on val by PR-AUC
  - T4
- **V. Experiments & Results (~1.25 pages):**
  - set-up: temporal split, the two operating points, metrics
  - **T5** + **F4** + **F5**, with the main observations
  - the imbalance experiment
  - **T6** (unseen scenarios), with the observation
  - **T8** (timing and detection delay)

**Done when:** both sections are full paragraphs, with every table and figure referenced.

### Y22 · Mon Nov 16 · VI-A, VI-C + precision/recall paragraph → M4
- **VI-A Feature Importance (~0.5 page):** F6, model agreement, per-scenario drivers, link to the ablation (T7).
- **VI-C False Positive / False Negative Analysis (~0.5 page):** the causes table and the proposed mitigations.
- **Precision/recall paragraph** (in V or VI). Use our real numbers: the % of malicious user-days, the accuracy a "always normal" model would get, and why PR-AUC and recall matter more. Cite Saito & Rehmsmeier.

**Done when:** all three are in Overleaf. → **M4**

### Y23 · Tue Nov 17 · Verify every number + polish figures
1. "Restart & Run All" on `04_evaluation.ipynb`; check that the outputs match the CSVs in `results/tables/`.
2. Compare **every number** in V, VI-A and VI-C (and the Abstract) against the outputs; fix any mismatch.
3. Figures: readable at single-column width (font ≥ 8 pt when printed), consistent model colors, clear captions, axis labels with units.

**Done when:** every number in the paper has been checked against the notebook output.

### Y24 · Wed Nov 18 · Review the full draft
Read the whole PDF Supriye circulates (by 18:00); comment in Overleaf by Thu morning. Focus on technical correctness and whether the numbers match.

### Y25 · Thu Nov 19 · Final read-through → submission-ready
Attend the final meeting; fix everything assigned to you the same day.

### Y-LIT · Literature reading
| Task | Date | Papers |
|---|---|---|
| Y-LIT1 | Wed Oct 28 | Saito & Rehmsmeier (2015) — PR vs. ROC under imbalance |
| Y-LIT2 | Sun Nov 1 | **L6** — Liu, De Vel, Han, Zhang & Xiang (2018) |
| Y-LIT3 | Sat Nov 7 | **L7** — Yuan & Wu (2021) |
| Y-LIT4 | Sun Nov 8 | **L8** — Log2vec (2019); **L11a** — one 2022–2026 paper on supervised / explainable insider-threat detection (TEAM_PLAN 7.3). L11b only if time allows |
| — | When writing IV-C / VI-A | Skim Breiman (2001), Chen & Guestrin (2016), Lundberg & Lee (2017) for correct citations |

For each: fill in the note template (TEAM_PLAN 7.4) as `paper/lit_notes/<ID>.md` and add it to Zotero.

---

## 6. Do This Yourself — No AI Agents

On top of the [team-wide list](TEAM_PLAN.md#12-human-only-work-no-ai-agents):

- [ ] **Read L6, L7, L8, L11a and the method papers**, and write their notes and Related Work paragraphs in your own words.
- [ ] **Hand-check the metric functions** with your 10-row paper example (Y3).
- [ ] **Design the LOSO experiment** and be able to explain why it measures "unseen" behavior.
- [ ] **Interpret the SHAP plots**: which features drive detection, and does that make security sense?
- [ ] **Do the FP/FN root-cause analysis** by looking at the actual cases.
- [ ] **Draw the conclusions** from the comparison and the LOSO results.
- [ ] **Write the precision/recall-vs-accuracy explanation** with our real numbers.
- [ ] **Write** IV-C (supervised), V, VI-A and VI-C.
- [ ] **Cross-check every number** in the paper against the notebook output (Y23).
- [ ] **Explain** `evaluate.py`, `models_supervised.py` and `explain.py` line by line if asked.

---

## 7. Your Literature

| ID | Paper | What to extract |
|---|---|---|
| L6 | Liu, De Vel, Han, Zhang & Xiang, IEEE Communications Surveys & Tutorials (2018) | Categories of insider-threat detection approaches |
| L7 | Yuan & Wu, Computers & Security (Elsevier) (2021) | Deep-learning approaches; evaluation challenges (imbalance, metrics) |
| L8 | Liu et al., "Log2vec," ACM CCS (2019) | A strong CERT result for comparison in T1 |
| L11a (L11b optional) | 2022–2026 paper on supervised / explainable insider-threat detection (you find it) | Recent results and XAI methods to compare |
| — | Breiman, Machine Learning (2001) | Random Forest citation |
| — | Chen & Guestrin, ACM KDD (2016) | XGBoost citation |
| — | Lundberg & Lee, NeurIPS (2017) | SHAP citation |
| — | Saito & Rehmsmeier, PLoS ONE (2015) | Why PR curves beat ROC under imbalance |

## 8. Your Models

| Model | Library | Imbalance handling | Score | Key settings to tune |
|---|---|---|---|---|
| **Random Forest** | `sklearn.ensemble.RandomForestClassifier` | `class_weight="balanced"` (or best from Y10) | `predict_proba(X)[:, 1]` | `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features` |
| **XGBoost** | `xgboost.XGBClassifier` | `scale_pos_weight = n_neg / n_pos` (or best from Y10) | `predict_proba(X)[:, 1]` | `max_depth`, `learning_rate`, `subsample`, `min_child_weight` |
| LOSO variants | Same | Same | Same | Same settings as the final models |

## 9. Your Tools
Python, Pandas, NumPy, **Scikit-learn**, **XGBoost**, **imbalanced-learn**, **SHAP**, **Matplotlib/Seaborn**, Jupyter, Git/GitHub.

## 10. Your Evaluation Responsibilities
You own the evaluation for the **whole team** (TEAM_PLAN Section 10):

| Metric / result | Where reported |
|---|---|
| Accuracy (with the explanation of why it misleads) | V |
| Precision, Recall, F1, FPR, FNR at both operating points | T5 |
| ROC-AUC, **PR-AUC** | T5, F4 |
| Confusion matrices | F5 |
| Per-scenario recall | T5 / T6 |
| Unseen-scenario (LOSO) results | T6 |
| Detection time (a) for RF/XGB + **detection time (b)** delay; user-level recall | T8 |
| Imbalance experiment | V |
| Feature importance (SHAP), per scenario | F6, VI-A |
| FP / FN causes | VI-C |
