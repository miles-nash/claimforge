# Token Strategy

Purpose: make every 30-minute automation fire convert Codex tokens into durable frontier progress.

## Core Principle

Spend tokens where they create external evidence:

- clean benchmark rollouts
- reproducible scripts
- local baselines
- failure taxonomies
- reports
- commits / PR updates

Avoid spending tokens on repeated broad planning, generic literature summaries, or unbounded exploration without an artifact.

## Cycle Shape

Each automation fire should follow this order:

1. Read state
   - Check `state/next_actions.md`.
   - Check latest `logs/*.md`.
   - Check `git status --short --branch`.

2. Pick one cycle mode
   - `rollout`: run one clean Codex/FIRE-Bench rollout with a strict cap.
   - `analysis`: inspect a completed rollout and write a report.
   - `harness`: fix tooling that blocked or contaminated measurement.
   - `triage`: identify the next best benchmark/task using safe metadata only.
   - `publish`: commit, push, update PR, or open issue.

3. Produce one durable artifact
   - report, script, metric file, evidence ledger, patch, or PR update.

4. Record next state
   - Append a short log entry.
   - Update `state/next_actions.md`.
   - Commit and push if the artifact is worth preserving.

## Token Allocation

Default 30-minute fire:

- 3 minutes: orient from local state, no web unless needed.
- 20 minutes: execute one concrete task.
- 5 minutes: summarize evidence and update files.
- 2 minutes: commit/push if changes are coherent.

Heavy token use is justified when:

- running a clean benchmark rollout
- comparing raw vs ClaimForge behavior
- generating/refining code that will be reused
- producing a report with metrics from real outputs

Heavy token use is not justified when:

- the task would require external model API keys that are absent
- the agent is only restating known benchmark docs
- the workdir is not benchmark-clean
- there is no measurable output planned

## FIRE-Bench Rules

- Use `scripts/run_firebench_codex.py`; do not use the upstream runner directly.
- Keep workdirs outside `.cache/FIRE-Bench`.
- Do not inspect evaluator-only files: `conclusion.txt`, `instruction_gt.txt`, `rubric.json`, `expected_result.json`.
- If a run reads evaluator-only files, mark it invalid and stop trusting it.
- Prefer 300-second caps for scout pairs; use 600 seconds for serious comparisons.

## Current Best Use Of Tokens

1. Shorten `templates/blocked_model_fallback.md` and add an explicit final-summary phase.
2. Update the runner prompt so fallback runs reserve time for `run_summary.json` and a final conclusion.
3. Rerun raw+fallback only after the shorter preamble is in place.
4. Improve the Codex-token judge and calibrate it against one hand-written mini example.
5. If model API keys become available later, run milestone API evaluations only after local baselines and prompt manifests exist.
