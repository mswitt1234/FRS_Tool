# Queue Settings Coverage Matrix

Every configurable setting on a Genesys Cloud queue, and whether this tool can set it.

**Source of truth:** the `Queue` model in `PureCloudPlatformClientV2` (42 fields, 9 of them read-only) plus its five nested media-settings models, cross-checked against the queue configuration screens in the Genesys Cloud admin UI. Settings are counted as individual configurable values, so a service level counts as two (percentage and target).

| | Count | Share |
|---|---|---|
| **Full** — settable from the CSV as intended | 21 | 23% |
| **Partial** — settable, with a defect or limitation | 21 | 23% |
| **Not supported** — no CSV column | 48 | 53% |
| **Total settings** | **90** | |

The tool reaches **42 of 90** queue settings (47%). Coverage is concentrated in voice, callback service levels, and email — the channels an FRS workbook actually specifies. Chat, message, and direct routing are untouched.

## Coverage by configuration area

| Area | Settings | Full | Partial | None | Coverage |
|---|---|---|---|---|---|
| General | 11 | 4 | 3 | 4 | 64% |
| Routing | 9 | 3 | 3 | 3 | 67% |
| Voice | 15 | 4 | 6 | 5 | 67% |
| Callback | 21 | 5 | 3 | 13 | 38% |
| Email | 10 | 4 | 4 | 2 | 80% |
| Chat | 5 | 0 | 0 | 5 | 0% |
| Message | 11 | 0 | 1 | 10 | 9% |
| Direct Routing | 4 | 0 | 0 | 4 | 0% |
| Wrap-up Codes | 1 | 0 | 1 | 0 | 100% |
| Canned Responses | 1 | 1 | 0 | 0 | 100% |
| Members | 2 | 0 | 0 | 2 | 0% |

---

## Full matrix

### General

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Name | `name` | `queue` | **Full** |  |
| Division | `division.id` | `division` | **Partial** | Name lookup takes first match |
| Description (API only) | `description` | `description` | **Full** |  |
| Peer ID | `peerId` | — | — | Immutable after create |
| Default language | `defaultMediaLanguage` | — | — |  |
| After Call Work mode | `acwSettings.wrapupPrompt` | `acw` | **Full** |  |
| ACW timeout | `acwSettings.timeoutMs` | `acw` | **Full** | Seconds in CSV, ms on wire; max 3600s |
| Enable Manual Assignment | `enableManualAssignment` | `enableManualAssignment` | **Partial** | bool() defect |
| Auto answer (digital channels) | `per-media enableAutoAnswer` | `enableAutoAnswerAll` | **Partial** | bool() defect; wider scope than UI toggle |
| Last Agent Routing mode | `lastAgentRoutingMode` | — | — | Disabled/QueueMembersOnly/AnyAgent |
| Auto answer only (legacy flag) | `autoAnswerOnly` | — | — |  |

### Routing

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Scoring Method | `scoringMethod` | `scoreMethod` | **Full** |  |
| Evaluation Method | `skillEvaluationMethod` | `evaluation` | **Full** |  |
| Standard routing rules | `routingRules[]` | `routingRules` | **Full** |  |
| Bullseye rings | `bullseye` | `bullseye` | **Partial** | Member groups per ring; last ring is implicit default |
| Conditional Group Routing | `conditionalGroupRouting` | `groupRouting` | **Partial** | 4-vs-5 field mismatch; multi-rule collapses to last rule |
| Conditional Group Activation | `conditionalGroupActivation` | — | — | Members tab feature |
| Preferred agent routing | `(via conditionalGroupRouting/agentOwnedRouting)` | — | — |  |
| Predictive routing config | `(separate API)` | — | — |  |
| Member groups | `memberGroups[]` | `MemberGroups` | **Partial** | First-match lookups; per-ring segmentation |

