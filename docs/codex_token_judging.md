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
