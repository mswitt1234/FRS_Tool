# Queue Import CSV — Column and Syntax Reference

Derived from `queues.py` as of 2026-09-19. This is the authoritative list; the example CSVs in `Example CSVs/` predate several columns and will not run.

---

## 1. Ground rules

**Every column below must be present in the header row**, even if you never populate it. The tool validates all 38 settings columns and calls `exit()` on the first one it can't find. It does not care about column *order*.

**Headers are case-sensitive.** `MemberGroups` and `CallbackLiveVoice` are capitalised; `callerIDNum`, `slPercentage`, and `alerting_timeout_seconds` follow their own conventions. Copy the header row from `templates/queue_import_template.csv` rather than typing it. Trailing spaces in a header will also fail the match.

**A blank cell never means "set this to empty."** It means either "leave as-is" or "reset to default", depending on the clear-blanks prompt — see §5.

**Quote any value containing a comma.** Most compound fields are comma-delimited internally, so they need standard CSV double-quoting:

```csv
queue,routingRules,...
Sales,"10:90:MEETS_THRESHOLD,10:ANY",...
```

**Delimiter conventions inside compound fields:**

| Delimiter | Meaning |
|---|---|
| `:` | separates parts *within* one item (e.g. metric from operator) |
| `,` | separates *items in a list* (rings, rules, group names, code names) |
| `\|` | separates *groups of items* — one segment per bullseye ring or per CGR rule |

---

## 2. Column reference

### Identity and basics

| Column | Required | Format | Notes |
|---|---|---|---|
| `queue` | **Yes, always** | Queue name | The match key. Determines create vs. skip in CREATE mode, and which queue is updated in UPDATE mode. Not null-checked — a blank cell will error. |
| `division` | **Yes in CREATE** | Division name | Resolved by name lookup. Required on create even when the target is `Home`. |
| `description` | No | Free text | |

### Routing

| Column | Format | Notes |
|---|---|---|
| `evaluation` | `ALL` \| `BEST` \| `NONE` | Skill evaluation method. `ALL`=all skills matching, `BEST`=best available, `NONE`=disregard skills/next agent. |
| `scoreMethod` | `TimestampAndPriority` \| `PriorityOnly` | Queue scoring method (UI: Conversation score / Priority score). `ConversationScore` is **not** a valid value. |
| `routingRules` | `waitSeconds:operator` or `waitSeconds:threshold:operator`, comma-separated | See §3.1 |
| `bullseye` | See §3.2 | Bullseye rings. Mutually exclusive with `groupRouting`. |
| `groupRouting` | See §3.3 | Conditional group routing. Mutually exclusive with `bullseye`. |
| `MemberGroups` | See §3.4 | Interpreted differently depending on whether `bullseye` / `groupRouting` are populated. |

### Voice media settings

| Column | Format | Notes |
|---|---|---|
| `alerting_timeout_seconds` | Integer seconds, e.g. `8` | Voice alerting timeout |
| `slPercentage` | Decimal fraction, e.g. `0.8` | **Not a whole percent.** The FRS workbook stores `80`; divide by 100. |
| `slDuration_ms` | Milliseconds, e.g. `20000` | **Milliseconds, not seconds.** The FRS workbook stores `20`; multiply by 1000. |
| `callerIDNum` | Digits only, e.g. `8005551234` | Processed as `"+" + str(round(value))`. The `+` is added automatically; do not include it. No spaces, dashes, or parentheses — they raise an exception. |
| `callerIDName` | Free text | |
| `callScript` | Script **GUID** | Not a name. This field is assigned directly as an ID with no lookup, so a name here produces a broken reference or an API rejection. |
| `inQueueFlow` | Flow name | Resolved via `GET /architect/flows?name=`, takes the first match. Must be published. |
| `acw` | `MODE` or `MODE:timeoutSeconds` | See §3.5 |
| `enableTranscription` | See §4 | Voice transcription |
| `suppressInQueueCallRecording` | See §4 | **Note the inverted default:** clearing this sets it to `True` (suppression on). |
| `enableManualAssignment` | See §4 | |
| `enableAutoAnswerVoice` | See §4 | Voice channel only |
| `enableAutoAnswerAll` | See §4 | Sets auto-answer on voice, email, and every message subtype (webmessaging, sms, whatsapp, facebook, instagram, twitter, open). **Takes precedence** — if this is populated, `enableAutoAnswerVoice` is ignored. |

