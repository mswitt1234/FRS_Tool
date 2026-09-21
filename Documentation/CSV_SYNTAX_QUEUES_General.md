# Queue CSV Syntax — Core Columns

Covers all 35 queue CSV columns **except** the four advanced-routing fields (`routingRules`, `bullseye`, `groupRouting`, `MemberGroups`), which are documented separately.

Values are given from the Genesys Cloud side first — what the setting is, where it lives in the admin UI, and what the Platform API accepts — then how this tool's CSV expresses it. Enum values below were read from the `PureCloudPlatformClientV2` SDK models, not inferred from the tool's code.

---

## 1. Conventions

| | |
|---|---|
| **Header case** | Exact match required. 31 of the 35 are lowercase or snake_case; `CallbackLiveVoice`, `CallbackLiveVoiceFlow`, `CallbackAnswerMachine`, `CallbackAnswerMachineFlow` are PascalCase. |
| **All headers present** | Every column must appear in the header row even when unused. The tool `exit()`s on the first missing header. |
| **Blank cell** | Never means "set to empty." Means *leave as-is* (clear-blanks = NO) or *reset to default* (clear-blanks = YES). |
| **Enum case** | The SDK validates case-insensitively but sends what you typed. Use the exact casing in this doc. |
| **Invalid enum** | **Fails silently at assignment.** The SDK replaces an unrecognised value with the literal string `outdated_sdk_version`, so the error surfaces later as a rejected PUT that doesn't name your CSV cell. Enum typos are the hardest failure to diagnose in this tool. |

---

## 2. General tab

| CSV column | Genesys setting | API field | Value / syntax | Notes |
|---|---|---|---|---|
| `queue` | Queue **Name** | `name` | Text | Must be org-unique. **No special characters** (Genesys constraint). The tool's match key for create-vs-update. |
| `division` | **Division** | `division.id` | Division name | Resolved by name → GUID. A queue belongs to exactly one division. Mandatory on create, including for `Home`. |
| `description` | — | `description` | Text | API-only field; not surfaced on the queue config screens. |
| `acw` | **After Call Work** + **ACW Timeout (Seconds)** | `acwSettings.wrapupPrompt`, `acwSettings.timeoutMs` | `MODE` or `MODE:seconds` | See §2.1 |
| `enableManualAssignment` | **Enable Manual Assignment** | `enableManualAssignment` | See §7 | |
| `enableAutoAnswerAll` | **Auto answer** (General tab) | per-media `enableAutoAnswer` | See §7 | Broader than the UI toggle — see §7.1 |

### 2.1 `acw`

The timeout is supplied in **seconds** and multiplied by 1000 before sending. Genesys caps it at **3600 seconds**.

| CSV value | UI label | Timeout applies? |
|---|---|---|
| `OPTIONAL` | Optional | No |
| `MANDATORY` | Mandatory, Discretionary | No |
| `MANDATORY_TIMEOUT` | Mandatory, Time-boxed | Yes |
| `MANDATORY_FORCED_TIMEOUT` | Mandatory, Time-boxed no early exit | Yes |
| `AGENT_REQUESTED` | Agent Requested | Yes |

```
MANDATORY_TIMEOUT:90
MANDATORY
```

Two Genesys behaviours worth knowing: the ACW timeout applies **only to voice** unless *Enforce Communication Level After Call Work* is enabled org-wide, and `AGENT_REQUESTED` only appears to agents when that same org setting is on. Callbacks always require a wrap-up code regardless of ACW mode.

---

## 3. Routing tab (scoring and evaluation only)

| CSV column | Genesys setting | API field | Value / syntax |
|---|---|---|---|
| `scoreMethod` | **Scoring Method** | `scoringMethod` | `TimestampAndPriority` \| `PriorityOnly` |
| `evaluation` | **Evaluation Method** | `skillEvaluationMethod` | `ALL` \| `BEST` \| `NONE` |

**`scoreMethod` value mapping** — the UI labels and API values don't resemble each other:

