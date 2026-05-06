# Next Actions

Last updated: 2026-05-06

## Active Hypothesis

ClaimForge improves research-agent usefulness under blocked or partial benchmark conditions by forcing evidence ledgers, fallback experiments, and explicit separation of measured evidence from inference.

## Immediate Queue

1. Run a raw fallback ablation on `uncertainty_in_instruction_following`: `--agent codex-raw-fallback --no-protocol --fallback-template always --timeout 300`.
2. Compare three runs: ClaimForge+fallback, raw, and raw+fallback.
3. Write or update a three-way report if the ablation isolates the fallback template effect.
4. If raw+fallback still times out, fold the fallback template into a shorter mandatory preamble.
5. After the ablation, consider a controlled-only milestone run if `HF_TOKEN` plus local model dependencies become available.

## Parking Lot

- Improve `scripts/codex_claim_judge.py` with saved raw prompts/responses.
- Investigate whether Hugging Face plugin access can support gated datasets without `HF_TOKEN`.
- Run `mcq_selection_bias` only in a clean fresh context because this thread previously inspected its hidden conclusion.

## Stop Conditions

- Stop and mark invalid if a rollout reads evaluator-only files.
- Stop direct model runs if API keys are missing; switch to local baselines.
- Do not start multiple long rollouts in one heartbeat unless the previous one is finished and logged.
