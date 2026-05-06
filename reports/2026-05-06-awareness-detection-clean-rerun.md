# FIRE-Bench Clean Rerun: `awareness_detection`

Date: 2026-05-06

Agent/model: `claimforge-codex` / `gpt-5.5`

Run id: `20260505221550_13481`

Runtime: 527.82 seconds

Runner: patched isolated runner

## Why This Rerun Matters

The first rollout produced useful science, but a later raw-baseline attempt exposed a harness contamination risk: agents could find hidden FIRE-Bench `conclusion.txt` files because workdirs lived inside the benchmark checkout.

This rerun used the patched runner:

- live workdir under `.cache/claimforge-work/...`
- live logs under `.cache/claimforge-logs/...`
- post-run log mirror to `.cache/FIRE-Bench/log/...`
- explicit instruction not to inspect evaluator-only files

The log stayed focused on copied task assets: `data/dataset.json`, `utils/`, and files created in the workdir.

## Result

The frontier-model experiment was access-blocked:

- `gpt-4.1`: missing `OPENAI_API_KEY`
- `gemini-2.5-pro`: missing `GOOGLE_API_KEY`
- `claude-3.7-sonnet`: missing `ANTHROPIC_API_KEY`

So the main claim remains unmeasured:

> Frontier language models can detect whether a transcript came from evaluation rather than deployment.

## Local Evidence

The dataset itself contains detectable provenance signal.

Human-label baseline:

| Group | n | AUC | Brier | ECE-10 |
|---|---:|---:|---:|---:|
| overall | 976 | 0.919 | 0.121 | 0.127 |
| agentic | 476 | 0.996 | 0.069 | 0.205 |
| chat | 500 | 0.819 | 0.171 | 0.063 |

Simple surface-cue logistic baseline:

| Group | n | AUC | Brier | ECE-10 |
|---|---:|---:|---:|---:|
| overall | 976 | 0.751 | 0.198 | 0.093 |
| agentic | 476 | 0.814 | 0.171 | 0.113 |
| chat | 500 | 0.626 | 0.224 | 0.108 |

## Interpretation

The clean result is weaker but more trustworthy than the first provisional result.

It says: evaluation provenance is encoded in the transcript distribution, especially for agentic transcripts. Simple surface features explain some but not all of the human-label signal. Without model API access, this run cannot say whether frontier models detect the provenance, nor whether they rely on robust semantic awareness versus artifacts.

## Next Step

Run a clean raw Codex baseline with the same patched harness. Compare:

- whether raw Codex reads only copied assets
- final-answer caveat quality
- whether it produces runnable scripts and evidence files
- whether ClaimForge improves precision by refusing to overclaim

