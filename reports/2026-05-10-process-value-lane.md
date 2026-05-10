# Process-Value Lane

Date: 2026-05-10

Mode: harness.

## Purpose

Create a separate process-value fixture so ClaimForge's planning output can be credited without weakening the task-claim overclaim guard.

Task-claim quality answers: did the final conclusion accurately separate measured evidence, blockers, and unsupported claims?

Process value answers: did the run leave useful scaffolding for the next research step?

## Artifact

Added:

- `scripts/score_process_value_cases.py`
- `fixtures/judge_calibration/process_value_cases.jsonl`
- `reports/process_value/2026-05-10-claimforge-process-fixture/`

The process-value rubric is deterministic and local. It scores artifact bundles for:

- access audit
- data audit
- prompt manifest and preview
- local non-model sanity baselines
- budgeting and scale-up notes
- evidence ledger
- research plan
- measured-vs-blocked claim boundary
- reusable blocked-fallback script
- evaluator-only-file hygiene

## Result

| Case | Agent | Run | Process Score | Points | Expected? |
|---|---|---|---:|---:|---|
| `uncertainty_claimforge_process_20260506000056_13352` | ClaimForge | `20260506000056_13352` | 1.000 | 10/10 | yes |

Snapshot highlights:

- 9 artifacts captured: access check, data audit, evidence ledger, local baselines, prompt manifest, prompt preview, research plan, fallback script, and run summary.
- Prompt manifest contained 9,000 dry-run requests.
- Run summary separated 4 measured local claims from 2 blocked model claims.
- No evaluator-only files were present in the artifact bundle.

## Interpretation

The two-lane picture is now coherent:

- Task-claim lane: ClaimForge uncertainty final had lower precision because it included planning and methodology claims not present in the task-claim ground truth.
- Process-value lane: those same planning artifacts are now credited separately, where ClaimForge scores 10/10.

This preserves the hard overclaim guard while recognizing the thing ClaimForge is actually trying to improve: research usefulness under blocked or partial benchmark conditions.

## Next Step

Add process-value cases for the short-fallback runs and write a two-lane comparison report: task-claim quality beside process value.
