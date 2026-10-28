# Supriye — Data & Feature Engineering Lead + Paper Integrator

**Your stream in one sentence:** turn the raw CERT logs into a clean, labeled, one-row-per-user-day feature table that captures each user's **normal behavior and deviations from it**, then assemble the team's research paper.

**Deadline: Fri Nov 20, 2026. Target: submission-ready Thu Nov 19.**

Before starting, read [TEAM_PLAN.md](TEAM_PLAN.md) fully, especially **Section 5 (Team Rules)** and **Section 6 (Dataset Facts)**. You are responsible for enforcing the rules in 5.1, 5.3, 5.5, 5.7 and 5.10. Your stream is the **critical path** in Week 1: Arva and Ayo depend on v0 (Tue Nov 3) and v1 (Sun Nov 8), so protect those two dates above everything else.

---

## 1. Your Responsibilities

1. Set up the repository, environment, Overleaf and Zotero for the team.
2. Download and convert the CERT r4.2 data; build ground-truth labels.
3. Exploratory data analysis (EDA), including class imbalance and insider timelines.
4. Decide the final train/val/test split dates.
5. Engineer behavioral features: login patterns, activity times, USB/file access, email, web usage, organizational context.
6. **Establish normal behavior:** per-user baselines, peer-group baselines, deviation (`z_*`) features and novelty (`new_*`) flags.
7. Run the **feature-group ablation** study (which features matter most?).
8. *(Stretch)* LANL authentication features, which add authentication failures and compromised accounts.
9. Write paper sections I, III, IV-A, IV-B, VII and the Abstract; merge Related Work; **assemble and edit the whole paper**.

## 2. Hand-offs

| You give | To | Due |
|---|---|---|
| GitHub repo, `requirements.txt`, Overleaf + Zotero invites | Arva, Ayo | Thu Oct 29 |
| CERT Parquet files on the shared drive | Arva, Ayo | Sat Oct 31 (M0) |
| Final split dates (TEAM_PLAN 5.3) | Arva, Ayo | Mon Nov 2 |
| `features_v0.parquet` + `get_model_matrix()` | Arva, Ayo | Tue Nov 3 (M1) |
| `features_v1.parquet` + feature dictionary | Arva, Ayo | Sun Nov 8 (M2) |
| Any v1 bug fix (`features_v1_1.parquet`) | Arva, Ayo | Tue Nov 10, 12:00 at the latest |
| Data-processing time (for table T8) | Ayo | Fri Nov 13 |
| Merged full paper draft | Arva, Ayo | Wed Nov 18, 18:00 (M5) |

| You need | From | Due |
|---|---|---|
| `evaluate.py` | Ayo | Sun Nov 1 |
| `models_unsupervised.py` and `models_supervised.py` with tuned settings (for the ablation) | Arva, Ayo | Tue Nov 10 |
| Related Work paragraphs | Arva, Ayo | Fri Nov 13 |
| Paper sections IV-C, IV-D, V, VI-B | Arva, Ayo | Sun Nov 15 |
| Paper sections VI-A, VI-C, VIII | Arva, Ayo | Mon Nov 16 (M4) |

## 3. Files You Own
`src/data_loader.py`, `src/features.py`, `src/baseline.py`, `src/lanl_features.py` (stretch), `notebooks/01_eda.ipynb`, `notebooks/02_feature_engineering.ipynb`, `docs/feature_dictionary.md`, `README.md`, `requirements.txt`, `paper/`

---

## 4. Day-by-Day Timeline

