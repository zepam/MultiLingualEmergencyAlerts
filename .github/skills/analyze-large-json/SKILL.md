---
name: analyze-large-json
description: "Analyze large JSON files without loading unnecessary data into chat. Use when searching, filtering, comparing, or summarizing JSON by language, service, client, alert type, prompt, date, or other nested fields."
argument-hint: "JSON path plus optional language, service/client, alert type, or search term"
user-invocable: true
---

# Analyze Large JSON

## Purpose

Provide reliable, targeted analysis of a large JSON file while keeping output bounded and preserving the file's nested structure. Support searches by language and service/client as first-class filters.

## Procedure

1. Identify the input file and the requested operation.
   - Confirm the path exists and determine whether the file is JSON, JSON Lines, or another format.
   - Do not assume that a filename describes the schema.
   - Record the requested filters: language, service/client, alert type, prompt, date, text term, or combinations.

2. Inspect the structure cheaply before reading the whole file.
   - Use a parser or a small script to report the root type, top-level keys, nesting depth, representative keys, and approximate counts.
   - For very large files, prefer streaming tools or a streaming parser such as `ijson` when available.
   - Never print the complete file into chat. Sample only a few records and redact or truncate long text.
   - Check whether service is represented as a root key, a nested field, or a differently named field such as `client` or `provider`.

3. Resolve filters against actual keys.
   - Match language, service/client, and other categorical filters exactly after normalizing only case and surrounding whitespace for comparison.
   - Show the available near matches when a requested key is absent; do not silently broaden an exact search.
   - For this repository's translation results, expect paths like `service/client -> language -> alert_type -> prompt -> entries`, where entries commonly contain `text` and `date`.
   - For gold standards, also check for paths like `language -> alert_type -> source/reference`.

4. Run the narrowest useful query.
   - Filter as early as possible by service/client and language before inspecting text or calculating aggregates.
   - Preserve the full path for every match, including service/client, language, alert type, prompt, and entry index when applicable.
   - Return counts and a bounded sample by default. Include full text only when explicitly requested or when the result is small.
   - For text searches, search string values recursively but distinguish exact matches from substring matches.
   - For comparisons, align records by stable dimensions such as language, alert type, prompt, and date; report missing counterparts instead of dropping them.

5. Save the result as JSON.
   - Save every requested result, not just the displayed sample, under the repository's `data/` folder.
   - Use a predictable descriptive filename such as `data/<service>_<language>_results.json`; sanitize path components to lowercase letters, numbers, underscores, and hyphens.
   - Preserve the filtered hierarchy and include the service/client and language keys when the source uses that structure.
   - Create the `data/` folder if it does not exist, and use UTF-8 with non-ASCII characters preserved.
   - Do not overwrite an unrelated existing file. If the target exists, ask for a filename or choose a clearly suffixed alternative.

6. Validate the result.
   - Confirm the filtered count against the traversal logic.
   - Parse the saved JSON and confirm its count matches the extracted result count.
   - Check for malformed JSON, unexpected types, missing required fields, duplicate paths, and invalid dates where relevant.
   - Separate zero matches from parsing or schema errors.
   - If the file is too large for an in-memory parser, say which streaming approach was used and avoid claiming a complete result from a partial sample.

7. Report findings concisely.
   - Start with the file, filters, and number of matches.
   - State the schema path used and any assumptions about aliases such as `service` versus `client`.
   - Link to or name the saved JSON file in `data/`.
   - Present representative results with paths, dates, and truncated text where useful.
   - List missing languages, services, alert types, or prompts separately from successful matches.
   - Include the exact reproducible command or script logic when the user is likely to repeat the analysis.

## Search Examples

Use a streaming or command-line query when possible. Adapt field names after structure inspection.

```bash
# Inspect top-level keys without dumping the full file
python - <<'PY'
import json
from pathlib import Path

path = Path("output_file.json")
with path.open(encoding="utf-8") as handle:
    data = json.load(handle)
print(type(data).__name__)
print(list(data)[:20] if isinstance(data, dict) else len(data))
PY
```

For a nested translation-results object, traverse service/client first and then language:

```python
for service, languages in data.items():
    if service.casefold() != requested_service.casefold():
        continue
    for language, alert_types in languages.items():
        if language.casefold() != requested_language.casefold():
            continue
        # Continue through alert type, prompt, and entry arrays.
```

When the JSON is too large for `json.load`, use a streaming parser or a command such as `jq` and emit only matching paths and bounded fields. Do not install a dependency without checking the repository's existing environment first.

Save a filtered result with the original nested shape. For example, a ChatGPT/Dari extraction should be written as `data/chatgpt_dari_results.json` with the structure `{ "chatgpt": { "dari": ... } }`, not as a flattened text report.

## Completion Checklist

- [ ] Input format and root structure were verified.
- [ ] Language and service/client filters were resolved against actual keys.
- [ ] Results retain their original JSON paths.
- [ ] The complete result was saved as UTF-8 JSON under `data/`.
- [ ] Output is bounded and long text is truncated unless requested.
- [ ] The saved JSON was reparsed and its count matches the extracted result.
- [ ] Counts, zero matches, missing fields, and parse errors are distinguished.
- [ ] The query or traversal is reproducible.
