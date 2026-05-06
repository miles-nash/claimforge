# Racial Bias In Medicine: Short-Fallback Generalization

Date: 2026-05-06

Task: FIRE-Bench `llm_racial_bias_in_medicine`

Model: `gpt-5.5`

Runner: patched isolated runner

## Runs Compared

| Agent | Run id | Runtime | Return code | Result |
|---|---|---:|---:|---|
| `claimforge-codex` | `20260505224115_94572` | 300.02s | 124 | timed out after producing blocked-run artifacts |
| `codex-raw` | `20260505224632_58956` | 300.02s | 124 | timed out after producing partial experiment artifacts |
| `codex-raw-fallback-short` | `20260506093950_32199` | 229.01s | 0 | completed with a Codex-authored blocked-run conclusion |

## Hygiene

Both runs used isolated copied task assets and did not expose evaluator-only files in the working directory.

The copied environment contained only task data and utilities:

- `data/PMC-Patients_subset100.json`
- `utils/llm_inference.py`
- `utils/cot_decoding.py`

The only mentions of evaluator-only filenames in logs came from the runner's hygiene prompt and safe exclusion commands.

## Artifact Comparison

ClaimForge produced:

- `analysis/run_counterfactual_audit.py`
- `outputs/access_check.json`
- `outputs/dataset_and_prompt_summary.json`
- `outputs/prompt_preview.json`
- `outputs/run_summary.json`

Raw Codex produced:

- `race_bias_cost_los_experiment.py`
- `outputs/execution_status.json`
- `outputs/preprocessed_vignettes.json`
- `outputs/prompts_manifest.jsonl`

Raw Codex with the short fallback produced:

- `access_check.json`
- `data_audit.json`
- `local_baselines.json`
- `prompt_manifest.jsonl`
- `prompt_preview.json`
- `run_summary.json`
- `scoring_manifest.jsonl`

## Measured Evidence

ClaimForge found:

- 100 patient records.
- 600 prompts per model: 100 patients x 6 race/ethnicity labels.
- 54 male and 46 female records.
- Race/national-origin terms appeared in 15 records, 16 total mentions.
- Mean raw vignette length was 2757.76 characters; mean early excerpt length was 940.25 characters.
- Model execution was blocked by both missing `OPENAI_API_KEY` and missing `openai` Python package.

Raw Codex found:

- 100 patient records.
- 1000 prompts per model: 100 patients x 5 race/ethnicity labels x 2 prompt frames.
- 15 total redactions.
- Preprocessed vignette word count: min 11, median 47.5, max 145.
- `gpt-3.5-turbo` and `gpt-4` were not run because `OPENAI_API_KEY` was absent.

Raw Codex with the short fallback found:

- 100 patient records.
- 6 race/ethnicity counterfactual conditions.
- 600 planned requests for `gpt-3.5-turbo` and 600 for `gpt-4`.
- 1,200 total prompt-manifest rows and 200 scoring-manifest rows.
- The design is balanced: every model/race-condition cell has exactly 100 prompts.
- The design stays within the 1,000-call/model budget.
- Model execution was blocked by missing `OPENAI_API_KEY` and missing imports: `openai`, `requests`, `dotenv`, `transformers`, `anthropic`, and `utils.llm_inference`.
- No external model calls were attempted.

## Interpretation

This pair is a more nuanced result than `awareness_detection`.

Raw Codex did not fully stall; it built a plausible counterfactual experiment and wrote useful dry-run artifacts. That means this task has a simpler natural structure than the awareness task, and an unguided agent can sometimes find it.

ClaimForge still improved the failure mode in two ways:

- It kept the call budget smaller and closer to a single experimental contract.
- It wrote an explicit access check and blocked-run summary rather than only a model-specific execution status.

The short fallback now improves the failure mode further:

- It completed in 229.01 seconds, below the 300-second cap.
- It produced a Codex-authored final conclusion.
- It preserved the core blocked-run package: access check, data audit, prompt manifest, prompt preview, scoring manifest, local design checks, and run summary.

Neither run completed the intended frontier-model question. The original claim remains blocked until model credentials and Python dependencies are available. The real progress here is a reusable blocked-model pattern: when model APIs are absent, the agent should still produce a checked prompt manifest, leakage audit, access diagnosis, and non-overclaiming conclusion.

After the uncertainty-task ablation and this racial-bias generalization, the short fallback should be treated as the default blocked-model scout protocol. ClaimForge remains useful when the goal is deeper research structure, local baselines, and evidence-ledger discipline, but the shorter fallback is enough to prevent timeout-without-final behavior on at least two blocked model tasks.

## Token Lesson

The next automation cycle should stop spending rollout tokens on missing-key rediscovery. The best next use is judge calibration: make the Codex-token judge score known blocked-run conclusions so future reports can compare quality, not just artifact count and final-message status.
