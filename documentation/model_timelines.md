

## Change Event Log

| Timestamp (UTC) | Provider | Model | Change Type | Before | After | Why | Outcome | Evidence |
|---|---|---|---|---|---|---|---|---|
| 2026-04-11 04:30 UTC | Openrouter | deepseek-chat-v3-0324 | max_tokens | 2048 | 300 | Lower max produces more responses before hitting limit | Purchased credits | ~~commit/PR/link~~ |
| 2026-04-13 22:14 UTC | Openrouter | deepseek-chat-v3-0324 | max_tokens | 300 | 400 | The runs are <$1 each, raised the token limit because I can afford it |  |  |
| 2026-07-03 18:30:00 UTC | Gemini | gemini 2.5 flash | pricing | free | Paid 1 $250 Billing Account Tier Cap | need paid credits to run | | 
| 2026-07-03 20:00:00 UTC | OpenAI | gpt-5.4-nano-2026-03-17 | pricing | free | XXX | out of Azure Open AI credits | | 
| 2026-07-03 23:14:00 UTC | ALL |  | Split Chinese into zh-Hant and zh-Hans | zh for both | more specific outputs | |


Recommended `Change Type` values: `model_switch`, `max_tokens`, `temperature`, `prompt_update`, `other`

## Active Configuration by Date Range

| Start Date | End Date | Provider | Model | max_tokens | temperature | Notes |
|---|---|---|---|---:|---:|---|
| 2026-04-01 | 2026-04-11 | Azure OpenAI           | gpt-4o-mini             | 360   | 0.2? | Baseline period |
| 2026-04-11 | 2026-07-03 | Azure OpenAI           | gpt-4.1-mini            | 512   | 0.2? | Switched model + higher token budget |
| 2026-07-03 | present    | Gemini AI Studio | gemini-2.5-flash        | 1048K | 1.0 | topP=0.95, topK=64 |
| 2026-07-03 | present    | OpenAI           | gpt-5.4-nano-2026-03-17 | 128K  |  1.0   |  topP=1.0 (topK not supported)                  |


## Model Configuration Timeline

Use this document as a change log for:
- Which model was active during a period
- Parameter changes (especially `max_tokens`)
- Why the change was made and how it affected results
- Link to the exact file or commit when possible.

<!-- 
## Monthly Review Checklist

- Which model changes improved quality metrics?
- Did `max_tokens` increases reduce truncation enough to justify cost?
- Are there long periods without documented config updates?
- Are results files mapped to a known configuration window? -->
