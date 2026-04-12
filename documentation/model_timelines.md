# Model Configuration Timeline

Use this document as a change log for:
- Which model was active during a period
- Parameter changes (especially `max_tokens`)
- Why the change was made and how it affected results

## Quick Rules

- Add one row for every change event.
- Use UTC timestamps in ISO format: `YYYY-MM-DD HH:MM UTC`.
- Keep the reason and outcome short (1 line each).
- Link to the exact file or commit when possible.

## Change Event Log

| Timestamp (UTC) | Provider | Model | Change Type | Before | After | Why | Outcome | Evidence |
|---|---|---|---|---|---|---|---|---|
| 2026-04-11 04:30 UTC | Openrouter | deepseek-chat-v3-0324 | max_tokens | 2048 | 300 | Free access capped at 302 | Pending evaluation | commit/PR/link |


Recommended `Change Type` values:
- `model_switch`
- `max_tokens`
- `temperature`
- `prompt_update`
- `other`

## Active Configuration by Date Range

Track stable periods so you can map outputs to configuration quickly.

| Start Date | End Date | Provider | Model | max_tokens | temperature | Notes |
|---|---|---|---|---:|---:|---|
| 2026-04-01 | 2026-04-11 | OpenAI | gpt-4o-mini | 360 | 0.2 | Baseline period |
| 2026-04-11 | present | OpenAI | gpt-4.1-mini | 512 | 0.2 | Switched model + higher token budget |



## Monthly Review Checklist

- Which model changes improved quality metrics?
- Did `max_tokens` increases reduce truncation enough to justify cost?
- Are there long periods without documented config updates?
- Are results files mapped to a known configuration window?
