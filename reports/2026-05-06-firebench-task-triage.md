# FIRE-Bench Task Triage

Date: 2026-05-06

Question: which verified FIRE-Bench tasks can be completed under a Codex-token-only constraint, without external model API keys?

## Finding

In the verified FIRE-Bench split, every task instruction mentions external models, API calls, Hugging Face model loading, or model-specific resources. That means a clean Codex-only rollout can often produce useful local baselines and access-blocker reports, but it usually cannot complete the intended frontier-model experiment exactly.

This is not a dead end. It changes the strategy:

1. Prefer tasks with local datasets where Codex can build artifact baselines.
2. Treat direct model-comparison claims as blocked unless model keys are present.
3. Use Codex-only work for reproducibility scaffolding, benchmark hygiene, baselines, and failure analysis.
4. Use external model APIs sparingly only when a specific milestone needs the original task semantics.

## Best Near-Term Candidates

These are not API-free; they are just the best candidates for useful Codex-only fallback work.

| Task | Why It Is Useful | Local Data |
|---|---|---:|
| `awareness_detection` | Already produced clean local baselines; good for comparing raw vs ClaimForge discipline. | yes |
| `llm_racial_bias_in_medicine` | Has local data and a clear statistical question; likely supports non-model fairness analysis baselines. | yes |
| `mcq_selection_bias` | Small local MMLU-style data; can test option-position mechanics with non-frontier baselines. | yes |
| `uncertainty_in_instruction_following` | Has local data; can analyze calibration structure and task construction. | yes |
| `llms_lack_self_correction` | Has local benchmark files; may support reproduction of aggregate patterns without fresh model calls. | yes |
| `introspective_learning` | Has many local files; likely useful for dataset/artifact analysis, but heavier. | yes |

## Operational Rule

For every Codex-only FIRE-Bench run, the final answer must explicitly separate:

- measured local evidence
- inferred implications
- blocked original benchmark claims

That separation is currently the main thing ClaimForge appears to improve.

