# FIRE-Bench Log-To-Judge Helper

Date: 2026-05-10

Mode: harness.

## Purpose

Remove the manual copy step between FIRE-Bench logs and the Codex claim judge. The helper should extract real final messages from logs, preserve artifact/final-status metadata, and score the extracted conclusion in the `task_claim_quality` lane.

## Artifact

Added `scripts/judge_firebench_finals.py` plus `fixtures/judge_calibration/real_log_cases.jsonl`.

The helper:

- reads each `log.log`
- extracts `CLAIMFORGE_FINAL_RESULT`, falling back to sibling `last_message.txt`
- summarizes artifacts and evaluator-only-file exposure with `scripts/compare_firebench_runs.py`
- writes per-case `ground_truth.txt`, extracted `conclusion.txt`, `log_summary.json`, `score.json`, and `runner_stdout.txt`
- calls `scripts/codex_claim_judge.py`

`scripts/codex_claim_judge.py` now prefers the installed `codex` binary over `npx @openai/codex@latest` and runs nested judge calls with a temporary writable `CODEX_HOME` seeded from local auth. This avoids the old npm dependency and the read-only `~/.codex` session-state failure.

## Validation

Command:

```bash
python3 scripts/judge_firebench_finals.py \
  --cases fixtures/judge_calibration/real_log_cases.jsonl \
  --output-dir reports/judge_calibration/2026-05-10-log-helper-real-finals \
  --timeout 180
```

The first sandboxed attempt failed on DNS to `chatgpt.com`; the escalated retry completed all three judge calls.

| Case | Agent | Run | Artifacts | Final | Precision | Recall | F1 | Overclaims |
|---|---|---|---:|---|---:|---:|---:|---:|
| `uncertainty_claimforge_20260506000056_13352` | ClaimForge | `20260506000056_13352` | 9 | codex | 0.654 | 0.957 | 0.776 | 9 |
| `uncertainty_short_fallback_20260506090130_28396` | short fallback | `20260506090130_28396` | 6 | codex | 1.000 | 0.950 | 0.974 | 0 |
| `racial_short_fallback_20260506093950_32199` | short fallback | `20260506093950_32199` | 7 | codex | 1.000 | 1.000 | 1.000 | 0 |

All three cases had zero evaluator-only-file exposure in the summarized workdir artifacts.

## Interpretation

The helper reproduces the prior manual direction: short fallback conclusions are cleaner task-claim outputs, while ClaimForge includes useful planning/process claims that the task-claim judge penalizes as unsupported. That is the desired guardrail; the next step is a separate process-value fixture rather than loosening the task-claim judge.

Outputs are saved under `reports/judge_calibration/2026-05-10-log-helper-real-finals/`.
