# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Run the calibrated Codex judge on real final messages from ClaimForge and short-fallback runs:
   - uncertainty ClaimForge `20260506000056_13352`
   - uncertainty short fallback `20260506090130_28396`
   - racial-bias short fallback `20260506093950_32199`
2. Write a comparison report with artifact count, final status, precision, recall, F1, and overclaim count.
3. If the calibrated judge remains stable, add a small helper that extracts final messages from logs and feeds them into `scripts/codex_claim_judge.py`.
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
