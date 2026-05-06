# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Shorten `templates/blocked_model_fallback.md` and add an explicit 60/120/60 second time budget.
2. Update `scripts/run_firebench_codex.py` prompt wording so fallback runs must reserve the final minute for `run_summary.json` and a final message.
3. Rerun a short raw+fallback ablation on `uncertainty_in_instruction_following` only after the fallback preamble is shortened.
4. If the shorter fallback still times out, make the runner synthesize a final conclusion from `run_summary.json` when present.
5. Consider a controlled-only milestone run if `HF_TOKEN` plus local model dependencies become available.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
