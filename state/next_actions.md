# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Test generality by running a raw+short-fallback scout on `llm_racial_bias_in_medicine`:
   `python3 scripts/run_firebench_codex.py --task llm_racial_bias_in_medicine --model gpt-5.5 --agent codex-raw-fallback-short --no-protocol --fallback-template always --timeout 300`
2. Compare the new run against the earlier racial-bias ClaimForge/raw pair (`20260505224115_94572`, `20260505224632_58956`) with `scripts/compare_firebench_runs.py`.
3. Update `reports/2026-05-06-racial-bias-raw-vs-claimforge.md` if the rerun is informative.
4. If short fallback generalizes, promote it from task-specific patch to default blocked-model scout protocol and then return to Codex-token judge calibration.
5. Consider a controlled-only milestone run if `HF_TOKEN` plus local model dependencies become available.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
