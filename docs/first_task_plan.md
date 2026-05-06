# First Task Plan

Date: 2026-05-06

## Goal

Get one real FIRE-Bench rollout trace quickly, then use it to improve the ClaimForge protocol.

## Clean First Task

`awareness_detection`

Why:

- verified FIRE-Bench task
- local data is present but small
- parent thread has not inspected the hidden conclusion
- research question is about evaluation-awareness detection, which is conceptually close to agent reliability

## Run Matrix

1. `claimforge-codex` on `awareness_detection`, 10-minute cap
2. `codex-raw` on `awareness_detection`, 10-minute cap
3. Compare:
   - final conclusion specificity
   - number of unsupported claims
   - whether it created and used an evidence ledger
   - execution failures

Claim-level F1 remains the official metric, but upstream FIRE-Bench judging currently uses API-based RAGChecker. Until we decide to spend API credits for judging or build a Codex-compatible judge, use qualitative trace review plus extracted conclusions.

## Immediate Hypotheses

- ClaimForge should improve precision by reducing unsupported narrative.
- It may reduce recall if the protocol makes the agent too conservative.
- The first failure is likely to be execution-resource related, not reasoning related.