| Date | Task | What |
|---|---|---|
| **Week 0** | | |
| Wed Oct 28 | S1, S2 | Start the CERT download; start repo setup |
| Thu Oct 29 | S2, S3 | Finish setup; run the kickoff meeting |
| Fri Oct 30 | S4 | Convert CSVs to Parquet |
| Sat Oct 31 | S5 | Data loaders and cleaning; share Parquet files → **M0** |
| Sun Nov 1 | S6, S7, S8 | Labels + insider timeline; EDA part 1; propose split dates |
| **Week 1** | | |
| Mon Nov 2 | S7, S8 | EDA part 2; finalize split at stand-up |
| Tue Nov 3 | S9 | Feature table v0 + `get_model_matrix()` → **M1** |
| Wed Nov 4 | S10, S11 | Login + activity-time features |
| Thu Nov 5 | S12, S13 | USB + file features; start the web-log job overnight |
| Fri Nov 6 | S14, S15 | Email + web-usage features |
| Sat Nov 7 | S16, S17 | Context features; per-user baselines (`z_user_*`) |
| Sun Nov 8 | S18, S19, S20 | Peer baselines + novelty flags; checks; **v1** → **M2** *(long day)* |
| **Week 2** | | |
| Mon Nov 9 | S20, S-LIT1 | v1 walkthrough at stand-up; read L1, L2 |
| Tue Nov 10 | S21, S23 | Bug-fix window (until 12:00); write III. Dataset |
| Wed Nov 11 | S22, S-LIT2 | Feature-group ablation; read L3 |
| Thu Nov 12 | S23, S-LIT3 | Write IV-A and IV-B; read L9a |
| Fri Nov 13 | S25, S26, S27 | Your Related Work paragraphs; Introduction; Limitations & Ethics |
| Sat Nov 14 | S28 | Results walkthrough; merge Related Work + table T1 |
| Sun Nov 15 | S29 | Assemble Overleaf with everything received so far |
| **Week 3** | | |
| Mon Nov 16 | S29 | Collect the remaining sections → **M4** |
| Tue Nov 17 | S30 | Abstract; integrate figures, tables, references |
| Wed Nov 18 | S31, S32 | Editing pass; circulate draft by 18:00 → **M5** |
| Thu Nov 19 | S33, S34 | Final read-through; README results; fresh-clone test → **submission-ready** |
| Fri Nov 20 | S35 | **Submit** |

---

## 5. Task Cards

### S1 · Wed Oct 28 · Start the download
**Goal:** get the data downloading today, because it is large.
1. Go to `kilthub.cmu.edu`, search **"Insider Threat Test Dataset"**, and download **`r4.2.tar.bz2`** and **`answers.tar.bz2`**.
2. Save them in `data/raw/` (which will be git-ignored).
3. Check you have ≥ 40 GB of free disk space.

**Done when:** both archives are fully downloaded, and the file sizes match the website.

