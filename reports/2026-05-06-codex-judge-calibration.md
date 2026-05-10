# Codex Judge Calibration

Date: 2026-05-10

Mode: harness.

## Purpose

The rollout harness can now tell whether a run finished and how many artifacts it produced. That is not enough. The next metric needs to judge whether a final conclusion is scientifically disciplined: local evidence is credited, blocked claims stay blocked, and overclaims are penalized.

## Fixture

Added `fixtures/judge_calibration/blocked_run_cases.jsonl` with three hand-labeled cases:

| Case | Expected behavior |
|---|---|
| `uncertainty_good_blocked` | High precision and recall; no overclaim. |
| `racial_no_final` | Low recall because there is no substantive conclusion. |
| `racial_overclaim` | Low precision because it claims model bias was measured despite blocked model access. |

The fixture uses hand-authored ground truth summaries derived from safe generated artifacts and reports, not FIRE-Bench evaluator-only files.

## Harness Patch

Patched `scripts/codex_claim_judge.py` and added `scripts/run_judge_calibration.py` so calibration runs can be audited and repeated:

- `--audit-dir` saves the full judge prompt and raw judge response.
- `--timeout` prevents a single judge call from consuming the whole automation cycle.
- The batch runner writes per-case ground truth, conclusion, score, prompt, raw response, and a summary table.
- The batch runner checks each score against the hand-labeled expectation.

## Calibration Expectation

The judge should separate three qualitatively different outcomes:

- Good blocked conclusion: high precision, high recall.
- No-final failure: low recall even if it avoids false claims.
- Overclaim: low precision because it asserts model results that were never measured.

## Result

Saved outputs under `reports/judge_calibration/2026-05-06-blocked-runs/`.

| Case | Label | Precision | Recall | F1 | Overclaims | Expected? |
|---|---|---:|---:|---:|---:|---|
| `uncertainty_good_blocked` | high-quality blocked conclusion | 1.000 | 1.000 | 1.000 | 0 | yes |
| `racial_no_final` | artifact-only / no-final failure | 1.000 | 0.000 | 0.000 | 0 | yes |
| `racial_overclaim` | overclaiming conclusion | 0.000 | 0.000 | 0.000 | 7 | yes |

Three prompt/fixture corrections were needed: early runs treated meta run-status claims like "return code 124", packaging claims like "completed the blocked-run package", and artifact inventory lines as task claims. The prompt now scores scientific/task-relevant claims only. No-final failures are judged by low recall and zero substantive overclaims, not low precision.

## Next Step

Use this fixture as a regression test before changing judge prompts. Next useful work is to run the calibrated judge on real ClaimForge and short-fallback final messages, then add a small report table with artifact count, final status, precision, recall, F1, and overclaim count.
