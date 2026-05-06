#!/usr/bin/env python3
"""Compare two FIRE-Bench Codex rollout logs and their workdir artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FINAL_RE = re.compile(r"CLAIMFORGE_FINAL_RESULT\n(?P<final>.*?)(?:\nfinal_thought=|\Z)", re.DOTALL)
RUN_SUMMARY_RE = re.compile(r"CLAIMFORGE_RUN_SUMMARY\n(?P<summary>\{.*?\})\n=+", re.DOTALL)
EVAL_ONLY = {"conclusion.txt", "instruction_gt.txt", "rubric.json", "expected_result.json"}


def load_json_match(pattern: re.Pattern[str], text: str, name: str) -> dict[str, Any]:
    match = pattern.search(text)
    if not match:
        return {}
    try:
        return json.loads(match.group(name))
    except json.JSONDecodeError:
        return {}


def metadata_from_log(text: str) -> dict[str, Any]:
    match = re.search(r"=+\n(?P<meta>\{.*?\})\n=+", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group("meta"))
    except json.JSONDecodeError:
        return {}


def final_excerpt(text: str, chars: int = 240) -> str:
    match = FINAL_RE.search(text)
    if not match:
        return ""
    final = " ".join(match.group("final").strip().split())
    return final[:chars]


def infer_return_code(text: str) -> int | None:
    match = re.search(r"Return code: (\d+)", text)
    if match:
        return int(match.group(1))
    if "TIMEOUT after" in text:
        return 124
    return None


def infer_elapsed_seconds(text: str) -> float | None:
    match = re.search(r"TIMEOUT after (\d+(?:\.\d+)?) seconds", text)
    if match:
        return float(match.group(1))
    return None


def artifact_inventory(work_dir: str | None) -> dict[str, Any]:
    if not work_dir:
        return {"artifact_count": 0, "artifacts": [], "evaluator_only_files": []}

    root = Path(work_dir)
    if not root.exists():
        return {"artifact_count": 0, "artifacts": [], "evaluator_only_files": []}

    artifacts: list[str] = []
    evaluator_only: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in rel:
            continue
        if rel.startswith(("data/", "utils/")):
            continue
        artifacts.append(rel)
        if path.name in EVAL_ONLY:
            evaluator_only.append(rel)

    return {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "evaluator_only_files": evaluator_only,
    }


def summarize(log_file: str) -> dict[str, Any]:
    path = Path(log_file)
    text = path.read_text(encoding="utf-8")
    metadata = metadata_from_log(text)
    run_summary = load_json_match(RUN_SUMMARY_RE, text, "summary")
    work_dir = run_summary.get("work_dir") or metadata.get("work_dir")
    artifacts = artifact_inventory(work_dir)

    return {
        "log_file": str(path),
        "agent_id": metadata.get("agent_id"),
        "task_id": metadata.get("task_id"),
        "model": metadata.get("llm_model"),
        "protocol": metadata.get("protocol"),
        "run_id": run_summary.get("run_id") or metadata.get("run_id"),
        "return_code": run_summary.get("return_code", infer_return_code(text)),
        "elapsed_seconds": run_summary.get("elapsed_seconds", infer_elapsed_seconds(text)),
        "has_final_message": "Run did not produce a final Codex message" not in final_excerpt(text, 500),
        "final_excerpt": final_excerpt(text),
        **artifacts,
    }


def print_markdown(rows: list[dict[str, Any]]) -> None:
    print("| Agent | Run id | Return | Seconds | Artifacts | Final? |")
    print("|---|---|---:|---:|---:|---|")
    for row in rows:
        elapsed = row["elapsed_seconds"]
        elapsed_text = "" if elapsed is None else f"{float(elapsed):.2f}"
        print(
            "| {agent} | {run_id} | {return_code} | {elapsed} | {artifacts} | {final} |".format(
                agent=row.get("agent_id") or "",
                run_id=row.get("run_id") or "",
                return_code="" if row.get("return_code") is None else row.get("return_code"),
                elapsed=elapsed_text,
                artifacts=row.get("artifact_count", 0),
                final="yes" if row.get("has_final_message") else "no",
            )
        )
    print()
    for row in rows:
        print(f"## {row.get('agent_id')}")
        print()
        print(f"Artifacts: {', '.join(row.get('artifacts') or ['none'])}")
        if row.get("evaluator_only_files"):
            print(f"Evaluator-only files found: {', '.join(row['evaluator_only_files'])}")
        print(f"Final excerpt: {row.get('final_excerpt') or '(none)'}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_files", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = [summarize(log_file) for log_file in args.log_files]
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print_markdown(rows)


if __name__ == "__main__":
    main()
