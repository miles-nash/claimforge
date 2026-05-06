# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Turn `templates/blocked_model_fallback.md` into a reusable prompt block or runner option for future FIRE-Bench model-access blockers.
2. Use `scripts/compare_firebench_runs.py` when comparing future scout pairs.
3. Run the next clean scout pair on `uncertainty_in_instruction_following` with 300-second caps.
4. Compare whether the blocked-model fallback template reduces timeout-without-final behavior.
5. Update the automation prompt if the next run still spends tokens rediscovering missing API keys.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
