# Real Final Judge Scores

Date: 2026-05-10

Mode: analysis.

## Purpose

Run the calibrated Codex-token judge on real final messages, then compare conclusion quality alongside artifact count and final-message status.

The judge is a task-claim scorer: it checks whether a final conclusion accurately separates measured local evidence from blocked model claims. It intentionally ignores artifact bookkeeping, file paths, links, validation text, and generic run-status packaging.

## Runs Scored

| Run | Task | Agent | Artifacts | Final | Precision | Recall | F1 | Overclaims |
|---|---|---|---:|---|---:|---:|---:|---:|
| `20260506000056_13352` | uncertainty | ClaimForge | 9 | codex | 0.697 | 0.962 | 0.808 | 10 |
| `20260506090130_28396` | uncertainty | short fallback | 6 | codex | 1.000 | 0.941 | 0.970 | 0 |
| `20260506093950_32199` | racial bias | short fallback | 7 | codex | 1.000 | 1.000 | 1.000 | 0 |

Outputs and audit trails are saved under `reports/judge_calibration/2026-05-10-real-finals/`.

## Interpretation

The short fallback conclusions are cleaner under this task-claim judge. They focus on the blocked status, local data availability, prompt-manifest construction, missing credentials/packages, and the fact that no target model metric was measured.

The ClaimForge uncertainty conclusion has high recall but lower precision because it includes extra planning and methodology claims: baseline AUROC ranges, feasibility of a controlled evaluation, recommended label contrasts, metric choice, and budget implications. These are useful research-process claims, but the current judge treats them as unsupported task claims unless the ground truth explicitly includes them.

So the result is not "ClaimForge is worse." It is narrower:

- Short fallback is better for compact blocked-run conclusions.
- ClaimForge produces richer planning context that needs a separate process-value rubric.
- A single claim-precision score should not be used as the only measure of research-agent usefulness.

## Next Step

Add a small helper that extracts final messages from FIRE-Bench logs and feeds them into the judge, but keep two score lanes separate:

- task-claim quality: measured evidence, blockers, and non-overclaiming conclusions
- process value: plans, baselines, budgets, evidence ledgers, and reusable scaffolding