### S2 · Wed Oct 28 – Thu Oct 29 · Repository, environment and writing tools
**Goal:** a shared setup that works the same on all three laptops.
1. Create a GitHub repo; add Arva and Ayo as collaborators.
2. Create the folder structure from [README.md](README.md) (empty folders need a `.gitkeep` file).
3. Create `.gitignore` containing at least: `data/`, `results/scores/`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`.
4. Create a virtual environment and install: `pandas numpy pyarrow scikit-learn xgboost imbalanced-learn torch shap matplotlib seaborn jupyter streamlit`.
5. Run `pip freeze > requirements.txt` and commit it.
6. Create the **Overleaf** project from the IEEE conference template with empty sections I–VIII; invite Arva and Ayo.
7. Create a **Zotero group library**; invite Arva and Ayo.
8. Commit the planning `.md` files.

**Done when:** Arva and Ayo have each cloned the repo and installed `requirements.txt` without errors, and both have accepted the Overleaf and Zotero invites.

### S3 · Thu Oct 29 · Run the kickoff meeting
1. Share your screen with [TEAM_PLAN.md](TEAM_PLAN.md) and go through Sections 2–5 and 11–13.
2. Confirm: the paper page limit, the course AI-use policy, PyTorch vs. Keras, and exactly what must be submitted on Nov 20 (paper only? paper + code? a demo?).
3. Agree on every rule in Section 5 and write any changes into TEAM_PLAN.md during the meeting.
4. Agree on the group chat and the stand-up times (Mon / Wed / Fri).

**Done when:** TEAM_PLAN.md is updated and pushed with the agreed decisions.

### S4 · Fri Oct 30 · Convert CSVs to Parquet
**Goal:** fast loading for everyone from here on.
1. Extract `r4.2.tar.bz2` and `answers.tar.bz2` into `data/raw/`.
2. For each CSV, read it with `pd.read_csv(path, chunksize=1_000_000)`. Parse `date` with `format="%m/%d/%Y %H:%M:%S"` (check the first rows to confirm the format). Write each chunk to Parquet with `pyarrow.parquet.ParquetWriter`.
3. For `http.csv` and `email.csv`, **drop the `content` column** while converting to save space (keep a note that it exists).
4. Print the row count and date range of every file and save them into `notebooks/01_eda.ipynb` (you will reuse these in the Dataset section).

**Done when:** every log has a Parquet file, and row counts match the CSVs.

### S5 · Sat Oct 31 · Data loaders and cleaning (`src/data_loader.py`) → M0
1. Write one function per log: `load_logon()`, `load_device()`, `load_file()`, `load_email()`, `load_http()`, `load_ldap()`, `load_psychometric()`. Each returns a clean DataFrame.
2. In every loader: convert `date` to `datetime`; add `day = date.dt.normalize()` and `hour = date.dt.hour + date.dt.minute / 60`; strip whitespace from `user` and `pc`; drop exact duplicate rows.
3. `load_ldap()`: read every monthly file, add a `month` column, and stack them into one table.
4. Print the number of duplicates and missing values removed per file. You will report these in the paper.
5. Upload the Parquet files to the shared drive, post the link, and push `data_loader.py`.

**Done when:** every loader runs in a fresh Python session; Arva and Ayo can download the Parquet files. → **M0**

### S6 · Sun Nov 1 · Ground-truth labels + insider timeline
**Goal:** know exactly which user-days are malicious.
1. Read `answers/insiders.csv`; keep rows for dataset 4.2. Note each insider's `user`, `scenario`, `start`, `end`.
2. For each insider, open their answer file in `answers/r4.2-<scenario>/`. Each line is a copy of one malicious log record. Extract the user and date of every line.
3. Build a table `malicious_days` with columns `user, day, scenario`.
4. **Check:** every malicious day falls between that insider's `start` and `end`. Investigate any that don't.
5. Make an **insider timeline table**: number of malicious user-days per **month × scenario**. You need it for S8.
6. Save it as `data/processed/labels.parquet`.

**Done when:** the number of insiders per scenario matches `insiders.csv`, and the timeline table is saved.

### S7 · Sun Nov 1 – Mon Nov 2 · Exploratory data analysis (`notebooks/01_eda.ipynb`)
Produce these outputs, each with a 1–2 sentence observation written by you underneath. Do items 2 and 6 **first**, because v0 needs them.
1. Events per log type per month (line chart).
2. Activity by **hour of day** and by **day of week**, for all users. Use this to decide "working hours" (see S11).
3. Distribution of events per user (histogram), to spot very active or very quiet users.
4. **Class imbalance:** total user-days, malicious user-days, % malicious, broken down by scenario. This becomes table **T2**.
5. **Insider vs. normal comparison (figure F1):** for one insider per scenario, plot daily activity over time and mark the malicious period. Show one normal user from the same role next to them.
6. Top 50 email recipient domains (to identify the company's own domain) and top 100 web domains (for the S15 keyword lists).

**Done when:** all 6 outputs are in the notebook with your written observations, and figures are saved to `results/figures/`.

### S8 · Sun Nov 1 – Mon Nov 2 · Decide the train/val/test split
1. Using the insider timeline table (S6), propose month boundaries close to 60% / 15% / 25% (TEAM_PLAN 5.3).
2. Check that **each** split contains malicious days from **all three** scenarios. Adjust the boundaries until it does.
3. Post the proposal in chat on Sun evening; confirm at the Mon stand-up.
4. Write the final dates into TEAM_PLAN.md Section 5.3 and push.

**Done when:** the dates are in TEAM_PLAN.md and every split has malicious days from all 3 scenarios.

### S9 · Tue Nov 3 · Feature table v0 + `get_model_matrix()` → M1
**Goal:** give Arva and Ayo real data early, even if simple.
1. **Users:** about 20 insiders (mix of all 3 scenarios) + 80 randomly chosen normal users (`random_state=42`), **all dates**.
2. **Rows:** one per user per day on which the user has at least one logon. Days with no activity are skipped; write this down for the paper.
3. **Features (basic only):** `f_logon_count`, `f_logoff_count`, `f_afterhours_logon`, `f_usb_connect`, `f_file_copy`, `f_email_sent`, `f_email_external`.
4. Add `split`, `label`, `scenario`, `insider`, `role`, `department` exactly as in TEAM_PLAN 5.1.
5. In `src/features.py` write:
   ```python
   def get_model_matrix(df, split=None, columns=None):
       """Return X (DataFrame), y (Series), feature_names.
       - split: 'train' / 'val' / 'test' / None (all rows)
       - columns: list of feature columns to use (default: every f_*, z_user_*, z_peer_*, new_* column)
       Applies log1p to f_* count columns and fills missing values with 0."""
   ```
   The `columns` argument is what makes the ablation (S22) possible.
6. Save as `data/processed/features_v0.parquet`, share it, and post in chat.

**Done when:** Arva and Ayo confirm that `get_model_matrix(pd.read_parquet("data/processed/features_v0.parquet"), split="train")` works in their code. → **M1**

### S10 · Wed Nov 4 · Login features
For each user-day, from `logon.csv`:

| Feature | Definition |
|---|---|
| `f_logon_count` | Number of Logon events |
| `f_logoff_count` | Number of Logoff events |
| `f_first_logon_hour` | Hour (decimal) of the first logon |
| `f_last_logoff_hour` | Hour of the last logoff (if missing, use the last event of the day) |
| `f_work_duration` | `f_last_logoff_hour − f_first_logon_hour` |
| `f_n_pcs` | Number of distinct PCs used |
| `f_logon_other_pc` | Logons on a PC that is not the user's **primary PC** (the PC they used most in the `train` split) |

`f_logon_other_pc` and `f_n_pcs` are our **authentication-behavior** signals, since CERT has no failed logins (TEAM_PLAN Section 6).

**Done when:** the features exist for all users, and you have checked a few user-days by hand against the raw log.

### S11 · Wed Nov 4 · Activity-time features
1. **Decide "after hours"** from the hour-of-day plot in S7 (e.g. before 07:00 or after 19:00). This is your decision; write down the reason.
2. Features:

| Feature | Definition |
|---|---|
| `f_afterhours_logon` | Logons outside working hours |
| `f_afterhours_events` | All events (logon, USB, file, email, web) outside working hours |
| `f_afterhours_ratio` | `f_afterhours_events / total events` |
| `f_weekend` | 1 if Saturday or Sunday, else 0 |

**Done when:** the features are added, and the after-hours definition and its reason are written into the feature dictionary.

### S12 · Thu Nov 5 · USB device features
| Feature | Definition |
|---|---|
| `f_usb_connect` | Number of Connect events |
| `f_usb_afterhours` | Connects outside working hours |
| `f_usb_n_pcs` | Distinct PCs with a USB connect |
| `f_usb_duration` | Total minutes connected (pair each Connect with the next Disconnect on the same PC; cap unmatched ones at the end of the day) |

**Done when:** the features are added, and you have checked one scenario-1 insider: their USB use should jump during the malicious period.

### S13 · Thu Nov 5 · File features
From `file.csv` (file copies to removable media). Group extensions from the `filename` column:

| Feature | Definition |
|---|---|
| `f_file_copy` | Total files copied |
| `f_file_doc` | `.doc`, `.docx`, `.pdf`, `.txt` |
| `f_file_exe` | `.exe` |
| `f_file_zip` | `.zip` and other archive types |
| `f_file_img` | `.jpg`, `.png` |
| `f_file_afterhours` | Copies outside working hours |

Before you finish today, also start **S15 step 2** so the long web-log job runs overnight.

**Done when:** the features are added, and the extension groups cover over 95% of files (check with `value_counts()`).

### S14 · Fri Nov 6 · Email features
1. Identify the **company domain** from the S7 domain counts (e.g. `dtaa.com`; confirm it in the data).
2. Use the rows where the user is the sender. Split `to`, `cc` and `bcc` on `;` to get the recipients.

| Feature | Definition |
|---|---|
| `f_email_sent` | Emails sent |
| `f_email_recipients` | Total recipients |
| `f_email_external` | Emails with at least one non-company recipient |
| `f_email_attach` | Total attachments |
| `f_email_external_attach` | External emails with ≥ 1 attachment |
| `f_email_size` | Mean email size |
| `f_email_bcc` | Emails using BCC |
| `f_email_afterhours` | Emails sent outside working hours |

**Done when:** the features are added; a scenario-3 insider shows a spike in `f_email_recipients` on their mass-email day.

### S15 · Thu Nov 5 (start) – Fri Nov 6 · Web-usage features
`http.csv` is huge, so process it **in chunks** and **only once**.
1. **(Thu) Keyword lists:** from the top web domains in S7, make 4 lists, e.g.:
   - `job`: job-search and recruiting sites
   - `leak`: `wikileaks` and similar
   - `cloud`: file-sharing / cloud-storage sites
   - `hack`: keylogger, spyware, hacking-tool sites

   Inspect the data to build the lists yourself; don't guess.
2. **(Thu night)** Read the Parquet file with only `user, date, url`. Per chunk: extract the domain, assign a category (or `other`), aggregate to `user, day, category → count`, and append to a small result table. Let it run overnight.
3. **(Fri)** Turn the aggregated table into features:

| Feature | Definition |
|---|---|
| `f_http_count` | Total page visits |
| `f_http_domains` | Distinct domains visited |
| `f_http_job` / `f_http_leak` / `f_http_cloud` / `f_http_hack` | Visits per category |
| `f_http_afterhours` | Visits outside working hours |

**Done when:** the features are added; scenario-1 insiders show `f_http_leak > 0` and scenario-2 insiders show increased `f_http_job`.

### S16 · Sat Nov 7 · Organizational context
1. Join `role` and `department` from the LDAP file for **that month** (people can change role).
2. *(Optional feature group)* Add the psychometric scores as `f_ctx_O`, `f_ctx_C`, `f_ctx_E`, `f_ctx_A`, `f_ctx_N`.
3. **Do NOT create a "days until leaving" feature.** It uses future information (in reality you don't know someone will leave), so it would be data leakage. Mention this in the paper as a deliberate choice.

**Done when:** every row has a `role` and `department`, and there are no "future" features.

### S17 · Sat Nov 7 · Per-user baselines (`src/baseline.py`) — the core of UEBA
**Goal:** measure how unusual each day is **for that specific user**.
1. Choose ~15 key features to baseline: logon count, first logon hour, work duration, after-hours events, USB connects, file copies, external emails, email recipients, HTTP count and each HTTP category, `f_logon_other_pc`.
2. For each user, sort by date and compute a rolling **mean** and **std** over the **previous 30 active days**, using `.shift(1)` so **today is never included**:
   ```python
   g = df.sort_values("date").groupby("user")[col]
   mean = g.transform(lambda s: s.shift(1).rolling(30, min_periods=10).mean())
   std  = g.transform(lambda s: s.shift(1).rolling(30, min_periods=10).std())
   df[f"z_user_{col[2:]}"] = (df[col] - mean) / (std + 1)
   ```
   The `+ 1` stops tiny standard deviations from producing huge values. Explain this choice in IV-B.
3. **Cold start:** if a user has fewer than 10 past days, the value is missing. Fill it with the matching `z_peer_*` value after S18 (or 0 if that is missing too).
4. Malicious days stay in the history. In real life nobody knows which days were bad, so this is the realistic choice. Write it down.
5. **Figure F3:** for one insider, plot a feature with its rolling mean ± 2 std band and mark the malicious days.

**Done when:** the `z_user_*` columns exist, and F3 is saved.

### S18 · Sun Nov 8 · Peer-group baselines + novelty flags
1. **Peer group** = users with the same `role` on the same `date`. For each key feature: `z_peer_x = (x − peer_mean) / (peer_std + 1)`. Use the same 15 features as S17.
2. If a role has fewer than 5 users, use `department` instead.
3. **Novelty flags** (computed from past days only):

| Flag | 1 when |
|---|---|
| `new_usb_user` | First day this user ever connects a USB drive |
| `new_pc` | User logs on to a PC never used before |
| `new_leak_site` | First visit to a `leak` or `cloud` site |
| `new_afterhours` | First ever after-hours logon |

4. Fill the cold-start gaps from S17 step 3.

**Done when:** the `z_peer_*` and `new_*` columns exist with no missing values.

### S19 · Sun Nov 8 · Validation and leakage checks
Run these checks and put the results in a cell at the end of `02_feature_engineering.ipynb`:
1. No missing or infinite values in any model-input column.
2. Rows per split, malicious rows per split, malicious rows per split **per scenario** (all > 0).
3. **Leakage test:** recompute the baselines after deleting the last month of data. The `z_user` values for earlier months must not change.
4. **Hand check:** for 3 insiders (one per scenario), open the raw logs for one malicious day and confirm that 3–4 feature values match by counting manually.
5. The table contains no column derived from `label`, `scenario` or future LDAP months.

**Done when:** all 5 checks pass and are documented.

### S20 · Sun Nov 8 – Mon Nov 9 · Feature table v1 + dictionary + walkthrough → M2
1. **(Sun)** Save `data/processed/features_v1.parquet`, share it, and post in chat.
2. **(Sun)** Write `docs/feature_dictionary.md` with one row per feature: **name, group, definition, unit, why it can indicate insider activity**. The groups are logon / time / usb / file / email / http / context / z_user / z_peer / new. A short first version is fine; polish it on Thu Nov 12 for IV-A.
3. **(Mon stand-up)** Run the 30-minute walkthrough for Arva and Ayo; announce the **freeze** (TEAM_PLAN 5.10). Decide together whether the LANL stretch (S24) happens.

**Done when:** both teammates have loaded v1 in their code. → **M2**

### S21 · Tue Nov 10 · Bug-fix window
1. Fix only bugs reported through GitHub Issues that change results.
2. If anything changed, release `features_v1_1.parquet` **by 12:00** and post in chat what changed.
3. After 12:00 the features are final.

**Done when:** all reported feature issues are closed or explicitly postponed.

### S22 · Wed Nov 11 · Feature-group ablation
**Goal:** answer *"which behavioral features contribute most to detection?"* from a second angle (Ayo covers SHAP).
1. Use Ayo's XGBoost and Arva's Isolation Forest **with their tuned settings** (committed by Tue Nov 10), and `get_model_matrix(..., columns=...)`.
2. Run these feature sets:
   - (a) raw `f_*` only
   - (b) `f_*` + `z_user_*`
   - (c) `f_*` + `z_user_*` + `z_peer_*` + `new_*` (= full)
   - (d) full set **minus one group at a time**: logon, time, usb, file, email, http, context
3. Record **PR-AUC** and **recall at the top-1% budget** on `test`, using `evaluate.py`.
4. Save `results/tables/ablation.csv` (table **T7**) and write 3–5 sentences on what you see.

**Done when:** the table is saved, and the comparison of (a) vs. (b) vs. (c) answers whether the baselining helps.

### S23 · Tue Nov 10 and Thu Nov 12 · Paper sections III, IV-A, IV-B
Write directly in Overleaf. **Your own words, no AI** (see Section 6).
- **Tue — III. Dataset:** what CERT r4.2 is and how it was generated (cite L1), the log types, the 3 scenarios, preprocessing (duplicates, Parquet, dropped columns), the split dates, the class-imbalance table **T2**, and the "no failed logins" gap.
- **Thu — IV-A Preprocessing & Feature Engineering:** why user-day granularity (cite L2), each feature group with its intuition, the after-hours definition, the condensed feature table **T3**, and why there is no "days until leaving" feature.
- **Thu — IV-B Establishing Normal Behavior:** the per-user rolling baseline formula, peer groups, novelty flags, cold-start handling, the `+1` in the denominator, figure **F3**.

**Done when:** all three sections are full paragraphs (not bullets), with every figure and table referenced in the text.

### S24 · Stretch (only if agreed on Mon Nov 9) · LANL authentication features
**Goal:** cover **authentication failures** and **compromised accounts**, which CERT cannot provide. Work on it Tue Nov 10 – Wed Nov 11 in the evenings; Arva and Ayo would run their models on it Thu Nov 12. If not agreed, skip it; the gap is covered in III and VII.
1. Read and accept the LANL data-use terms yourself at `csr.lanl.gov/data/cyber1/`; download `auth.txt.gz` and `redteam.txt.gz`.
2. Stream `auth.txt.gz` with `chunksize`. Columns, in order: `time, src_user, dst_user, src_comp, dst_comp, auth_type, logon_type, orientation, outcome`.
3. Keep only human user accounts: `src_user` starting with `U` (drop computer accounts ending in `$` and `ANONYMOUS`).
4. **Scope:** all users that appear in `redteam.txt` + 1,000 random other users (`random_state=42`).
5. `day = time // 86400`, `hour = (time % 86400) // 3600`.
6. Per user-day features: `f_auth_count`, `f_auth_fail`, `f_auth_fail_ratio`, `f_auth_dst_hosts`, `f_auth_src_hosts`, `f_auth_new_dst` (destination never seen before for this user), `f_auth_ntlm`, `f_auth_network_logon`.
7. `label = 1` if the (user, day) appears in `redteam.txt`. Split by day using the same 60/15/25 idea, checking that red-team days exist in every split.
8. Save `data/processed/lanl_features.parquet` in the TEAM_PLAN 5.1 format (`scenario = 0/1`).

