# Arva's notes

<!--
How this file works:
- The headings and the comments are scaffolding. Everything after "Decision:" and "Reason:" is yours to write (TEAM_PLAN 2.6: design decisions and their reasons are human-only).
- Each comment holds the evidence on main (from the facts sheet) and the questions a reason should answer. Delete the comments when you're done.
- A good reason is 2-3 sentences: the decision, the evidence that supports it, and the trade-off or limit you accept.
-->

## DEC-A: design decisions

### 1. Autoencoder architecture and the tuning grids

<!--
Evidence (T4_hyperparameters_unsupervised.csv, tuning_log_unsupervised.csv on main):
- AE grid (16 runs): bottleneck {8, 16} x hidden {(64,32), (128,64)} x dropout {0, 0.1} x lr {1e-3, 1e-4}.
- Best by val PR-AUC: 76-128-64-16-64-128-76, no dropout, lr 1e-3. Val PR-AUC 0.109 (ROC-AUC 0.919). The card's 76-64-32-16-32-64-76 got 0.092.
- IF grid (18 runs): n_estimators {100, 200, 500} x max_samples {256, 1024, auto} x max_features {0.5, 1.0}. Best: 100 trees, 256 samples, all features, val PR-AUC 0.0156 (card 0.0147). Here max_samples 256 and "auto" build the same forest.
- Fit time on the M1 (T8): AE 20.9 s, IF 0.23 s.
- Selection used val only. Test was never used for tuning (TEAM_PLAN 2.5.4).

Questions your reason should answer:
- Why a bottleneck of 8-16 for 76 inputs? A bottleneck forces compression; if it's too wide, the network can copy anomalies back as well as normal days.
- Why compare those two widths and depths, and that dropout and those learning rates? What range did the grid cover, and what did it leave out?
- Do you accept "best val PR-AUC" as the rule, and why PR-AUC rather than ROC-AUC at a 0.3% base rate?
- Is the gain (0.092 to 0.109 on val) worth the larger network?
-->

**Decision:** Keep the tuned default 76-128-64-16-64-128-76 (no dropout, lr 1e-3) and the grids as run in #50 (decided Nov 17).

**Reason:**
<!-- What you said in chat on Nov 17, to turn into your reason: you first proposed 128-64-32, citing L4 (Tuor et al.: DNN and LSTM with 1-6 hidden layers, 20-500 units per layer, tanh, Adam; the DNN retrained daily, the LSTM with a per-user state). You then kept 128-64-16, the v1 grid winner by val PR-AUC, because T5-T8, the FP/FN tables and the case studies were all built from it on the M1, and a bottleneck of 32 was never tested. -->

### 2. Alert levels (`HIGH`, `MEDIUM` in `src/risk_scoring.py`, now 99 / 95)

<!--
Evidence:
- Daily risk = the percentile of a day's score among the normal training days. 99 means "more unusual than 99% of normal training days". The code comment ties High = 99 to the top-1% alert budget (the threshold rule is TEAM_PLAN 2.5.6).
- Alert volume (unsupervised_extra.csv, M1, test period): the top-1% budget is 6.14 alerts per test day for every model. At best-F1: IF 71.7/day (recall 0.52), AE 3.67/day (recall 0.165), OCSVM 0.10/day (recall 0.05).
- Not on file: alerts per day at daily risk >= 99 and >= 95. Claude can compute it once data/ is on this Mac.
- Depends on the levels: top_risky_users*.csv (high_days, medium_days, alert_level), F8's lines and IV-D.

Questions your reason should answer:
- What should High mean to an analyst (act now) and Medium (watch)? How many alerts per day can one analyst handle?
- Why the 99th and 95th percentiles rather than, say, 99.5 / 98? What do you gain or lose in missed insiders vs. alert load?
- Does the same level suit every model, given they're percentiles of each model's own normal scores?
-->

