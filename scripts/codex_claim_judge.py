#!/usr/bin/env python3
"""Claim-level judging through Codex CLI.

This is a Codex-token-compatible alternative to FIRE-Bench's API-backed
RAGChecker scoring. It is meant for iteration and audit, not leaderboard
comparability until calibrated.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCHEMA_HINT = {
    "agent_claims": ["atomic claim from the agent conclusion"],
    "ground_truth_claims": ["atomic claim from the supplied ground truth"],
    "precision_checks": [
        {
            "agent_claim": "claim",
            "supported_by_ground_truth": True,
            "rationale": "short reason",
        }
    ],
    "recall_checks": [
        {
            "ground_truth_claim": "claim",
            "covered_by_agent": True,
            "rationale": "short reason",
        }
    ],
    "unsupported_overclaims": ["scientific or task-result claim that asserts an unmeasured or contradicted result"],
    "precision": 1.0,
    "recall": 1.0,
    "f1": 1.0,
}


def read_text(path_or_literal: str) -> str:
    path = Path(path_or_literal)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return path_or_literal


def extract_json(text: str) -> dict[str, object]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def build_prompt(question: str, ground_truth: str, conclusion: str) -> str:
    return f"""You are a strict claim-level scientific replication judge.

Use only the supplied research question, ground-truth conclusion, and agent conclusion. Do not use outside knowledge. Break each conclusion into atomic scientific/task-relevant claims, then score. Do not include artifact inventories, file paths, links, packaging status, validation status, or generic run-status bookkeeping as agent_claims or ground_truth_claims unless they directly state scientific evidence, access blockers, data counts, experimental design, measured metrics, or blocked/unblocked task conclusions.

- Precision: fraction of agent claims supported by the ground truth.
- Recall: fraction of ground-truth claims covered by the agent.
- F1: harmonic mean of precision and recall.
- unsupported_overclaims: scientific/task-result claims that assert results, measurements, or conclusions contradicted by the ground truth or absent from it. Do not list run-status, artifact, validation, or packaging claims such as "completed the blocked-run package", "wrote artifacts", "validation passed", "no final message", or "return code 124" as overclaims; ignore those bookkeeping claims for this claim-quality score.

Return only valid JSON matching this shape:

{json.dumps(SCHEMA_HINT, indent=2)}

Research question:
{question}

Ground-truth conclusion:
{ground_truth}

Agent conclusion:
{conclusion}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--ground-truth-file", required=True)
    parser.add_argument("--conclusion-file", required=True)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--output", default="")
    parser.add_argument("--audit-dir", default="", help="Directory for prompt.txt and raw_response.txt audit artifacts.")
    parser.add_argument("--timeout", type=int, default=180, help="Seconds before aborting the Codex judge subprocess.")
    args = parser.parse_args()

    prompt = build_prompt(
        args.question,
        read_text(args.ground_truth_file),
        read_text(args.conclusion_file),
    )

    with tempfile.TemporaryDirectory(prefix="codex-judge.") as tmp:
        tmp_path = Path(tmp)
        last = tmp_path / "last.txt"
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        cmd = [
            "npx",
            "@openai/codex@latest",
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--cd",
            str(tmp_path),
            "--skip-git-repo-check",
            "--output-last-message",
            str(last),
            "--model",
            args.model,
            prompt,
        ]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            if args.audit_dir:
                audit_dir = Path(args.audit_dir)
                audit_dir.mkdir(parents=True, exist_ok=True)
                (audit_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
                (audit_dir / "raw_response.txt").write_text(exc.stdout or "", encoding="utf-8")
            print(f"Codex judge timed out after {args.timeout} seconds", file=sys.stderr)
            sys.exit(124)
        if result.returncode != 0:
            if args.audit_dir:
                audit_dir = Path(args.audit_dir)
                audit_dir.mkdir(parents=True, exist_ok=True)
                (audit_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
                (audit_dir / "raw_response.txt").write_text(result.stdout, encoding="utf-8")
            print(result.stdout, file=sys.stderr)
            sys.exit(result.returncode)

        raw = last.read_text(encoding="utf-8") if last.exists() else result.stdout
        if args.audit_dir:
            audit_dir = Path(args.audit_dir)
            audit_dir.mkdir(parents=True, exist_ok=True)
            (audit_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
            (audit_dir / "raw_response.txt").write_text(raw, encoding="utf-8")
        parsed = extract_json(raw)

    output = json.dumps(parsed, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
