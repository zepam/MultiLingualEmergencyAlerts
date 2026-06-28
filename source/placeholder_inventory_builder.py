#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

PLACEHOLDER_PATTERNS = [
    r"\{\{.*?\}\}",   # {{name}}
    r"\{[^{}]+\}",     # {name}
    r"\[[^\[\]]+\]",   # [name]
    r"%\d*\$?[sdif]",  # %s, %d, %1$s
    r"<\d+>",           # <1>
    r"\$[A-Z0-9_]+\$", # $CITY$
]
PLACEHOLDER_RE = re.compile("|".join(f"(?:{p})" for p in PLACEHOLDER_PATTERNS))

# Schema 1: deepl, google_translate
# service -> language -> event -> text
# service -> language -> event -> {text, date}
SCHEMA1_SERVICES = {"deepl", "google_translate"}

# Schema 2: chatgpt, gemini, deepseek
# service -> language -> event -> prompt -> text
# service -> language -> event -> prompt -> {text, date}
SCHEMA2_SERVICES = {"chatgpt", "gemini", "deepseek"}

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
DEFAULT_SOURCE_KEYS = [
    "source_text",
    "input_text",
    "original_text",
    "reference_text",
]
DEFAULT_DATE_KEYS = ["date", "timestamp", "created_at"]
DEFAULT_ID_KEYS = ["id", "alert_id", "uuid", "key"]

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR.parent / "output_file.json"
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "data" / "placeholder_inventory.csv"
DEFAULT_SUMMARY_OUTPUT = SCRIPT_DIR.parent / "results" / "placeholder_summary.csv"


def extract_placeholders(text: str) -> List[Dict[str, Any]]:
    return [
        {"token": m.group(0), "start": m.start(), "end": m.end()}
        for m in PLACEHOLDER_RE.finditer(text or "")
    ]


def tokens(items: List[Dict[str, Any]]) -> List[str]:
    return [x["token"] for x in items]


def find_first(record: Dict[str, Any], keys: Sequence[str]) -> str:
    for k in keys:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def find_first_any(record: Dict[str, Any], keys: Sequence[str]) -> Any:
    for k in keys:
        if k in record:
            return record[k]
    return None


def walk(obj: Any, path: List[str] | None = None) -> Iterable[Tuple[List[str], Dict[str, Any]]]:
    """Yield leaf dict records plus their path.

    Supported schemas:
      1) deepl/google_translate:
         service -> language -> event -> text
         service -> language -> event -> {text, date}

      2) chatgpt/gemini/deepseek:
         service -> language -> event -> prompt -> text
         service -> language -> event -> prompt -> {text, date}

    The function also tolerates list wrappers at the leaf level.
    """
    path = path or []

    if isinstance(obj, dict):
        if any(k in obj and isinstance(obj.get(k), str) for k in DEFAULT_TEXT_KEYS):
            yield path, obj

        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                yield from walk(v, path + [str(k)])

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, (dict, list)):
                yield from walk(v, path + [str(i)])


def path_meta(path: List[str]) -> Dict[str, Any]:
    service = path[0] if len(path) > 0 else ""
    language = path[1] if len(path) > 1 else ""
    event = path[2] if len(path) > 2 else ""

    if service in SCHEMA1_SERVICES:
        schema = "deepl_google_translate"
        prompt = ""
        record_index = path[3] if len(path) > 3 else ""
    elif service in SCHEMA2_SERVICES:
        schema = "chatgpt_gemini_deepseek"
        prompt = path[3] if len(path) > 3 else ""
        record_index = path[4] if len(path) > 4 else ""
    else:
        schema = "unknown"
        prompt = path[3] if len(path) > 3 else ""
        record_index = path[4] if len(path) > 4 else (path[3] if len(path) > 3 else "")

    return {
        "path": "/".join(path),
        "depth": len(path),
        "service": service,
        "language": language,
        "event": event,
        "hazard": event,  # compatibility with older nested schema naming
        "prompt": prompt,
        "record_index": record_index,
        "schema": schema,
    }


def multiset_diff(left: List[str], right: List[str]) -> List[str]:
    """Items in left not covered by right, preserving left order."""
    right_counts = Counter(right)
    out: List[str] = []
    for tok in left:
        if right_counts[tok] > 0:
            right_counts[tok] -= 1
        else:
            out.append(tok)
    return out


def compare_placeholders(source_text: str, target_text: str) -> Dict[str, Any]:
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


