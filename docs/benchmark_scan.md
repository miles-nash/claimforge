# Benchmark Scan

Date: 2026-05-06

## Recommendation

Start with FIRE-Bench.

Reason: it has a Codex runner, 35 verified tasks, claim-level precision/recall/F1, and the public leaderboard already shows Codex is close to the frontier but bottlenecked by research planning. That is exactly where a token-rich, iterative workflow can help.

## Candidate Benchmarks

| Benchmark | What It Measures | First-Week Fit | Notes |
|---|---|---:|---|
| FIRE-Bench | Whether agents can rediscover scientific insights from a high-level research question | High | 35 verified tasks, local task folders, Codex runner, claim-level F1. Public results: Claude Code Sonnet-4 F1 46.7, Codex CLI gpt-5-medium F1 41.9. Reported error bottleneck: planning. |
| PaperBench | Whether agents can replicate full ICML 2024 papers from scratch | Medium | Very valuable but heavier. Needs Docker, Git LFS data hydration, agent/judge API keys, and often GPU access. Good second stage. |
| CORE-Bench | Computational reproduction of papers across CS, social science, medicine | Medium | Strong fit for reproducibility. Original harness now points users to the Holistic Agent Leaderboard. Local runs need Docker and sometimes Azure/GPU. |
| MLE-Bench | ML engineering on Kaggle-style competitions | Medium-Low for this mission | Excellent benchmark, but more about competitive ML execution than scientific claim verification. Requires Kaggle credentials and large datasets. |

## First FIRE-Bench Slice

Prefer tasks with small local footprints and clear experimental plans:

- `awareness_detection`
- `cot_in_planning`
- `lost_in_the_middle`
- `llms_lack_self_correction`
- `mcq_selection_bias`

Initial run target:

- Run 1-2 tasks with the stock Codex runner.
- Manually inspect trajectory failures.
- Add the ClaimForge planning scaffold.
- Re-run the same tasks.
- Compare claim-level F1 and the failure taxonomy.

## FIRE-Bench Local Notes

Repo inspected: `https://github.com/maitrix-org/FIRE-Bench`

Useful commands from upstream:

```bash
pip install -r requirements.txt
cp .env.example .env  # if present, otherwise create .env manually
bash run_experiment.sh --agents codex --models gpt-5-medium --tasks mcq_selection_bias --run_times 1
bash run_eval.sh --agents codex --models gpt-5-medium --tasks mcq_selection_bias
```

Required access:

- `OPENAI_API_KEY`
- `HF_TOKEN` for model/data tasks when needed
- `ANTHROPIC_API_KEY` and `GOOGLE_API_KEY` only for cross-agent/model comparisons

Potential issue:

FIRE-Bench's Codex runner expects `npx @openai/codex@0.39.0`. This desktop Codex session may not expose the same API-key-based CLI environment as the runner expects, so the first setup cycle should verify CLI auth and version.

Local check:

- Node: present
- npm: present
- Docker: present
- `npx @openai/codex@0.39.0 --version`: works
- `HF_TOKEN`: missing from shell environment
- Codex CLI package: available via `npx @openai/codex@0.39.0`

Fairness note:

During initial scouting, I inspected the hidden ground-truth plan and conclusion for `mcq_selection_bias`. Do not use this same thread as a clean agent baseline for that task. A fresh CLI subprocess can still be used, and other tasks remain clean for this thread.

Execution note:

Miles clarified that the experiment should spend Codex tokens, not OpenAI API credits. Treat `OPENAI_API_KEY` as optional unless a third-party benchmark judge or cross-model comparison absolutely requires it.
