# Ayo: Supervised Models, Evaluation & Explainability Lead (v2, from Thu Nov 5)

Team rules, contracts and the shared schedule: [TEAM_PLAN.md](TEAM_PLAN.md). Tick progress in [PROGRESS.md](PROGRESS.md) §6.
**[H]** = human-only (TEAM_PLAN 2.6): do it yourself; an AI agent must not do it or tick it.

---

## 1. Executive Summary

### 1.1 Your role
- **Supervised detection:** Random Forest (RF) and XGBoost (XGB), their tuning and the imbalance experiment.
- **Team-wide evaluation:** every metric, both operating points, per scenario, detection delay, timing (T8), the master comparison (T5, F4, F5).
- **Unseen behavior:** the leave-one-scenario-out (LOSO) experiment (T6).
- **Explainability:** SHAP (F6, `feature_importance.csv`) and the false-positive / false-negative (FP/FN) analysis.
- **Results machine:** the paper's comparison numbers come from **your laptop** (TEAM_PLAN 2.5.12).
- **Paper:** IV-C (supervised), V, VI-A, VI-C, the precision/recall paragraph, and verifying every number.

### 1.2 Files you own
- **Code:** `src/models_supervised.py`, `src/evaluate.py`, `src/explain.py`.
- **Tests:** `tests/test_models_supervised.py`, `tests/test_evaluate.py`, `tests/test_explain.py`.
- **Notebooks:** `notebooks/03b_supervised_models.ipynb`, `notebooks/04_evaluation.ipynb` (new).

