#!/usr/bin/env python3
"""Inspect a local FIRE-Bench checkout without reading hidden conclusions."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


FIREBENCH_REPO = "https://github.com/maitrix-org/FIRE-Bench.git"


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


def dir_size_kb(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            total += item.stat().st_size
    return (total + 1023) // 1024


def task_summary(task_dir: Path) -> dict[str, object]:
    instruction = task_dir / "instruction" / "instruction.txt"
    data = task_dir / "data"
    return {
        "task_id": task_dir.name,
        "size_kb": dir_size_kb(task_dir),
        "has_local_data": data.exists(),
        "data_files": len([p for p in data.rglob("*") if p.is_file()]) if data.exists() else 0,
        "instruction_chars": len(instruction.read_text(encoding="utf-8")) if instruction.exists() else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--firebench-dir", default=".cache/FIRE-Bench")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = ensure_firebench(Path(args.firebench_dir))
    papers = root / "benchmark" / "papers"
    rows = sorted((task_summary(path) for path in papers.iterdir() if path.is_dir()), key=lambda r: (r["size_kb"], r["task_id"]))

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    print(f"{'task_id':40} {'KB':>8} {'data':>6} {'files':>6} {'chars':>8}")
    for row in rows:
        print(
            f"{row['task_id']:40} {row['size_kb']:8} "
            f"{str(row['has_local_data']):>6} {row['data_files']:6} {row['instruction_chars']:8}"
        )


if __name__ == "__main__":
    main()
