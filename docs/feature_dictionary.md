# Feature dictionary: `features_v1.parquet`

One row per **user-day** on which the user has at least one logon event (S9 step 2). Built by `python -m src.features v1` (`src/features.py` + `src/baseline.py`). Model inputs are the columns starting with `f_`, `z_user_`, `z_peer_` or `new_`; every model reads them through `get_model_matrix()`, which applies `log1p` to the `f_*` counts (all `f_*` except the non-count ones marked *(not logged)*) and fills missing values with 0 (TEAM_PLAN 5.5).

**Settings these features depend on** (`src/config.py`, decided by Supriye on Fri Nov 6, S8):
- **Working hours:** 07:00–19:00. An event is *after hours* when its hour is before 07:00 or at/after 19:00. *Reason (Supriye, S11): to be written from the hour-of-day plot in `notebooks/01_eda.ipynb`.*
- **Company domain:** `dtaa.com` (found in the data, not a judgement call).
- **Which emails count as sent:** all of them, including personal webmail sent from the work PC (`EMAIL_COUNT_PERSONAL = True`). *Reason (Supriye, S14): to be written.*
- **Web keyword lists:** `HTTP_CATEGORIES` (job, leak, cloud, hack), built from all 475 domains in the log. *Reason (Supriye, S15): to be written.*
- **Scenario-3 labels:** the 20 days the sysadmin spent logged in as their supervisor stay labeled on `FAW0032`/`FBA0348` (compromised-account view); those accounts have `insider` = 0. *Reason (Supriye, S6): to be written.*

## Metadata (never model inputs)

| Column | Definition |
|---|---|
| `user` | CERT user id |
| `date` | Calendar day (midnight) |
| `split` | `train` (≤ `TRAIN_END`), `val` (≤ `VAL_END`) or `test`, by date (TEAM_PLAN 5.3) |
| `label` | 1 if the answer files list a malicious event for this user on this day |
| `scenario` | 1, 2 or 3 for malicious days, else 0 |
| `insider` | 1 if the user is in `answers/insiders.csv` (the 2 hijacked supervisor accounts are 0) |
| `role`, `department` | From that month's LDAP snapshot; 14 senior staff without a department use their functional unit |

## Behavior features (`f_*`)

