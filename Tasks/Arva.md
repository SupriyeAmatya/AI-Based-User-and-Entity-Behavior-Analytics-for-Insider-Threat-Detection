# Arva: Unsupervised Models, Risk Scoring & Prototype Lead (v2, from Thu Nov 5)

Team rules, contracts and the shared schedule: [TEAM_PLAN.md](TEAM_PLAN.md). Tick progress in [PROGRESS.md](PROGRESS.md) §5.
**[H]** = human-only (TEAM_PLAN 2.6): do it yourself; an AI agent must not do it or tick it.

---

## 1. Executive Summary

### 1.1 Your role
- **Unsupervised detection:** Isolation Forest, the autoencoder (AE), the optional One-Class SVM (OCSVM), and the contamination variants.
- **Risk scoring:** 0–100 daily risk, 7-day user risk, alert levels.
- **The UEBA prototype:** `src/pipeline.py` (ranked users + 3 reasons), the case studies, the optional dashboard, and the demo.
- **Paper:** IV-C (unsupervised), IV-D, VI-B, VIII, figure F2, the README run section.

### 1.2 Files you own
- **Code:** `src/synthetic.py`, `src/models_unsupervised.py`, `src/risk_scoring.py`, `src/pipeline.py`, `app/dashboard.py` (optional).
- **Tests:** `tests/test_synthetic.py`, `test_models_unsupervised.py`, `test_risk_scoring.py`, `test_pipeline.py`, `test_dashboard.py` (optional).
- **Notebooks:** `notebooks/03a_unsupervised_models.ipynb`, `notebooks/05_anomaly_investigation.ipynb`.
- **Docs:** `docs/coverage.md`, `CLAUDE.md`.