| CSV value | UI label | Behaviour |
|---|---|---|
| `TimestampAndPriority` | Conversation score | Arrival time adjusted by priority; one priority point = 60,000 ms |
| `PriorityOnly` | Priority score | Ranked by priority, time-in-queue breaks ties |

There is **no `ConversationScore` value.** If your FRS workbook or a prior CSV carries it, it will be silently converted to `outdated_sdk_version`.

**`evaluation` value mapping:**

| CSV value | UI label |
|---|---|
| `ALL` | All skills matching |
| `BEST` | Best available skills |
| `NONE` | Disregard skills, next agent (longest idle) |

Note that "Disregard skills" is **`NONE`**, not `ALL` — the intuitive reading of "all agents" is wrong here.

---

## 4. Voice tab

| CSV column | Genesys setting | API field | Value / syntax | Notes |
|---|---|---|---|---|
| `slPercentage` | **Service Level** % | `mediaSettings.call.serviceLevel.percentage` | Decimal `0`–`1`, e.g. `0.8` | Not a whole percent. UI shows a percentage slider. |
| `slDuration_ms` | **Service Level Target (Seconds)** | `mediaSettings.call.serviceLevel.durationMs` | Milliseconds, e.g. `20000` | UI is in seconds; CSV is in ms. |
| `alerting_timeout_seconds` | **Alerting Timeout** | `mediaSettings.call.alertingTimeoutSeconds` | Integer **7–59** | Genesys-enforced range. Ignored when auto-answer is on (the UI hides the field). Timeout → agent goes Not Responding, interaction returns to queue. |
| `callerIDName` | **Calling Party Name** | `callingPartyName` | Text | A calling name configured on an external SIP trunk **overrides** this and the queue value never appears. |
| `callerIDNum` | **Calling Party Number** | `callingPartyNumber` | Digits only, e.g. `12223334444` | Genesys validates **E.164**. The tool prepends `+` for you and processes the cell as a number, so no `+`, spaces, dashes, or parentheses. |
| `inQueueFlow` | **In-Queue Flow** | `queueFlow.id` | Flow name | Resolved by name, first match, must be published. If unset, the org default in-queue flow applies. A Transfer to ACD action's in-queue flow beats both. |
| `callScript` | **Default Script** | `defaultScripts["CALL"]` | Script **GUID** | Not a name — assigned directly as an ID with no lookup. |
| `suppressInQueueCallRecording` | **Continue voice recording during queue wait** (inverted) | `suppressInQueueCallRecording` | See §7 | **The CSV column is the logical inverse of the UI checkbox.** `true` here = UI box unchecked = recording suppressed while in queue. |
| `enableTranscription` | **Voice Transcription** | `enableTranscription` | See §7 | Requires voice transcription enabled org-wide first. |
| `enableAutoAnswerVoice` | **Auto answer** (Voice tab) | `mediaSettings.call.enableAutoAnswer` | See §7 | Voice only. **Ignored entirely if `enableAutoAnswerAll` is populated.** |

`defaultScripts` is a map keyed by media type, and the tool reads the existing map before setting keys — so populating `callScript` alone won't disturb an existing email script.

---

## 5. Callback tab

| CSV column | Genesys setting | API field | Value / syntax |
|---|---|---|---|
| `cb_slPercentage` | **Service Level** % | `mediaSettings.callback.serviceLevel.percentage` | Decimal `0`–`1` |
| `cb_slDuration_ms` | **Service Level Target** | `mediaSettings.callback.serviceLevel.durationMs` | Milliseconds |
| `cb_alerting_timeout_seconds` | **Alerting Timeout (Seconds)** | `mediaSettings.callback.alertingTimeoutSeconds` | Integer seconds |
| `callBackMode` | **Callback Type** | `mediaSettings.callback.mode` | `AgentFirst` \| `CustomerFirst` |
| `CallbackLiveVoice` | **Live Voice** | `liveVoiceReactionType` | `TransferToQueue` \| `TransferToFlow` \| `HangUp` |
| `CallbackLiveVoiceFlow` | Live Voice → **Select Flow** | `liveVoiceFlow.id` | Flow name |
| `CallbackAnswerMachine` | **Answering Machine** | `answeringMachineReactionType` | `HangUp` \| `TransferToFlow` \| `TransferToQueue` |
| `CallbackAnswerMachineFlow` | Answering Machine → **Select Flow** | `answeringMachineFlow.id` | Flow name |

