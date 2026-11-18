# Progress Checker (v2)

**Last updated:** Tue Nov 17, 2026 (`main` at `dd84ba8`) · **Submit:** Fri Nov 20 (ready Thu Nov 19)
Plan: [TEAM_PLAN.md](TEAM_PLAN.md) · Task cards: [Supriye.md](Supriye.md), [Arva.md](Arva.md), [Ayo.md](Ayo.md)

---

## 1. Executive Summary

### 1.1 Snapshot (Tue Nov 17, checked against the repo and GitHub)
- **Code:**
  - **Merged:** PRs #1–#63 and #66 (#64 is an Issue, #65 is open); 193/193 tests on `main` (with `data/`).
  - **Every score file is final on v1:** the four main models have tuned defaults (Y15 #41, A16 #50); One-Class SVM runs at its card values (keep or drop is DEC-A). Tag `m3-all-scores`; M3 ticked (#66).
  - **Results on `main`:**
    - T5 `model_comparison.csv`, the per-scenario and delay tables, F4, F5 and T8 (#48, #52);
    - T6 `loso.csv` (#46, #52) and T7 `ablation.csv` (#51);
    - F6 and `feature_importance*.csv` (#53), and the FP/FN tables (#55);
    - `unsupervised_extra.csv` (#66);
    - the prototype outputs `precision_at_20.csv`, `top_risky_users*.csv` and F8 (#57, #66);
    - notebook 05 with the 4 case studies and F7 (#58, #66);
    - the Streamlit dashboard (A21, #63);
    - the README Results and "Run the prototype" sections (#54, #59, #61).
  - **Not on `main`:** F2 (the pipeline figure, Arva [H]); `paper/lit_notes/` is empty, and no notes branch is on GitHub.
- **Data:**
  - **Feature table v1 is frozen:** 330,268 user-days, 76 inputs, tag `m2-features-v1` (Nov 8).
  - **The data drop** is delivered; both teammates load v1.
  - **Bug-fix window** closed Tue Nov 10 12:00 with no feature bug, so there is no `features_v1_1.parquet`.
- **People:**
  - **Reviews:** since #39 every PR had an approving review before merge (branch protection).
  - **Post-merge reviews (§3.7):** Ayo's 9 are done (#62); Supriye's 5 are in open PR #65; Arva's 13 are open.
  - **Issue #64** (Arva): CLAUDE.md's PROVISIONAL list misses `MIN_REASON_Z`, and coverage.md's Nov 13 snapshot is out of date.
  - **Drafts for [H] work:** Claude drafts exist for Y18-H and Y20-H (`fp_fn_causes.csv`). Ayo checks them and ticks.
- **Decisions:**
  - **Supriye:** her 5 are final (Nov 6).
  - **Ayo:** the imbalance set-up is recorded in #41. The DEC-Y reasons and the LOSO justification are not written yet.
  - **Arva (DEC-A):** the AE architecture reasons, the alert levels (99 / 95) and the OCSVM decision are open, and so is the reasons floor `MIN_REASON_Z` (an open [H] sub-box of A18).
  - **Course rules (S3-rest):** page limit, AI-use policy and submission contents are not confirmed in TEAM_PLAN.
- **Milestones:**
  - **Done:** M0, `evaluate.py` ready, the split dates, M2, the tuned models and M3 (tags `m0-setup`, `m2-features-v1`, `m3-all-scores`).
  - **Open:** the kickoff (status unknown), M1 (the teammates' v0 confirmations), the `explain.py` confirmation, and "Analysis done" (the walkthrough is not recorded and the A18/A19 [H] parts are open).
  - **Not visible in the repo:** M4 (all sections drafted, due Mon Nov 16). The paper isn't in Git, and the Overleaf set-up (S2-rest) is still open in this tracker.
  - **Coming up:** M5 and the code freeze on Wed Nov 18; submission-ready on Thu Nov 19.

### 1.2 Next three actions each
| Person | 1 | 2 | 3 |
|---|---|---|---|
| **Supriye** | Paper sections III, IV-A, IV-B, I, VII [H] and the Abstract (M4 overdue; M5 Wed 18:00) | Course rules, AI-use policy above all (S3-rest), and the S22-H ablation reading [H] | Overleaf + Zotero (S2-rest); then the Thu read-through and fresh-clone test (S33, S34) |
| **Arva** | IV-C, IV-D, VI-B, VIII [H] and F2 | DEC-A (alert levels, OCSVM, `MIN_REASON_Z`) and the A19-H narratives and verdicts [H] | Issue #64; his 13 post-merge reviews (§3.7); the fresh-clone test (A24) |
| **Ayo** | IV-C (supervised), V, VI-A, VI-C [H] (Y21, Y22) | Check the Y18-H and Y20-H drafts; DEC-Y reasons; Y23 number check | Post the A3/M1/Y6 confirmations; review #65 |

### 1.3 Counts
| Area | Done | Open |
|---|---:|---:|
| Supriye lines (§3.4) | 21 | 26: setup leftovers, hand-checks, literature, paper, finish |
| Arva lines (§3.5) | 14 | 22: decisions, LIT, [H] parts of A17–A19, paper, A24–A26 |
| Ayo lines (§3.6) | 17 | 23: decisions, LIT, [H] readings, paper, Y23–Y25 |
| Hand-offs (§3.3) | 8 | 8 |
| Post-merge reviews (§3.7, PR rows) | 9 / 27 | 18 (5 of them in #65; plus the open `coverage.md` first-version line) |
| Milestones (§3.1) | 6 / 15 | 9 |

---

## 2. Prerequisites / Required Tools (how to use this file)

- **`[x]`** = done: every "Done when" item of that task card is true (code tasks: PR merged).
- **`[ ]`** = open. Partly done tasks show sub-boxes.
- **[H]** = human-only (TEAM_PLAN 2.6). **AI agents never tick an [H] box.**
- **(Claude)** = written by Claude at Supriye's request. The owner still reads, runs and explains it.
- **Tick** your own lines on the branch where you did the work, in the same PR.
- **Tick** reviews (§3.7) yourself after reviewing on `main`.
- **Update** §1 at least at every stand-up (Mon, Wed, Fri). Supriye owns this file.

---

## 3. Step-by-Step Instructions (checklists)

### 3.1 Milestones
- [ ] **Kickoff** (Thu Oct 29): rules agreed. *Status unknown; the rules are in TEAM_PLAN 2.5*
- [x] **M0 Setup complete** (Sat Oct 31) *(tag `m0-setup` pushed Nov 10, on #41's commit `5bbcf77`)*
  - [x] **Repo cloned:** Supriye, Arva (PRs #9, #10)
  - [x] **Repo cloned + installed:** Ayo (Y1) *(his PRs #41, #46 and #48 report the full test suite and the v1 runs on his laptop)*
  - [x] **Data on the drive:** the one data drop `ueba_data_v1.zip` (S4/S20) *(confirmed by Supriye Nov 8)*
- [x] **`evaluate.py` ready** (Sun Nov 1): merged Nov 3 (#3 via #7)
- [x] **Split dates final** (Mon Nov 2): in TEAM_PLAN 2.5.3 (S8) [H] *Done Nov 6 (#36); reason drafted by Claude at Supriye's request* *Supriye read the Claude-drafted reasons and adopted them as her own (Nov 17, after the whole-project review flagged the ticks).*
- [ ] **M1 Feature table v0** (Tue Nov 3)
  - [x] **v0 + `get_model_matrix()` merged** (#6 via #7, sampler fix #11)
  - [ ] **Arva and Ayo confirm** v0 loads in their code
- [ ] **`explain.py` ready** (Fri Nov 6)
  - [x] **Merged** (#24)
  - [ ] **Arva confirms** it for the case studies
- [x] **M2 Feature table v1 frozen** (Sun Nov 8)
  - [x] **v1 built**, feature dictionary, leakage checks 1/2/3/5 pass (#17, #18)
  - [x] **Decisions final** and v1 rebuilt if needed (S8, S20b) *Decided Nov 6 (#36); values unchanged, rebuild ran clean; reasons written*
  - [x] **Data drop uploaded**; both teammates load v1 *(confirmed by Supriye Nov 8)*
  - [x] **Tag** `m2-features-v1` *(Nov 8, on `main` at `2710789`; feature code unchanged since the drop's commit `e5dc881`; 142 tests pass; the real v1 matches the 76 frozen inputs)* **(Claude)**
- [x] **Tuned models + `final` commands** (Tue Nov 10): A16 and Y15 merged
  - [x] **Y15** merged (#41): tuned `RF_DEFAULTS` / `XGB_DEFAULTS`, `FINAL_SETUP`, `final`
  - [x] **A16** merged (#50): tuned Isolation Forest and autoencoder defaults, `final` (#33)
- [x] **M3 All score files final** (Wed Nov 11): A17, Y16 merged; `evaluate_file()` runs on all *(tag `m3-all-scores` pushed Nov 13; A17's `unsupervised_extra.csv` on `main` from Ayo's M1 on `ayo/A17-m1-results`, Nov 17)*
- [ ] **Analysis done** (Sat Nov 14): T5–T8, F4–F8, FP/FN, cases; walkthrough held
- [ ] **M4 All sections drafted** (Mon Nov 16)
- [ ] **M5 Full draft** circulated by 18:00 (Wed Nov 18)
- [ ] **Code freeze** (Wed Nov 18)
- [ ] **Submission-ready** (Thu Nov 19): fresh-clone test, `final-submission` tag
- [ ] **Submitted** (Fri Nov 20)

### 3.2 Meetings
- [ ] **Kickoff** (Thu Oct 29) *Status unknown*
- [ ] **Stand-ups** Mon Nov 2, Wed Nov 4 *Status unknown*
- [ ] **Stand-up + catch-up check** (Fri Nov 6)
- [ ] **Stand-up + v1 walkthrough** (Mon Nov 9): decide S24
- [ ] **Stand-up** (Wed Nov 11)
- [ ] **Stand-up** (Fri Nov 13)
- [ ] **Results walkthrough**, 45 min (Sat Nov 14): answer agreed
- [ ] **Stand-up** (Mon Nov 16)
- [ ] **Stand-up** (Wed Nov 18)
- [ ] **Final read-through**, 60 min (Thu Nov 19)

### 3.3 Hand-offs (code moves through Git; data moves once; TEAM_PLAN 2.5.12)
| ✓ | Due | What | From → To |
|---|---|---|---|
| [x] | Nov 1 → Nov 3 | `src/evaluate.py` merged | Ayo → all |
| [x] | Oct 29 → Nov 4 | `src/synthetic.py` merged (#10) | Arva → Ayo |
| [ ] | Thu Nov 5 | Overleaf + Zotero invites | Supriye → Arva, Ayo |
| [ ] | Fri Nov 6 | Final decision values (#36, #37 + competitor category) announced in chat | Supriye → all |
| [x] | Sat Nov 7 | **The one data drop** `ueba_data_v1.zip` (~360 MB, checksums) | Supriye → Arva, Ayo |
| [ ] | Sun Nov 8 | v1 frozen + feature dictionary *(tag `m2-features-v1` pushed; announce the freeze in chat)* | Supriye → Arva, Ayo |
| — | Tue Nov 10 12:00 | `features_v1_1.parquet` *(only if needed)* *(not needed: no feature bug was reported, so `features_v1.parquet` stays the final table and no second data drop happens)* | Supriye → Arva, Ayo |
| [ ] | Tue Nov 10 | Merged tuned defaults + `python -m src.models_unsupervised final` *(`final` in #33, tuned defaults in #50 on Nov 10; tick when announced)* | Arva → all (Git) |
| [x] | Tue Nov 10 | Merged tuned defaults + `python -m src.models_supervised final` + `timing_supervised.csv` *(#41, Nov 8)* | Ayo → all (Git) |
| [x] | Wed Nov 11 | `unsupervised_extra.csv` *(code merged in #34/#43; the CSV built on Ayo's M1, on `ayo/A17-m1-results`, Nov 17)* | Arva → Ayo (Git) |
| [x] | Wed Nov 11 | `loso.csv` (T6) *(#46, Nov 10)* *(regenerated Nov 10 with the tuned Isolation Forest and autoencoder on `ayo/Y17-rerun-tuned`)* | Ayo → all (Git) |
| [x] | Wed Nov 11 | `ablation.csv` (T7) + `data_processing_time.csv` *(the time table is on `main` since #32 and in T8 since #48; `ablation.csv` in #51, re-run Nov 11 with one fixed XGBoost tree count)* | Supriye → Ayo (Git) |
| [x] | Thu Nov 12 | T5, F4, F5, `T8_timing.csv` *(#48, Nov 10)* *(regenerated Nov 10 with the tuned Isolation Forest and autoencoder on `ayo/Y17-rerun-tuned`)* | Ayo → all (Git) |
| [ ] | Fri Nov 13 | Related Work paragraphs | Arva, Ayo → Supriye (Overleaf) |
| [ ] | Sun Nov 15 | IV-C, IV-D, V, VI-B | Arva, Ayo → Supriye (Overleaf) |
| [ ] | Mon Nov 16 | VI-A, VI-C, VIII, README run section | Arva, Ayo → Supriye |
| [ ] | Wed Nov 18 18:00 | Full paper PDF | Supriye → Arva, Ayo |

### 3.4 Supriye
**Done (Weeks 0–1):**
- [x] **S1** CERT r4.2 + answers downloaded, checksums match **(Claude)**
- [x] **S2** folders, `.gitignore`, `config.py`, pinned `requirements.txt`, collaborators added (#1) **(Claude)**
- [x] **S4** streaming converter, 32,770,222 rows (#4) **(Claude)**
- [x] **S5** loaders + cleaning report, no rows removed (#4) **(Claude)**
- [x] **S6** labels (70 insiders 30/30/10; 984 malicious user-days in the table) + timeline (#5, #11, #12) **(Claude)**
- [x] **S7** EDA notebook run, F1 + 7 tables (#5) **(Claude)**
- [x] **S8** split proposal + split check (#5, #12) **(Claude)**
- [x] **S9** v0 (100 users, 31,175 user-days) + `get_model_matrix()` (#6, #11) **(Claude)**
- [x] **S10, S12, S13, S16** login, USB, file, context features (#17) **(Claude)**
- [x] **S17, S18** `z_user_*`, `z_peer_*`, `new_*`, F3 (#18) **(Claude)**
- [x] **S19 checks 1, 2, 3, 5** pass; raw-log recount matches (#18) **(Claude)**
- [x] **S20 code** v1 (73 inputs) + `docs/feature_dictionary.md` (#18) **(Claude)**
- [x] **Tracker** audit (#16), Week 1 merged (#26)

**Open:**
- [ ] **S2-rest** branch protection; Overleaf + Zotero created and invites sent
  - [x] **Branch protection** on `main` *(Nov 7, after Supriye made the repo public; GitHub offers it on private repos only with Pro)*: a PR with 1 approval is required, admins included; no force-push or deletion. Checked by reading the rule back from the GitHub API, not by test-pushing to `main` **(Claude)**
  - [ ] **Overleaf** project (IEEE conference template) and **Zotero** group library created; Arva and Ayo invited and joined
- [ ] **S3-rest** page limit, AI policy, submission contents confirmed
- [x] **S8** decide split dates (2.5.3) [H] *Decided by Supriye Nov 6: 2010-10-31 / 2011-01-31 (#36); reason in TEAM_PLAN 2.5.3, drafted by Claude at Supriye's request **(Claude)**.* *Supriye read the Claude-drafted reasons and adopted them as her own (Nov 17, after the whole-project review flagged the ticks).*
- [x] **S11** decide the after-hours window + write the reason [H] *Decided by Supriye Nov 6: 07:00–19:00 (#36); reason in the feature dictionary, drafted by Claude at Supriye's request **(Claude)**.* *Supriye read the Claude-drafted reasons and adopted them as her own (Nov 17, after the whole-project review flagged the ticks).*
- [x] **S14** decide the email-count rule [H] *Decided by Supriye Nov 6: count all emails incl. webmail (#36); reason in the feature dictionary, drafted by Claude at Supriye's request **(Claude)**.* *Supriye read the Claude-drafted reasons and adopted them as her own (Nov 17, after the whole-project review flagged the ticks).*
- [x] **S15** check the web keyword lists (7 `f_http_*` features built; 8 since `competitor` was added Nov 6) [H] *Decided by Supriye Nov 6: the lists as built + a `competitor` category (5 defense contractors; added after the review) (#36); reason in the feature dictionary, drafted by Claude at Supriye's request **(Claude)**.* *Supriye read the Claude-drafted reasons and adopted them as her own (Nov 17, after the whole-project review flagged the ticks).*
- [x] **S6** decide the hijacked-account labels [H] *Decided by Supriye Nov 6: keep the 20 days on FAW0032/FBA0348 (#36); reason in the feature dictionary, drafted by Claude at Supriye's request **(Claude)**.* *Supriye read the Claude-drafted reasons and adopted them as her own (Nov 17, after the whole-project review flagged the ticks).*
- [x] **S20b** rebuild labels/v0/v1 + notebooks 01–02 if a value changed *(Done when met on `main` at `e5dc881`: tests pass, notebooks 01–02 ran top to bottom with no errors, the split is valid, every v1 check passes, no PROVISIONAL left in Supriye's files. `tests/test_rebuild_outputs.py` now checks all of these on the committed outputs)* **(Claude)**
  - [x] **Tooling:** `bash scripts/rebuild_data.sh` runs labels → v0 → v1 → notebooks 01–02 → tests → a final check that stops (exit 1) on an invalid split or a failed v1 check (run Nov 5: same counts, all pass). The web-log cache now rebuilds itself when the working hours change, or when it has no working-hours stamp on `supriye/S20-rebuild-data-drop` **(Claude)**
  - [x] **Run** it after the S8 decisions and commit the regenerated tables, figures and notebooks *(Nov 6, after adding `competitor`: v1 now 76 inputs; every check passes)* **(Claude)**
- [ ] **S6-H / S19-H** hand-check 3 insiders [H]
- [ ] **S7-H** EDA observation cells [H]
- [ ] **S4/S20** data drop uploaded with checksums
  - [x] **Tooling:** `python scripts/data_drop.py make` builds `data/ueba_data_v1.zip` (10 files, ~360 MB, `CHECKSUMS.txt` + `DROP_INFO.txt` with the commit and decisions); `make` refuses a web-log cache not built with the current working hours; `verify` lets Arva and Ayo check the files after unzipping and warns if their `src/config.py` differs from the drop's decisions on `supriye/S20-rebuild-data-drop` **(Claude)**
  - [x] **Build** the zip after S8/S20b, upload it to the drive and post the link *(built from `e5dc881` by Claude; uploaded by Supriye; both teammates loaded v1, confirmed Nov 8)*
- [ ] **REV-S** read own code [H]; reviews done (§3.7)
- [ ] **S20-tag** `m0-setup`, `m1-features-v0`, `m2-features-v1`
  - [x] **`m2-features-v1`** tagged and pushed (Nov 8) **(Claude)**
  - [x] **`m0-setup`** tagged and pushed (Nov 10) **(Claude)**
  - [ ] **`m1-features-v0`** once Arva and Ayo confirm v0 loads (§3.1); announce the freeze in chat
- [ ] **S20-walk** v1 walkthrough (Mon Nov 9)
- [x] **S21** bug-fix window closed (Tue Nov 10 12:00) *(checked at 12:01: the repo has never had a GitHub Issue, and PRs #46–#48 report no feature bug; feature code unchanged since the `m2-features-v1` tag; 145 tests pass; no `features_v1_1.parquet`)* **(Claude)**
- [ ] **S23a** III. Dataset [H]
- [x] **S22** `src/ablation.py` + tests → `ablation.csv` (T7) + `data_processing_time.csv` **(Claude)**
  - [x] **Code:** `feature_group()` (all v1 inputs → 7 groups; 76 since Nov 6), `feature_sets()` (a, b, c + 7 × d = 10 sets), `run_ablation()` (XGBoost + Isolation Forest retrained with their module defaults, test PR-AUC / ROC-AUC / recall at top 1% and best-F1; each row records the model settings and commit), tests on `supriye/S22-ablation` **(Claude)**
  - [x] **T8 data time:** `data_processing_time.csv` (3-run means): Parquet logs → v1 in ~138 s (labels 0.07 s, web-log pass 26 s, v1 incl. baselines 112 s) + the one-off conversion, an untimed ~10 min estimate (`measured` = False); 24 threads, 31.4 GB RAM on `supriye/S22-ablation` **(Claude)**
  - [x] **Run** `python -m src.ablation` once A16 and Y15 (tuned defaults) are merged → `ablation.csv` *(Nov 11, code at `d75fbf8`: 10 feature sets × 2 models = 20 rows. Method decided by Supriye on Nov 11 after Ayo's review of #51: XGBoost trains every set with one fixed tree count, the full set's early-stopped count (545), instead of early-stopping each set; the first run had stopped two sets at ~30 trees. Isolation Forest is unchanged and reproduced exactly on Ayo's M1)* on `supriye/S22-ablation-run` **(Claude)**
- [ ] **S22-H** interpret the ablation [H] *(Ayo's M1 re-run in his #51 review: every XGBoost row is within 0.011 PR-AUC of the committed table, and the M1 derives 576 trees vs. 545 here. Drops below about 0.01 (time, file, context, logon) are inside that machine difference, so he suggests the T7 caption or these notes say they shouldn't be ranked against each other)*
- [ ] **S24** LANL features *(stretch, only if agreed)*
- [ ] **S-LIT1** L1, L2 [H]
- [ ] **S-LIT2** L3 [H]
- [ ] **S-LIT3** L9a (+ L9b) [H]
- [ ] **S23b** IV-A, IV-B [H]
- [ ] **S25** Related Work paragraphs [H]
- [ ] **S26** I. Introduction [H]
- [ ] **S27** VII. Limitations & Ethics [H]
- [ ] **S28** walkthrough; II merged + T1 [H]
- [ ] **S29** assemble → M4
- [ ] **S30** Abstract + integration [H]
- [ ] **S31** editing pass [H]
- [ ] **S32** circulate → M5
- [ ] **S33** read-through + README results
  - [x] **README Results** table from `model_comparison.csv` (T5, all 7 score files × 2 operating points), written by `python scripts/readme_results.py`; `tests/test_readme_results.py` fails if README and T5 drift apart, so re-run the script after any `python -m src.evaluate report` on `supriye/S33-readme-results` **(Claude)**
  - [ ] **Final read-through** (Thu Nov 19), then re-run the script on the final T5
- [ ] **S34** fresh-clone test, tag, archive
- [ ] **S35** submit

### 3.5 Arva
**Done (Weeks 0–1):**
- [x] **A1 clone** (PRs #9, #10)
- [x] **A3** `synthetic.py` (#10) + `f_http_job` rename (#13)
- [x] **A4–A6** `train_and_score()`, Isolation Forest, AE (#14) **(Claude)**
- [x] **A7** risk scoring (#15) **(Claude)**
- [x] **A8** `feature_errors()`, `_contam` (#19) **(Claude)**
- [x] **A9–A10** v0 run + tuning workflow (#20) **(Claude)**
- [x] **A11–A12** `pipeline.py` + 3 reasons (#21) **(Claude)**
- [x] **A13 code** OCSVM (v0 val ROC-AUC 0.26) (#22) **(Claude)**
- [x] **A14 code** T4 draft (#22) **(Claude)**
- [x] **Docs** `CLAUDE.md` (#9), coverage refresh (#27)

**Open:**
- [ ] **A1-rest** environment installed; `arva/notes` pushed
- [ ] **A2** kickoff *(missed; replaced by the Fri Nov 6 check)*
- [ ] **REV-A** read own code [H]; `explain.py` confirmed; reviews done (§3.7)
- [ ] **DEC-A** AE architecture + grids [H]
- [ ] **DEC-A** alert levels [H]
- [ ] **DEC-A** keep/drop OCSVM [H]
- [x] **COV-A** `coverage.md` fixes (7 web features, timing claim, T2/T3) (#30)
- [ ] **A-LIT1** IF paper + Chandola [H]
- [ ] **A-LIT2** L4 [H]
- [ ] **A-LIT3** L5 [H]
- [ ] **A-LIT4** L10a (+ L10b) [H]
- [x] **A15** log-reset fix; v1 grids; `_contam` runs; T4 (v1) *(code in #33; v1 run Nov 10 in #50: 18 IF + 16 AE grid runs, the card reference, the `_contam` and OCSVM runs in the tuning log next to the v0 rows; T4 shows the v1 best)* **(Claude)**
- [ ] **A16** tuned defaults + `final` command; `evaluate_file()` on all files
  - [x] **`final` command** + its test (#33) **(Claude)**
  - [x] **Tuned defaults** merged (#50) (best v1 run by val PR-AUC: IF 100 trees / 256 samples / all features; AE 128-64-16, no dropout, lr 1e-3; the `card` dicts keep the card values for T4); notebook 03a runs `final` and `evaluate_file()` on all 5 files **(Claude)**
  - [x] **Ayo confirms** `final` + `evaluate_file()` run on his laptop (#50 review, Nov 10: 5 files in 82 s on the M1)
  - [ ] **Arva** reads the change and writes the DEC-A reasons [H]
- [x] **A17** `unsupervised_extra.csv` (per scenario, contamination, alerts/day, timing)
  - [x] **Code:** `results_extra()`, `timing()`, `alerts_per_day()` + tests (#34; restored by #43 after a merge dropped them)
  - [x] **`unsupervised_extra.csv`** on `main`, built on Ayo's M1 with `final` then `extra` *(Nov 17, `ayo/A17-m1-results`: rebuilt on `main` after #57/#58, the 5 score files are bit-identical to the Nov 10 run and every result column equals T5; the Nov 10 timings are kept because T8 already uses them)* **(Claude)** *(Arva's review of #57, Nov 13: a CSV built on Supriye's Intel laptop gave autoencoder rows and timings that differ from T5/T8, so it was taken out of that PR)*
- [ ] **A17-H** interpret it [H]
- [ ] **A18** pipeline on v1, `precision_at_20.csv`, F8
  - [x] **Code:** `precision_at_k()`, `f8_user()`, `plot_risk_timeline()` (#35); `python -m src.pipeline --prototype` writes every output in one run (#57) **(Claude)**
  - [x] **Outputs** from the v1 run (Nov 13, #57): `top_risky_users.csv`, `top_risky_users_autoencoder.csv`, `precision_at_20.csv`, `F8_risk_timeline.*`; step 6 (LANL) does not apply, S24 was not agreed **(Claude)** *(re-run on Ayo's M1, Nov 17: the IF table, precision@20 and F8 are unchanged; `top_risky_users_autoencoder.csv` is replaced by the M1 run)*
  - [ ] **F8 model** (Isolation Forest, as drawn, or the autoencoder) and the reasons floor `MIN_REASON_Z` chosen by Arva [H]; Arva runs `prototype()` himself
- [ ] **A19** notebook 05: 4 cases × parts 1–4, F7
  - [x] **Notebook 05** on `arva/A19-case-studies` (Nov 13): the 4 picks by the card rule (`pick_cases()`), context, baseline vs. the day, F7 (IF SHAP waterfall + AE feature errors, `F7_case<1-4>_*`), raw evidence incl. web domains; `case_studies.csv`; helper tests **(Claude)** *(re-run on Ayo's M1, Nov 17: the picks and IF outputs are unchanged; the AE risk, AE reasons and the 4 AE error figures now come from the results machine)*
  - [ ] **Arva confirms the picks** [H] and presents 2 cases at the Sat walkthrough
- [ ] **A19-H** narratives + verdicts [H]
- [ ] **A14-rest** F2 [H]; IV-C/IV-D notes [H]; `arva/notes` merged
- [ ] **A20** Related Work paragraphs [H]
- [x] **A21** dashboard *(optional)* *(Nov 16 on `arva/A21-dashboard`: `streamlit run app/dashboard.py` starts on v1 and shows all 3 parts (ranked table, user risk timeline, reasons for a chosen day); 9 tests, one of them starts the page)* **(Claude)**
- [ ] **A22** IV-C, IV-D, VI-B [H]
- [ ] **A23** VIII [H] + README run section
  - [x] **README "Run the prototype"** section (#59, follow-up #61)
  - [ ] **VIII** Conclusion & Future Work [H]
- [ ] **A24** fresh-clone test + demo ≤ 3 min
- [ ] **A25** draft review
- [ ] **A26** final fixes

### 3.6 Ayo
**Done (Weeks 0–1):**
- [x] **Y3** synthetic scores + core metrics (#3) **(Claude)**
- [x] **Y4** thresholds, `evaluate_file()`, `compare_files()` (#3) **(Claude)**
- [x] **Y5** plots (#3) **(Claude)**
- [x] **Y6 code** delay + user recall (#3) **(Claude)**
- [x] **Y7** RF + XGB (#23) **(Claude)**
- [x] **Y8** v0 run (#23) **(Claude)**
- [x] **Y9** tuning workflow (#23) **(Claude)**
- [x] **Y10 code** imbalance experiment on v0 (#23) **(Claude)**
- [x] **Y11 code** `explain.py` (#24) **(Claude)**
- [x] **Y12 code** LOSO (#25) **(Claude)**
- [x] **Y13 code** T4 draft (#23) **(Claude)**

**Open:**
- [ ] **Y1** clone, install, tests, `ayo/notes` *(overdue)*
  - [x] **Clone, install, tests** on his laptop (#41 reports the full suite passing)
  - [ ] **`ayo/notes`** branch on GitHub
- [ ] **Y2** kickoff *(missed; replaced by the Fri Nov 6 check)*
- [ ] **REV-Y** read own code [H]
- [ ] **REV-Y** Y3 10-row hand-check [H]
- [ ] **REV-Y** A3/M1/Y6 confirmations
- [x] **REV-Y** reviews done (§3.7) *(Nov 16: post-merge review comments on #1, #2, #8, #10, #13, #14, #19, #20, #22 after `python -m pytest tests` on `main` (172 passed); no Issue needed)* **(Claude)**
- [ ] **DEC-Y** imbalance set-up [H] *(#41 records it as decided by Ayo on Nov 8: RF with SMOTE, XGBoost with class weights; Ayo ticks this)*
- [ ] **DEC-Y** LOSO justification [H]
- [ ] **Y-LIT1** Saito & Rehmsmeier [H]
- [ ] **Y-LIT2** L6 [H]
- [ ] **Y-LIT3** L7 [H]
- [ ] **Y-LIT4** L8 + L11a (+ L11b) [H]
- [ ] **Y13-rest** IV-C/V notes [H]; `ayo/notes` merged
- [x] **Y14** log fixes; v1 imbalance; v1 grids; T4 (v1) (#41: 42 v1 runs in the tuning log, `imbalance.csv` keeps v0 and v1, T4 shows the v1 choice and set-up)
- [x] **Y15** tuned defaults + `FINAL_SETUP` + `final`; `timing_supervised.csv`; `evaluate_file()` on all 7 (#41; `evaluate_file()` on all 7 runs in notebook 04, #46)
- [x] **Y16** notebook 04 + `loso.csv` (T6) → M3 **(Claude)**
  - [x] **Notebook 04**, `loso.csv` (T6), `loso_pr_auc.csv` and the `loso` command merged (#46)
  - [x] **Re-run** with the tuned Isolation Forest and autoencoder (#50) on `ayo/Y17-rerun-tuned`: supervised LOSO rows reproduce exactly; notebook 04 re-run and its reading's numbers updated **(Claude)**
- [ ] **Y16-H** observations [H]
- [ ] **Y17** T5, per-scenario, delay, F4, F5, T8
  - [x] **Tables and figures:** `model_comparison.csv` (T5), `model_per_scenario.csv`, `detection_delay.csv`, `T8_timing.csv`, F4, F5, `python -m src.evaluate report` + tests (#48)
  - [x] **Regenerate** with `report` after A16 on `ayo/Y17-rerun-tuned`: only the IF, AE and `_contam` rows change **(Claude)**
  - [x] **Walkthrough material** (card step 8): notebook 04 section 5 (T5, per-scenario recall, F4) on `ayo/Y20-fp-fn` **(Claude)**
- [x] **Y18** F6, `feature_importance.csv`, per-scenario importance *(on `ayo/Y18-shap-fpfn`: `python -m src.explain shap` refits XGBoost, RF (tuned, `FINAL_SETUP`) and Isolation Forest (tuned, #50) and explains all 170 test positives + 5,000 negatives; F6 + RF/IF summaries, `feature_importance.csv`, `feature_importance_per_scenario.csv`, `feature_importance_top10_overlap.csv`; `importance_table()`, `top10_overlap()`, `per_scenario_importance()` + tests)* **(Claude)**
- [ ] **Y18-H** interpretation [H] *(reading drafted by Claude at Ayo's request in notebook 04 section 6, with the T7 numbers from #51; Ayo checks it and ticks)*
- [ ] **Y19** Related Work paragraphs [H]
- [x] **Y20** FP/FN tables *(on `ayo/Y20-fp-fn`: `python -m src.evaluate fpfn` picks XGBoost and the autoencoder by test PR-AUC from T5 and writes `fp_breakdown.csv`, `fp_top10.csv`, `fn_by_insider.csv` at best-F1; `fp_fn_rows()`, `fp_breakdown()`, `top_deviations()`, `fn_breakdown()`, `pick_fpfn_models()` + tests)* **(Claude)**
- [ ] **Y20-H** causes + fixes (`fp_fn_causes.csv`) [H] *(`fp_fn_causes.csv` and the notebook 04 section 7 reading drafted by Claude at Ayo's request, marked as drafts; Ayo checks them and ticks)*
- [ ] **Y20** walkthrough presented
- [ ] **Y21** IV-C (supervised), V [H]
- [ ] **Y22** VI-A, VI-C, P/R paragraph [H]
- [ ] **Y23** every number verified; figures polished
- [ ] **Y24** draft review
- [ ] **Y25** final fixes

### 3.7 Post-merge reviews (none of #1–#28 had a GitHub review)
Review on `main`, run the PR's "How to test" step, then tick. Fixes go in a new PR from a new branch.

| ✓ | PR | What | Author (written by) | Reviewer |
|---|---|---|---|---|
| [x] | #1 | S2 setup | Supriye (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [x] | #2 | Plans + tracker | Supriye (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [ ] | #3 | Y3–Y6 `evaluate.py` | Supriye for Ayo (Claude) | Arva |
| [ ] | #4 | S4–S5 data loader | Supriye (Claude) | Arva |
| [ ] | #5 | S6–S8 labels, EDA | Supriye (Claude) | Arva |
| [ ] | #6 | S9 v0 | Supriye (Claude) | Arva |
| — | #7 | Catch-up merge of #3–#6 | Supriye (Claude) | (covered by #3–#6) |
| [x] | #8 | Tracker | Supriye (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [ ] | #9 | `CLAUDE.md` | Arva | Supriye |
| [x] | #10 | A3 synthetic | Arva | Ayo *(comment, Nov 16)* **(Claude)** |
| [ ] | #11 | Review fixes | Supriye (Claude) | Arva |
| [ ] | #12 | Cross-check, split counts | Supriye (Claude) | Arva |
| [x] | #13 | A3 rename | Supriye for Arva (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [x] | #14 | A4–A6 | Supriye for Arva (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [ ] | #15 | A7 risk scoring | Supriye for Arva (Claude) | Supriye |
| [ ] | #16 | Tracker audit | Supriye (Claude) | Arva |
| [ ] | #17 | S10–S16 features | Supriye (Claude) | Arva |
| [ ] | #18 | S17–S20 baselines | Supriye (Claude) | Arva |
| [x] | #19 | A8 | Supriye for Arva (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [x] | #20 | A9–A10 | Supriye for Arva (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [ ] | #21 | A11–A12 pipeline | Supriye for Arva (Claude) | Supriye |
| [x] | #22 | A13–A14 | Supriye for Arva (Claude) | Ayo *(comment, Nov 16)* **(Claude)** |
| [ ] | #23 | Y7–Y10 | Supriye for Ayo (Claude) | Supriye |
| [ ] | #24 | Y11 `explain.py` | Supriye for Ayo (Claude) | Arva |
| [ ] | #25 | Y12 LOSO | Supriye for Ayo (Claude) | Arva |
| [ ] | #26 | Tracker | Supriye (Claude) | Arva |
| [ ] | #27 | Coverage refresh | Arva | Supriye |
| [ ] | #28 | S15 web-count fix | Supriye (Claude) | Arva |

- [ ] **`docs/coverage.md` first version** (pushed straight to `main` without a PR): read by a teammate.

### 3.8 Branches and PRs still to come (tick when merged)
- [x] **`supriye/S8-decisions`** (Arva) (#36)
- [x] **`arva/docs-coverage-fixes`** (any) (#30)
- [x] **`supriye/S21-v1-fixes`** *(only if needed)* (Arva) *(not needed: no feature bug by Tue Nov 10 12:00; S21 closed on `supriye/S21-close-tracker-audit`)*
- [x] **`arva/A15-final-models`** (Supriye) (#33; the v1 runs and tuned defaults still need a new branch)
- [x] **`ayo/Y14-final-models`** (Supriye) (#41)
- [x] **`supriye/S22-ablation`** (Ayo) (#32: code and the data time; the `ablation.csv` run needs a new branch after A16)
- [x] **`arva/A17-results`** (Ayo) (#34, restored by #43; the CSV is still to come)
- [x] **`ayo/Y16-loso-results`** (Arva) (#46)
- [ ] **`supriye/S24-lanl`** *(stretch)* (Arva)
- [x] **`ayo/Y17-comparison`** (Arva) (#48)
- [ ] **`supriye/notes`, `arva/notes`, `ayo/notes`** (any)
- [x] **`arva/A18-prototype-cases`** (Ayo) (#35: A18 code only; the outputs and A19 are still to come)
- [x] **`ayo/Y18-shap-fpfn`** (Arva) (#53; Y20 merged separately as #55)
- [x] **`arva/A21-dashboard`** *(optional)* (Supriye) (#63)
- [x] **`arva/A23-readme-run`** (Supriye) (#59, follow-up #61)
- [ ] **`arva/A24-fresh-clone-fixes`** *(if needed)* (Supriye)
- [ ] **`ayo/Y23-verify`** (Supriye)
- [ ] **`arva/A26-final-fixes`, `ayo/Y25-final-fixes`** *(if needed)* (Supriye)
- [ ] **`supriye/S33-final`** (Ayo)

### 3.9 Milestone tags (Supriye)
- [x] **`m0-setup`:** after M0 *(pushed Nov 10, `5bbcf77`: the first commit that shows Ayo's installed environment and the v1 data in use)*
- [ ] **`m1-features-v0`:** after M1
- [x] **`m2-features-v1`:** Sun Nov 8 *(pushed Nov 8, `2710789`)*
- [x] **`m3-all-scores`:** after A16, Y15, Y16, S22 merge *(pushed Nov 13 on `main` at `0729548`, after #51 (S22); A16 #50, Y15 #41, Y16 #46/#52)* **(Claude)**
- [ ] **`analysis-done`:** after A18–A19 and Y18–Y20 merge
- [ ] **`final-submission`:** Thu Nov 19

### 3.10 Paper, tables and figures
- [ ] **Abstract** (Supriye)
- [ ] **I.** (Supriye)
- [ ] **II + T1** (all → Supriye)
- [ ] **III + T2** (Supriye)
- [ ] **IV-A + T3** (Supriye)
- [ ] **IV-B + F3** (Supriye)
- [ ] **IV-C unsupervised + T4** (Arva)
- [ ] **IV-C supervised + T4** (Ayo)
- [ ] **IV-D + F2, F8** (Arva)
- [ ] **V + T5, T6, T8, F4, F5** (Ayo)
- [ ] **VI-A + F6, T7** (Ayo, with Supriye's T7)
- [ ] **VI-B + F7** (Arva)
- [ ] **VI-C** (Ayo)
- [ ] **VII** (Supriye)
- [ ] **VIII** (Arva)
- [x] **F1** `F1_insider_vs_normal.*`
- [x] **F3** `F3_user_baseline.*`
- [ ] **T2 data** ready (`class_imbalance.csv`); table in Overleaf
- [ ] **T3 data** ready (`feature_dictionary.md`); condensed table in Overleaf

### 3.11 Submission checklist (Thu Nov 19 – Fri Nov 20)
- [ ] **Tests** pass on `main` after the last merge
- [ ] **Notebooks** 01–05 run top to bottom
- [ ] **Fresh clone:** zip + both `final` commands + pipeline + notebook 04 work
- [ ] **Every paper number** traced to `results/tables/` (Y23)
- [ ] **Every citation** checked [H]
- [ ] **PDF** within the page limit
- [ ] **`final-submission` tag** pushed; `submission-code.zip` built from it
- [ ] **Submitted**; confirmation posted

---

## 4. Edge Cases & Troubleshooting

- **"Status unknown" lines:** the owner ticks the line, or replaces the note with what's left. Don't guess.
- **A task is partly done:** add sub-boxes rather than ticking the parent.
- **A decision changes a value after work was ticked:** untick what depends on it (e.g. S20b rebuild, then A15/Y14 re-run), and note why.
- **A PR was merged without a review:** it still needs one (§3.7); fixes go in a new PR.
- **An AI agent did a task:** mark it **(Claude)** (or the agent's name). The owner still owes the read-through.
- **A hand-off is late:** keep it unticked, add the new date in italics, and tell the team.
- **Two branches both edit this file:** keep both sides line by line when resolving the conflict (TEAM_PLAN 3.9).
- **A number here disagrees with the code or data:** the code/data wins; fix this file in the same PR.

---

## 5. Success Metrics / Definitions

### 5.1 Done means
- **Task:** every "Done when" item true and its PR merged.
- **Hand-off:** merged and announced (data: the drop uploaded and checksums confirmed).
- **Milestone:** all its sub-boxes ticked and its tag pushed.
- **Human-only:** done by the person, never by an agent.

### 5.2 Assignment requirements (tick when the proof exists)
- [ ] **Study insider threats / compromised accounts / UEBA:** §I + §II with checked citations
- [ ] **≥ 5 recent papers:** ≥ 5 `paper/lit_notes/*.md` + T1 (venue, year)
- [ ] **Dataset chosen:** §III; checksums
- [x] **Preprocessing:** `cleaning_report.csv`, `split_check.csv`; split final (Nov 6, #36)
- [x] **Login patterns:** `f_logon_*` family in v1 + feature dictionary
- [ ] **Authentication failures:** LANL features **or** the gap stated in §III + §VII
- [x] **File / resource access:** `f_file_*`, `f_usb_*` in v1
- [ ] **Application usage:** 8 `f_http_*` + 8 `f_email_*` in v1; keyword lists final; stand-in stated in §III
- [x] **Activity times:** after-hours/weekend/duration features in v1; window final with its reason (07:00–19:00, #36/#37)
- [x] **Deviation from baseline:** `z_user_*`, `z_peer_*`, `new_*`, F3
- [ ] **Normal-behavior baseline in the paper:** §IV-B
- [x] **≥ 2 models compared:** 7 score files + T5 (`model_comparison.csv`, #48) *(regenerated Nov 10 with the tuned Isolation Forest and autoencoder on `ayo/Y17-rerun-tuned`)*
- [ ] **Models justified:** §IV-C + T4
- [ ] **Risk score:** pipeline output, alert levels final, F8
- [x] **All listed metrics:** T5, F4, F5 (#48) *(regenerated Nov 10 with the tuned Isolation Forest and autoencoder on `ayo/Y17-rerun-tuned`)*
- [x] **Detection time:** T8 (`T8_timing.csv`, #48)
- [ ] **Precision/recall vs. accuracy:** §V paragraph
- [x] **Unseen behavior:** T6 (`loso.csv`, #46) *(regenerated Nov 10 with the tuned Isolation Forest and autoencoder on `ayo/Y17-rerun-tuned`)*
- [ ] **FP / FN analysis:** §VI-C + `fp_fn_causes.csv`
- [x] **Feature importance:** F6, `feature_importance.csv`, T7 (#53, #51)
- [ ] **Anomaly explanations:** notebook 05 + §VI-B + F7
- [ ] **Prototype:** fresh-clone run + README section
- [ ] **Paper:** IEEE PDF, all T1–T8 / F1–F8 referenced
- [ ] **Limitations:** §VII
- [ ] **Research question answered:** §VIII with numbers

### 5.3 Health checks (check at every stand-up)
- **`main` is green:** `python -m pytest tests` passes (83 on Nov 5, 153 on Nov 10; the count only grows).
- **No overdue hand-off is undiscussed:** every late item in §3.3 has a new date.
- **No [H] box was ticked by an agent.**
- **Data moved at most once** (twice if S21 or S24 needed it); no score file or model was sent around.