### Voice

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Service Level % | `mediaSettings.call.serviceLevel.percentage` | `slPercentage` | **Full** | Decimal 0-1 |
| Service Level Target | `mediaSettings.call.serviceLevel.durationMs` | `slDuration_ms` | **Full** | ms |
| Alerting Timeout | `mediaSettings.call.alertingTimeoutSeconds` | `alerting_timeout_seconds` | **Full** | 7-59s |
| Calling Party Name | `callingPartyName` | `callerIDName` | **Full** |  |
| Calling Party Number | `callingPartyNumber` | `callerIDNum` | **Partial** | Digits only; round() on the cell |
| In-Queue Flow | `queueFlow.id` | `inQueueFlow` | **Partial** | Name lookup takes first match |
| Default Script | `defaultScripts['CALL']` | `callScript` | **Partial** | GUID only, no name lookup |
| Auto answer (voice) | `mediaSettings.call.enableAutoAnswer` | `enableAutoAnswerVoice` | **Partial** | bool() defect; ignored if enableAutoAnswerAll set |
| Continue recording during queue wait | `suppressInQueueCallRecording` | `suppressInQueueCallRecording` | **Partial** | bool() defect; CSV is inverse of UI checkbox |
| Voice Transcription | `enableTranscription` | `enableTranscription` | **Partial** | bool() defect |
| Audio Monitoring | `enableAudioMonitoring` | — | — |  |
| Whisper Audio prompt | `whisperPrompt` | — | — |  |
| Hold Audio prompt | `onHoldPrompt` | — | — |  |
| Auto-answer alert tone duration | `mediaSettings.call.autoAnswerAlertToneSeconds` | — | — |  |
| Manual-answer alert tone duration | `mediaSettings.call.manualAnswerAlertToneSeconds` | — | — |  |

### Callback

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Service Level % | `mediaSettings.callback.serviceLevel.percentage` | `cb_slPercentage` | **Full** |  |
| Service Level Target | `mediaSettings.callback.serviceLevel.durationMs` | `cb_slDuration_ms` | **Full** |  |
| Alerting Timeout | `mediaSettings.callback.alertingTimeoutSeconds` | `cb_alerting_timeout_seconds` | **Full** |  |
| Callback Type (mode) | `mediaSettings.callback.mode` | `callBackMode` | **Full** |  |
| Live Voice reaction | `mediaSettings.callback.liveVoiceReactionType` | `CallbackLiveVoice` | **Full** | CustomerFirst only |
| Live Voice flow | `mediaSettings.callback.liveVoiceFlow` | `CallbackLiveVoiceFlow` | **Partial** | First-match lookup; cannot be cleared |
| Answering Machine reaction | `mediaSettings.callback.answeringMachineReactionType` | `CallbackAnswerMachine` | **Partial** | Tool default uses non-canonical 'Hangup' |
| Answering Machine flow | `mediaSettings.callback.answeringMachineFlow` | `CallbackAnswerMachineFlow` | **Partial** | First-match lookup; cannot be cleared |
| Auto answer (callback) | `mediaSettings.callback.enableAutoAnswer` | — | — | Existing value preserved, never set |
| Automatically start/end callbacks | `mediaSettings.callback.enableAutoDialAndEnd` | — | — | Preserved on AgentFirst rebuild |
| Auto-dial delay | `mediaSettings.callback.autoDialDelaySeconds` | — | — |  |
| Auto-end delay | `mediaSettings.callback.autoEndDelaySeconds` | — | — |  |
| Pacing Modifier | `mediaSettings.callback.pacingModifier` | — | — |  |
| Max retry count | `mediaSettings.callback.maxRetryCount` | — | — |  |
| Time between retries | `mediaSettings.callback.retryDelaySeconds` | — | — |  |
| Routing site | `mediaSettings.callback.site` | — | — |  |
| Edge group | `mediaSettings.callback.edgeGroup` | — | — |  |
| Agent-owned callbacks enabled | `agentOwnedRouting.enableAgentOwnedCallbacks` | — | — |  |
| Max owned callback hours | `agentOwnedRouting.maxOwnedCallbackHours` | — | — |  |
| Schedule-in-advance hours | `agentOwnedRouting.maxOwnedCallbackDelayHours` | — | — |  |
| Alert tone durations | `mediaSettings.callback.*AlertToneSeconds` | — | — | 2 fields |

