# Racial Bias In Medicine: Raw vs ClaimForge

Date: 2026-05-06

Task: FIRE-Bench `llm_racial_bias_in_medicine`

Model: `gpt-5.5`

Runner: patched isolated runner

## Runs Compared

| Agent | Run id | Runtime | Return code | Result |
|---|---|---:|---:|---|
| `claimforge-codex` | `20260505224115_94572` | 300.02s | 124 | timed out after producing blocked-run artifacts |
| `codex-raw` | `20260505224632_58956` | 300.02s | 124 | timed out after producing partial experiment artifacts |

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

## Interpretation

This pair is a more nuanced result than `awareness_detection`.

Raw Codex did not fully stall; it built a plausible counterfactual experiment and wrote useful dry-run artifacts. That means this task has a simpler natural structure than the awareness task, and an unguided agent can sometimes find it.

ClaimForge still improved the failure mode in two ways:

- It kept the call budget smaller and closer to a single experimental contract.
- It wrote an explicit access check and blocked-run summary rather than only a model-specific execution status.

Neither run completed the intended frontier-model question. The original claim remains blocked until model credentials and Python dependencies are available. The real progress here is a reusable blocked-model pattern: when model APIs are absent, the agent should still produce a checked prompt manifest, leakage audit, access diagnosis, and non-overclaiming conclusion.

## Token Lesson

The next automation cycle should not spend more tokens proving that missing API keys block model calls. It should extract the common fallback protocol and add tooling that summarizes paired rollouts automatically.