### Callback media settings

| Column | Format | Notes |
|---|---|---|
| `cb_alerting_timeout_seconds` | Integer seconds | |
| `cb_slPercentage` | Decimal fraction | |
| `cb_slDuration_ms` | Milliseconds | |
| `callBackMode` | `AgentFirst` \| `CustomerFirst` | See §3.6 |
| `CallbackLiveVoice` | `TransferToQueue` \| `TransferToFlow` \| `HangUp` | Only applied when `callBackMode=CustomerFirst`. Note capital U in `HangUp`. |
| `CallbackLiveVoiceFlow` | Flow name | **Mandatory** when `CallbackLiveVoice=TransferToFlow`; the row is skipped otherwise |
| `CallbackAnswerMachine` | `HangUp` \| `TransferToFlow` \| `TransferToQueue` | Only applied when `callBackMode=CustomerFirst`. Note capital U in `HangUp`. |
| `CallbackAnswerMachineFlow` | Flow name | **Mandatory** when `CallbackAnswerMachine=TransferToFlow` |

### Email media settings

| Column | Format | Notes |
|---|---|---|
| `email_alerting_timeout_seconds` | Integer seconds | FRS suggests `300` |
| `email_slPercentage` | Decimal fraction | |
| `email_slDuration_ms` | Milliseconds | FRS suggests `86400` seconds → `86400000` |
| `emailInQueueFlow` | Flow name | Resolved by name, first match |
| `emailScript` | Script **GUID** | Same caveat as `callScript` |
| `emailAddress` | Route pattern, e.g. `support` | Must be an **existing** inbound route under `emailDomain`. Matched exactly against the route pattern. |
| `emailDomain` | Domain ID, e.g. `mycompany.mypurecloud.com` | Required whenever `emailAddress` is set. Used as both the lookup key and the domain ID. |

### Associations

| Column | Format | Notes |
|---|---|---|
| `wrapUpCodes` | Comma-separated code names | Resolved by name, then `POST`ed to the queue. **Additive only** — this never removes existing codes, and clear-blanks cannot clear it. A name that doesn't resolve logs a warning and is skipped without failing the row. |
| `cannedResponses` | `All` \| `Blank` \| comma-separated library names | `All` = all libraries. `Blank` = none (maps to mode `None`). A list of names sets mode `SelectedOnly` with those libraries. Names must match exactly. |

---

## 3. Compound field syntax

### 3.1 `routingRules`

Comma-separated list of rules, applied in order.

```
waitSeconds:threshold:operator      (3 parts)
waitSeconds:operator                (2 parts — no threshold)
```

`operator` is a Genesys routing rule operator: `MEETS_THRESHOLD` or `ANY`. `threshold` is the skill-match percentage.

```csv
"10:90:MEETS_THRESHOLD,10:80:MEETS_THRESHOLD,10:70:MEETS_THRESHOLD,10:ANY"
```

Reads as: wait 10s requiring a 90% skill match, then 10s at 80%, then 10s at 70%, then accept any agent.

### 3.2 `bullseye`

Comma-separated list of rings, one per expansion step. Each ring is:

```
expansionType:thresholdSeconds                       (no skill removal)
expansionType:thresholdSeconds:Skill1|Skill2|Skill3  (remove these skills at this ring)
```

`expansionType` is currently always `TIMEOUT_SECONDS` in practice. Note that skills to remove are pipe-delimited *inside* the third part — the pipe means something different here than it does in `MemberGroups`.

```csv
"TIMEOUT_SECONDS:5:Spanish,TIMEOUT_SECONDS:10:Tier2|Escalation,TIMEOUT_SECONDS:15"
```

Three rings: after 5s drop the `Spanish` skill, after another 10s drop `Tier2` and `Escalation`, after another 15s expand with no further removal.

Each ring can have its own member groups — see §3.4.

### 3.3 `groupRouting` (conditional group routing)

Comma-separated list of rules. **Each rule currently requires five colon-delimited parts:**

```
metric:operator:conditionValue:waitSeconds:queueName
```

