# Progress Checker (v2)

**Last updated:** Thu Nov 5, 2026 (`main` at `8060fc3`) · **Submit:** Fri Nov 20 (ready Thu Nov 19)
Plan: [TEAM_PLAN.md](TEAM_PLAN.md) · Task cards: [Supriye.md](Supriye.md), [Arva.md](Arva.md), [Ayo.md](Ayo.md)

---

## 1. Executive Summary

### 1.1 Snapshot (Thu Nov 5)
- **Code:**
  - **Weeks 0–1 are complete and merged:** PRs #1–#28, 83/83 tests on `main`.
  - **Week 2 has not started:** no v1 model results, final score files, T5–T8, F4–F8 or notebooks 04–05.
- **Data:**
  - **Feature table v1** is built on Supriye's laptop: 330,268 user-days, 73 inputs.
  - **The data drop** is not on the shared drive yet.
- **People:**
  - **Reviews:** none of the 28 merged PRs has a review.
  - **Ayo** has no commits yet.
  - **Literature:** `paper/lit_notes/` is empty.
- **Decisions:** 5 PROVISIONAL values (Supriye), the AE architecture and alert levels (Arva), and the imbalance set-up and LOSO justification (Ayo) are open.
- **Milestones:** M0, split dates and M1 are past due. M2 (Sun Nov 8) is close: only the decisions, the data drop and teammate confirmations remain.

### 1.2 Next three actions each
| Person | 1 | 2 | 3 |
|---|---|---|---|
| **Supriye** | Decide the 5 PROVISIONAL values (S8) | Upload `ueba_data_v1.zip` (Sat) | Branch protection + Overleaf/Zotero |
| **Arva** | Read `models_unsupervised`/`risk_scoring`/`pipeline` | AE architecture + alert levels (DEC-A) | Reviews + fix `coverage.md` |
| **Ayo** | Clone, install, run tests (Y1) | Read `evaluate`/`models_supervised`/`explain` | Reviews + Y3 hand-check |

