# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Run `claimforge-codex` on `llm_racial_bias_in_medicine` with the patched runner and a 300-second cap.
2. Run `codex-raw` on `llm_racial_bias_in_medicine` with the patched runner and a 300-second cap.
3. Compare artifacts, timeout behavior, and overclaiming.
4. Write `reports/YYYY-MM-DD-racial-bias-raw-vs-claimforge.md`.
5. Extract a reusable blocked-model fallback template.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Add a command that summarizes rollout artifact counts automatically.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.

