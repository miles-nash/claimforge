# Blocked Model Fallback Template

Use this when the task needs external model calls, gated weights, paid APIs, or packages that are unavailable inside the Codex run.

## Objective

Finish a minimal blocked-run package within the run cap. Do not pretend the original model claim was tested.

## Hard Time Budget

- First 60 seconds: write `access_check.json` and `data_audit.json`.
- Next 120 seconds: write `prompt_manifest.jsonl`, optional `scoring_manifest.jsonl`, and `prompt_preview.json`.
- Final 60 seconds: stop expanding scope, write `run_summary.json`, then give the final assistant conclusion.

## Required Outputs

- `access_check.json`
- `data_audit.json`
- `prompt_manifest.jsonl` or equivalent dry-run request table
- `prompt_preview.json`
- `run_summary.json`
- Optional only if already on track: `scoring_manifest.jsonl`, `local_baselines.json`, runnable script

## Procedure

1. Check access without printing secrets: required env vars, SDK imports, package/import errors.
2. Audit local data: rows, fields, splits, labels, missing values, leakage risks, sensitive attributes.
3. Build the dry-run table: stable IDs, manipulated variables, exact prompt/input payload, and no more than 1000 scout calls per model unless the task budget explicitly requires it.
4. Write a preview: first 10-20 requests with prompts truncated enough for review.
5. Gate execution: if access is missing, do not attempt paid/external calls; if access exists, run the smallest end-to-end sample first.
6. Summarize conservatively: separate measured local evidence from blocked claims and name the exact unblocker.

Priority rule: `run_summary.json` plus a final conclusion beats optional scripts, extra analysis, or larger manifests.

## Minimal `run_summary.json`

```json
{
  "blocked": true,
  "blocker": {
    "missing_env": ["OPENAI_API_KEY"],
    "missing_imports": ["openai"]
  },
  "n_records": 100,
  "n_requests_per_model": 600,
  "artifacts": [
    "access_check.json",
    "data_audit.json",
    "prompt_manifest.jsonl",
    "prompt_preview.json"
  ],
  "measured_claims": [
    "Local data were available and promptable."
  ],
  "blocked_claims": [
    "No frontier-model race-sensitivity estimate was measured."
  ],
  "next_unblocker": "Provide model credentials and install SDK dependencies."
}
```
