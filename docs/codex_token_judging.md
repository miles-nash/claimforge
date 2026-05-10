# Codex-Token Judging Plan

FIRE-Bench rollouts can now run through Codex tokens, but upstream scoring still uses API-backed RAGChecker. To keep the experiment aligned with Codex-token execution, we need a comparable judging path.

## Options

1. Use upstream API judge sparingly
   - Best for public comparability.
   - Costs API credits.
   - Use only for selected milestone runs.

2. Codex-as-judge subprocess
   - Use `npx @openai/codex@latest exec` to decompose the ground truth and agent conclusion into atomic claims.
   - Ask the judge to emit strict JSON with precision/recall support decisions.
   - Pros: stays in Codex-token budget.
   - Cons: not directly comparable to upstream leaderboard without calibration.

3. Hybrid deterministic pre-judge
   - Extract claims using a rigid prompt plus local JSON schema validation.
   - Use exact/semantic overlap heuristics to flag likely unsupported claims.
   - Use Codex only for ambiguous comparisons.

## First Implementation

Created `scripts/codex_claim_judge.py`.

Usage:


```bash
python3 scripts/codex_claim_judge.py \
  --question "..." \
  --ground-truth-file gt.txt \
  --conclusion-file final.txt
```

Output:

```json
{
  "precision": 0.0,
  "recall": 0.0,
  "f1": 0.0,
  "agent_claims": [],
  "ground_truth_claims": [],
  "support_matrix": []
}
```

Guardrails:

- Judge prompt must forbid using hidden context beyond the supplied conclusion and ground truth.
- Save the full judge prompt and raw response for audit.
- Calibrate on one or two tasks with upstream API judging if API use becomes acceptable later.

## Calibration Fixture

Added `fixtures/judge_calibration/blocked_run_cases.jsonl` and `scripts/run_judge_calibration.py`.

Run:

```bash
python3 scripts/run_judge_calibration.py --timeout 180
```

Outputs are saved under `reports/judge_calibration/2026-05-06-blocked-runs/`, including:

- per-case `ground_truth.txt`
- per-case `conclusion.txt`
- per-case `score.json`
- per-case `audit/prompt.txt`
- per-case `audit/raw_response.txt`
- `summary.json`
- `summary.md`

Current calibration result:

| Case | Precision | Recall | Overclaims | Expected? |
|---|---:|---:|---:|---|
| high-quality blocked conclusion | 1.000 | 1.000 | 0 | yes |
| no-final failure | 1.000 | 0.000 | 0 | yes |
| overclaiming conclusion | 0.000 | 0.000 | 7 | yes |

The key calibration rule: score scientific/task-relevant claims only. Ignore artifact inventories, file paths, validation notes, and packaging text such as "return code 124" or "completed the blocked-run package". A no-final failure can have vacuous precision but should have low recall.

## FIRE-Bench Log Helper

Added `scripts/judge_firebench_finals.py` so automation fires can score real Codex finals without hand-copying conclusions from log files.

Run:

```bash
python3 scripts/judge_firebench_finals.py \
  --cases fixtures/judge_calibration/real_log_cases.jsonl \
  --output-dir reports/judge_calibration/2026-05-10-log-helper-real-finals \
  --timeout 180
```

The helper:

- extracts `CLAIMFORGE_FINAL_RESULT` from each FIRE-Bench log, falling back to sibling `last_message.txt`
- copies the matched ground truth into a per-case output directory
- feeds the extracted final into `scripts/codex_claim_judge.py`
- saves `score.json`, `log_summary.json`, `runner_stdout.txt`, `summary.json`, and `summary.md`

Use `--dry-run` to verify extraction and metadata without spending judge tokens. Use `--save-audit` when prompt and raw judge response artifacts are worth the extra files.

Keep two score lanes separate:

- `task_claim_quality`: measured evidence, blockers, and non-overclaiming conclusions
- `process_value`: plans, baselines, budgets, evidence ledgers, and reusable scaffolding

Do not weaken the task-claim judge to credit planning output. Add process-value fixtures instead.

## Process-Value Lane

Added `fixtures/judge_calibration/process_value_cases.jsonl` and `scripts/score_process_value_cases.py`.

Run:

```bash
python3 scripts/score_process_value_cases.py \
  --fixture fixtures/judge_calibration/process_value_cases.jsonl \
  --output-dir reports/process_value/2026-05-10-claimforge-process-fixture
```

This is a deterministic local rubric over artifact bundles, not a Codex claim judge. It scores whether a blocked run produced useful research-process scaffolding:

- access audit
- data audit
- prompt manifest and preview
- local non-model sanity baselines
- budget and scale-up notes
- evidence ledger
- research plan
- measured-vs-blocked claim boundary
- reusable fallback script
- evaluator-file hygiene

The first ClaimForge uncertainty process fixture scored 10/10. That result should be read beside, not merged into, the task-claim score. The split is the point: ClaimForge can be valuable for planning and scaffolding even when its final task conclusion is less compact than the short fallback.