| Part | Values |
|---|---|
| `metric` | `EstimatedWaitTime` \| `ServiceLevel` |
| `operator` | `GreaterThan` \| `GreaterThanOrEqualTo` \| `LessThan` \| `LessThanOrEqualTo` |
| `conditionValue` | Numeric threshold |
| `waitSeconds` | How long to wait before evaluating the next rule |
| `queueName` | Parsed and then discarded by the code; the rule is always scoped to the queue being written |

```csv
"EstimatedWaitTime:GreaterThan:30:20:Sales,EstimatedWaitTime:GreaterThan:60:20:Sales"
```

> **Two known problems here.** (1) The example CSVs and `FRS_to_CSV.py` both emit only four parts, which raises an uncaught `ValueError`. Until that's reconciled, include the fifth field (any value) or fix the unpacking in `queues.py`. (2) Multi-rule CGR does not currently produce correct output — all emitted rules end up carrying the condition from the *last* rule in the list, paired with differing member-group sets. See README §6, items 2 and 7. Treat multi-rule CGR as unreliable until fixed.

### 3.4 `MemberGroups`

A list of member group references. Each reference is:

```
GroupName:none              → a standard Group (resolved via exact group search)
GroupName:DivisionName      → a Skill Expression Group in that division
```

How the list is segmented depends on the other routing columns:

| `bullseye` | `groupRouting` | How `MemberGroups` is read |
|---|---|---|
| blank | blank | One flat comma-separated list, assigned directly to the queue's member groups |
| populated | blank | Pipe-separated segments — **segment N supplies the member groups for ring N** |
| blank | populated | Pipe-separated segments — segment N is intended to supply the groups for rule N |
| populated | populated | Not supported; `groupRouting` wins and `bullseye` is cleared |

Flat (no bullseye, no CGR):

```csv
"Sales_Team:none,Tier1_Agents:Home"
```

Per-ring (three bullseye rings, two groups each):

```csv
"Ring1_Grp:none,Ring1_Skills:Home|Ring2_Grp:none,Ring2_Skills:Home|Ring3_Grp:none,Ring3_Skills:Home"
```

Notes:
- The `:none` form uses an **exact** group-name search. The division form uses a prefix search and then matches names in a loop, so it's more forgiving but slower.
- A trailing pipe (`...|`) produces an empty segment, which the code skips silently. The workbook's staging tab emits these; harmless.
- In the FRS workbook, the `SG` column holds the skill-expression-group reference (`Name:Division`) and the `MG` column holds the plain group references (`Name:none,Name2:none`); the converter joins them with a comma.

### 3.5 `acw` (after-call work)

```
MODE                  → set the ACW mode
MODE:timeoutSeconds   → set the mode and a timeout
```

The timeout is entered in **seconds** here and multiplied by 1000 before it's sent — one of the few places the tool does the unit conversion for you.

| Mode | Timeout applicable |
|---|---|
| `MANDATORY` | No |
| `OPTIONAL` | No |
| `AGENT_REQUESTED` | Yes |
| `MANDATORY_TIMEOUT` | Yes |
| `MANDATORY_FORCED_TIMEOUT` | Yes |

```csv
MANDATORY_TIMEOUT:120
```

### 3.6 `callBackMode`

`AgentFirst` clears all CustomerFirst-specific fields by rebuilding the callback settings object from scratch, preserving auto-answer, alerting timeout, service level, and the auto-dial/end values. The four `Callback*` columns are ignored.

`CustomerFirst` applies the four `Callback*` columns. If the queue has no existing live-voice reaction and you leave `CallbackLiveVoice` blank, it defaults to `TransferToQueue` and logs a notice. Same pattern for answering machine → `Hangup`.

---

## 4. Boolean columns

Applies to `enableTranscription`, `enableManualAssignment`, `suppressInQueueCallRecording`, `enableAutoAnswerVoice`, `enableAutoAnswerAll`.

> **Current behaviour is a bug you have to work around.** The value goes through Python's `bool()`, which returns `True` for *any* non-empty string. `false`, `FALSE`, `no`, and `0` all evaluate to **True**.

Until this is fixed, the only reliable usage is:

| Intent | What to put |
|---|---|
| Turn the setting **on** | `true` (or any non-empty text) |
| Turn the setting **off** | Leave the cell **blank** and run UPDATE with clear-blanks = YES |
| Leave it alone | Leave the cell blank and run with clear-blanks = NO |

