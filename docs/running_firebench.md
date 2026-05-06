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

Summarize a run:

```bash
python3 scripts/summarize_firebench_run.py .cache/FIRE-Bench/log/<agent>/<model>/<task>/<timestamp>/log.log
```

The wrapper:

- clones FIRE-Bench into `.cache/FIRE-Bench` if needed
- reads only `instruction/instruction.txt` for the selected task
- copies task `data/` and FIRE-Bench `utils/` into an isolated work directory
- runs `npx @openai/codex@latest exec`
- writes logs under `.cache/FIRE-Bench/log/<agent>/<model>/<task>/<timestamp>/log.log`
- appends an OpenHands-style `final_thought='...', outputs={}` marker so FIRE-Bench's evaluator can extract the final conclusion

Evaluation caveat:

FIRE-Bench's evaluator currently uses OpenAI API based judging through RAGChecker. If we keep the whole experiment purely on Codex tokens, use the rollouts and logs first, then either:

- implement a Codex-token-compatible judge, or
- run API judging only for selected final results where external comparability matters.