### 1.3 Already done (Y3–Y13 code by Claude at Supriye's request; you must read and explain it)
- **Y3–Y6:** `evaluate.py`: `threshold_metrics`, `ranking_metrics`, best-F1 and top-k thresholds, `evaluate_file`, `compare_files`, ROC/PR/confusion/score plots, `detection_delay`, `user_level_recall`, `make_synthetic_scores` (#3 via #7).
- **Y7–Y10:** `train_and_score_supervised()` (all train rows, XGB early stopping), `tune_supervised()` (RF 24 runs, XGB 16), `imbalance_experiment()` (no weighting / class weights / SMOTE on training rows only), T4 draft (#23).
  - **v0 results:** best val PR-AUC RF 0.273, XGB 0.324.
  - **Imbalance on v0:** SMOTE (XGB 0.413) and no weighting beat class weights.
- **Y11:** `explain.py`: `get_shap_values()` for RF, XGB and Isolation Forest (positive = more suspicious), `explain_sample()`, `plot_summary()`, `plot_waterfall()`, `top_features()`, plus a v0 demo (#24).
- **Y12:** `loso_masks()`, `run_loso()`, `loso_table()`. The held-out scenario's accounts are kept out of training and early stopping (#25).
- **Y13 (code part):** `hyperparameter_table()` → `T4_hyperparameters_supervised.csv`.

### 1.4 What's left (in order)
1. **Catch-up (Nov 5–8, overdue):** clone + install, `ayo/notes`, reading your code, the Y3 hand-check, reviews, your two design decisions, literature.
2. **Models (Nov 9–11):** tune on v1 → tuned defaults + `final` command + timing → LOSO (T6) → M3.
3. **Analysis (Nov 12–14):** T5, F4, F5, delay, T8 → SHAP (F6, `feature_importance.csv`) → FP/FN → walkthrough.
4. **Paper + finish (Nov 15–19):** IV-C, V, VI-A, VI-C, P/R paragraph, verify every number, reviews, fixes.

---

## 2. Prerequisites / Required Tools

- **GitHub:** collaborator access (`Bizzlefresh`, accepted) and a local clone.
- **Environment:** Python 3.13 venv outside the repo with `requirements.txt` (TEAM_PLAN 2.3). You use xgboost, imbalanced-learn and shap.
- **Data:** the one drop `ueba_data_v1.zip` (Supriye, by Sat Nov 7; TEAM_PLAN 2.5.12). You only need `data/processed/`.
- **Everyone else's scores:** never downloaded. Run `python -m src.models_unsupervised final` (after Arva's A16 merges) and `python -m src.models_supervised final` (yours, Y15) to rebuild all score files on your laptop.
- **Tables from teammates via Git:** `unsupervised_extra.csv` (Arva, A17), `ablation.csv` and `data_processing_time.csv` (Supriye, S22).
- **Tools:** Jupyter, Matplotlib/Seaborn, Overleaf, Zotero.

---

## 3. Step-by-Step Instructions

### Catch-up block: Thu Nov 5 – Sun Nov 8

#### Y1 · Thu Nov 5 · Environment, clone, notes branch (overdue)
1. **Clone** the repo, create the venv and run `pip install -r requirements.txt` (TEAM_PLAN 2.3).
2. **Run** `python -m pytest tests`. Expect 81 passed + 2 skipped without data, or 83 passed with it.
3. **Create** your notes branch: `git checkout -b ayo/notes main`, then `git push -u origin ayo/notes`.
4. **Post** "Y1 done" in chat.

**Done when:** tests pass on your laptop, and `ayo/notes` is on GitHub.

#### REV-Y · Thu Nov 5 – Sun Nov 8 · Read your code, hand-check, reviews
1. **Read** `evaluate.py`, `models_supervised.py` and `explain.py` until you can explain every function [H].
2. **Hand-check** `threshold_metrics()` against your own 10-row paper example (Y3) [H].
3. **Confirm** the hand-offs:
   - **A3:** `from src.synthetic import make_synthetic_features` loads;
   - **M1:** `get_model_matrix(pd.read_parquet('data/processed/features_v0.parquet'), split='train')` works;
   - **Y6:** `evaluate_file()` imports and runs.
4. **Review** on `main` the PRs assigned to you: Supriye's #1, #2, #8, and Arva's #10, #13, #14, #19, #20, #22. Run each "How to test" step.
5. **Open** a GitHub Issue for the owner for anything that needs changing, and tick each review in PROGRESS §7.

**Done when:** every review assigned to you is ticked, and the three confirmations are posted in chat.

#### DEC-Y · by Sun Nov 8 · Your design decisions [H]
1. **Decide** how the final models handle imbalance (Y10). The default rule is the set-up with the highest **v1** val PR-AUC, which Y14 measures; you confirm it or override it with a reason.
2. **Justify** the LOSO design (Y12): why removing a scenario's accounts from training measures "unseen" behavior, and why the test rows keep only scenario 0 + the held-out scenario.
3. **Write** both in `paper/notes_ayo.md` on `ayo/notes`.

**Done when:** both reasons are written down.

#### Y-LIT1–4 · by Sun Nov 8 · Literature (partly overdue) [H]
1. **Read** Saito & Rehmsmeier (Y-LIT1), L6 Liu et al. (Y-LIT2), L7 Yuan & Wu (Y-LIT3), and L8 Log2vec + L11a, plus **L11b, strongly recommended** (Y-LIT4).
2. **Write** `paper/lit_notes/<ID>.md` for each (TEAM_PLAN 3.14 template) on `ayo/notes`, and add each to Zotero.

**Done when:** the notes are on `ayo/notes` (merged with Y13 by Fri Nov 13).

### Models block: Mon Nov 9 – Wed Nov 11

#### Y14 · Mon Nov 9 · Retrain and tune on v1
Branch: `ayo/Y14-final-models` from `main` after M2 (reviewer Supriye).
1. **Fix** the log reset first. In `notebooks/03b_supervised_models.ipynb`, replace `log_path.unlink(missing_ok=True)` with a helper that drops only the current dataset's rows (e.g. `clear_log(dataset)`), so the v0 history stays.
2. **Write** the tuning log by concatenation (`pd.concat([old, new])` + `to_csv(index=False)`), not `mode="a"`. A new column then can't shift the old rows.
3. **Log** which imbalance set-up each run used (a `setup` column); old v0 rows count as `b_class_weights`.
4. **Keep** both datasets in `imbalance.csv`: replace only the current dataset's rows.
5. **Filter** `hyperparameter_table()` by dataset, so T4 shows the v1 choice and its set-up.
6. **Set** `DATASET = 'v1'`, run `imbalance_experiment(df, dataset='v1')`, and pick each model's set-up with the card rule (highest val PR-AUC) [H confirm, DEC-Y].
7. **Run** the RF grid (24 runs) and the XGB grid (16 runs) with each model's chosen set-up: `tune_supervised(df, model, dataset='v1', **setup)`.
8. **Run** the notebook with Restart & Run All.
9. **Add** tests: aligned log after a new column, the setup name per option pair, `imbalance.csv` keeping other datasets, and the T4 dataset filter.

**Done when:** the best RF and XGB settings by val PR-AUC, and their set-ups, are in the tuning log and in `T4_hyperparameters_supervised.csv`.

#### Y15 · Tue Nov 10 · Tuned defaults, `final` command, timing
1. **Use** `features_v1_1.parquet` if Supriye releases it by 12:00.
2. **Commit** the tuned settings as `RF_DEFAULTS` / `XGB_DEFAULTS`, keeping the card values (`RF_CARD`, `XGB_CARD`) for T4.
3. **Add** `FINAL_SETUP = {"random_forest": ..., "xgboost": ...}`, and make `train_and_score_supervised()` use it when `weighting` and `smote` are left out. Supriye's ablation and your LOSO then use the chosen set-up automatically.
4. **Add** a `final` command, `python -m src.models_supervised final [features_v1]`, that writes `results/scores/random_forest.parquet` and `xgboost.parquet` for **every row** with the defaults. Teammates rebuild your scores this way; **you never send score files**.
5. **Add** `timing(df, model, repeats=3)`: mean fit seconds and inference seconds per 1,000 user-days (`time.perf_counter()`), plus CPU, threads and RAM (`psutil`). It writes `results/tables/timing_supervised.csv`.
6. **Update** `test_card_settings` to pass `RF_CARD` / `XGB_CARD` explicitly, and add tests for `FINAL_SETUP` and `final`.
7. **Run** `python -m src.models_unsupervised final` once Arva's A16 is merged, then `evaluate_file()` on all 7 score files.

**Done when:**
- **PR:** the tuned-defaults PR is merged;
- **Commands:** both `final` commands run on your laptop;
- **Evaluation:** `evaluate_file()` runs on every score file without errors.

#### Y16 · Wed Nov 11 · Run LOSO → T6 → M3
Branch: `ayo/Y16-loso-results` (reviewer Arva).
1. **Create** `notebooks/04_evaluation.ipynb`. Its first cell runs any missing `final` command, so the notebook never depends on received files.
2. **Run** `loso_table(df, unsupervised={'iforest': ..., 'autoencoder': ...})`. RF and XGB use the tuned defaults and set-up (6 runs); IF and the AE are evaluated on the same test rows.
3. **Save** `results/tables/loso.csv` (T6) and a pivot of PR-AUC per held-out scenario.
4. **Write** 3–4 sentences [H]: does supervised PR-AUC drop on the unseen scenario while unsupervised stays steady? Note that held-out scenario 3 has only ~4 test days.

**Done when:** `loso.csv` is merged, and all score files are final → **M3** (Supriye tags `m3-all-scores`).

### Analysis block: Thu Nov 12 – Sat Nov 14

#### Y17 · Thu Nov 12 · Master comparison (T5, F4, F5, delay, T8)
Branch: `ayo/Y17-comparison` (reviewer Arva).
1. **Run** `compare_files()` on all 7 score files, and save `results/tables/model_comparison.csv` (**T5**: both operating points, accuracy, precision, recall, F1, FPR, FNR, ROC-AUC, PR-AUC, user recall, delay).
2. **Add** `per_scenario_table(paths)`, and save `model_per_scenario.csv` (PR-AUC and recall per scenario at both thresholds).
3. **Plot** **F4** with `plot_roc()` and `plot_pr()` on the 5 main models (`F4_roc_curves`, `F4_pr_curves`).
4. **Add** `plot_confusion_grid(paths)` for **F5**: one panel per main model at best-F1.
5. **Add** `delay_table(paths)`, and save `detection_delay.csv` (median and mean delay, user recall, missed insiders).
6. **Add** `timing_table()` for **T8**: it merges `timing_supervised.csv`, the timing columns of `unsupervised_extra.csv`, the best-F1 delay and `data_processing_time.csv`. Save `T8_timing.csv`.
7. **Add** tests on two synthetic score files (per-scenario and delay tables, F5 written, T8 merging all sources).
8. **Prepare** the walkthrough material (a notebook section or 3–4 slides).

**Done when:** T5, F4 and F5 are saved, and T8 is complete (Supriye's row arrives with S22).

#### Y18 · Fri Nov 13 · SHAP analysis (F6, `feature_importance.csv`)
Branch: `ayo/Y18-shap-fpfn` (reviewer Arva).
1. **Explain** `explain_sample(df)` (all test positives + 5,000 negatives) with refitted XGB and RF (tuned defaults) and Isolation Forest (Arva's tuned defaults).
2. **Plot** the summaries: `F6_shap_summary_xgboost` (paper figure), `shap_summary_random_forest`, `shap_summary_iforest`.
3. **Save** `results/tables/feature_importance.csv` (mean |SHAP| per feature per model).
4. **Add** `top10_overlap(rankings)` (shared top-10 features between models) and `per_scenario_importance(sv, rows)` (mean |SHAP| over each scenario's malicious rows); save `feature_importance_per_scenario.csv`.
5. **Compare** with Supriye's `ablation.csv` (T7) and write your reading [H].

**Done when:** F6 and both CSVs are saved, and your notes on agreement and per-scenario drivers are written.

#### Y19 · Fri Nov 13 · Related Work paragraphs [H]
1. **Write** one paragraph each for L6, L7, L8 (note its CERT numbers for T1) and L11a in Overleaf II.
2. **Merge** `ayo/notes` (lit notes + `notes_ayo.md`) by Fri Nov 13.

#### Y20 · Sat Nov 14 · FP/FN analysis + walkthrough
1. **Pick** the best supervised and best unsupervised model by test PR-AUC from T5, at the best-F1 threshold.
2. **Add** `fp_fn_rows()`, `fp_breakdown()`, `top_deviations()` and `fn_breakdown()` to `evaluate.py`, with tests.
3. **Save** `fp_breakdown.csv` (by role, department, weekday, user), `fp_top10.csv` (with each FP's top `z_user` features) and `fn_by_insider.csv` (missed days per scenario and insider).
4. **Group** the FPs into causes and explain each missed insider; propose a fix per cause; save `results/tables/fp_fn_causes.csv` [H].
5. **Present** T5, T6, F4 and the FP/FN findings at the walkthrough, and agree on the answer to the research question.

**Done when:** `fp_fn_causes.csv` exists with a fix per cause, and the walkthrough is done (Supriye tags `analysis-done`).

### Paper + finish block: Sun Nov 15 – Thu Nov 19

#### Y21 · Sun Nov 15 · IV-C (supervised) + V [H]
1. **Write** IV-C: why supervised (the best case with labels); RF (cite Breiman) and XGB (cite Chen & Guestrin); imbalance handling and the Y10 result; tuning on val by PR-AUC; T4.
2. **Write** V: set-up (temporal split, two operating points, metrics); T5 + F4 + F5 with observations; the imbalance experiment; T6; T8 with detection delay.

#### Y22 · Mon Nov 16 · VI-A, VI-C, P/R paragraph → M4 [H]
1. **Write** VI-A (F6, model agreement, per-scenario drivers, link to T7) and VI-C (causes table + mitigations).
2. **Write** the precision/recall paragraph: 0.298% malicious, so "always normal" scores 99.70% accuracy with 0 recall. Cite Saito & Rehmsmeier.

#### Y23 · Tue Nov 17 · Verify every number + polish figures
Branch: `ayo/Y23-verify` (reviewer Supriye).
1. **Run** both `final` commands, then Restart & Run All on `04_evaluation.ipynb`, on your laptop (the results machine).
2. **Check** every number in V, VI-A, VI-C and the Abstract against `results/tables/`, and fix mismatches.
3. **Polish** the figures: ≥ 8 pt text at column width, `MODEL_COLORS` consistent, captions, axis labels.

**Done when:** every number in the paper has been checked against the notebook output.

#### Y24 · Wed Nov 18 · Review the full draft
1. **Comment** in Overleaf by Thu morning, focusing on technical correctness and matching numbers.

#### Y25 · Thu Nov 19 · Final read-through
1. **Attend** the read-through, and fix everything assigned to you the same day (`ayo/Y25-final-fixes` if code changes).

---

## 4. Edge Cases & Troubleshooting

- **v1 supervised scores look near-perfect:** an unsaved Nov 5 run gave val PR-AUC ≈ 0.95–0.99 with all inputs, ≈ 0.99 without the psychometrics, and 0.51 val / 0.38 test with only raw `f_*`. Re-run, check against SHAP (Y18) and the ablation (T7), and say clearly in V that the baselines drive it.
- **XGBoost stops at iteration 0:** this happens on synthetic data (24 val positives, `scale_pos_weight` ≈ 374). On real data it trains 81–221 trees; `min_child_weight=5` helps.
- **SMOTE leaks into val/test:** it can't if SMOTE stays inside the imblearn `Pipeline` and you predict with that pipeline. Never call SMOTE on a full table.
- **`evaluate_file()` on a LOSO file gives an infinite best-F1 threshold:** LOSO files hold only test rows. Use `loso_metrics()` / `loso_table()` for T6.
- **SHAP returns 3-D values for RF:** `get_shap_values()` keeps class 1 already. For IF it flips the sign so positive = anomalous.
- **The tuning-log CSV has shifted columns:** it was appended with a new column; rebuild it with `pd.concat` (Y14 step 2).
- **Arva's numbers differ slightly from yours for the AE:** expected across CPUs. Your laptop is the results machine; don't trade score files.
- **Someone asks you for score files:** send the command (`python -m src.models_supervised final`), not files.
- **Scenario 3 results swing wildly:** only ~4 test days. Report counts next to rates, and rely on LOSO + the case studies.
- **`UnicodeEncodeError` on Windows:** set `PYTHONIOENCODING=utf-8`.

---

## 5. Success Metrics / Definitions

| Task | Verified by |
|---|---|
| Y1 | Tests pass on your laptop; `ayo/notes` on GitHub |
| REV-Y | Your reviews ticked in PROGRESS §7; Y3 hand-check written; A3/M1/Y6 confirmations posted |
| DEC-Y | Imbalance choice and LOSO justification in `paper/notes_ayo.md` |
| Y14 | v1 rows (with `setup`) in the tuning log, v0 rows kept; `imbalance.csv` has v0 + v1; T4 shows the v1 best |
| Y15 | Tuned defaults + `FINAL_SETUP` + `final` merged; `timing_supervised.csv` (3-run means + CPU/RAM); `evaluate_file()` runs on all 7 files |
| Y16 | `loso.csv` (6 supervised + unsupervised rows per scenario) → M3 |
| Y17 | `model_comparison.csv` (T5), `model_per_scenario.csv`, `detection_delay.csv`, `T8_timing.csv`, F4, F5 |
| Y18 | F6 + `feature_importance.csv` + `feature_importance_per_scenario.csv`; notes written |
| Y20 | FP/FN tables + your `fp_fn_causes.csv` with fixes; walkthrough done |
| Y21, Y22 | IV-C, V, VI-A, VI-C, P/R paragraph drafted → M4 |
| Y23 | Every paper number traced to a CSV on the results machine |

**Your numbers in the paper:**
- **T5, F4, F5:** all metrics at both operating points.
- **T6:** LOSO.
- **T8:** timing + delay.
- **F6 / VI-A:** SHAP.
- **VI-C:** FP/FN causes.
- **V:** the imbalance experiment and the P/R paragraph (0.298% / 99.70%).