**Done when:** the file is shared by Wed Nov 11 night.

### S25 · Fri Nov 13 · Your Related Work paragraphs
Write one paragraph each for L1, L2, L3 and L9a in **II. Related Work**, from your notes. Check that Arva and Ayo have posted theirs (also due today).

**Done when:** your paragraphs are in Overleaf.

### S26 · Fri Nov 13 · I. Introduction
Cover, in this order:
1. The insider-threat problem and why it's hard (insiders already have legitimate access).
2. What UEBA is and why behavior-based detection helps.
3. The research question (quoted exactly).
4. A bulleted list of our contributions: features with per-user and peer baselines, a comparison of unsupervised vs. supervised models, the unseen-scenario evaluation, explainable risk scoring.
5. A paper outline sentence ("Section II reviews…").

Any statistic you quote (e.g. the cost of insider incidents) must have a citation you have checked yourself.

**Done when:** the section is ~0.75 page and every claim is cited.

### S27 · Fri Nov 13 · VII. Limitations & Ethics
Cover at least:
- the data is **synthetic** (CERT)
- labels were used to clean the training data for the unsupervised models
- few insiders per scenario
- **concept drift**: normal behavior changes over time
- thresholds depend on the alert budget
- the cold-start problem
- no authentication failures in CERT
- **privacy and ethics** of monitoring employees: proportionality, transparency, the risk of false accusations, and why a human analyst must stay in the loop

