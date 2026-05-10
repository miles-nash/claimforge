# Next Actions

Last updated: 2026-05-10

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Add process-value cases for the short-fallback runs and score them with `scripts/score_process_value_cases.py`.
2. Write a two-lane comparison report that places task-claim quality beside process value for ClaimForge and short fallback.
3. Keep two score lanes separate in all reports and fixtures:
   - task-claim quality: measured evidence, blockers, and non-overclaiming conclusions
   - process value: plans, baselines, budgets, evidence ledgers, and reusable scaffolding
4. Use `scripts/judge_firebench_finals.py` for future real-log task-claim scores instead of hand-copying final messages.
5. Treat `templates/blocked_model_fallback.md` as the default blocked-model scout protocol after success on two tasks and judge-fixture calibration.
6. Consider a controlled-only milestone run if `HF_TOKEN` plus local model dependencies become available.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
