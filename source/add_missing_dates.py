#!/usr/bin/env python3
"""Add a default date to JSON records that are missing one.

Supports nested alert schemas like:
- service -> language -> event -> text
- service -> language -> event -> {text, date}
- service -> language -> event -> prompt -> text
- service -> language -> event -> prompt -> {text, date}

Plain string leaf values are upgraded to {"text": ..., "date": DEFAULT_DATE} so they can carry the missing date.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR.parent / "output_file.json"
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "output_file_dated.json"
DEFAULT_DATE = "2025-06-01"


def add_dates(value: Any, default_date: str) -> Any:
    if isinstance(value, dict):
        # If this is a leaf record, add a missing date.
        if "text" in value and isinstance(value["text"], str):
            out = dict(value)
            out.setdefault("date", default_date)
            return out
        # Otherwise recurse through nested structures.
        return {k: add_dates(v, default_date) for k, v in value.items()}

    if isinstance(value, list):
        return [add_dates(item, default_date) for item in value]

    if isinstance(value, str):
        # Upgrade old string-only records so they can carry a date.
        return {"text": value, "date": default_date}

    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Add default dates to missing JSON leaf records.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON file")
    parser.add_argument("--date", default=DEFAULT_DATE, help="Default date to insert when missing")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the input file")
    args = parser.parse_args()

    input_path = args.input
    output_path = input_path if args.in_place else args.output

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    updated = add_dates(deepcopy(data), args.date)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
