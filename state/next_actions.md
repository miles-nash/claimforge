# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Add a small helper that extracts final messages from FIRE-Bench logs and feeds them into `scripts/codex_claim_judge.py`.
2. Keep two score lanes separate:
   - task-claim quality: measured evidence, blockers, and non-overclaiming conclusions
   - process value: plans, baselines, budgets, evidence ledgers, and reusable scaffolding
3. Extend the judge fixture with one process-value case so ClaimForge's extra planning output can be credited without weakening the task-claim overclaim guard.
4. Treat `templates/blocked_model_fallback.md` as the default blocked-model scout protocol after success on two tasks and judge-fixture calibration.
5. Consider a controlled-only milestone run if `HF_TOKEN` plus local model dependencies become available.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
