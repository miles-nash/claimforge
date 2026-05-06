#!/usr/bin/env python3
"""Summarize a FIRE-Bench Codex run log."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FINAL_RE = re.compile(r"CLAIMFORGE_FINAL_RESULT\n(?P<final>.*?)(?:\nfinal_thought=|\Z)", re.DOTALL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file")
    parser.add_argument("--chars", type=int, default=1600)
    args = parser.parse_args()

    log_path = Path(args.log_file)
    text = log_path.read_text(encoding="utf-8")

    metadata = {}
    match = re.search(r"=+\n(?P<meta>\{.*?\})\n=+", text, re.DOTALL)
    if match:
        try:
            metadata = json.loads(match.group("meta"))
        except json.JSONDecodeError:
            metadata = {}

    final = ""
    final_match = FINAL_RE.search(text)
    if final_match:
        final = final_match.group("final").strip()
    else:
        lines = [line for line in text.strip().splitlines() if line.strip()]
        final = "\n".join(lines[-20:])

    print(json.dumps(metadata, indent=2))
    print("\n--- final excerpt ---")
    print(final[: args.chars])


if __name__ == "__main__":
    main()