**Done when:** each limitation says what its effect on our results is.

### S28 · Sat Nov 14 · Results walkthrough + merge II. Related Work
1. Attend the results walkthrough: present the ablation (S22), and note the agreed answer to the research question.
2. Order the Related Work paragraphs by theme (surveys → feature/granularity → unsupervised/deep → supervised/explainable), not by person.
3. Add linking sentences so it reads as one text.
4. Build table **T1**: paper, year, dataset, models, best result, limitation.
5. End with 2–3 sentences on the **gap our project fills**.

**Done when:** Related Work reads as one coherent section, and T1 is complete.

### S29 · Sun Nov 15 – Mon Nov 16 · Assemble the paper → M4
1. **(Sun)** Check that IV-C, IV-D, V and VI-B are in Overleaf and the project compiles.
2. **(Mon)** Check that VI-A, VI-C and VIII are in. Chase anything missing; it must be in by Mon night.

**Done when:** every section in TEAM_PLAN Section 11 exists as a full draft. → **M4**

### S30 · Tue Nov 17 · Abstract + integration
1. **Abstract** (~200 words): problem → approach → dataset → models → key results (best PR-AUC, recall, FPR) → main finding about features and unseen scenarios.
2. Number figures and tables consistently; make sure every one is referenced in the text.
3. Export the Zotero library in IEEE style; check all citations compile.