### Email

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Service Level % | `mediaSettings.email.serviceLevel.percentage` | `email_slPercentage` | **Full** |  |
| Service Level Target | `mediaSettings.email.serviceLevel.durationMs` | `email_slDuration_ms` | **Full** |  |
| Alerting Timeout | `mediaSettings.email.alertingTimeoutSeconds` | `email_alerting_timeout_seconds` | **Full** |  |
| Outbound Email Address | `outboundEmailAddress.route` | `emailAddress` | **Partial** | Route must pre-exist; exact match |
| Email Domain | `outboundEmailAddress.domain.id` | `emailDomain` | **Full** |  |
| In-Queue Email Flow | `emailInQueueFlow.id` | `emailInQueueFlow` | **Partial** | First-match lookup |
| Default Script | `defaultScripts['EMAIL']` | `emailScript` | **Partial** | GUID only |
| Auto answer (email) | `mediaSettings.email.enableAutoAnswer` | `enableAutoAnswerAll` | **Partial** | Only via the all-channels column |
| Multiple outbound addresses | `mediaSettings.email.allOutboundEmailAddresses` | — | — | Manage Addresses in UI |
| Alert tone durations | `mediaSettings.email.*AlertToneSeconds` | — | — | 2 fields |

### Chat

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Service Level % / Target | `mediaSettings.chat.serviceLevel.*` | — | — | 2 fields |
| Alerting Timeout | `mediaSettings.chat.alertingTimeoutSeconds` | — | — |  |
| Auto answer | `mediaSettings.chat.enableAutoAnswer` | — | — | Not covered by enableAutoAnswerAll |
| Default Script | `defaultScripts['CHAT']` | — | — |  |
| Alert tone durations | `mediaSettings.chat.*AlertToneSeconds` | — | — | 2 fields |

### Message

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Auto answer (message + subtypes) | `mediaSettings.message.enableAutoAnswer, subTypeSettings` | `enableAutoAnswerAll` | **Partial** | Auto-answer only; all 7 subtypes |
| Service Level % / Target | `mediaSettings.message.serviceLevel.*` | — | — | 2 fields |
| Alerting Timeout | `mediaSettings.message.alertingTimeoutSeconds` | — | — |  |
| In-Queue Message Flow | `messageInQueueFlow.id` | — | — |  |
| Default Script | `defaultScripts['MESSAGE']` | — | — |  |
| Inactivity timeout enabled | `mediaSettings.message.enableInactivityTimeout` | — | — |  |
| Inactivity timeout settings | `mediaSettings.message.inactivityTimeoutSettings` | — | — |  |
| Outbound SMS number | `outboundMessagingAddresses.smsAddress` | — | — |  |
| Outbound WhatsApp recipient | `outboundMessagingAddresses.whatsAppRecipient` | — | — |  |
| Outbound Open Messaging recipient | `outboundMessagingAddresses.openMessagingRecipient` | — | — |  |
| Alert tone durations | `mediaSettings.message.*AlertToneSeconds` | — | — | 2 fields |

### Direct Routing

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Backup queue | `directRouting.backupQueueId` | — | — |  |
| Wait for agent | `directRouting.waitForAgent` | — | — |  |
| Agent wait seconds | `directRouting.agentWaitSeconds` | — | — |  |
| Per-media direct routing settings | `directRouting.{call,email,message}MediaSettings` | — | — | 3 fields |

### Wrap-up Codes

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Assigned wrap-up codes | `POST /routing/queues/{id}/wrapupcodes` | `wrapUpCodes` | **Partial** | Additive only; cannot remove or clear |

### Canned Responses

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Library mode + selection | `cannedResponseLibraries` | `cannedResponses` | **Full** |  |

### Members

| Genesys setting | API field | CSV column | Support | Notes |
|---|---|---|---|---|
| Individual user members | `POST /routing/queues/{id}/members` | — | — | Separate endpoint |
| Work teams | `(separate API)` | — | — |  |

---