**Mode gates the rest.** `AgentFirst` (the Genesys default — agent connects first, system then dials the customer) causes the tool to rebuild the callback settings object from scratch, dropping all four `Callback*` values. They're only applied under `CustomerFirst`.

**Casing:** the API value is `HangUp`, capital U. The tool hardcodes `Hangup` as its fallback default, which survives the SDK's case-insensitive check but reaches the API with non-canonical casing. Write `HangUp` in the CSV.

**Flow columns are conditionally mandatory.** `TransferToFlow` without the matching `*Flow` column populated fails the row. Leaving `CallbackLiveVoice` blank under `CustomerFirst` defaults it to `TransferToQueue` with a logged notice; answering machine defaults to hangup the same way.

**UI vs API scope:** the admin UI offers only Transfer to Queue / Transfer to Flow for Live Voice, and only Transfer to Flow / Hangup for Answering Machine. The API accepts all three for both, so the CSV can set combinations the UI won't show you.

Not exposed by this tool: pacing modifier, retry attempt controls, agent ownership period, auto-start/end callbacks, routing site.

---

## 6. Email tab

| CSV column | Genesys setting | API field | Value / syntax | Notes |
|---|---|---|---|---|
| `email_slPercentage` | **Service Level** % | `mediaSettings.email.serviceLevel.percentage` | Decimal `0`–`1` | |
| `email_slDuration_ms` | **Service Level Target** | `mediaSettings.email.serviceLevel.durationMs` | Milliseconds | FRS often states 86400 s → `86400000` |
| `email_alerting_timeout_seconds` | **Alerting Timeout (Seconds) for Manual Answer** | `mediaSettings.email.alertingTimeoutSeconds` | Integer seconds | Hidden in the UI when email auto-answer is on |
| `emailAddress` | **Outbound Email Address** | `outboundEmailAddress.route` | Route pattern, e.g. `support` | Must **already exist** as an inbound route under the domain. Matched exactly. |
| `emailDomain` | **Email Domain** | `outboundEmailAddress.domain.id` | Domain ID, e.g. `acme.mypurecloud.com` | Required whenever `emailAddress` is set; used as both lookup key and domain ID |
| `emailInQueueFlow` | **In-Queue Email Flow** | `emailInQueueFlow.id` | Flow name | Resolved by name, first match |
| `emailScript` | **Default Script** (Email) | `defaultScripts["EMAIL"]` | Script **GUID** | Same as `callScript` |

The tool sets the single outbound address only. Genesys also supports assigning multiple addresses per queue via **Manage Addresses** with one flagged default; that isn't reachable from the CSV.

---

## 7. Boolean columns

Applies to `enableTranscription`, `enableManualAssignment`, `suppressInQueueCallRecording`, `enableAutoAnswerVoice`, `enableAutoAnswerAll`.

> **This is a real defect, but it does not fire on every value.** The tool passes the cell through Python's `bool()`, which for a *string* just tests non-emptiness — `bool("off")` is `True`. What saves it most of the time is pandas: if a column holds only `true`/`false` (any casing) plus blanks, `read_csv` converts them to real booleans first and the result is correct.

The failure is therefore **column-level and data-dependent**, not per-cell:

| Column contains | Result for a "false" value |
|---|---|
| `true`/`false` (any casing) + blanks | Correct |
| `1`/`0` + blanks | Correct |
| `on`/`off` — **the FRS workbook's spelling** | **Wrong — evaluates True** |
| `yes`/`no`, `Y`/`N` | **Wrong — evaluates True** |
| `true`/`false` **plus any other token anywhere in the column** | **Wrong — evaluates True** |

One stray cell — a note, `N/A`, a typo — changes the column's inferred type and silently flips every `false` in every row to `True`, with no error raised.

Safe usage until a real string-to-bool parser is added:

