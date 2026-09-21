# FRS Tool — User Guide

Covers the interactive run flow for the **Queues** and **Groups** importers. For column-by-column CSV detail see [`CSV_REFERENCE_QUEUES_General.md`](https://github.com/mswitt1234/FRS_Tool/blob/main/Documentation/CSV_REFERENCE_QUEUES_General.md) and `CSV_REFERENCE_GROUPS.md`.

---

## 1. Before you run

Rename ".sample.env" to ".env" and update credentials within. This will be the org the tool connects to.

| Check | Why |
|---|---|
| Python 3.12+ | Earlier versions can't parse the f-strings in `queues.py` |
| `pip install PureCloudPlatformClientV2 pandas requests` | Runtime dependencies |
| `results/` folder exists in your working directory | The results file is opened without creating the folder |
| `globals.py` points at the intended org | Wrong credentials = wrong org, silently |
| CSV has **every** required column header, exact case | The tool exits on the first missing column |
| You are running against a sandbox first | There is no dry-run and no undo |

Launch from inside the `FRS_Tool` directory:

```bash
cd FRS_Tool
python main.py
```

---

## 2. The prompt sequence

### Prompt 1 — Org confirmation

```
***Python Bulk Import Utility***

You are currently connected to "Acme Corp - Prod". If this is not expected,
please exit. Otherwise hit any key to continue.
```

The org name comes from a live `GET /api/v2/tokens/me` using the credentials in `globals.py`. **Read it.** This is the only guard against pointing a prod credential at a test CSV. If the name is wrong, Ctrl-C and fix `globals.py`.

If authentication failed, you'll have seen a `TokensApi->get_tokens_me` exception above this line and the org name will be blank or missing.

### Prompt 2 — Object type

```
For Queues press 1
For Groups press 2
For Data Action > Flow Dependencies Mapping press 3
For Script Details press 4
SELECTION:
```

Options 1 and 2 are the importers, and the rest of §2 describes their prompt flow. Option 2 currently fails with a `TypeError` on an argument-count mismatch (see README §6).

Option 3 is a read-only report and skips every prompt below — see §5. Option 4 references a module that isn't in the current repo and will raise `ModuleNotFoundError`.

### Prompt 3 — Results file

```
Would you like to generate a results file?
Press 1 for YES
Press 2 for NO
```

YES writes a transcript of everything printed to the console to `.\results\result_MM.DD.YYYY_HH.MM.SS.txt`. Anything other than `1` or `2` defaults to NO. Only `queues.py` honours this; the group path has no results-file support.

**Always choose YES for a real migration run.** The console output is the only record of which rows succeeded, and errors scroll past quickly.

### Prompt 4 — CSV path

```
Please specify the Queues file path:
```

Absolute or relative to your current working directory. No quoting needed — the whole line is taken literally, so don't wrap the path in quotes (they'd become part of the filename). Pandas reads it comma-delimited.

### Prompt 5 — Create or update

```
Would you like to create Queues or update Queues settings?
1 for CREATE or 2 for UPDATE:
```

**CREATE (1)** — for each row, if the queue name is *not* already in the org: `POST` a new queue with name + division, then immediately `PUT` the full set of CSV settings onto it. If the name *already exists*, the row is skipped with `> ALREADY EXISTS. USE UPDATE OPTION INSTEAD`. Nothing is overwritten.

Division is mandatory in create mode. A blank division fails the row with `Must include a Division when creating a queue for the first time`, even for Home.

**UPDATE (2)** — for each row, if the queue name exists: `PUT` the CSV settings onto the existing object. If not found, the row is skipped with `> NOT FOUND, USE CREATE OPTION INSTEAD`.

There is no upsert mode. A mixed CSV of new and existing queues needs two runs.

### Prompt 6 — Clear blanks (update mode only)

```
Would you like to reset Queues settings for blank values in the CSV?
1 for YES or 2 for NO:
```

This is the most consequential prompt in the tool.

| | Blank cell means | Use when |
|---|---|---|
| **NO (2)** | *Leave the existing value untouched.* | You want to change a few settings across many queues. Safe default. |
| **YES (1)** | *Reset the setting to its Genesys default.* | You want the CSV to be the authoritative definition of these queues. |