### 1.3 Already done (A4–A14 code by Claude at Supriye's request; you must read and explain it)
- **A3:** `make_synthetic_features()` (your PR #10) + the `f_http_job` rename (#13).
- **A4–A6:** `train_and_score()`, Isolation Forest, the AE (n→64→32→16→32→64→n, early stopping) (#14).
- **A7:** `score_risk()`, alert levels High ≥ 99 / Medium ≥ 95 (PROVISIONAL), `rank_users()` (#15).
- **A8:** `feature_errors()` and `train_on="all"` → `<model>_contam` (#19).
- **A9–A10:** `tune()` with the card grids (IF 18 runs, AE 16) and the v0 tuning log. Best val PR-AUC on v0: IF 0.063, AE 0.122 (#20).
- **A11–A12:** `python src/pipeline.py` with saved models in `models/` and 3 readable reasons per user (#21).
- **A13–A14 (code part):** `OneClassSVMDetector` (v0 val ROC-AUC 0.26) and `hyperparameter_table()` → T4 draft (#22).
- **Docs:** `CLAUDE.md` (#9) and the coverage refresh (#27).

### 1.4 What's left (in order)
1. **Catch-up (Nov 5–8):** environment, `arva/notes`, reading the code, your design decisions, reviews, the coverage fixes, literature, the tuning-notebook fix.
2. **Models (Nov 9–11):** tune on v1 → final score files + tuned defaults → per-scenario, contamination, alert-volume and timing results.
3. **Analysis (Nov 12–14):** the prototype on v1, precision@20, F8, the 4 case studies with F7, F2, Related Work, the dashboard (optional).
4. **Paper + finish (Nov 15–19):** IV-C, IV-D, VI-B, VIII, README run section, fresh-clone test + demo, reviews, fixes.

---

## 2. Prerequisites / Required Tools

- **Environment:** Python 3.13 venv outside the repo with `requirements.txt` (TEAM_PLAN 2.3); `python -m pytest tests` passes.
- **Data:** the one drop `ueba_data_v1.zip` from the shared drive (Supriye, by Sat Nov 7; TEAM_PLAN 2.5.12). It holds `features_v0/v1.parquet`, `labels.parquet`, the web cache and the 4 small logs you need for A19. You never need `http.parquet` or the raw archive.
- **Merged code you use:** Ayo's `src/evaluate.py` (metrics, thresholds) and `src/explain.py` (SHAP for A19), and Supriye's `get_model_matrix()`.
- **Compute:** the v1 AE grid takes about an hour on a 24-thread CPU; run it in the background and keep the laptop awake.
- **Tools:** PyTorch (CPU), scikit-learn, joblib, Matplotlib, Jupyter, draw.io or PowerPoint (F2), Streamlit (optional), Overleaf, Zotero.

---

## 3. Step-by-Step Instructions

### Catch-up block: Thu Nov 5 – Sun Nov 8

#### A1-rest · Thu Nov 5 · Environment and notes branch
1. **Install** `requirements.txt` in your venv and run `python -m pytest tests`.
2. **Create** your notes branch: `git checkout -b arva/notes main`, then `git push -u origin arva/notes`.

**Done when:** tests pass on your laptop, and `arva/notes` is on GitHub.

#### REV-A · Thu Nov 5 – Sun Nov 8 · Read your code and do your reviews
1. **Read** `models_unsupervised.py`, `risk_scoring.py`, `pipeline.py` and `synthetic.py` until you can explain every function [H].
2. **Confirm** `src/explain.py` works for your case studies: run `python -m src.explain demo` (Y11 hand-off).
3. **Review** on `main` the PRs assigned to you: Supriye's #4, #5, #6, #11, #12, #16, #17, #18, #26, #28 and Ayo's #3, #24, #25. Run each "How to test" step.
4. **Open** a GitHub Issue for the owner for anything that needs changing.
5. **Tick** each review in PROGRESS §7.

**Done when:** every review assigned to you is ticked, and you've told Ayo whether `explain.py` works for A19.

#### DEC-A · by Sun Nov 8 · Your design decisions [H]
1. **Choose** the AE architecture and both tuning grids, and write down why (A6/A10).
2. **Choose** the alert levels (`HIGH`, `MEDIUM` in `src/risk_scoring.py`, now 99 / 95), and justify them by alert volume vs. recall.
3. **Decide** whether to keep, tune or drop the optional OCSVM: it ranked v0 malicious days *below* random (val ROC-AUC 0.26).
4. **Commit** any changed values on `arva/A15-final-models`, and record the reasons in `paper/notes_arva.md`.

**Done when:** no PROVISIONAL tag is left in `risk_scoring.py`, and the reasons are written down.

#### COV-A · Fri Nov 6 · Correct `docs/coverage.md`
Branch: `arva/docs-coverage-fixes` (any reviewer).
1. **Change** "8 web features" to **7** (`f_http_count`, `_domains`, `_afterhours`, `_job`, `_leak`, `_cloud`, `_hack`) in the Application usage row and in "What's missing".
2. **Soften** "every model logs its fit time and scoring time": scoring time per 1,000 rows is returned in `info` but not saved anywhere until A17/Y15.
3. **Add** T2 (`class_imbalance.csv`) and T3 (`docs/feature_dictionary.md`) to the "exists" list in the Research paper row.

**Done when:** the PR is merged.

#### A-LIT1–4 · by Sat Nov 7 · Literature (overdue) [H]
1. **Read** the Isolation Forest paper + skim Chandola et al. (A-LIT1), L4 Tuor et al. (A-LIT2), L5 Lu & Wong (A-LIT3), and L10a, plus **L10b, strongly recommended** (A-LIT4).
2. **Write** `paper/lit_notes/<ID>.md` for each (TEAM_PLAN 3.14 template) on `arva/notes`, and add each to Zotero.

**Done when:** the notes are on `arva/notes` (merged with A14 by Fri Nov 13).

### Models block: Mon Nov 9 – Wed Nov 11

#### A15 · Mon Nov 9 · Retrain and tune on v1
Branch: `arva/A15-final-models` from `main` after M2 (reviewer Supriye).
1. **Fix** the log reset first. In `notebooks/03a_unsupervised_models.ipynb`, replace `log_path.unlink(missing_ok=True)` with a helper that drops only the current dataset's rows, e.g. `clear_log(dataset)` in `models_unsupervised.py`, so the v0 history stays.
2. **Write** the log by concatenation (`pd.concat([old, new])`), not `to_csv(mode="a")`, so the columns stay aligned if one is added.
3. **Filter** `hyperparameter_table()` to one dataset and to `train_on == "normal"` runs, so T4 shows the v1 choice.
4. **Set** `DATASET = 'v1'` and run the card-settings reference, the IF grid (18 runs) and the AE grid (16 runs), each with `tune(df, model, dataset='v1')`.
5. **Train** the `_contam` variants with the chosen settings: `tune(df, model, grid={}, fixed=best, dataset='v1', train_on='all')`.
6. **Run** the notebook with Restart & Run All in the background (about an hour).

**Done when:** the best IF and AE settings by val PR-AUC are in the tuning log and in `T4_hyperparameters_unsupervised.csv`.

#### A16 · Tue Nov 10 · Final scores + tuned defaults
1. **Use** `features_v1_1.parquet` if Supriye releases it by 12:00; otherwise v1.
2. **Commit** the tuned settings as the detector defaults in `models_unsupervised.py`, keeping the card values (e.g. a `card` dict) for T4. Supriye's ablation and Ayo's comparison depend on these defaults.
3. **Add** a `final` command, `python -m src.models_unsupervised final [features_v1]`, that writes the score files for **every row** with the defaults (no grid search): `iforest`, `autoencoder`, `iforest_contam`, `autoencoder_contam` and `ocsvm` (if kept). This is how teammates get your scores; **you never send score files** (TEAM_PLAN 2.5.12).
4. **Update** tests that assume the card AE architecture (e.g. `[64, 32, 16, 32, 64, n]`) to read the sizes from `detector.params`.
5. **Run** `evaluate_file()` on every score file in the notebook.
6. **Delete** the stale `models/*_features_v1.*` files, or run the pipeline with `--retrain`, because `pipeline.py` reuses a saved model whenever the columns match.
7. **Add** a test that `final` writes the expected files on synthetic data (patch `SCORES_DIR` to `tmp_path`).
8. **Post** the merged commit; teammates run `python -m src.models_unsupervised final` themselves.

**Done when:** the tuned-defaults PR is merged, and Ayo confirms `final` + `evaluate_file()` run on his laptop.

#### A17 · Wed Nov 11 · Per-scenario results, contamination, alert volume, timing → M3
Branch: `arva/A17-results` (reviewer Ayo).
1. **Add** `results_extra(df)` to `models_unsupervised.py`, with one row per final score file:
   - **Ranking:** test PR-AUC and ROC-AUC;
   - **Operating points:** precision, recall and user-level recall at best-F1 and top-1%;
   - **Per scenario:** recall for scenarios 1, 2 and 3 at both thresholds, and PR-AUC per scenario;
   - **Alerts per day:** at both thresholds (mean flagged user-days per test day);
   - **Contamination effect:** `<model>_contam` PR-AUC minus `<model>` PR-AUC.
2. **Add** `timing(df, model, repeats=3)`: mean fit seconds and inference seconds per 1,000 user-days over 3 runs (`time.perf_counter()`), plus CPU, threads and RAM (`psutil`).
3. **Add** tests: alerts-per-day on a toy frame; a `results_extra()` row with every column; missing score files are skipped.
4. **Run** it on the score files `final` wrote on your laptop, which writes `results/tables/unsupervised_extra.csv`. It reaches Ayo through the merged PR, not by chat or drive.
5. **Write** what the per-scenario and contamination numbers mean in your notes [H].

**Done when:** the CSV has all four result groups for every file, and Ayo has it → **M3**.

### Analysis block: Thu Nov 12 – Sat Nov 14

#### A18 · Thu Nov 12 · Prototype on v1
Branch: `arva/A18-prototype-cases` (reviewer Ayo).
1. **Run** `python src/pipeline.py --features data/processed/features_v1.parquet --model iforest --top 20 --retrain`, then the same with `--model autoencoder`.
2. **Add** `precision_at_k(table, risk, k=20)`: how many of the top 20 users have malicious days in the test period, plus recall of test insiders.
3. **Add** `plot_risk_timeline(risk, user)` to `risk_scoring.py` for **F8**: daily risk, 7-day user risk, malicious days shaded, the High and Medium lines, and the test period marked.
4. **Pick** the F8 user as the test-period insider with the highest 7-day risk, and save `F8_risk_timeline.png/.pdf`.
5. **Save** `results/tables/top_risky_users.csv` (IF), `top_risky_users_autoencoder.csv` and `precision_at_20.csv`.
6. **Run** *(only if S24 was agreed)* IF and the AE on `lanl_features.parquet`, and save `iforest_lanl` / `autoencoder_lanl`.

**Done when:** `top_risky_users.csv`, `precision_at_20.csv` and F8 are saved.

#### A19 · Fri Nov 13 – Sat Nov 14 · Case studies (`notebooks/05_anomaly_investigation.ipynb`)
1. **Pick** 4 test-period cases with Isolation Forest at its best-F1 threshold: for each scenario, the highest-scoring true positive (or its highest-scoring **missed** day if none, and tell Ayo), plus the highest-scoring normal day (top false positive) [H confirms the picks].
2. **Show** the context for each: user, role, date, score, daily risk, user risk, alert level.
3. **Show** baseline vs. flagged day: the top 5 baselined features by |z_user|, with the day's value, the mean of the user's previous 30 active days, `z_user` and `z_peer`.
4. **Draw** **F7**: an IF SHAP waterfall (`explain.get_shap_values(detector, X)` → `plot_waterfall`) and an AE bar chart of the 10 largest `feature_errors()`.
5. **List** the raw evidence: every logon, USB, file and email event of that user that day from the 4 small Parquet logs in the drop, plus that day's web domains, visit counts and after-hours visits from `data/processed/http_user_day_domain.parquet`. Don't ask for `http.parquet`.
6. **Write** the narrative (4–6 sentences) [H] and the analyst verdict (escalate or not, and why) [H].
7. **Present** 2 cases at the Sat walkthrough.

**Done when:** all 4 cases have all 6 parts, and the F7 figures are saved.

#### A14-rest · by Fri Nov 13 · F2 + section notes [H]
1. **Draw** **F2** (raw logs → features → baselines → models → risk score → ranked alerts + reasons) and export PNG + PDF to `results/figures/F2_pipeline.*`.
2. **Write** bullet notes for IV-C and IV-D in `paper/notes_arva.md`.
3. **Merge** `arva/notes` (lit notes + F2 + notes) by Fri Nov 13.

#### A20 · Fri Nov 13 · Related Work paragraphs [H]
1. **Write** one paragraph each for L4, L5 and L10a in Overleaf II, saying how each relates to our approach.

#### A21 · Sat Nov 14 · Dashboard *(optional, only after A19)*
Branch: `arva/A21-dashboard` (reviewer Supriye).
1. **Build** `app/dashboard.py` (`streamlit run app/dashboard.py`): the ranked table, a user selector with the risk timeline, and the 3 reasons for a chosen day. Reuse `pipeline.run()`, `get_detector()`, `contributions()` and `alert_reasons()`.
2. **Keep** the data functions testable outside Streamlit, and add `tests/test_dashboard.py`.

**Done when:** it starts and shows all 3 parts, or it is explicitly skipped.

### Paper + finish block: Sun Nov 15 – Thu Nov 19

#### A22 · Sun Nov 15 · IV-C (unsupervised), IV-D, VI-B [H]
1. **Write** IV-C: why unsupervised; IF (cite Liu, Ting & Zhou); the AE architecture and score; training on normal days and the contamination variant; OCSVM (cite Schölkopf et al.) if kept; T4.
2. **Write** IV-D: F2, percentile risk, 7-day user risk, the alert levels and why, how the reasons are made, precision@20.
3. **Write** VI-B: the 2–3 strongest cases with F7 (and F8): what happened, why it was flagged, the verdict.

**Done when:** all three are full paragraphs, with T4, F2, F7 and F8 referenced.

#### A23 · Mon Nov 16 · VIII + README run section → M4
1. **Write** VIII: the agreed answer to the research question in 2–3 sentences, the main findings, and future work (LSTM, cite L5; graphs, cite L8; streaming; LANL authentication data; analyst feedback).
2. **Add** a "Run the prototype" section to `README.md` with the exact commands, on `arva/A23-readme-run` (reviewer Supriye).

#### A24 · Tue Nov 17 · Fresh-clone test + demo rehearsal
1. **Clone** into a new folder, install, unzip `ueba_data_v1.zip`, run `python -m src.models_unsupervised final`, then `python src/pipeline.py`. Fix anything machine-specific on `arva/A24-fresh-clone-fixes`.
2. **Write** a 3-minute demo script (pipeline → top 20 → one case → its reasons), and rehearse it with a timer.

**Done when:** the pipeline runs from the fresh clone, and the demo fits in 3 minutes.

#### A25 · Wed Nov 18 · Review the full draft
1. **Comment** in Overleaf on the PDF by Thu morning: technical errors, numbers that don't match, unclear text, especially in your own sections.

#### A26 · Thu Nov 19 · Final read-through
1. **Attend** the read-through, and fix everything assigned to you the same day (`arva/A26-final-fixes` if code changes).

---

## 4. Edge Cases & Troubleshooting

- **The v0 rows vanish from the tuning log:** the old notebook deletes the whole log at the start; apply A15 steps 1–2 first.
- **The log CSV has shifted columns:** it was appended with a different column set. Rebuild it with `pd.concat` and re-run the affected dataset.
- **The pipeline prints old results after re-tuning:** `models/<model>_features_v1.*` holds the old model. Use `--retrain` or delete the file.
- **`UnicodeEncodeError` on "σ":** run with `PYTHONIOENCODING=utf-8` on Windows.
- **AE tuning is slow with `lr=1e-4`:** it may run all 50 epochs. Run the grid in the background, and don't lower `patience` just to save time.
- **IF looks weak on v1** (val PR-AUC ≈ 0.014 in an unsaved Nov 5 run): report it honestly; check the per-scenario numbers (A17) and the AE.
- **OCSVM ranks malicious days as normal:** it's optional, so drop it (or try a smaller `gamma`), and say so in IV-C.
- **No true positive for a scenario in A19:** use that scenario's highest-scoring missed day, and tell Ayo for the FP/FN analysis.
- **You need web evidence for a case:** use the web cache `http_user_day_domain.parquet` (domains, visits, after-hours per user-day); `http.parquet` is deliberately not in the drop.
- **Ayo's or Supriye's numbers differ slightly from yours:** the AE is not bit-identical across CPUs. The paper uses the results machine's numbers (TEAM_PLAN 2.5.12); never swap score files to "fix" it.
- **Someone asks for your score files or models:** send the command (`python -m src.models_unsupervised final`), not the files.
- **A test asserts the old AE architecture:** read the layer sizes from `detector.params` (A16 step 4).
- **A stacked PR closes on merge:** retarget it to `main` before merging its base (TEAM_PLAN 3.9).

---

## 5. Success Metrics / Definitions

| Task | Verified by |
|---|---|
| A1-rest | Tests pass on your laptop; `arva/notes` on GitHub |
| REV-A | Every review assigned to you ticked in PROGRESS §7; you can explain your 4 modules |
| DEC-A | No PROVISIONAL in `risk_scoring.py`; reasons in `paper/notes_arva.md` |
| COV-A | `coverage.md` fixes merged |
| A15 | v1 rows in `tuning_log_unsupervised.csv` (v0 rows kept); T4 shows the v1 best |
| A16 | Tuned defaults + `final` command merged; `final` writes 5 score files (4 if OCSVM dropped) for every row on any laptop; `evaluate_file()` runs on each |
| A17 | `unsupervised_extra.csv` with per-scenario recall, contamination delta, alerts/day, 3-run timing + CPU/RAM → M3 |
| A18 | `top_risky_users.csv`, `precision_at_20.csv`, F8 saved |
| A19 | 4 cases × 6 parts in notebook 05; F7 saved; narratives and verdicts are yours |
| A14-rest, A20, A22, A23 | F2 saved; II, IV-C, IV-D, VI-B, VIII drafted; README run section merged |
| A24 | Fresh-clone run works; demo ≤ 3 min |

**Your numbers in the paper:**
- **T4:** IF/AE/OCSVM settings.
- **T8:** unsupervised fit time and inference time per 1,000 user-days (via Ayo).
- **V / VI-B:** per-scenario recall (every scenario is "unseen" for unsupervised models), the contamination effect, alerts per day, precision@20.