| Intent | CSV value | Run mode |
|---|---|---|
| Enable | `true` | either |
| Disable | `false` | either — **but only if the column contains nothing but `true`, `false` and blanks** |
| Disable (guaranteed) | *blank* | UPDATE, clear-blanks = **YES** |
| Leave unchanged | *blank* | UPDATE, clear-blanks = **NO** |

Never write `on`/`off`/`yes`/`no`, and keep these columns free of any other text.

### 7.1 Auto-answer precedence

`enableAutoAnswerAll` is checked first. If populated, `enableAutoAnswerVoice` is **ignored** and the value is written to voice, email, and all seven message subtypes (webmessaging, sms, whatsapp, facebook, instagram, twitter, open). Only when `enableAutoAnswerAll` is blank does `enableAutoAnswerVoice` apply, and then to voice alone.

This is wider than the UI's General-tab **Auto answer** toggle, which covers digital channels only — voice auto-answer is a separate Voice-tab setting there.

---

## 8. Associations

| CSV column | Genesys setting | API | Value / syntax |
|---|---|---|---|
| `wrapUpCodes` | **Wrap-up Codes** tab | `POST /routing/queues/{id}/wrapupcodes` | Comma-separated code names |
| `cannedResponses` | **Canned Responses** tab | `cannedResponseLibraries` | `All` \| `Blank` \| comma-separated library names |

**`wrapUpCodes` is additive only.** The endpoint adds; nothing in the tool removes. Re-running with a shorter list leaves the old codes attached, and clear-blanks cannot clear it. Codes that don't resolve log a warning and are skipped without failing the row. Genesys recommends codes assigned to the same division as the queue, for cleaner reporting.

**`cannedResponses` maps to three modes:**

| CSV value | API mode | UI option |
|---|---|---|
| `All` | `All` | All libraries |
| `Blank` | `None` | No libraries |
| `Lib1,Lib2` | `SelectedOnly` | Specific libraries |

Library names must match exactly. Genesys allows a maximum of 50 libraries per organization. Note the CSV literal is the word `Blank`, not an empty cell — an empty cell means leave-as-is or reset-to-`All`.

---

## 9. Defaults applied when clear-blanks = YES

| Column | Reset to |
|---|---|
| `division` | `Home` |
| `description`, `callerIDNum`, `callerIDName` | empty string |
| `evaluation` | `ALL` |
| `scoreMethod` | `TimestampAndPriority` |
| `alerting_timeout_seconds` | `8` |
| `slPercentage`, `cb_slPercentage`, `email_slPercentage` | `0.8` |
| `slDuration_ms`, `cb_slDuration_ms`, `email_slDuration_ms` | `20000` |
| `cb_alerting_timeout_seconds`, `email_alerting_timeout_seconds` | `30` |
| `acw` | cleared |
| `inQueueFlow`, `emailInQueueFlow`, `emailAddress` | cleared |
| `callScript` / `emailScript` | removed from `defaultScripts` |
| `enableTranscription`, `enableManualAssignment`, auto-answer columns | `False` |
| `suppressInQueueCallRecording` | **`True`** — inverted relative to the others |
| `callBackMode` | `AgentFirst`, CustomerFirst fields dropped |
| `cannedResponses` | `All` |
| `CallbackLiveVoiceFlow`, `CallbackAnswerMachineFlow` | **cannot be cleared** — logs a notice |
| `wrapUpCodes` | **cannot be cleared** — no-op |

---

## 10. Genesys queue settings with no CSV column

Configure these in the admin UI; the importer can't reach them.

**General:** Peer ID (immutable after create), default language, Last Agent Routing mode (`lastAgentRoutingMode`: `Disabled` / `QueueMembersOnly` / `AnyAgent`), queue members and work teams.

**Voice:** whisper audio prompt and playback options, hold audio, audio monitoring.

**Chat / Message:** every setting — service level, alerting timeout, default script, in-queue message flow, outbound SMS number, WhatsApp and Open Messaging integrations, inactivity handling.

**Other:** predictive routing configuration, direct-routing backup queue, workitem alerting, Conditional Group Activation.
