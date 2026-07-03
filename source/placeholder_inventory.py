#!/usr/bin/env python3
"""
Placeholder inventory generator for multilingual emergency alerts.

This module reads a nested JSON export of emergency-alert translations, extracts
placeholder tokens from each text field, and writes two CSV outputs:

- a detailed inventory with one row per normalized record
- a grouped summary with placeholder counts per schema/service/language/event/prompt

The script understands two broad JSON layouts:

- Schema 1: direct translation services such as DeepL or Google Translate
- Schema 2: LLM-oriented services such as ChatGPT, Gemini, or DeepSeek

Placeholder detection is intentionally broad so that the inventory can capture
common token styles used in alert systems, including braces, angle brackets,
percent-style specifiers, and other service-specific markers.

Usage:
    python placeholder_inventory.py [--input INPUT] [--output OUTPUT] [--summary-output SUMMARY]
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

# Regex patterns for identifying various placeholder formats
PLACEHOLDER_PATTERNS = [
    r"\{\{.*?\}\}",      # {{name}}
    r"\{[^{}]+\}",       # {name}
    r"\<[^{}]+\>",       # <name>
    r"\[[^\[\]]+\]",     # [name]
    r"%\d*\$?[sdif]",    # %s, %d, %1$s
    r"<\d+>",            # <1>
    r"\$[A-Z0-9_]+\$",   # $CITY$
    r"《[^》]+》",        #《沸水警报》
]
# Compiled regex combining all placeholder patterns
PLACEHOLDER_RE = re.compile("|".join(f"(?:{p})" for p in PLACEHOLDER_PATTERNS))

# Service categories by data schema
SCHEMA1_SERVICES = {"deepl", "google_translate"}
SCHEMA2_SERVICES = {"chatgpt", "gemini", "deepseek"}

# Common field names for extracting text content from records
DEFAULT_TEXT_KEYS = [
    "text",
    "source_text",
    "translated_text",
    "translation",
    "output",
    "value",
    "message",
    "content",
    "body",
]
# Common field names for extracting date/timestamp information
DEFAULT_DATE_KEYS = ["date", "timestamp", "created_at"]
# Common field names for extracting record identifiers
DEFAULT_ID_KEYS = ["id", "alert_id", "uuid", "key"]

# Default file paths
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR.parent / "output_file.json"
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "results" / "placeholder_inventory.csv"
DEFAULT_SUMMARY_OUTPUT = SCRIPT_DIR.parent / "results" / "placeholder_summary.csv"


def extract_placeholders(text: str) -> List[Dict[str, Any]]:
    """Return all placeholder matches found in *text* with character offsets.

    Each result includes the matched token plus its start and end offsets so the
    inventory can support manual review and downstream alignment checks.
    """
    return [
        {"token": m.group(0), "start": m.start(), "end": m.end()}
        for m in PLACEHOLDER_RE.finditer(text or "")
    ]


def tokens(items: List[Dict[str, Any]]) -> List[str]:
    """Extract just the placeholder token strings from match dictionaries."""
    return [x["token"] for x in items]


def find_first(record: Dict[str, Any], keys: Sequence[str]) -> str:
    """Return the first non-empty string value found under *keys* in *record*."""
    for k in keys:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def find_first_any(record: Dict[str, Any], keys: Sequence[str]) -> Any:
    """Return the first present value found under *keys* in *record*."""
    for k in keys:
        if k in record:
            return record[k]
    return None


def multiset_diff(left: List[str], right: List[str]) -> List[str]:
    """Return values in *left* that are missing from *right*, preserving order.

    Duplicate tokens are handled as a multiset so repeated placeholders are
    compared by count rather than only by unique membership.
    """
    right_counts = Counter(right)
    out: List[str] = []
    for tok in left:
        if right_counts[tok] > 0:
            right_counts[tok] -= 1
        else:
            out.append(tok)
    return out


def compare_placeholders(source_text: str, target_text: str) -> Dict[str, Any]:
    """Compare placeholder usage between two texts.

    The returned dictionary includes token counts, missing/extra token lists,
    order matching, and raw match metadata for both sides.
    """
    source_ph = extract_placeholders(source_text)
    target_ph = extract_placeholders(target_text)
    source_tokens = tokens(source_ph)
    target_tokens = tokens(target_ph)

    missing = multiset_diff(source_tokens, target_tokens)
    extra = multiset_diff(target_tokens, source_tokens)
    order_matches = source_tokens == target_tokens if source_tokens or target_tokens else True

    return {
        "source_placeholder_count": len(source_tokens),
        "target_placeholder_count": len(target_tokens),
        "source_placeholder_tokens": source_tokens,
        "target_placeholder_tokens": target_tokens,
        "missing_placeholder_count": len(missing),
        "extra_placeholder_count": len(extra),
        "missing_placeholder_tokens": missing,
        "extra_placeholder_tokens": extra,
        "placeholder_order_matches": order_matches,
        "placeholder_order_note": "exact sequence match" if order_matches else "placeholder order differs",
        "source_placeholder_details": source_ph,
        "target_placeholder_details": target_ph,
        "has_missing_placeholders": bool(missing),
        "has_extra_placeholders": bool(extra),
    }


def _jsonish(value: Any) -> str:
    """Serialize values for storage in CSV-friendly inventory fields."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _normalize_leaf(
    service: str,
    language: str,
    event: str,
    prompt: str,
    leaf: Any,
    schema: str,
    record_index: str = "",
) -> Dict[str, Any] | None:
    """Normalize a single leaf record into the common inventory row format.

    The function accepts either a raw string or a dict-like record. It extracts
    the best available text, timestamp, and identifier fields, then records all
    placeholder metadata needed for both detailed and summary CSV outputs.
    """
    if isinstance(leaf, str):
        text = leaf.strip()
        date = ""
        rec_id = record_index
    elif isinstance(leaf, dict):
        text = find_first(leaf, DEFAULT_TEXT_KEYS)
        date = find_first(leaf, DEFAULT_DATE_KEYS)
        rec_id = find_first_any(leaf, DEFAULT_ID_KEYS)
        if rec_id is None:
            rec_id = record_index
    else:
        return None

    if not text:
        return None

    ph = extract_placeholders(text)
    tok = tokens(ph)

    return {
        "schema": schema,
        "service": service,
        "language": language,
        "event": event,
        "prompt": prompt,
        "record_index": rec_id,
        "date": date,
        "text": text,
        "normalized_depth": 4,
        "placeholder_count": len(tok),
        "placeholder_tokens": tok,
        "placeholder_details": ph,
        "has_placeholders": bool(tok),
    }


