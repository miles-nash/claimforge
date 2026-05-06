# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Calibrate `scripts/codex_claim_judge.py` against known blocked-run cases from `uncertainty_in_instruction_following` and `llm_racial_bias_in_medicine`.
2. Create a tiny hand-labeled fixture with at least one high-quality blocked conclusion, one artifact-only/no-final failure, and one overclaiming conclusion.
3. Save judge prompts/responses or scores in a durable report so later automation fires can track conclusion quality, not just final-message presence.
4. Treat `templates/blocked_model_fallback.md` as the default blocked-model scout protocol after success on two tasks.
5. Consider a controlled-only milestone run if `HF_TOKEN` plus local model dependencies become available.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