| Name | Group | Definition | Unit | Why it can indicate insider activity |
|---|---|---|---|---|
| `f_logon_count` | logon | Logon events | count | Unusual session volume |
| `f_logoff_count` | logon | Logoff events | count | Sessions left open, or many short sessions |
| `f_first_logon_hour` | logon | Hour of the first logon *(not logged)* | hour (decimal) | Arriving at unusual times |
| `f_last_logoff_hour` | logon | Hour of the last logoff; the last event of the day if there is no logoff *(not logged)* | hour | Staying late |
| `f_work_duration` | logon | `f_last_logoff_hour − f_first_logon_hour` *(not logged)* | hours | Unusually long or odd working days |
| `f_n_pcs` | logon | Distinct PCs with a logon or logoff | count | Moving between machines; stand-in for authentication behavior (CERT has no failed logins) |
| `f_logon_other_pc` | logon | Logons on a PC that is not the user's primary PC (most logons in train; users without train logons: their first 30 active days) | count | Using someone else's machine, as in scenario 3 |
| `f_afterhours_logon` | time | Logons outside working hours | count | Scenario 1 starts working after hours |
| `f_afterhours_events` | time | Logon, USB, file, email and web events outside working hours | count | Activity when fewer people are watching |
| `f_afterhours_ratio` | time | `f_afterhours_events / all events that day` *(not logged)* | share 0–1 | Shift of activity into the night, independent of volume |
| `f_weekend` | time | 1 on Saturday or Sunday *(not logged)* | 0/1 | Weekend work is rare in this company |
| `f_usb_connect` | usb | USB Connect events | count | Removable media is the main exfiltration route in scenarios 1 and 2 |
| `f_usb_afterhours` | usb | Connects outside working hours | count | Copying data at night |
| `f_usb_n_pcs` | usb | Distinct PCs with a connect | count | Using drives on several machines |
| `f_usb_duration` | usb | Minutes connected: each Connect is paired with the next Disconnect on the same PC that day, else capped at midnight | minutes | Long sessions = large transfers |
| `f_file_copy` | file | Files copied to removable media | count | Volume of data leaving |
| `f_file_doc` | file | `.doc`, `.docx`, `.pdf`, `.txt` copies | count | Documents are what gets stolen |
| `f_file_exe` | file | `.exe` copies | count | Bringing tools in or out (scenario 3's keylogger) |
| `f_file_zip` | file | Archive copies (`.zip`, `.rar`, `.7z`, `.tar`, `.gz`) | count | Packing data for transfer |
| `f_file_img` | file | `.jpg`, `.jpeg`, `.png` copies | count | Usually harmless; gives the model a contrast |
| `f_file_afterhours` | file | Copies outside working hours | count | Copying at night |
| `f_email_sent` | email | Emails sent | count | Unusual communication volume |
| `f_email_recipients` | email | Recipients over to + cc + bcc | count | Mass emails (scenario 3) |
| `f_email_external` | email | Emails with ≥ 1 recipient outside `dtaa.com` | count | Contact with competitors or personal accounts |
| `f_email_attach` | email | Attachments | count | Sending files out |
| `f_email_external_attach` | email | External emails with ≥ 1 attachment | count | The most direct email exfiltration signal |
| `f_email_size` | email | Mean email size *(not logged)* | bytes | Large emails carry data |
| `f_email_bcc` | email | Emails using BCC | count | Hiding recipients |
| `f_email_afterhours` | email | Emails sent outside working hours | count | Night-time communication |
| `f_http_count` | http | Page visits | count | Unusual browsing volume |
| `f_http_domains` | http | Distinct domains | count | Browsing outside one's usual sites |
| `f_http_job` | http | Visits to job sites (`HTTP_CATEGORIES["job"]`) | count | Scenario 2: looking for a new job before leaving |
| `f_http_leak` | http | Visits to leak sites (`wikileaks.org`) | count | Scenario 1: uploading data to WikiLeaks |
| `f_http_cloud` | http | Visits to file-sharing / cloud-storage sites | count | Moving data out without a drive |
| `f_http_hack` | http | Visits to keylogger / spyware / hacking sites | count | Scenario 3: getting a keylogger |
| `f_http_afterhours` | http | Visits outside working hours | count | Night-time browsing |
| `f_ctx_O`, `f_ctx_C`, `f_ctx_E`, `f_ctx_A`, `f_ctx_N` | context | Big-Five psychometric scores from `psychometric.csv`, constant per user *(not logged)* | score 10–50 | Optional group; lets the ablation (S22) test whether personality helps |

There is **no "days until leaving" feature**: it would use future information (S16 step 3).

## Baselines (`src/baseline.py`)

Computed for 14 key features: `logon_count`, `first_logon_hour`, `work_duration`, `afterhours_events`, `usb_connect`, `file_copy`, `email_external`, `email_recipients`, `http_count`, `http_job`, `http_leak`, `http_cloud`, `http_hack`, `logon_other_pc`. The `+ 1` in each denominator keeps users with an almost constant history from producing huge values.

| Name | Group | Definition | Unit | Why it can indicate insider activity |
|---|---|---|---|---|
| `z_user_<x>` | z_user | `(x − mean) / (std + 1)` over the user's **previous 30 active days** (today excluded). With fewer than 10 past days (cold start) it takes the `z_peer_<x>` value, else 0. Malicious days stay in the history. | std units | Change against the user's **own** normal: the core of UEBA |
| `z_peer_<x>` | z_peer | `(x − mean) / (std + 1)` over the user's peer group **on the same date**. Peer group = same role; a role with fewer than 5 users that day uses the department. The group includes the user. A group of one gives 0. | std units | Behavior unusual for the job, even if the user has always done it |
| `new_usb_user` | new | 1 on the first day the user connects a USB drive | 0/1 | Scenario 1 users had never used drives before |
| `new_pc` | new | 1 on a day the user logs on to a PC never used before | 0/1 | Logging on to someone else's machine |
| `new_leak_site` | new | 1 on the first visit to a leak or cloud site | 0/1 | First contact with an exfiltration channel |
| `new_afterhours` | new | 1 on the first after-hours logon | 0/1 | Start of a new working pattern |

All `new_*` flags use past days only and are 0 on a user's first active day, since nothing can be "new" on the day the history starts.