def _iter_rows_from_schema1(service: str, service_obj: Any) -> Iterable[Dict[str, Any]]:
    """Yield normalized rows for Schema 1 direct-translation service objects."""
    if not isinstance(service_obj, dict):
        return

    for language, lang_obj in service_obj.items():
        if not isinstance(lang_obj, dict):
            continue

        for event, event_obj in lang_obj.items():
            if isinstance(event_obj, list):
                for i, item in enumerate(event_obj):
                    row = _normalize_leaf(service, language, event, "", item, "deepl_google_translate", str(i))
                    if row:
                        yield row
            else:
                row = _normalize_leaf(service, language, event, "", event_obj, "deepl_google_translate")
                if row:
                    yield row


def _iter_rows_from_schema2(service: str, service_obj: Any) -> Iterable[Dict[str, Any]]:
    """Yield normalized rows for Schema 2 prompt-oriented service objects."""
    if not isinstance(service_obj, dict):
        return

    for language, lang_obj in service_obj.items():
        if not isinstance(lang_obj, dict):
            continue

        for event, event_obj in lang_obj.items():
            if isinstance(event_obj, dict):
                for prompt, prompt_obj in event_obj.items():
                    if isinstance(prompt_obj, list):
                        for i, item in enumerate(prompt_obj):
                            row = _normalize_leaf(service, language, event, prompt, item, "chatgpt_gemini_deepseek", str(i))
                            if row:
                                yield row
                    else:
                        row = _normalize_leaf(service, language, event, prompt, prompt_obj, "chatgpt_gemini_deepseek")
                        if row:
                            yield row
            elif isinstance(event_obj, list):
                for i, item in enumerate(event_obj):
                    row = _normalize_leaf(service, language, event, "", item, "chatgpt_gemini_deepseek", str(i))
                    if row:
                        yield row
            else:
                row = _normalize_leaf(service, language, event, "", event_obj, "chatgpt_gemini_deepseek")
                if row:
                    yield row


