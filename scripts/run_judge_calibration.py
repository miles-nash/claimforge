#!/usr/bin/env python3
"""Run Codex claim-judge calibration fixtures."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_cases(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
        if not isinstance(case, dict) or not case.get("id"):
            raise SystemExit(f"{path}:{lineno}: case must be an object with an id")
        cases.append(case)
    return cases


def run_case(case: dict[str, object], output_dir: Path, model: str, timeout: int, dry_run: bool) -> dict[str, object]:
    case_id = str(case["id"])
    case_dir = output_dir / case_id
    ground_truth_path = case_dir / "ground_truth.txt"
    conclusion_path = case_dir / "conclusion.txt"
    score_path = case_dir / "score.json"
    audit_dir = case_dir / "audit"

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
        "--audit-dir",
        str(audit_dir),
        "--timeout",
        str(timeout),
    ]

    result: dict[str, object] = {
        "id": case_id,
        "label": case.get("label"),
        "task": case.get("task"),
        "expected_quality": case.get("expected_quality"),
        "command": cmd,
        "score_path": str(score_path),
        "audit_dir": str(audit_dir),
    }
    if dry_run:
        result["status"] = "dry_run"
        return result

    case_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_path.write_text(str(case.get("ground_truth", "")), encoding="utf-8")
    conclusion_path.write_text(str(case.get("conclusion", "")), encoding="utf-8")
    (case_dir / "case.json").write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (case_dir / "runner_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    result["return_code"] = completed.returncode
    if completed.returncode != 0:
        result["status"] = "failed"
        return result

    score = json.loads(score_path.read_text(encoding="utf-8"))
    result["status"] = "scored"
    result["precision"] = score.get("precision")
    result["recall"] = score.get("recall")
    result["f1"] = score.get("f1")
    result["unsupported_overclaims"] = score.get("unsupported_overclaims", [])
    result["expectation_met"] = expectation_met(result)
    return result


def expectation_met(row: dict[str, object]) -> bool:
    expected = row.get("expected_quality")
    if not isinstance(expected, dict):
        return False

    precision = row.get("precision")
    recall = row.get("recall")
    overclaims = row.get("unsupported_overclaims")
    n_overclaims = len(overclaims) if isinstance(overclaims, list) else 0

    checks: list[bool] = []
    if "precision_min" in expected:
        checks.append(precision is not None and float(precision) >= float(expected["precision_min"]))
    if "precision_max" in expected:
        checks.append(precision is not None and float(precision) <= float(expected["precision_max"]))
    if "recall_min" in expected:
        checks.append(recall is not None and float(recall) >= float(expected["recall_min"]))
    if "recall_max" in expected:
        checks.append(recall is not None and float(recall) <= float(expected["recall_max"]))
    if "should_flag_overclaim" in expected:
        checks.append((n_overclaims > 0) is bool(expected["should_flag_overclaim"]))
    return bool(checks) and all(checks)


def write_summary(output_dir: Path, rows: list[dict[str, object]]) -> None:
    (output_dir / "summary.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Judge Calibration Results",
        "",
        "| Case | Label | Status | Precision | Recall | F1 | Overclaims | Expected? |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        overclaims = row.get("unsupported_overclaims")
        n_overclaims = len(overclaims) if isinstance(overclaims, list) else ""
        lines.append(
            "| {id} | {label} | {status} | {precision} | {recall} | {f1} | {overclaims} | {expected} |".format(
                id=row.get("id", ""),
                label=row.get("label", ""),
                status=row.get("status", ""),
                precision="" if row.get("precision") is None else f"{float(row['precision']):.3f}",
                recall="" if row.get("recall") is None else f"{float(row['recall']):.3f}",
                f1="" if row.get("f1") is None else f"{float(row['f1']):.3f}",
                overclaims=n_overclaims,
                expected="yes" if row.get("expectation_met") else "no",
            )
        )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/judge_calibration/blocked_run_cases.jsonl")
    parser.add_argument("--output-dir", default="reports/judge_calibration/2026-05-06-blocked-runs")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cases = load_cases(Path(args.fixture))
    output_dir = Path(args.output_dir)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    rows = [run_case(case, output_dir, args.model, args.timeout, args.dry_run) for case in cases]
    if not args.dry_run:
        write_summary(output_dir, rows)
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