With YES, a CSV containing only `queue` plus one populated column will wipe every other setting on those queues back to defaults. The per-field default values are listed in `CSV_REFERENCE_QUEUES.md` §5.

In CREATE mode this prompt is skipped and the clear flag is forced off, because a brand-new queue has nothing to clear.

---

## 3. Reading the output

```
FETCHING ALL QUEUES INFO...
...
...DONE

QUEUE: Sales_English
> CREATED
> UPDATED
QUEUE: Sales_Spanish
> ERROR: The Division: "Retail" may not exist. Skipping
QUEUE: Support_Tier1
> ALREADY EXISTS. USE UPDATE OPTION INSTEAD

<<< PROCESSED ALL >>>
<<< START:     09/19/2026 14:02:11 >>>
<<< END:       09/19/2026 14:09:47 >>>
<<< Duration:  7 MIN 36 SEC >>>
<<< APPROX. API CALLS: 1184 >>>
```

- The initial fetch pages through **all** queues in the org at 100/page before processing starts. On a large org this takes a while and is normal.
- In create mode you'll see `> CREATED` (the POST) followed by `> UPDATED` (the settings PUT). Both lines for one queue is the success case.
- `> ERROR: ... Skipping` means that row was abandoned partway through. Because settings are applied to an in-memory object and PUT at the end, a row that errors during name resolution is **not** written at all — but if it was a create, the empty queue has already been POSTed and will exist with default settings. Those need cleanup or a follow-up update run.
- `APPROX. API CALLS` undercounts. Treat it as a rate-limit sanity check, not an audit.

### Common messages

| Message | Cause |
|---|---|
| `You are missing require column in CSV: X` | Header missing or wrong case. Tool exits immediately; nothing was written. |
| `The Division: "X" may not exist` | Division name doesn't match, or the token lacks `authorization:division:view` |
| `The Skill Expression Group "X" may not exist` | Name mismatch in a `MemberGroups` entry that specified a division |
| `The Group "X" may not exist` | Name mismatch in a `MemberGroups` entry that used `:none` |
| `The In Queue Flow "X" may not exist` | Flow name mismatch, or the flow is unpublished |
| `Could not locate Wrapup Code: X` | Wrap-up code name mismatch. Row continues; that code is just omitted. |
| `Specified outbound email address not found` | The email route must already exist under that domain |
| `CustomerFirst being enabled with default Transfer to Queue Live Voice Action` | Informational. You set `callBackMode=CustomerFirst` without a `CallbackLiveVoice` value. |
| `Cannot Clear "CallbackLiveVoiceFlow" setting. Leaving as-is` | Informational. That field has no clearable default. |
| `Exception when updating queue ...` | The PUT was rejected. The SDK message follows and usually names the offending field. |

---

## 4. Operational cautions

**No dry run, no rollback.** Every row writes as it is processed. If you abort mid-run, the rows already processed stay written. Before a production run, do the same CSV against a sandbox org and diff the results.

**Order matters for dependencies.** The tool resolves references by name and does not create them. Divisions, skill expression groups, groups, flows, scripts, wrap-up codes, canned response libraries, and email domains/routes must all exist *before* the queue import runs. Build in that order.

**Updates are whole-object PUTs against a snapshot** taken at the start of the run. If someone edits a queue in the admin UI while your import is running, your PUT will silently revert their change. Run imports in a change window.

**Batch size.** With per-field name resolution, a row with bullseye rings and several member groups can cost 15–30 API calls. Genesys Cloud throttles routing endpoints at roughly 300 requests/minute per token and the tool has no backoff. Split large workbooks into chunks of ~100 rows and check the API-call count afterwards to calibrate.

**Boolean columns are currently unreliable.** `enableTranscription`, `enableManualAssignment`, `suppressInQueueCallRecording`, and the auto-answer columns treat any non-empty text as `True` — including the word `false`. Until that's fixed, leave the cell blank to mean off (and use update-with-clear if you need to turn something off), and only populate it to mean on.