**Decision:** Keep HIGH = 99 and MEDIUM = 95 (decided Nov 17).

**Reason:**
<!-- What you said in chat on Nov 17: 95 gives more false positives and 99 is less sensitive. You considered High = 98 (between the two), then kept 99 / 95 because 99 is already used in the code, tests and outputs. -->

### 3. Keep or drop the One-Class SVM

<!--
Evidence (T5, model_per_scenario.csv, T8):
- Test PR-AUC 0.057, ROC-AUC 0.741. At best-F1: precision 0.818, recall 0.053.
- Per-scenario PR-AUC s1 / s2 / s3: 0.741 / 0.007 / 0.097 (IF 0.004 / 0.010 / 0.003; AE 0.923 / 0.024 / 0.338).
- Trains on <= 20k train rows. Fit 0.52 s; inference 0.039 s per 1,000 user-days, the slowest unsupervised model.
- It's optional in TEAM_PLAN 2.7.3. On v0 its val ROC-AUC was 0.26; on v1 it's 0.775.

Questions your reason should answer:
- Does it add something IF and the AE don't (a different notion of "normal", high precision at a tiny recall)?
- Is it a fair comparison when it sees at most 20k rows?
- If you keep it, what does IV-C say about it? If you drop it, which files, tables and figures lose a row?
-->

**Decision:** Leave the One-Class SVM out of the paper's comparison; report the Isolation Forest and the autoencoder. Its code and the committed tables stay as they are (decided Nov 17).

**Reason:**
<!-- What you said in chat on Nov 17: it catches about 5% of malicious days and adds noise, and both L4 (Tuor et al.) and L5 (Lu & Wong) compare against an SVM and report it doing worse than their LSTM. Check both claims against your L4 and L5 notes before citing them. -->

### 4. Which model F8 uses

<!--
Evidence:
- F8 (results/figures/F8_risk_timeline.*) is drawn from the Isolation Forest risk, the pipeline default. The F8 user by the card rule is MAR0955.
- prototype(f8_model="autoencoder") switches it, and Claude can re-run it.
- The AE has the higher test PR-AUC (0.093 vs 0.012); the IF is the prototype's default model.

Questions your reason should answer:
- Which model's risk does IV-D describe, and should F8 show the same one?
- Which gives the clearer picture of one insider over time?
-->

**Decision:** Keep the Isolation Forest risk for F8 (user MAR0955) (decided Nov 17).

**Reason:**
<!-- What you said in chat on Nov 17: keep it as is. (It is also the prototype's default model, used by the README run section and the dashboard.) -->

### 5. Alert-reason cutoff (`MIN_REASON_Z = 1.0` in `src/pipeline.py`)

<!--
Evidence:
- Added in #57 after your Nov 13 review. A z_* feature is named as a reason only if |z| >= 1.0, so reasons like "0.0σ above own baseline" are gone. A row can now have fewer than 3 reasons.
- Supriye's Claude chose 1.0. You decide whether to keep it.

Questions your reason should answer:
- What is the smallest deviation an analyst should be told about?
- What does a higher or lower cutoff hide or show?
-->

**Decision:** Keep MIN_REASON_Z = 1.0 (decided Nov 17).

**Reason:**
<!-- What you said in chat on Nov 17: keep the threshold. -->

## IV-C notes: unsupervised models (A14-rest)

<!--
The A22 card asks IV-C for: why unsupervised; IF (cite Liu, Ting & Zhou); the AE architecture and its score; training on normal days and the contamination variant; OCSVM (cite Schölkopf et al.) if kept; T4. The facts sheet has the numbers.
-->

## IV-D notes: risk scoring and prototype (A14-rest)

<!--
The A22 card asks IV-D for: F2, percentile risk, the 7-day user risk, the alert levels and why, how the reasons are made, and precision@20 (IF 5/20 = 0.25, AE 6/20 = 0.30, 15 test insiders).
-->