def build_inventory(
    data: Any,
    text_keys: Sequence[str],
    date_keys: Sequence[str],
    id_keys: Sequence[str],
    source_keys: Sequence[str] | None = None,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    source_keys = source_keys or []

    for path, rec in walk(data):
        text = find_first(rec, text_keys)
        if not text:
            continue

        date = find_first(rec, date_keys)
        rec_id = find_first_any(rec, id_keys)
        if rec_id is None:
            rec_id = path[-1] if path else ""

        ph = extract_placeholders(text)
        tok = tokens(ph)
        meta = path_meta(path)

        row = {
            **meta,
            "id": rec_id,
            "date": date,
            "text": text,
            "placeholder_count": len(tok),
            "placeholder_tokens": tok,
            "placeholder_details": ph,
            "has_placeholders": bool(tok),
        }

        source_text = find_first(rec, source_keys) if source_keys else ""
        if source_text and source_text != text:
            row.update(compare_placeholders(source_text, text))
        else:
            row.update({
                "source_placeholder_count": "",
                "target_placeholder_count": len(tok),
                "source_placeholder_tokens": [],
                "target_placeholder_tokens": tok,
                "missing_placeholder_count": "",
                "extra_placeholder_count": "",
                "missing_placeholder_tokens": [],
                "extra_placeholder_tokens": [],
                "placeholder_order_matches": "",
                "placeholder_order_note": "",
                "source_placeholder_details": [],
                "target_placeholder_details": ph,
                "has_missing_placeholders": "",
                "has_extra_placeholders": "",
            })

        rows.append(row)

    return rows


def _jsonish(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _is_truthy(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.lower() == "true")


def _is_falsey(value: Any) -> bool:
    return value is False or (isinstance(value, str) and value.lower() == "false")


def write_json(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flat = [{
        "path": r.get("path", ""),
        "depth": r.get("depth", ""),
        "service": r.get("service", ""),
        "language": r.get("language", ""),
        "event": r.get("event", ""),
        "hazard": r.get("hazard", ""),
        "prompt": r.get("prompt", ""),
        "record_index": r.get("record_index", ""),
        "schema": r.get("schema", ""),
        "id": r.get("id", ""),
        "date": r.get("date", ""),
        "text": r.get("text", ""),
        "placeholder_count": r.get("placeholder_count", ""),
        "has_placeholders": r.get("has_placeholders", ""),
        "placeholder_tokens": " | ".join(r.get("placeholder_tokens", [])),
        "source_placeholder_count": r.get("source_placeholder_count", ""),
        "target_placeholder_count": r.get("target_placeholder_count", ""),
        "source_placeholder_tokens": _jsonish(r.get("source_placeholder_tokens", [])),
        "target_placeholder_tokens": _jsonish(r.get("target_placeholder_tokens", [])),
        "missing_placeholder_count": r.get("missing_placeholder_count", ""),
        "extra_placeholder_count": r.get("extra_placeholder_count", ""),
        "missing_placeholder_tokens": _jsonish(r.get("missing_placeholder_tokens", [])),
        "extra_placeholder_tokens": _jsonish(r.get("extra_placeholder_tokens", [])),
        "placeholder_order_matches": r.get("placeholder_order_matches", ""),
        "placeholder_order_note": r.get("placeholder_order_note", ""),
        "source_placeholder_details": _jsonish(r.get("source_placeholder_details", [])),
        "target_placeholder_details": _jsonish(r.get("target_placeholder_details", [])),
        "has_missing_placeholders": r.get("has_missing_placeholders", ""),
        "has_extra_placeholders": r.get("has_extra_placeholders", ""),
    } for r in rows]

    fieldnames = list(flat[0].keys()) if flat else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat)


def _placeholder_token_counts(rows: List[Dict[str, Any]]) -> Counter:
    counter: Counter = Counter()
    for r in rows:
        counter.update(r.get("placeholder_tokens", []) or [])
    return counter


def _summary_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    record_count = len(rows)
    records_with_placeholders = sum(1 for r in rows if int(r.get("placeholder_count", 0) or 0) > 0)
    placeholder_token_count = sum(int(r.get("placeholder_count", 0) or 0) for r in rows)
    token_counts = _placeholder_token_counts(rows)
    unique_placeholder_tokens = set(token_counts)

    comparison_records = [r for r in rows if r.get("source_placeholder_count", "") != ""]
    comparison_count = len(comparison_records)
    missing_records = sum(1 for r in comparison_records if _is_truthy(r.get("has_missing_placeholders", False)))
    extra_records = sum(1 for r in comparison_records if _is_truthy(r.get("has_extra_placeholders", False)))
    order_mismatch_records = sum(1 for r in comparison_records if _is_falsey(r.get("placeholder_order_matches", True)))
    exact_match_records = sum(
        1
        for r in comparison_records
        if not _is_truthy(r.get("has_missing_placeholders", False))
        and not _is_truthy(r.get("has_extra_placeholders", False))
        and not _is_falsey(r.get("placeholder_order_matches", True))
    )

    return {
        "record_count": record_count,
        "records_with_placeholders": records_with_placeholders,
        "records_without_placeholders": record_count - records_with_placeholders,
        "placeholder_token_count": placeholder_token_count,
        "unique_placeholder_token_count": len(unique_placeholder_tokens),
        "placeholder_types": " | ".join(sorted(unique_placeholder_tokens)),
        "comparison_records": comparison_count,
        "records_with_missing_placeholders": missing_records,
        "records_with_extra_placeholders": extra_records,
        "records_with_order_mismatch": order_mismatch_records,
        "exact_match_records": exact_match_records,
        "placeholder_preservation_rate": round(exact_match_records / comparison_count, 4) if comparison_count else "",
        "exact_match_rate": round(exact_match_records / comparison_count, 4) if comparison_count else "",
    }


def make_summary_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def add_token_columns(group_rows: List[Dict[str, Any]], row: Dict[str, Any]) -> Dict[str, Any]:
        token_counts = _placeholder_token_counts(group_rows)
        for token, count in sorted(token_counts.items(), key=lambda item: item[0]):
            row[f"placeholder_token__{token}"] = count
        return row

    def group_by(fields: List[str], group_type: str) -> List[Dict[str, Any]]:
        buckets: Dict[Tuple[str, ...], List[Dict[str, Any]]] = defaultdict(list)
        for r in rows:
            key = tuple(str(r.get(f, "")) for f in fields)
            buckets[key].append(r)

        out: List[Dict[str, Any]] = []
        for key, group_rows in sorted(buckets.items(), key=lambda item: item[0]):
            stats = _summary_stats(group_rows)
            row = {
                "summary_scope": group_type,
                "group_value": " / ".join(key) if key else "all",
                "service": key[0] if len(key) > 0 else "",
                "language": key[1] if len(key) > 1 else "",
                "event": key[2] if len(key) > 2 else "",
                "schema": key[3] if len(key) > 3 else "",
                **stats,
            }
            out.append(add_token_columns(group_rows, row))
        return out

    overall_stats = _summary_stats(rows)
    overall = [add_token_columns(rows, {
        "summary_scope": "overall",
        "group_value": "all",
        "service": "",
        "language": "",
        "event": "",
        "schema": "",
        **overall_stats,
    })]
    by_service = group_by(["service"], "service")
    by_language = group_by(["language"], "language")
    by_event = group_by(["event"], "event")
    by_schema = group_by(["schema"], "schema")
    by_service_language = group_by(["service", "language"], "service_language")
    return overall + by_service + by_language + by_event + by_schema + by_service_language


def write_summary_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = make_summary_rows(rows)
    base_fieldnames = [
        "summary_scope",
        "group_value",
        "service",
        "language",
        "event",
        "schema",
        "record_count",
        "records_with_placeholders",
        "records_without_placeholders",
        "placeholder_token_count",
        "unique_placeholder_token_count",
        "placeholder_types",
        "comparison_records",
        "records_with_missing_placeholders",
        "records_with_extra_placeholders",
        "records_with_order_mismatch",
        "exact_match_records",
        "placeholder_preservation_rate",
        "exact_match_rate",
    ]
    token_fieldnames = sorted(
        {
            key
            for row in summary_rows
            for key in row.keys()
            if key.startswith("placeholder_token__")
        }
    )
    fieldnames = base_fieldnames + token_fieldnames
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a placeholder inventory from nested JSON outputs.")
    ap.add_argument("input", nargs="?", default=str(DEFAULT_INPUT), help="Input JSON file (default: ../output_file.json)")
    ap.add_argument("output", nargs="?", default=str(DEFAULT_OUTPUT), help="Output file (.json or .csv) (default: ../data/placeholder_inventory.csv)")
    ap.add_argument("--summary-output", default=str(DEFAULT_SUMMARY_OUTPUT), help="Summary CSV output (default: ../data/placeholder_summary.csv)")
    ap.add_argument("--text-key", action="append", default=[], help="Text key to scan for the main text (repeatable)")
    ap.add_argument("--date-key", action="append", default=[], help="Date key to capture (repeatable)")
    ap.add_argument("--id-key", action="append", default=[], help="ID key to capture (repeatable)")
    ap.add_argument("--source-key", action="append", default=[], help="Optional source text key for placeholder comparison (repeatable)")
    args = ap.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    summary_path = Path(args.summary_output)

    text_keys = args.text_key or DEFAULT_TEXT_KEYS
    date_keys = args.date_key or DEFAULT_DATE_KEYS
    id_keys = args.id_key or DEFAULT_ID_KEYS
    source_keys = args.source_key or DEFAULT_SOURCE_KEYS

    data = json.loads(input_path.read_text(encoding="utf-8"))
    rows = build_inventory(data, text_keys, date_keys, id_keys, source_keys=source_keys)

    if output_path.suffix.lower() == ".csv":
        write_csv(output_path, rows)
    else:
        write_json(output_path, rows)

    write_summary_csv(summary_path, rows)

    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Wrote summary table to {summary_path}")


if __name__ == "__main__":
    main()