---

## 5. Data Action → Flow dependency report (menu option 3)

Unlike everything else in the tool, this option **writes nothing to the org.** It only reads, and its output is a CSV report on disk. That makes it the one module that's safe to run against production without a change window.

It also takes no input and asks no questions. Select `3` at the menu and it runs.

```
Data Actions Total: 218
Done
```

The report lands at:

```
FRS_Tool\architectDependency\GCDependecies\GCDependecies_{org}_{MM.DD.YYYY_HH.MM.SS}.csv
```

The org name comes from the token, so the filename records which org was surveyed. The path uses Windows separators and will fail on macOS/Linux.

### What's in it

One row per data action **per consuming flow**, so an action used by four flows produces four rows. Actions that nothing consumes get a single row with an empty flow and status `UNUSED`.

| Column | Contents |
|---|---|
| `Data Action Name` | e.g. `DA_Get Agent Alias` |
| `Data Action ID` | e.g. `custom_-_03f40efc-...` |
| `Integration` | The parent integration, e.g. `Genesys Cloud Data Actions` |
| `Flow Type` | `INBOUNDCALL`, `WORKFLOW`, `INQUEUECALL`, etc. Blank when `UNUSED`. |
| `Flow Name` | The consuming flow. Blank when `UNUSED`. |
| `Status` | See below |

| Status | What to do about it |
|---|---|
| `IN LASTEST` | Nothing. The flow's published version uses the current action. *(The misspelling is in the code, so it's in the data too.)* |
| `NOT IN LASTEST` | **Republish the flow.** It references an older version of the data action than what's currently saved. |
| `Flow Not Published` | The flow uses the action but has never been published. Expect it to be work-in-progress. |
| `FLOW DELETED` | The consuming flow is gone; the dependency record is stale. Usually safe to ignore, but a high count suggests dependency-tracking cruft. |
| `UNUSED` | No flow consumes this action. Cleanup candidate — verify it isn't called from a script or externally before deleting. |

### Using it

The three lists worth pulling out before a migration:

- Filter `Status = NOT IN LASTEST` → your republish backlog. These flows will behave unexpectedly because they're pinned to a stale action version.
- Filter `Status = UNUSED` → actions you may not need to migrate at all.
- Group by `Integration` → which integrations are actually load-bearing, and which can be deprioritised.

### Cautions

**The output may be incomplete, silently.** Neither API call in this module pages its results. The data action fetch requests an oversized page and gets capped by the platform; the flow lookup takes the default page size. If your org has more data actions than the cap, or any action consumed by more flows than one page holds, those are simply absent from the report with no warning. Sanity-check the `Data Actions Total` line printed at the start against the action count in the admin UI before trusting the file as a complete inventory.

**It depends on Genesys dependency tracking**, which is an index that rebuilds periodically. If a rebuild is in progress or recently triggered, results can lag reality.

**Errors are near-silent.** A failure inside the per-action loop prints `Whoops, I broke inside "FindFlows"` and moves on without naming the data action, so the row is just missing.

**Don't run it twice in one session.** The row accumulator is a module-level list that never resets, so a second run in the same process would emit the first run's rows again.

---

## 6. The FRS → CSV converter

`FRS_to_CSV.py` is a prototype and does not currently run — it imports a `CSVDataManager` module that isn't in the repo. Its intended invocation is:

```bash
python FRS_to_CSV.py --excel_file FRS_Workbook_for_scripting.xlsx --sheet_name_to_process CGRQueues
```

It understands two sheet names, `BullseyeQueues` and `CGRQueues`, reads up to six ring/rule column groups from each, and emits an `Output\Output_YYYYMMDD_HHMM.csv` containing only `bullseye`/`groupRouting` plus `MemberGroups`. Everything else still has to be filled in by hand. See `FRS_WORKBOOK_MAP.md` for what a complete version needs to cover.

In the meantime, the `BullseyeQueuesCSV` tab in the example workbook shows the manual pattern: a staging sheet with CSV-shaped headers and formulas that concatenate the human-readable FRS columns into the compound syntax.