Do not write `false` expecting it to disable anything.

---

## 5. Defaults applied when clearing

When you run UPDATE with clear-blanks = **YES**, a blank cell resets that setting to the value below. With clear-blanks = NO, blank cells are skipped entirely and nothing is sent for that field.

| Column | Reset to |
|---|---|
| `division` | `Home` |
| `description` | empty string |
| `evaluation` | `ALL` |
| `scoreMethod` | `TimestampAndPriority` |
| `alerting_timeout_seconds` | `8` |
| `slPercentage` | `0.8` |
| `slDuration_ms` | `20000` |
| `cb_alerting_timeout_seconds` | `30` |
| `cb_slPercentage` | `0.8` |
| `cb_slDuration_ms` | `20000` |
| `email_alerting_timeout_seconds` | `30` |
| `email_slPercentage` | `0.8` |
| `email_slDuration_ms` | `20000` |
| `callerIDNum` | empty string |
| `callerIDName` | empty string |
| `callScript` / `emailScript` | removed from the queue's default scripts |
| `inQueueFlow` | cleared |
| `emailInQueueFlow` | cleared |
| `emailAddress` | cleared |
| `routingRules` | cleared |
| `acw` | cleared |
| `bullseye` | cleared |
| `groupRouting` | cleared |
| `MemberGroups` | cleared |
| `enableTranscription` | `False` |
| `enableManualAssignment` | `False` |
| `suppressInQueueCallRecording` | **`True`** (inverted relative to the others) |
| `enableAutoAnswerVoice` / `enableAutoAnswerAll` | `False` |
| `callBackMode` | `AgentFirst` (CustomerFirst fields dropped) |
| `cannedResponses` | `All` |
| `CallbackLiveVoiceFlow` | **cannot be cleared** — logs a notice, leaves as-is |
| `CallbackAnswerMachineFlow` | **cannot be cleared** — logs a notice, leaves as-is |
| `wrapUpCodes` | **cannot be cleared** — no-op |

---

## 6. Worked examples

### Minimal create

```csv
queue,division,alerting_timeout_seconds,slPercentage,slDuration_ms,acw,evaluation
Sales_English,Home,8,0.8,20000,MANDATORY,BEST
```
(Plus the remaining 32 columns as empty headers.)

### Bullseye queue, three rings

```csv
queue,division,acw,inQueueFlow,bullseye,MemberGroups,evaluation,callerIDNum,callerIDName,alerting_timeout_seconds,slPercentage,slDuration_ms
Support_Tier1,Home,MANDATORY_TIMEOUT:120,Default In-Queue Flow,"TIMEOUT_SECONDS:5:Spanish,TIMEOUT_SECONDS:10,TIMEOUT_SECONDS:15","T1_Core:none,T1_Skills:Home|T2_Core:none|T3_Core:none",BEST,8005551234,Acme Support,8,0.8,20000
```

### Update service levels across many queues, touching nothing else

Run UPDATE with clear-blanks = **NO**:

```csv
queue,slPercentage,slDuration_ms
Sales_English,0.85,15000
Sales_Spanish,0.85,15000
Support_Tier1,0.8,30000
```
(Plus the remaining columns as empty headers.)

### Turn off transcription on a queue

Leave `enableTranscription` blank, populate nothing else you don't want reset, and run UPDATE with clear-blanks = **YES** — accepting that every other blank column also resets. In practice, safer to do this one in the admin UI until the boolean parsing is fixed.

---

## 7. Pre-flight checklist

Before an import run, confirm these already exist in the target org, since the tool resolves them by name and never creates them:

- [ ] Divisions
- [ ] Groups and Skill Expression Groups referenced in `MemberGroups`
- [ ] Skills referenced in `bullseye` removal lists
- [ ] Architect flows for `inQueueFlow`, `emailInQueueFlow`, `CallbackLiveVoiceFlow`, `CallbackAnswerMachineFlow` — **published**
- [ ] Scripts, and you have their **GUIDs** not their names
- [ ] Wrap-up codes
- [ ] Canned response libraries
- [ ] Email domain and inbound routes
- [ ] Names in the CSV are unique enough that a prefix match can't grab the wrong object
