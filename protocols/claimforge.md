# ClaimForge Protocol

Purpose: improve agent research by forcing every claim to become an experiment, and every experiment to become evidence.

## Core Rule

Never let the agent optimize for "a plausible conclusion." Optimize for a ledger of checkable claims.

## Workflow

1. Claim inventory
   - State the research question in one sentence.
   - List candidate atomic claims that would answer it.
   - Mark each claim as unknown, supported, contradicted, or out of scope.

2. Artifact inventory
   - List available data, models, APIs, code, and expected outputs.
   - Note missing access before spending effort around it.

3. Experimental contract
   - Define the smallest result that would change belief.
   - Name the metric, table, figure, or comparison before running code.
   - Write down expected failure modes.

4. Execution
   - Run the simplest end-to-end path first.
   - Save commands, environment notes, and outputs.
   - Prefer one clean measurement over five half-built branches.

5. Evidence ledger
   - Link each conclusion to a command, result file, or observed output.
   - Separate measured results from interpretation.
   - Record uncertainty plainly.

6. Postmortem
   - If the run failed, classify it:
     - planning error
     - implementation error
     - execution/environment error
     - analysis error
     - access/compute blocker
   - Choose one intervention for the next run.

## Hypothesized Intervention

Most research-agent failures are planning failures, so insert this planning gate before code:

```text
Before implementing, produce:
1. The exact claim-level answer shape you expect.
2. The minimum experiment that can support or refute each claim.
3. The artifact list needed to run it.
4. Three ways this plan could fool you.
5. A fallback experiment if the ideal one is too expensive.
```

## First Metric

For FIRE-Bench:

- Primary: claim-level F1
- Secondary: precision, recall
- Process metrics: time to first valid run, number of planning deviations, number of unsupported claims in final answer

