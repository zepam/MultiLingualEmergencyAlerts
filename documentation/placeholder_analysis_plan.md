# Placeholder Analysis Plan for Emergency Alerts

For emergency alerts, placeholder handling has multiple failure modes, and small errors can make alerts unclear or unsafe.

## What to Analyze

### 1) Placeholder Preservation

Check whether each placeholder:

- still exists
- appears the same number of times
- uses the same syntax
- wasn’t accidentally translated

**Examples:**

- `%s`, `{name}`, `{{count}}`, `<1>`, `$CITY$`
- Bad translation: `{nombre}` instead of `{name}`

### 2) Placeholder Position

Check whether placeholders remain in a grammatically and logically correct position.

Look for:

- moved to the wrong clause
- separated from the word they modify
- placed before/after punctuation incorrectly
- reordered in a way that changes meaning

This is especially important when source and target languages use different word order.

### 3) Placeholder Integrity

Check for edits that break placeholders:

- missing braces or percent signs
- extra spaces inside tokens
- changed capitalization (if case-sensitive)
- duplicated or merged placeholders
- partial translation of a token

**Examples:**

- `{count} → { count }`
- `%s → % s`
- `{{city}} → {city}`

### 4) Meaning Preservation Around Placeholders

Even if a placeholder is intact, verify that surrounding text is still correct:

- agreement in gender/number
- articles/prepositions around variables
- singular/plural handling
- tense changes that affect interpretation

**Example:**

- “3 alerts” may need different forms depending on target-language number rules.

### 5) Formatting and Punctuation

Check:

- punctuation attached to placeholders
- line breaks around placeholders
- spacing before/after variables
- capitalization consistency

**Example:**

- Source: `Evacuate {location}.`
- Target should **not** become: `Evacuate {location} .`

### 6) Severity and Action Content

For emergency alerts, ensure the translation preserves:

- urgency
- location
- requested action
- timing
- affected population
- source authority (if included)

Even perfect placeholder handling is not enough if the message is softened or meaning is altered.

### 7) Omission and Addition

Check whether translators:

- removed placeholder content
- added text not present in source
- added explanations inside variable slots
- invented new placeholders

### 8) Consistency Across Alerts

Across multiple alerts, check consistent handling of:

- same token format
- same placement strategy
- same recurring term translations
- same dates, times, locations, and names

## A Practical Plan

### Phase 1: Build a Placeholder Inventory

For each source alert, extract:

- alert ID
- source text
- placeholder list
- placeholder count
- placeholder types
- surrounding text snippets

Then compare each translation to the source.

### Phase 2: Run Automated Checks

Score each translation on:

- **Preserved:** all placeholders present
- **Unchanged syntax:** token format intact
- **Order match:** placeholders appear in valid positions
- **Count match:** no missing/extra placeholders
- **Spacing/punctuation valid**
- **No translated token fragments**

Output a pass/fail flag plus reason.

### Phase 3: Human Review for Risky Cases

Prioritize alerts where:

- placeholders were reordered
- any placeholder was altered
- language is highly inflected
- message contains numbers, dates, or locations
- alert is high severity

### Phase 4: Categorize Errors

Use labels such as:

- translated placeholder
- missing placeholder
- extra placeholder
- broken syntax
- wrong order
- punctuation issue
- semantic mismatch
- grammatical mismatch

### Phase 5: Summarize Patterns

Look for trends by:

- language
- translator
- alert type
- placeholder type
- severity level

This helps determine whether issues are systematic or isolated.

## Useful Metrics

Track quality with:

- placeholder preservation rate
- exact syntax match rate
- correct position rate
- missing placeholder rate
- broken placeholder rate
- semantic fidelity rate
- high-risk alert error rate

For a quick first pass, start with:

- preserved
- not translated
- correct order
- no missing/extra tokens

## Recommended Output Format

For each alert, use one row with:

- Alert ID
- Source text
- Target text
- Placeholder type
- Source placeholder(s)
- Target placeholder(s)
- Count match
- Order correct
- Syntax intact
- Translated? (yes/no)
- Notes
- Severity

## Biggest Things People Miss

Beyond translation and position, also check:

- plural/gender agreement
- date/time formats
- numbers and units
- line breaks
- punctuation around variables
- tag/markup integrity
- whether the alert still sounds urgent and actionable

If useful, this can be converted into a review checklist, spreadsheet template, or scoring rubric.