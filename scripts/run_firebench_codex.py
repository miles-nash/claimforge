#!/usr/bin/env python3
"""Run a FIRE-Bench task with the current Codex subscription CLI.

The upstream FIRE-Bench Codex runner pins an older CLI that does not support
this account/model setup. This runner keeps the FIRE-Bench log layout while
calling `npx @openai/codex@latest`.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
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


def safe_model_name(model: str) -> str:
    return model.replace("/", "-").replace(":", "-")


def shell_quote_for_log(cmd: list[str]) -> str:
    return " ".join(json.dumps(part) if re.search(r"\s", part) else part for part in cmd)


def build_prompt(instruction: str, protocol: str | None) -> str:
    harness_notice = """Benchmark hygiene rule:
Do not inspect benchmark ground-truth files or evaluator-only files, including any file named `conclusion.txt`, `instruction_gt.txt`, `rubric.json`, `expected_result.json`, or paths under `benchmark/papers` other than the task data copied into this working directory. Treat this working directory as the complete task environment.
"""

    if not protocol:
        return f"{harness_notice}\n--- FIRE-Bench task ---\n{instruction}"

    return f"""{harness_notice}

You are running a FIRE-Bench research task.

Use the following ClaimForge protocol as your operating discipline. Do not mention the protocol unless it affects the research conclusion.

{protocol}

Now complete the benchmark task below. Run experiments where possible. Keep an evidence ledger in your working directory. Your final assistant message must be a concise research conclusion that answers the question directly.

--- FIRE-Bench task ---
{instruction}
"""


def copy_task_assets(firebench: Path, task: str, work_dir: Path) -> None:
    task_dir = firebench / "benchmark" / "papers" / task
    if not task_dir.exists():
        raise SystemExit(f"Unknown FIRE-Bench task: {task}")

    data_dir = task_dir / "data"
    if data_dir.exists():
        shutil.copytree(data_dir, work_dir / "data")

    utils_dir = firebench / "utils"
    if utils_dir.exists():
        shutil.copytree(utils_dir, work_dir / "utils")


def append_final_markers(log_file: Path, final_text: str) -> None:
    escaped = final_text.replace("\\", "\\\\").replace("'", "\\'")
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write("\n" + "=" * 40 + "\n")
        handle.write("CLAIMFORGE_FINAL_RESULT\n")
        handle.write(final_text.strip() + "\n")
        handle.write(f"final_thought='{escaped}', outputs={{}}\n")
        handle.write(json.dumps({"result": final_text.strip()}, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--agent", default="claimforge-codex")
    parser.add_argument("--firebench-dir", default=".cache/FIRE-Bench")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--no-protocol", action="store_true", help="Run the raw FIRE-Bench prompt without ClaimForge conditioning.")
    parser.add_argument("--dry-run", action="store_true", help="Prepare files and print the command without launching Codex.")
    parser.add_argument("--sandbox", default="workspace-write", choices=["read-only", "workspace-write", "danger-full-access"])
    parser.add_argument("--dangerous", action="store_true", help="Use Codex's sandbox bypass flag. Only for debugging trusted local harnesses.")
    args = parser.parse_args()

    workspace = Path.cwd()
    firebench = ensure_firebench(workspace / args.firebench_dir)
    task_dir = firebench / "benchmark" / "papers" / args.task
    instruction_file = task_dir / "instruction" / "instruction.txt"
    if not instruction_file.exists():
        raise SystemExit(f"Instruction file not found: {instruction_file}")

    timestamp = time.strftime("%Y%m%d%H%M%S")
    suffix = random.randint(10000, 99999)
    run_id = f"{timestamp}_{suffix}"
    model_name = safe_model_name(args.model)

    live_log_dir = workspace / ".cache" / "claimforge-logs" / args.agent / model_name / args.task / run_id
    mirror_log_dir = firebench / "log" / args.agent / model_name / args.task / run_id
    log_dir = live_log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "log.log"
    final_file = log_dir / "last_message.txt"
    work_dir = workspace / ".cache" / "claimforge-work" / f"{args.agent}_{model_name}_{args.task}_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    copy_task_assets(firebench, args.task, work_dir)

    protocol = None
    if not args.no_protocol:
        protocol_path = workspace / "protocols" / "claimforge.md"
        protocol = protocol_path.read_text(encoding="utf-8")

    instruction = instruction_file.read_text(encoding="utf-8").strip()
    prompt = build_prompt(instruction, protocol)

    cmd = [
        "npx",
        "@openai/codex@latest",
        "exec",
        "--cd",
        str(work_dir),
        "--skip-git-repo-check",
        "--output-last-message",
        str(final_file),
        "--model",
        args.model,
        prompt,
    ]
    if args.dangerous:
        cmd.insert(3, "--dangerously-bypass-approvals-and-sandbox")
    else:
        cmd[3:3] = ["--sandbox", args.sandbox]

    metadata = {
        "agent_id": args.agent,
        "task_id": args.task,
        "llm_model": model_name,
        "run_id": run_id,
        "work_dir": str(work_dir),
        "live_log_file": str(log_file),
        "mirror_log_file": str(mirror_log_dir / "log.log"),
        "protocol": "none" if args.no_protocol else "claimforge",
        "sandbox": "dangerously-bypassed" if args.dangerous else args.sandbox,
        "command": shell_quote_for_log(cmd[:-1] + ["<prompt>"]),
    }
    with log_file.open("w", encoding="utf-8") as handle:
        handle.write(f"agent_id: {args.agent}\n")
        handle.write(f"task_id: {args.task}\n")
        handle.write(f"llm_model: {model_name}\n")
        handle.write("=" * 40 + "\n")
        handle.write(json.dumps(metadata, indent=2) + "\n")
        handle.write("=" * 40 + "\n")

    if args.dry_run:
        print(json.dumps(metadata, indent=2))
        print(f"log_file={log_file}")
        print(f"work_dir={work_dir}")
        return

    env = os.environ.copy()
    start = time.time()
    with log_file.open("a", encoding="utf-8") as handle:
        try:
            result = subprocess.run(cmd, cwd=work_dir, env=env, stdout=handle, stderr=subprocess.STDOUT, timeout=args.timeout)
            return_code = result.returncode
        except subprocess.TimeoutExpired:
            return_code = 124
            handle.write(f"\nTIMEOUT after {args.timeout} seconds\n")

    final_text = ""
    if final_file.exists():
        final_text = final_file.read_text(encoding="utf-8").strip()
    if not final_text:
        final_text = f"Run did not produce a final Codex message. Return code: {return_code}."
    append_final_markers(log_file, final_text)
    mirror_log_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(log_file, mirror_log_dir / "log.log")
    if final_file.exists():
        shutil.copy2(final_file, mirror_log_dir / "last_message.txt")

    elapsed = time.time() - start
    summary = {
        "log_file": str(log_file),
        "mirror_log_file": str(mirror_log_dir / "log.log"),
        "work_dir": str(work_dir),
        "run_id": run_id,
        "return_code": return_code,
        "elapsed_seconds": round(elapsed, 2),
    }
    print(json.dumps(summary, indent=2))
    if return_code not in (0, 124):
        sys.exit(return_code)


if __name__ == "__main__":
    main()
