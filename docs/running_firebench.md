# Running FIRE-Bench With Codex Tokens

This project uses Codex subscription execution rather than OpenAI API billing for agent rollouts.

The upstream FIRE-Bench runner currently pins `@openai/codex@0.39.0`. On this machine, that older CLI cannot use the current ChatGPT/Codex account with `gpt-5`/`gpt-5.5`, so use the local wrapper:

```bash
python3 scripts/firebench_inventory.py
python3 scripts/run_firebench_codex.py --task awareness_detection --model gpt-5.5
```

For a raw baseline without the ClaimForge planning protocol:

```bash
python3 scripts/run_firebench_codex.py --task awareness_detection --model gpt-5.5 --agent codex-raw --no-protocol
```

ClaimForge runs inject `templates/blocked_model_fallback.md` by default. This tells access-blocked model tasks to produce an access check, data audit, prompt manifest, prompt preview, and blocked-run summary instead of spending the whole timeout rediscovering missing API keys. Disable it only for ablations:

```bash
python3 scripts/run_firebench_codex.py --task awareness_detection --model gpt-5.5 --fallback-template off
```

Summarize a run:

```bash
python3 scripts/summarize_firebench_run.py .cache/FIRE-Bench/log/<agent>/<model>/<task>/<timestamp>/log.log
```

Compare paired scout runs:

```bash
python3 scripts/compare_firebench_runs.py <claimforge-log.log> <raw-log.log>
```

The wrapper:

- clones FIRE-Bench into `.cache/FIRE-Bench` if needed
- reads only `instruction/instruction.txt` for the selected task
- copies task `data/` and FIRE-Bench `utils/` into an isolated work directory outside the FIRE-Bench checkout
- runs `npx @openai/codex@latest exec`
- writes live logs under `.cache/claimforge-logs/...`
- mirrors logs after completion to `.cache/FIRE-Bench/log/<agent>/<model>/<task>/<timestamp>/log.log` for evaluator compatibility
- records whether the blocked-model fallback template was included
- appends an OpenHands-style `final_thought='...', outputs={}` marker so FIRE-Bench's evaluator can extract the final conclusion

Benchmark hygiene:

The wrapper includes an explicit instruction not to inspect evaluator-only files such as `conclusion.txt`, `instruction_gt.txt`, rubrics, or expected results. This matters because local benchmark checkouts contain hidden conclusions that a non-isolated subprocess could otherwise read accidentally.

Evaluation caveat:

FIRE-Bench's evaluator currently uses OpenAI API based judging through RAGChecker. If we keep the whole experiment purely on Codex tokens, use the rollouts and logs first, then either:

- implement a Codex-token-compatible judge, or
- run API judging only for selected final results where external comparability matters.
