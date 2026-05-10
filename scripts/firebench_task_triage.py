#!/usr/bin/env python3
"""Rank FIRE-Bench tasks by likely Codex-only feasibility.

Reads only task instructions and local data-file metadata. It intentionally
does not read evaluator-only files such as conclusion.txt or instruction_gt.txt.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


FIREBENCH_REPO = "https://github.com/maitrix-org/FIRE-Bench.git"
EVALUATOR_ONLY = {"conclusion.txt", "instruction_gt.txt", "rubric.json", "expected_result.json"}


MODEL_PATTERNS = [
    r"\bapi\b",
    r"\bopenai\b",
    r"\bgpt[-\w.]*\b",
    r"\bgemini\b",
    r"\bclaude\b",
    r"\banthropic\b",
    r"\bhugging\s*face\b",
    r"\btransformers\b",
    r"\bllama\b",
    r"\bmodel[s]?:\b",
    r"load with huggingface",
]


LOCAL_DATA_BONUS = 2


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_firebench(path: Path) -> Path:
    if path.exists():
        if not (path / ".git").exists():
            raise SystemExit(f"{path} exists but is not a git checkout")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", FIREBENCH_REPO, str(path)])
    return path


def file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file() and item.name not in EVALUATOR_ONLY)


def dir_size_kb(path: Path) -> int:
    if not path.exists():
        return 0
    total = sum(item.stat().st_size for item in path.rglob("*") if item.is_file() and item.name not in EVALUATOR_ONLY)
    return (total + 1023) // 1024


def triage_task(task_dir: Path) -> dict[str, object]:
    instruction_file = task_dir / "instruction" / "instruction.txt"
    instruction = instruction_file.read_text(encoding="utf-8") if instruction_file.exists() else ""
    lower = instruction.lower()
    hits = sorted({pattern for pattern in MODEL_PATTERNS if re.search(pattern, lower)})
    data_dir = task_dir / "data"
    data_files = file_count(data_dir)
    score = 10 - len(hits) * 2
    if data_files:
        score += LOCAL_DATA_BONUS
    if "you can find dataset at data/" in lower or "datasets:" in lower:
        score += 1
    if "api key" in lower or "1000 api calls" in lower:
        score -= 4
    if "image" in lower or "visual" in lower or "vlm" in lower:
        score -= 1

    return {
        "task_id": task_dir.name,
        "score": score,
        "instruction_chars": len(instruction),
        "has_local_data": data_files > 0,
        "data_files": data_files,
        "data_size_kb": dir_size_kb(data_dir),
        "dependency_hits": hits,
        "likely_external_model_api": bool(hits) or "api key" in lower,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--firebench-dir", default=".cache/FIRE-Bench")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    root = ensure_firebench(Path(args.firebench_dir))
    papers = root / "benchmark" / "papers"
    rows = [triage_task(path) for path in sorted(papers.iterdir()) if path.is_dir()]
    rows.sort(key=lambda row: (-int(row["score"]), bool(row["likely_external_model_api"]), int(row["data_size_kb"]), str(row["task_id"])))

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    print(f"{'task_id':38} {'score':>5} {'api?':>5} {'data':>5} {'KB':>7} hits")
    for row in rows[: args.limit]:
        hits = ",".join(str(hit) for hit in row["dependency_hits"]) or "-"
        print(
            f"{row['task_id']:38} {row['score']:5} {str(row['likely_external_model_api']):>5} "
            f"{row['data_files']:5} {row['data_size_kb']:7} {hits}"
        )


if __name__ == "__main__":
    main()