def walk_normalized(data: Any) -> Iterable[Dict[str, Any]]:
    """Traverse the top-level JSON object and yield normalized inventory rows.

    Known services are routed to the schema-specific iterator. Unknown services
    fall back to both schema interpretations when their values are dict-like.
    """
    if not isinstance(data, dict):
        return

    for service, service_obj in data.items():
        if service in SCHEMA1_SERVICES:
            yield from _iter_rows_from_schema1(service, service_obj)
        elif service in SCHEMA2_SERVICES:
            yield from _iter_rows_from_schema2(service, service_obj)
        elif isinstance(service_obj, dict):
            # Fallback: try both schemas for unknown top-level services.
            yield from _iter_rows_from_schema1(service, service_obj)
            yield from _iter_rows_from_schema2(service, service_obj)


def build_inventory(data: Any) -> List[Dict[str, Any]]:
    """Materialize the full placeholder inventory as a list of row dictionaries."""
    return list(walk_normalized(data))


def summarize_inventory(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Aggregate inventory rows into grouped summary rows and token columns.

    Rows are grouped by schema, service, language, event, and prompt. The return
    value contains the summary table plus the sorted list of distinct placeholder
    tokens used to create per-token count columns.
    """
    groups: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    all_tokens: List[str] = []

    for row in rows:
        key = (
            row.get("schema", ""),
            row.get("service", ""),
            row.get("language", ""),
            row.get("event", ""),
            row.get("prompt", ""),
        )
        groups[key].append(row)
        all_tokens.extend(row.get("placeholder_tokens", []))

    token_columns = sorted(set(all_tokens))
    summary_rows: List[Dict[str, Any]] = []

    for (schema, service, language, event, prompt), group in sorted(groups.items()):
        token_counts = Counter()
        total_ph = 0
        rows_with_ph = 0

        for row in group:
            toks = row.get("placeholder_tokens", [])
            if toks:
                rows_with_ph += 1
            total_ph += len(toks)
            token_counts.update(toks)

        summary = {
            "schema": schema,
            "service": service,
            "language": language,
            "event": event,
            "prompt": prompt,
            "row_count": len(group),
            "rows_with_placeholders": rows_with_ph,
            "total_placeholder_count": total_ph,
            "unique_placeholder_count": len(token_counts),
            "placeholder_tokens": sorted(token_counts.keys()),
        }
        # for tok in token_columns:
        #     summary[f"placeholder_token__{tok}"] = token_counts.get(tok, 0)

        summary_rows.append(summary)

    return summary_rows, token_columns


def _jsonify_cell(value: Any) -> str:
    """Convert a value into a CSV-safe string representation."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_csv(rows: List[Dict[str, Any]], output_path: Path) -> None:
    """Write rows to a CSV file, preserving the first-seen field order."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _jsonify_cell(v) for k, v in row.items()})


def load_json(path: Path) -> Any:
    """Load and return JSON content from *path*."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    """Command-line entry point for generating inventory and summary CSV files."""
    parser = argparse.ArgumentParser(description="Build placeholder inventory and summary from nested JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Detailed inventory CSV")
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_OUTPUT, help="Summary CSV")
    args = parser.parse_args()

    data = load_json(args.input)
    rows = build_inventory(data)
    write_csv(rows, args.output)

    summary_rows, _ = summarize_inventory(rows)
    write_csv(summary_rows, args.summary_output)

    print(f"Wrote {len(rows)} inventory rows to {args.output}")
    print(f"Wrote {len(summary_rows)} summary rows to {args.summary_output}")


if __name__ == "__main__":
    main()