**Done when:** the paper compiles with no missing references (`??`) and is within the page limit.

### S31 · Wed Nov 18 · Editing pass
Go through the whole paper with this checklist:
- [ ] Terms are consistent: "user-day", "insider", "anomaly score", "risk score"
- [ ] Every number in the text matches the tables, and the tables match `results/tables/`
- [ ] Every figure has a caption and is readable when printed
- [ ] The research question is answered explicitly in VI or VIII
- [ ] Each section is in one consistent voice
- [ ] Page limit is respected

**Done when:** every checklist item is ticked.

### S32 · Wed Nov 18 · Circulate the full draft → M5
Export the PDF **by 18:00**, post it in chat, and ask each teammate for comments by Thu morning.

### S33 · Thu Nov 19 · Final read-through + README
1. Lead the final read-through meeting; assign and apply the last fixes.
2. Fill the **Results** section of [README.md](README.md) with the main comparison table.

### S34 · Thu Nov 19 · Fresh-clone test → submission-ready
1. Clone the repo into a **new folder**, create a new virtual environment, and run `pip install -r requirements.txt`.
2. Run the prototype (`python src/pipeline.py`) and `04_evaluation.ipynb` from top to bottom.
3. Produce the final PDF and the code archive, exactly as the course requires.

**Done when:** everything needed for submission is ready on Thu night.

