# Access Requests

Date: 2026-05-06

Concrete blockers for benchmark execution through Codex:

1. `HF_TOKEN`
   - Needed for Hugging Face datasets/models in FIRE-Bench and PaperBench.
   - Current shell status: missing.
   - Public FIRE-Bench metadata is available without a token through the Hugging Face Dataset Viewer API.

Soon useful:

2. GitHub access
   - Status: available through `gh` as `miles-nash` with `repo` scope.
   - Needed to publish the evolving harness, push results, open benchmark/tooling issues, and make work externally verifiable.

3. Codex CLI/subscription path
   - Needed only if we want FIRE-Bench to spawn fresh Codex CLI subprocesses instead of using this 30-minute Codex thread as the acting research agent.
   - Local check: `npx @openai/codex@0.39.0 --version` works.

4. Cloud/GPU path
   - Needed later for PaperBench and some CORE-Bench/PaperBench reproductions.
   - Not needed for the first FIRE-Bench setup pass.

Optional later:

5. Non-Codex model API keys
   - `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, and `OPENAI_API_KEY` are useful only for comparing against other agents/models or for benchmark judge configurations that cannot be routed through Codex.

Tool note:

- The local `hf` command exists, but version `0.34.3` exposes `download` and auth commands, not the newer `hf datasets` subcommands. Dataset metadata can still be read with the Hugging Face Dataset Viewer API.

6. Calendar/Gmail access
   - Useful for nudging Miles when a blocker appears or contacting benchmark authors/researchers.
