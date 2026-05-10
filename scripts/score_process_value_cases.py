#!/usr/bin/env python3
"""Score process-value fixtures from ClaimForge/FIRE-Bench artifact bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EVAL_ONLY = {"conclusion.txt", "instruction_gt.txt", "rubric.json", "expected_result.json"}


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
        if not case.get("artifact_dir"):
            raise SystemExit(f"{path}:{lineno}: case must include artifact_dir")
        cases.append(case)
    return cases


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.open(encoding="utf-8"))


def artifact_inventory(root: Path) -> dict[str, Any]:
    artifacts: list[str] = []
    evaluator_only: list[str] = []
    if root.exists():
        for path in sorted(p for p in root.iterdir() if p.is_file()):
            artifacts.append(path.name)
            if path.name in EVAL_ONLY:
                evaluator_only.append(path.name)
    return {"artifacts": artifacts, "evaluator_only_files": evaluator_only}


def build_snapshot(case: dict[str, Any], fixture_dir: Path) -> dict[str, Any]:
    artifact_dir = Path(str(case["artifact_dir"]))
    if not artifact_dir.is_absolute():
        artifact_dir = Path.cwd() / artifact_dir

    access = load_json(artifact_dir / "access_check.json")
    data_audit = load_json(artifact_dir / "data_audit.json")
    baselines = load_json(artifact_dir / "local_baselines.json")
    run_summary = load_json(artifact_dir / "run_summary.json")
    evidence_ledger = read_text(artifact_dir / "evidence_ledger.md")
    research_plan = read_text(artifact_dir / "research_plan.md")

    datasets = data_audit.get("datasets", {}) if isinstance(data_audit.get("datasets"), dict) else {}
    controlled = datasets.get("controlled", {}) if isinstance(datasets.get("controlled"), dict) else {}
    realistic = datasets.get("realistic", {}) if isinstance(datasets.get("realistic"), dict) else {}

    inventory = artifact_inventory(artifact_dir)
    imports = access.get("imports", {}) if isinstance(access.get("imports"), dict) else {}
    env_present = access.get("env_present", {}) if isinstance(access.get("env_present"), dict) else {}
    missing_env = sorted(key for key, present in env_present.items() if present is False)
    missing_imports = sorted(
        key
        for key, value in imports.items()
        if isinstance(value, dict) and value.get("available") is False
    )

    baseline_notes = [
        value.get("note", "")
        for value in baselines.values()
        if isinstance(value, dict) and isinstance(value.get("note"), str)
    ]
    baseline_splits = [
        key
        for key, value in baselines.items()
        if isinstance(value, dict) and isinstance(value.get("feature_aurocs"), dict)
    ]

    snapshot: dict[str, Any] = {
        "case_id": case.get("id"),
        "score_lane": "process_value",
        "task": case.get("task"),
        "agent": case.get("agent"),
        "run_id": case.get("run_id"),
        "artifact_dir": str(artifact_dir),
        **inventory,
        "access": {
            "exists": (artifact_dir / "access_check.json").exists(),
            "missing_env": missing_env,
            "missing_imports": missing_imports,
            "external_calls_attempted": access.get("external_calls_attempted"),
        },
        "data_audit": {
            "exists": (artifact_dir / "data_audit.json").exists(),
            "controlled_rows": controlled.get("n_rows"),
            "realistic_rows": realistic.get("n_rows"),
            "leakage_risk_count": len(data_audit.get("leakage_risks", []))
            if isinstance(data_audit.get("leakage_risks"), list)
            else 0,
        },
        "prompting": {
            "manifest_exists": (artifact_dir / "prompt_manifest.jsonl").exists(),
            "manifest_lines": line_count(artifact_dir / "prompt_manifest.jsonl"),
            "preview_exists": (artifact_dir / "prompt_preview.json").exists(),
        },
        "baselines": {
            "exists": (artifact_dir / "local_baselines.json").exists(),
            "splits_with_aurocs": baseline_splits,
            "notes_mark_non_model": any("non-model" in note for note in baseline_notes),
        },
        "budgeting": {
            "budget_per_model": run_summary.get("budget_per_model"),
            "full_controlled_requests_per_model": run_summary.get("full_controlled_requests_per_model"),
            "full_controlled_plus_realistic_requests_per_model": run_summary.get(
                "full_controlled_plus_realistic_requests_per_model"
            ),
            "budget_note": run_summary.get("budget_note"),
        },
        "boundary": {
            "run_summary_exists": (artifact_dir / "run_summary.json").exists(),
            "blocked": run_summary.get("blocked"),
            "measured_claim_count": len(run_summary.get("measured_claims", []))
            if isinstance(run_summary.get("measured_claims"), list)
            else 0,
            "blocked_claim_count": len(run_summary.get("blocked_claims", []))
            if isinstance(run_summary.get("blocked_claims"), list)
            else 0,
            "next_unblocker_present": bool(str(run_summary.get("next_unblocker") or "").strip()),
        },
        "ledger": {
            "exists": (artifact_dir / "evidence_ledger.md").exists(),
            "has_initial_inventory": "Initial Inventory" in evidence_ledger,
            "has_planned_evidence": "Planned Evidence" in evidence_ledger,
            "has_fallback_run": "Fallback Run" in evidence_ledger,
        },
        "plan": {
            "exists": (artifact_dir / "research_plan.md").exists(),
            "has_claim_shape": "Claim-level answer shape" in research_plan,
            "has_minimum_experiment": "Minimum experiment" in research_plan,
            "has_failure_modes": "Three ways this plan could fool me" in research_plan,
            "has_fallback_experiment": "Fallback experiment" in research_plan,
        },
        "reusable_scaffold": {
            "blocked_fallback_script_exists": (artifact_dir / "run_blocked_fallback.py").exists()
        },
    }
    return snapshot


def criterion_rows(snapshot: dict[str, Any], case: dict[str, Any]) -> list[dict[str, Any]]:
    min_manifest_lines = int(case.get("min_prompt_manifest_lines", 1))
    checks = [
        (
            "access_audit",
            "Records missing credentials/imports and avoids external calls.",
            snapshot["access"]["exists"]
            and (snapshot["access"]["missing_env"] or snapshot["access"]["missing_imports"])
            and snapshot["access"]["external_calls_attempted"] is False,
        ),
        (
            "data_audit",
            "Counts local data and names leakage risks.",
            snapshot["data_audit"]["exists"]
            and int(snapshot["data_audit"]["controlled_rows"] or 0) > 0
            and int(snapshot["data_audit"]["realistic_rows"] or 0) > 0
            and snapshot["data_audit"]["leakage_risk_count"] > 0,
        ),
        (
            "prompt_manifest",
            "Builds dry-run prompts plus a preview.",
            snapshot["prompting"]["manifest_exists"]
            and snapshot["prompting"]["manifest_lines"] >= min_manifest_lines
            and snapshot["prompting"]["preview_exists"],
        ),
        (
            "baseline_sanity",
            "Runs local non-model sanity baselines without promoting them to model evidence.",
            snapshot["baselines"]["exists"]
            and len(snapshot["baselines"]["splits_with_aurocs"]) >= 2
            and snapshot["baselines"]["notes_mark_non_model"],
        ),
        (
            "budgeting",
            "States request budget and scale-up tradeoffs.",
            snapshot["budgeting"]["budget_per_model"] is not None
            and snapshot["budgeting"]["full_controlled_requests_per_model"] is not None
            and bool(snapshot["budgeting"]["budget_note"]),
        ),
        (
            "evidence_ledger",
            "Keeps an evidence ledger with inventory, planned evidence, and fallback run notes.",
            snapshot["ledger"]["exists"]
            and snapshot["ledger"]["has_initial_inventory"]
            and snapshot["ledger"]["has_planned_evidence"]
            and snapshot["ledger"]["has_fallback_run"],
        ),
        (
            "research_plan",
            "Defines claim shape, minimum experiment, failure modes, and fallback path.",
            snapshot["plan"]["exists"]
            and snapshot["plan"]["has_claim_shape"]
            and snapshot["plan"]["has_minimum_experiment"]
            and snapshot["plan"]["has_failure_modes"]
            and snapshot["plan"]["has_fallback_experiment"],
        ),
        (
            "blocked_boundary",
            "Separates measured local claims, blocked model claims, and next unblocker.",
            snapshot["boundary"]["run_summary_exists"]
            and snapshot["boundary"]["blocked"] is True
            and snapshot["boundary"]["measured_claim_count"] > 0
            and snapshot["boundary"]["blocked_claim_count"] > 0
            and snapshot["boundary"]["next_unblocker_present"],
        ),
        (
            "reusable_scaffold",
            "Leaves reusable fallback script scaffolding.",
            snapshot["reusable_scaffold"]["blocked_fallback_script_exists"],
        ),
        (
            "evaluator_hygiene",
            "Does not include evaluator-only files in the artifact bundle.",
            not snapshot["evaluator_only_files"],
        ),
    ]
    return [
        {"id": criterion_id, "description": description, "earned": bool(earned), "points": 1}
        for criterion_id, description, earned in checks
    ]


def expectation_met(row: dict[str, Any]) -> bool:
    expected = row.get("expected_quality")
    if not isinstance(expected, dict):
        return False
    if "score_min" in expected:
        return float(row["score"]) >= float(expected["score_min"])
    return False


def score_case(case: dict[str, Any], fixture_dir: Path, output_dir: Path, dry_run: bool) -> dict[str, Any]:
    case_id = str(case["id"])
    case_dir = output_dir / case_id
    snapshot = build_snapshot(case, fixture_dir)
    criteria = criterion_rows(snapshot, case)
    earned = sum(item["points"] for item in criteria if item["earned"])
    possible = sum(item["points"] for item in criteria)
    score = earned / possible if possible else 0.0
    row: dict[str, Any] = {
        "id": case_id,
        "label": case.get("label"),
        "score_lane": "process_value",
        "task": case.get("task"),
        "agent": case.get("agent"),
        "run_id": case.get("run_id"),
        "status": "dry_run" if dry_run else "scored",
        "earned_points": earned,
        "possible_points": possible,
        "score": score,
        "criteria": criteria,
        "expected_quality": case.get("expected_quality"),
    }
    row["expectation_met"] = expectation_met(row)

    if not dry_run:
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "case.json").write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (case_dir / "snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (case_dir / "score.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return row


def write_summary(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Process-Value Fixture Results",
        "",
        "| Case | Agent | Run | Score | Points | Expected? | Failed Criteria |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        failed = [
            item["id"]
            for item in row.get("criteria", [])
            if isinstance(item, dict) and not item.get("earned")
        ]
        lines.append(
            "| {case} | {agent} | {run} | {score:.3f} | {earned}/{possible} | {expected} | {failed} |".format(
                case=row.get("id", ""),
                agent=row.get("agent", ""),
                run=row.get("run_id", ""),
                score=float(row.get("score", 0.0)),
                earned=row.get("earned_points", 0),
                possible=row.get("possible_points", 0),
                expected="yes" if row.get("expectation_met") else "no",
                failed=", ".join(failed) if failed else "none",
            )
        )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/judge_calibration/process_value_cases.jsonl")
    parser.add_argument("--output-dir", default="reports/process_value/2026-05-10-claimforge-process-fixture")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    fixture_path = Path(args.fixture)
    rows = [
        score_case(case, fixture_path.parent, Path(args.output_dir), args.dry_run)
        for case in load_cases(fixture_path)
    ]
    if not args.dry_run:
        write_summary(Path(args.output_dir), rows)
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