### S35 · Fri Nov 20 · Submit
Submit the paper and code. Post a confirmation (screenshot) in the group chat.

### S-LIT1 / S-LIT2 / S-LIT3 · Literature reading
| Task | Date | Papers |
|---|---|---|
| S-LIT1 | Mon Nov 9 | L1 — Glasser & Lindauer (2013); L2 — Le, Zincir-Heywood & Heywood (2020) |
| S-LIT2 | Wed Nov 11 | L3 — Homoliak et al. (2019) |
| S-LIT3 | Thu Nov 12 | **L9a** — one 2022–2026 paper you find (TEAM_PLAN 7.3). L9b only if time allows |

For each paper: read it, fill in the note template (TEAM_PLAN 7.4) as `paper/lit_notes/<ID>.md`, and add it to Zotero. Skim L1 and L2 earlier if you can, since they help with S7 and S10.

---

## 6. Do This Yourself — No AI Agents

On top of the [team-wide list](TEAM_PLAN.md#12-human-only-work-no-ai-agents):

- [ ] **Read L1, L2, L3, L9a** and write their notes and Related Work paragraphs in your own words.
- [ ] **Choose the granularity** (user-day) and write the justification.
- [ ] **Define "working hours / after hours"** from your own reading of the EDA plots.
- [ ] **Build the web-category keyword lists** by inspecting the real domains.
- [ ] **Decide the split boundaries** (S8).
- [ ] **Hand-check labels and features** for 3 insiders (S6 step 4, S19 step 4).
- [ ] **Write the EDA observations** under each plot.
- [ ] **Interpret the ablation** (S22): which feature groups matter, and why that makes sense for each scenario.
- [ ] **Write** I. Introduction, III. Dataset, IV-A, IV-B, VII. Limitations & Ethics and the Abstract.
- [ ] **Merge and edit** Related Work and the full paper.
- [ ] **Verify every reference** in the final paper (it exists; authors, title, venue and year are correct).
- [ ] **Explain** `data_loader.py`, `features.py` and `baseline.py` line by line if asked.

---

## 7. Your Literature

| ID | Paper | What to extract |
|---|---|---|
| L1 | Glasser & Lindauer, IEEE S&P Workshops (2013) | How CERT was generated; why it's synthetic; limitations to cite in VII |
| L2 | Le, Zincir-Heywood & Heywood, IEEE TNSM (2020) | Their feature set and granularity comparison; their results on CERT (for T1) |
| L3 | Homoliak et al., ACM Computing Surveys (2019) | Insider-threat definitions and taxonomy for the Introduction |
| L9a (L9b optional) | 2022–2026 paper on insider-threat features / UEBA / compromised accounts (you find it) | Recent feature ideas; results to compare |
| — | Lindauer, CERT dataset, CMU KiltHub | Dataset citation |
| — | Kent, LANL (2015) | Only if S24 is done |

## 8. Your Models
You don't build models. You **run** Arva's Isolation Forest and Ayo's XGBoost with their tuned settings for the ablation (S22).

## 9. Your Tools
Python, **Pandas**, **NumPy**, **PyArrow** (Parquet, chunked reading), Jupyter, Matplotlib/Seaborn, Git/GitHub, **Overleaf**, **Zotero**.

## 10. Your Evaluation Responsibilities
| What | Where reported |
|---|---|
| Dataset size, class imbalance overall and per scenario | III. Dataset, table T2 |
| Feature-group ablation (PR-AUC, recall at top 1%) | V / VI-A, table T7 |
| Data-processing time (raw logs → v1 features) | Detection-time table T8 (send it to Ayo by Fri Nov 13) |
