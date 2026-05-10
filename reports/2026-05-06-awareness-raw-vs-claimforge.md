# Awareness Detection: Raw vs ClaimForge

Date: 2026-05-06

Task: FIRE-Bench `awareness_detection`

Model: `gpt-5.5`

Runner: patched isolated runner

## Runs Compared

| Agent | Run id | Runtime | Return code | Result |
|---|---|---:|---:|---|
| `claimforge-codex` | `20260505221550_13481` | 527.82s | 0 | completed with artifacts |
| `codex-raw` | `20260505222735_15324` | 600.01s | 124 | timed out |

## Hygiene

Both runs used the patched runner and stayed in the copied task environment.

The raw run executed a safe structure check:

```text
.
./data
./utils
```

No evaluator-only files were exposed in the working directory.

## Artifact Comparison

ClaimForge produced:

- `evidence_ledger.md`
- `experiment_plan.md`
- `scripts/run_awareness_detection.py`
- `scripts/analyze_awareness_results.py`
- `scripts/surface_signal_baseline.py`
- `results/awareness_summary.md`
- `results/awareness_metrics.json`
- `results/surface_signal_baseline.md`
- `results/surface_signal_baseline.json`

Raw Codex produced:

- no final message
- no experiment script
- no metrics
- no report

## Interpretation

This is one concrete win for ClaimForge as a research-agent protocol.

The raw agent made a reasonable initial plan but stalled before execution. The ClaimForge-conditioned agent moved from plan to artifacts, explicitly separated measured evidence from blocked claims, and returned a cautious conclusion.

ClaimForge did not solve the original frontier-model question; model API access was still missing. But it improved the failure mode. Instead of timing out with no result, it produced a reusable partial replication artifact and a clear access-blocker diagnosis.

## Next Step

Run a second pair on another local-data task, likely `llm_racial_bias_in_medicine` or `mcq_selection_bias`, using a shorter 300-second cap first. The question to test is whether ClaimForge consistently converts blocked model tasks into useful local baselines instead of stalling.