### 1.3 Counts
| Area | Done | Open |
|---|---:|---:|
| Supriye tasks (S1–S35, LIT) | 13 lines | Decisions, paper, finish |
| Arva tasks (A1–A26, LIT) | 10 lines | A15–A26, decisions, LIT |
| Ayo tasks (Y1–Y25, LIT) | 11 lines | Y14–Y25, decisions, LIT |
| Post-merge reviews | 0 / 27 | 27 |
| Milestones | 1 / 15 | 14 |

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
- [ ] **M0 Setup complete** (Sat Oct 31)
  - [x] **Repo cloned:** Supriye, Arva (PRs #9, #10)
  - [ ] **Repo cloned + installed:** Ayo (Y1)
  - [ ] **Data on the drive:** the one data drop `ueba_data_v1.zip` (S4/S20)
- [x] **`evaluate.py` ready** (Sun Nov 1): merged Nov 3 (#3 via #7)
- [ ] **Split dates final** (Mon Nov 2): in TEAM_PLAN 2.5.3 (S8) [H]
- [ ] **M1 Feature table v0** (Tue Nov 3)
  - [x] **v0 + `get_model_matrix()` merged** (#6 via #7, sampler fix #11)
  - [ ] **Arva and Ayo confirm** v0 loads in their code
- [ ] **`explain.py` ready** (Fri Nov 6)
  - [x] **Merged** (#24)
  - [ ] **Arva confirms** it for the case studies
- [ ] **M2 Feature table v1 frozen** (Sun Nov 8)
  - [x] **v1 built**, feature dictionary, leakage checks 1/2/3/5 pass (#17, #18)
  - [ ] **Decisions final** and v1 rebuilt if needed (S8, S20b)
  - [ ] **Data drop uploaded**; both teammates load v1
  - [ ] **Tag** `m2-features-v1`
- [ ] **Tuned models + `final` commands** (Tue Nov 10): A16 and Y15 merged
- [ ] **M3 All score files final** (Wed Nov 11): A17, Y16 merged; `evaluate_file()` runs on all
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
| [ ] | Fri Nov 6 | Final PROVISIONAL values | Supriye → all |
| [ ] | Sat Nov 7 | **The one data drop** `ueba_data_v1.zip` (~360 MB, checksums) | Supriye → Arva, Ayo |
| [ ] | Sun Nov 8 | v1 frozen + feature dictionary | Supriye → Arva, Ayo |
| [ ] | Tue Nov 10 12:00 | `features_v1_1.parquet` *(only if needed)* | Supriye → Arva, Ayo |
| [ ] | Tue Nov 10 | Merged tuned defaults + `python -m src.models_unsupervised final` | Arva → all (Git) |
| [ ] | Tue Nov 10 | Merged tuned defaults + `python -m src.models_supervised final` + `timing_supervised.csv` | Ayo → all (Git) |
| [ ] | Wed Nov 11 | `unsupervised_extra.csv` | Arva → Ayo (Git) |
| [ ] | Wed Nov 11 | `loso.csv` (T6) | Ayo → all (Git) |
| [ ] | Wed Nov 11 | `ablation.csv` (T7) + `data_processing_time.csv` | Supriye → Ayo (Git) |
| [ ] | Thu Nov 12 | T5, F4, F5, `T8_timing.csv` | Ayo → all (Git) |
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
- [ ] **S3-rest** page limit, AI policy, submission contents confirmed
- [ ] **S8** decide split dates (2.5.3) [H]
- [ ] **S11** decide the after-hours window + write the reason [H]
- [ ] **S14** decide the email-count rule [H]
- [ ] **S15** check the web keyword lists (7 `f_http_*` features built) [H]
- [ ] **S6** decide the hijacked-account labels [H]
- [ ] **S20b** rebuild labels/v0/v1 + notebooks 01–02 if a value changed
  - [x] **Tooling:** `bash scripts/rebuild_data.sh` runs labels → v0 → v1 → notebooks 01–02 → tests → a final check that stops (exit 1) on an invalid split or a failed v1 check (run Nov 5: same counts, all pass). The web-log cache now rebuilds itself when the working hours change, or when it has no working-hours stamp on `supriye/S20-rebuild-data-drop` **(Claude)**
  - [ ] **Run** it after the S8 decisions and commit the regenerated tables, figures and notebooks
- [ ] **S6-H / S19-H** hand-check 3 insiders [H]
- [ ] **S7-H** EDA observation cells [H]
- [ ] **S4/S20** data drop uploaded with checksums
  - [x] **Tooling:** `python scripts/data_drop.py make` builds `data/ueba_data_v1.zip` (10 files, ~360 MB, `CHECKSUMS.txt` + `DROP_INFO.txt` with the commit and decisions); `make` refuses a web-log cache not built with the current working hours; `verify` lets Arva and Ayo check the files after unzipping and warns if their `src/config.py` differs from the drop's decisions on `supriye/S20-rebuild-data-drop` **(Claude)**
  - [ ] **Build** the zip after S8/S20b, upload it to the drive and post the link
- [ ] **REV-S** read own code [H]; reviews done (§3.7)
- [ ] **S20-tag** `m0-setup`, `m1-features-v0`, `m2-features-v1`
- [ ] **S20-walk** v1 walkthrough (Mon Nov 9)
- [ ] **S21** bug-fix window closed (Tue Nov 10 12:00)
- [ ] **S23a** III. Dataset [H]
- [ ] **S22** `src/ablation.py` + tests → `ablation.csv` (T7) + `data_processing_time.csv`
- [ ] **S22-H** interpret the ablation [H]
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
- [ ] **COV-A** `coverage.md` fixes (7 web features, timing claim, T2/T3)
- [ ] **A-LIT1** IF paper + Chandola [H]
- [ ] **A-LIT2** L4 [H]
- [ ] **A-LIT3** L5 [H]
- [ ] **A-LIT4** L10a (+ L10b) [H]
- [ ] **A15** log-reset fix; v1 grids; `_contam` runs; T4 (v1)
- [ ] **A16** tuned defaults + `final` command; `evaluate_file()` on all files
- [ ] **A17** `unsupervised_extra.csv` (per scenario, contamination, alerts/day, timing)
- [ ] **A17-H** interpret it [H]
- [ ] **A18** pipeline on v1, `precision_at_20.csv`, F8
- [ ] **A19** notebook 05: 4 cases × parts 1–4, F7
- [ ] **A19-H** narratives + verdicts [H]
- [ ] **A14-rest** F2 [H]; IV-C/IV-D notes [H]; `arva/notes` merged
- [ ] **A20** Related Work paragraphs [H]
- [ ] **A21** dashboard *(optional)*
- [ ] **A22** IV-C, IV-D, VI-B [H]
- [ ] **A23** VIII [H] + README run section
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
- [ ] **Y2** kickoff *(missed; replaced by the Fri Nov 6 check)*
- [ ] **REV-Y** read own code [H]
- [ ] **REV-Y** Y3 10-row hand-check [H]
- [ ] **REV-Y** A3/M1/Y6 confirmations
- [ ] **REV-Y** reviews done (§3.7)
- [ ] **DEC-Y** imbalance set-up [H]
- [ ] **DEC-Y** LOSO justification [H]
- [ ] **Y-LIT1** Saito & Rehmsmeier [H]
- [ ] **Y-LIT2** L6 [H]
- [ ] **Y-LIT3** L7 [H]
- [ ] **Y-LIT4** L8 + L11a (+ L11b) [H]
- [ ] **Y13-rest** IV-C/V notes [H]; `ayo/notes` merged
- [ ] **Y14** log fixes; v1 imbalance; v1 grids; T4 (v1)
- [ ] **Y15** tuned defaults + `FINAL_SETUP` + `final`; `timing_supervised.csv`; `evaluate_file()` on all 7
- [ ] **Y16** notebook 04 + `loso.csv` (T6) → M3
- [ ] **Y16-H** observations [H]
- [ ] **Y17** T5, per-scenario, delay, F4, F5, T8
- [ ] **Y18** F6, `feature_importance.csv`, per-scenario importance
- [ ] **Y18-H** interpretation [H]
- [ ] **Y19** Related Work paragraphs [H]
- [ ] **Y20** FP/FN tables
- [ ] **Y20-H** causes + fixes (`fp_fn_causes.csv`) [H]
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
| [ ] | #1 | S2 setup | Supriye (Claude) | Ayo |
| [ ] | #2 | Plans + tracker | Supriye (Claude) | Ayo |
| [ ] | #3 | Y3–Y6 `evaluate.py` | Supriye for Ayo (Claude) | Arva |
| [ ] | #4 | S4–S5 data loader | Supriye (Claude) | Arva |
| [ ] | #5 | S6–S8 labels, EDA | Supriye (Claude) | Arva |
| [ ] | #6 | S9 v0 | Supriye (Claude) | Arva |
| — | #7 | Catch-up merge of #3–#6 | Supriye (Claude) | (covered by #3–#6) |
| [ ] | #8 | Tracker | Supriye (Claude) | Ayo |
| [ ] | #9 | `CLAUDE.md` | Arva | Supriye |
| [ ] | #10 | A3 synthetic | Arva | Ayo |
| [ ] | #11 | Review fixes | Supriye (Claude) | Arva |
| [ ] | #12 | Cross-check, split counts | Supriye (Claude) | Arva |
| [ ] | #13 | A3 rename | Supriye for Arva (Claude) | Ayo |
| [ ] | #14 | A4–A6 | Supriye for Arva (Claude) | Ayo |
| [ ] | #15 | A7 risk scoring | Supriye for Arva (Claude) | Supriye |
| [ ] | #16 | Tracker audit | Supriye (Claude) | Arva |
| [ ] | #17 | S10–S16 features | Supriye (Claude) | Arva |
| [ ] | #18 | S17–S20 baselines | Supriye (Claude) | Arva |
| [ ] | #19 | A8 | Supriye for Arva (Claude) | Ayo |
| [ ] | #20 | A9–A10 | Supriye for Arva (Claude) | Ayo |
| [ ] | #21 | A11–A12 pipeline | Supriye for Arva (Claude) | Supriye |
| [ ] | #22 | A13–A14 | Supriye for Arva (Claude) | Ayo |
| [ ] | #23 | Y7–Y10 | Supriye for Ayo (Claude) | Supriye |
| [ ] | #24 | Y11 `explain.py` | Supriye for Ayo (Claude) | Arva |
| [ ] | #25 | Y12 LOSO | Supriye for Ayo (Claude) | Arva |
| [ ] | #26 | Tracker | Supriye (Claude) | Arva |
| [ ] | #27 | Coverage refresh | Arva | Supriye |
| [ ] | #28 | S15 web-count fix | Supriye (Claude) | Arva |

- [ ] **`docs/coverage.md` first version** (pushed straight to `main` without a PR): read by a teammate.

### 3.8 Branches and PRs still to come (tick when merged)
- [ ] **`supriye/S8-decisions`** (Arva)
- [ ] **`arva/docs-coverage-fixes`** (any)
- [ ] **`supriye/S21-v1-fixes`** *(only if needed)* (Arva)
- [ ] **`arva/A15-final-models`** (Supriye)
- [ ] **`ayo/Y14-final-models`** (Supriye)
- [ ] **`supriye/S22-ablation`** (Ayo)
- [ ] **`arva/A17-results`** (Ayo)
- [ ] **`ayo/Y16-loso-results`** (Arva)
- [ ] **`supriye/S24-lanl`** *(stretch)* (Arva)
- [ ] **`ayo/Y17-comparison`** (Arva)
- [ ] **`supriye/notes`, `arva/notes`, `ayo/notes`** (any)
- [ ] **`arva/A18-prototype-cases`** (Ayo)
- [ ] **`ayo/Y18-shap-fpfn`** (Arva)
- [ ] **`arva/A21-dashboard`** *(optional)* (Supriye)
- [ ] **`arva/A23-readme-run`** (Supriye)
- [ ] **`arva/A24-fresh-clone-fixes`** *(if needed)* (Supriye)
- [ ] **`ayo/Y23-verify`** (Supriye)
- [ ] **`arva/A26-final-fixes`, `ayo/Y25-final-fixes`** *(if needed)* (Supriye)
- [ ] **`supriye/S33-final`** (Ayo)

### 3.9 Milestone tags (Supriye)
- [ ] **`m0-setup`:** after M0
- [ ] **`m1-features-v0`:** after M1
- [ ] **`m2-features-v1`:** Sun Nov 8
- [ ] **`m3-all-scores`:** after A16, Y15, Y16, S22 merge
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
- [ ] **Preprocessing:** `cleaning_report.csv`, `split_check.csv`; split final
- [x] **Login patterns:** `f_logon_*` family in v1 + feature dictionary
- [ ] **Authentication failures:** LANL features **or** the gap stated in §III + §VII
- [x] **File / resource access:** `f_file_*`, `f_usb_*` in v1
- [ ] **Application usage:** 7 `f_http_*` + 8 `f_email_*` in v1; keyword lists final; stand-in stated in §III
- [ ] **Activity times:** after-hours/weekend/duration features in v1; window final with its reason
- [x] **Deviation from baseline:** `z_user_*`, `z_peer_*`, `new_*`, F3
- [ ] **Normal-behavior baseline in the paper:** §IV-B
- [ ] **≥ 2 models compared:** 7 score files + T5
- [ ] **Models justified:** §IV-C + T4
- [ ] **Risk score:** pipeline output, alert levels final, F8
- [ ] **All listed metrics:** T5, F4, F5
- [ ] **Detection time:** T8
- [ ] **Precision/recall vs. accuracy:** §V paragraph
- [ ] **Unseen behavior:** T6
- [ ] **FP / FN analysis:** §VI-C + `fp_fn_causes.csv`
- [ ] **Feature importance:** F6, `feature_importance.csv`, T7
- [ ] **Anomaly explanations:** notebook 05 + §VI-B + F7
- [ ] **Prototype:** fresh-clone run + README section
- [ ] **Paper:** IEEE PDF, all T1–T8 / F1–F8 referenced
- [ ] **Limitations:** §VII
- [ ] **Research question answered:** §VIII with numbers

### 5.3 Health checks (check at every stand-up)
- **`main` is green:** `python -m pytest tests` passes (83 on Nov 5; the count only grows).
- **No overdue hand-off is undiscussed:** every late item in §3.3 has a new date.
- **No [H] box was ticked by an agent.**
- **Data moved at most once** (twice if S21 or S24 needed it); no score file or model was sent around.
