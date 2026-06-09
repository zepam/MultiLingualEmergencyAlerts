#!/usr/bin/env python3
"""Run collect_responses.py sequentially, allowing one provider at a time.

This wrapper executes collect_responses.py five times. On each run, it passes
four --skip_* flags so that exactly one provider remains enabled.
"""

from __future__ import annotations

import subprocess
import sys
from typing import List, Tuple

SCRIPT = "collect_responses.py"

PROVIDERS: List[Tuple[str, str]] = [
    ("gemini", "--skip_gemini"),
    ("chatgpt", "--skip_chatgpt"),
    ("deepseek", "--skip_deepseek"),
    ("deepL", "--skip_deepL"),
    ("google_translate", "--skip_google_translate"),
]


def main() -> int:
    for allowed_provider, _ in PROVIDERS:
        skip_flags = [flag for provider, flag in PROVIDERS if provider != allowed_provider]
        cmd = [sys.executable, SCRIPT, *skip_flags]

        print(f"\n=== Running with only {allowed_provider} enabled ===")
        print("Command:", " ".join(cmd))

        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(
                f"\nStopping: run with {allowed_provider} enabled failed "
                f"with exit code {result.returncode}",
                file=sys.stderr,
            )
            return result.returncode

    print("\nAll sequential runs completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
