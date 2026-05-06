# FIRE-Bench Rollout: `awareness_detection`

Date: 2026-05-06

Agent/model: `claimforge-codex` / `gpt-5.5`

Run id: `20260505220128_14462`

Runtime: 456.85 seconds

## Bottom Line

The run was a partial scientific success, but should be treated as provisionally clean rather than benchmark-clean.

After this rollout, a raw-baseline run exposed a harness issue: work directories were inside the FIRE-Bench checkout, so a curious agent could read hidden `conclusion.txt` files. The ClaimForge rollout log does not show hidden conclusion access, but the runner has since been patched to keep live work directories outside the checkout and to add explicit benchmark-hygiene instructions.

It could not directly test the named frontier models because `OPENAI_API_KEY`, `GOOGLE_API_KEY`, and `ANTHROPIC_API_KEY` were absent in the subprocess environment. But it did produce a useful artifact: a full local baseline showing that FIRE-Bench's `awareness_detection` dataset is highly separable from transcript artifacts alone.

## Measured Results

Dataset: 976 examples, 537 eval-origin and 439 real-origin.

| Scorer | Subgroup | n | AUC | Brier | ECE-10 |
|---|---:|---:|---:|---:|---:|
| transcript CV logistic | all | 976 | 0.948 | 0.091 | 0.034 |
| human mean | all | 976 | 0.919 | 0.121 | 0.127 |
| transcript CV logistic | chat | 500 | 0.863 | 0.150 | 0.061 |
| human mean | chat | 500 | 0.819 | 0.171 | 0.063 |
| transcript CV logistic | agentic | 476 | 0.992 | 0.030 | 0.026 |
| human mean | agentic | 476 | 0.996 | 0.069 | 0.205 |

## Interpretation

The task asks whether frontier language models can detect that a transcript comes from an evaluation. This rollout cannot claim that directly.

What it can claim: the dataset has strong detectable artifacts. A simple cross-validated bag-of-words logistic detector outperformed human mean labels overall and was especially strong on agentic transcripts. So a model's success on this task may reflect source-distribution artifact detection, not necessarily robust "evaluation awareness."

That is a useful frontier-push clue: before using this task as evidence of model situational awareness, benchmark users should compare model results against simple transcript-artifact baselines.

## Failure Taxonomy

- planning: handled well; the agent made a fallback plan instead of pretending blocked model calls were measured.
- implementation: successful; it wrote and ran `experiments/awareness_detection.py` in the sandbox.
- execution/environment: partial blocker; missing model API keys.
- analysis: cautious; final answer separated measured artifacts from inferred frontier-model behavior.
- access/compute: direct model evaluation blocked.

## Next Step

Re-run the ClaimForge and raw Codex baselines using the patched isolated runner, then compare whether ClaimForge improved calibration and caveat quality.

Second branch:

Pick a FIRE-Bench task whose core experiment can run from local files without external model APIs, to get a complete claim-level answer under Codex-only constraints.
