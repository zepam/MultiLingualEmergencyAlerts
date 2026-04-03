#!/usr/bin/env python3
import json
import sys
from pathlib import Path

PATH = Path("/home/jen/MultiLingualEmergencyAlerts/output_file.json")

def main():
    if not PATH.exists():
        print(f"ERROR: file not found: {PATH}", file=sys.stderr)
        sys.exit(2)

    try:
        with PATH.open("r", encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        print(f"INVALID JSON: {PATH}", file=sys.stderr)
        print(f"  {e.msg} at line {e.lineno}, column {e.colno} (char {e.pos})", file=sys.stderr)

        # show the bad line + caret
        try:
            line = PATH.read_text(encoding="utf-8").splitlines()[e.lineno - 1]
            print(f"\n{e.lineno:>6} | {line}", file=sys.stderr)
            print("       | " + " " * (e.colno - 1) + "^", file=sys.stderr)
        except Exception:
            pass

        sys.exit(1)

    print(f"OK: valid JSON ({PATH})")
    sys.exit(0)

if __name__ == "__main__":
    main()