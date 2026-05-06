# Uncertainty In Instruction Following: Raw vs ClaimForge

Date: 2026-05-06

Task: FIRE-Bench `uncertainty_in_instruction_following`

Model: `gpt-5.5`

Runner: patched isolated runner

## Runs Compared

| Agent | Run id | Runtime | Return code | Final? | Artifacts |
|---|---|---:|---:|---|---:|
| `claimforge-codex` | `20260506000056_13352` | 294.35s | 0 | yes | 9 |
| `codex-raw` | `20260506000555_10100` | 300.01s | 124 | no | 0 |

## Hygiene

Both runs used isolated copied task assets and did not expose evaluator-only files in the workdir.

The copied task environment contained:

- `data/controlled_ver.jsonl`
- `data/realistic_ver.jsonl`
- `utils/llm_inference.py`
- `utils/cot_decoding.py`

No evaluator-only files were found by `scripts/compare_firebench_runs.py`.

## ClaimForge Result

ClaimForge completed before the 300-second cap and produced the standard blocked-model fallback artifacts:

- `access_check.json`
- `data_audit.json`
- `evidence_ledger.md`
- `local_baselines.json`
- `prompt_manifest.jsonl`
- `prompt_preview.json`
- `research_plan.md`
- `run_blocked_fallback.py`
- `run_summary.json`

Measured local evidence:

- Controlled data: 1,221 rows: 429 `correct`, 411 `incorrect`, 381 `subtle_off`.
- Realistic data: 714 rows: 369 `correct`, 345 `incorrect`.
- Missing access: `OPENAI_API_KEY`, `HF_TOKEN`.
- Missing imports: `openai`, `transformers`, `torch`, plus supporting analysis packages.
- `utils.llm_inference` import failed because `openai` was absent.
- No external model calls were attempted.

The dry-run manifest contains 9,000 requests total, 1,800 per model. The full controlled Easy+Hard design would be 9,900 calls/model, inside the 10,000-call/model budget; adding all realistic examples would require 14,184 calls/model.

Local non-model baselines were weak:

| Split | Best shallow AUROC | Note |
|---|---:|---|
| Controlled-Easy | 0.535 | response line count |
| Controlled-Hard | 0.511 | response line count |
| Realistic | 0.455 | instruction count |

Interpretation: response length, prompt length, instruction count, and line count are not meaningful substitutes for the intended uncertainty methods.

## Raw Result

Raw Codex recognized that `python` was missing, retried some checks with `python3`, and noticed missing `OPENAI_API_KEY`, `HF_TOKEN`, and `torch`. It did not write a final message or any durable artifacts before the 300-second timeout.

## Interpretation

This is the strongest process result so far.

The new blocked-model fallback prompt appears to have changed the failure mode: ClaimForge turned an access-blocked model task into a complete dry-run manifest, data audit, baseline sanity check, and conservative final conclusion. Raw Codex spent the same budget inspecting the files and environment but timed out without leaving artifacts.

The original benchmark claim remains blocked. This run did not measure verbalized confidence, p(true), normalized p(true), perplexity, sequence probability, or entropy for target models. It did verify that the controlled subset is a good next milestone because the full controlled design fits the 10,000-call/model budget.

## Next Experiment

Run a raw ablation with `--no-protocol --fallback-template always` on the same task. That will separate the effect of the fallback template from the broader ClaimForge protocol.

