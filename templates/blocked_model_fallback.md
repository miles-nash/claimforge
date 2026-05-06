# Blocked Model Fallback Template

Use this when the original task requires external model calls, gated weights, or API credentials that are not available inside the Codex run.

## Objective

Convert an access-blocked model task into durable evidence without pretending the original claim was tested.

## Required Outputs

- `access_check.json`
- `data_audit.json`
- `prompt_manifest.jsonl` or equivalent dry-run request table
- `prompt_preview.json`
- `run_summary.json`
- optional runnable script for the eventual model run

## Procedure

1. State the ideal experiment.
   - Name the model/provider/weights required.
   - Name the metric or comparison that would answer the original task.

2. Check access without printing secrets.
   - Report whether required environment variables are set.
   - Try imports for required SDKs.
   - Record package/import errors verbatim.

3. Audit local data.
   - Count rows, fields, splits, labels, and missing values.
   - Identify possible leakage or post-outcome information.
   - Record sensitive attributes and any redaction rule.

4. Build the dry-run request table.
   - Include stable IDs.
   - Include all manipulated variables.
   - Include the exact prompt or input payload.
   - Keep scout runs below 1000 calls per model.

5. Write a preview.
   - Save the first 10-20 requests with prompts truncated enough for review.
   - Include enough metadata to inspect whether the manipulation is valid.

6. Gate model execution.
   - If access is missing, do not attempt paid or external calls.
   - If access exists, run the smallest end-to-end sample first.

7. Summarize conservatively.
   - Mark the original model claim as blocked unless calls actually ran.
   - Separate measured local evidence from inferred implications.
   - Name the exact unblocker for a full run.

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

