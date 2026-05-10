#!/usr/bin/env python3
"""Extract FIRE-Bench final messages and score them with the Codex claim judge."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from compare_firebench_runs import FINAL_RE, summarize


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
        if not isinstance(case, dict) or not case.get("id"):
            raise SystemExit(f"{path}:{lineno}: case must be an object with an id")
        if not case.get("log_file"):
            raise SystemExit(f"{path}:{lineno}: case must include log_file")
        cases.append(case)
    return cases


def resolve_case_path(value: object, fixture_dir: Path, prefer_fixture_dir: bool) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    if prefer_fixture_dir:
        candidate = fixture_dir / path
        if candidate.exists():
            return candidate
    return Path.cwd() / path


def case_text(case: dict[str, Any], key: str, fixture_dir: Path) -> str:
    file_key = f"{key}_file"
    if file_key in case:
        path = resolve_case_path(case[file_key], fixture_dir, prefer_fixture_dir=True)
        return path.read_text(encoding="utf-8")
    return str(case.get(key, ""))


def extract_final(log_file: Path) -> str:
    text = log_file.read_text(encoding="utf-8")
    match = FINAL_RE.search(text)
    if match:
        return match.group("final").strip()

    last_message = log_file.with_name("last_message.txt")
    if last_message.exists():
        return last_message.read_text(encoding="utf-8").strip()

    raise ValueError(f"{log_file}: could not find CLAIMFORGE_FINAL_RESULT or sibling last_message.txt")


def run_case(
    case: dict[str, Any],
    fixture_dir: Path,
    output_dir: Path,
    model: str,
    timeout: int,
    save_audit: bool,
    dry_run: bool,
) -> dict[str, Any]:
    case_id = str(case["id"])
    case_dir = output_dir / case_id
    ground_truth_path = case_dir / "ground_truth.txt"
    conclusion_path = case_dir / "conclusion.txt"
    score_path = case_dir / "score.json"
    log_file = resolve_case_path(case["log_file"], fixture_dir, prefer_fixture_dir=False)

    try:
        log_summary = summarize(str(log_file))
        final_text = extract_final(log_file)
    except Exception as exc:  # noqa: BLE001 - report per-case extraction failures.
        return {
            "id": case_id,
            "status": "extract_failed",
            "error": str(exc),
            "log_file": str(log_file),
        }

    cmd = [
        sys.executable,
        "scripts/codex_claim_judge.py",
        "--question",
        str(case.get("question", "")),
        "--ground-truth-file",
        str(ground_truth_path),
        "--conclusion-file",
        str(conclusion_path),
        "--model",
        model,
        "--output",
        str(score_path),
        "--timeout",
        str(timeout),
    ]
    if save_audit:
        cmd.extend(["--audit-dir", str(case_dir / "audit")])

    row: dict[str, Any] = {
        "id": case_id,
        "task": case.get("task") or log_summary.get("task_id"),
        "agent": case.get("agent") or log_summary.get("agent_id"),
        "run_id": case.get("run_id") or log_summary.get("run_id"),
        "log_file": str(log_file),
        "artifact_count": log_summary.get("artifact_count"),
        "final_status": log_summary.get("final_status"),
        "evaluator_only_files": log_summary.get("evaluator_only_files", []),
        "score_lane": case.get("score_lane", "task_claim_quality"),
        "command": cmd,
        "score_path": str(score_path),
    }
    if dry_run:
        row["status"] = "dry_run"
        row["final_chars"] = len(final_text)
        return row

    case_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_path.write_text(case_text(case, "ground_truth", fixture_dir), encoding="utf-8")
    conclusion_path.write_text(final_text + "\n", encoding="utf-8")
    (case_dir / "case.json").write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (case_dir / "log_summary.json").write_text(json.dumps(log_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (case_dir / "runner_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    row["return_code"] = completed.returncode
    if completed.returncode != 0:
        row["status"] = "judge_failed"
        return row

    score = json.loads(score_path.read_text(encoding="utf-8"))
    overclaims = score.get("unsupported_overclaims", [])
    row.update(
        {
            "status": "scored",
            "precision": score.get("precision"),
            "recall": score.get("recall"),
            "f1": score.get("f1"),
            "unsupported_overclaim_count": len(overclaims) if isinstance(overclaims, list) else 0,
        }
    )
    return row


def write_summary(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# FIRE-Bench Log Final Judge Results",
        "",
        "| Case | Agent | Run | Lane | Artifacts | Final | Precision | Recall | F1 | Overclaims | Status |",
        "|---|---|---|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {id} | {agent} | {run} | {lane} | {artifacts} | {final} | {precision} | {recall} | {f1} | {overclaims} | {status} |".format(
                id=row.get("id", ""),
                agent=row.get("agent", ""),
                run=row.get("run_id", ""),
                lane=row.get("score_lane", ""),
                artifacts="" if row.get("artifact_count") is None else row.get("artifact_count"),
                final=row.get("final_status", ""),
                precision="" if row.get("precision") is None else f"{float(row['precision']):.3f}",
                recall="" if row.get("recall") is None else f"{float(row['recall']):.3f}",
                f1="" if row.get("f1") is None else f"{float(row['f1']):.3f}",
                overclaims="" if row.get("unsupported_overclaim_count") is None else row.get("unsupported_overclaim_count"),
                status=row.get("status", ""),
            )
        )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="fixtures/judge_calibration/real_log_cases.jsonl")
    parser.add_argument("--output-dir", default="reports/judge_calibration/2026-05-10-log-helper-real-finals")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--save-audit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cases_path = Path(args.cases)
    cases = load_cases(cases_path)
    rows = [
        run_case(
            case,
            cases_path.parent,
            Path(args.output_dir),
            args.model,
            args.timeout,
            args.save_audit,
            args.dry_run,
        )
        for case in cases
    ]
    if not args.dry_run:
        write_summary(Path(args.output_dir), rows)
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
