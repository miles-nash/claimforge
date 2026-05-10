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
| high-quality blocked conclusion | 0.952 | 1.000 | 0 | yes |
| no-final failure | 0.000 | 0.000 | 0 | yes |
| overclaiming conclusion | 0.000 | 0.000 | 5 | yes |

The key calibration rule: `unsupported_overclaims` should only include substantive scientific/task-result overclaims, not meta run-status or packaging text such as "return code 124" or "completed the blocked-run package".
