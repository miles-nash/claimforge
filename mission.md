# Mission Decision Memo

Date: 2026-05-06

## Chosen Problem

Make autonomous research agents more trustworthy by improving their ability to reproduce and verify computational scientific claims.

In simple words: many agents can sound like researchers. Fewer can do the boring, sacred work of making a claim stand up. We should become excellent at that second thing.

## Why This Is The Right Bet

The world problem is epistemic load-bearing: science, medicine, AI safety, and policy all depend on knowing which claims are real. AI will make it cheaper to produce plausible research-looking output, so verification becomes more valuable, not less.

This is also a good fit for a 30-minute autonomous loop. The work naturally decomposes into repeatable chunks: read a paper, inspect a repo, run an experiment, compare a figure, write down a failure, patch a harness, or open an issue.

## Frontier Surface

Useful frontier movement can be verified through:

- Benchmark scores or traces on CORE-Bench, PaperBench, FIRE-Bench, MLE-Bench, or a small derived benchmark.
- Reproduction reports for published papers.
- Public PRs that fix broken research code or benchmark tooling.
- A reusable planning scaffold that improves agent success on repeated research tasks.
- Error taxonomies showing where agents fail and what mitigations help.

## Initial Strategy

Focus on the planning bottleneck in research-agent reproduction:

1. Compare existing benchmark protocols.
2. Pick a small, public, runnable subset.
3. Build a "claim-to-experiment" planning template.
4. Run baseline Codex attempts.
5. Add interventions: pre-mortem, artifact inventory, environment-first setup, expected figure/table contracts, and evidence ledger.
6. Measure whether the intervention changes success rate, time-to-first-valid-run, or claim-level F1 on a subset.

## Working Name

ClaimForge.

Not a product yet. Just a handle for the workflow: turn claims into tests.

## First Questions To Resolve

- Which benchmark is most runnable locally without special access?
- Which tasks are small enough for many 30-minute cycles but still externally meaningful?
- What exact metric should the first week optimize?
- What access does Miles need to grant before the automation can act independently?

## Current Constraint

Miles clarified that the experiment should spend Codex tokens rather than OpenAI API credits. That means agent rollouts can use Codex subprocesses, but benchmark judging may need a Codex-token-compatible scorer unless we choose to spend API credits for milestone evaluations.
