# Lexsi DataAgent — Hugging Face dataset-only route (prepared 2026-11-06)

## Why dataset-only
No fine-tuned model exists (no GPU / no HF credits linked, and no payment
method is to be linked without Umar's explicit decision). The submission form
at https://hackathon.lexsi.ai/submission/ asks for HF model AND dataset
collections, but the work that exists is evaluation data, not a model.
The honest route is: dataset collection only, model collection left blank /
explained as "no fine-tuned model — baseline measurement only", matching the
abstract's own line "No fine-tuning is claimed".

## Verified local material (checked 2026-11-06, files exist, non-empty)
All under `~/workspace/lexsi-hackathon/outputs/`:

| File | Size | Contents verified |
|---|---|---|
| `trajectories.jsonl` | 44,621 bytes | 24 trajectories (12 tasks x base + improved). Each row: `trajectory_id`, `task`, `steps[]` (state/action/observation/thought/reward), `final_response`, `reward`, `metadata`. First task: "What is the total revenue by product for delivered orders?" |
| `eval_results.json` | 7,969 bytes | AgentTune before/after: base 0/12 task accuracy, tool-call accuracy 0.0; improved 12/12 (per SUBMISSION-ABSTRACT.md). Tool-call F1 0.800 -> 1.000. |
| `auditkit_eval.json` | 80,543 bytes | AuditKIT recorded mode, 24 cases (`T01-base` ...), scorers: tool_call_f1_name, tool_call_validity, redundant_tool_calls, agent_loop_detection, tool_permission. |

Source of truth for the numbers: `SUBMISSION-ABSTRACT.md` in this folder
(Track 3, Statement No. 6, repo https://github.com/umarshareef0165-netizen/lexsi-dataagent,
demo https://youtu.be/yXklaZhqHs0).

## Dataset card draft (paste into the HF dataset README)
- **Name suggestion:** `lexsi-dataagent-trajectories` (under Umar's HF account — username NOT recorded here; fill in at upload time, do not invent one)
- **Description:** 24 real AgentTune trajectories + full AgentTune/AuditKIT eval logs for Lexsi DataAgent (Track 3, Statement No. 6). Read-only SQL data agent; base agent 0/12 vs improved agent 12/12 over the same 12 tasks. No fine-tuned model is included and none is claimed.
- **Files:** `trajectories.jsonl` (24 rows), `eval_results.json`, `auditkit_eval.json`
- **Licence:** same as repo (check repo LICENSE before publishing; do not assume)
- **Reproducibility:** evals rerun from the public repo; demo video https://youtu.be/yXklaZhqHs0

## Upload steps (needs Umar's HF login — Muse cannot do this alone)
1. huggingface.co -> New Dataset -> name `lexsi-dataagent-trajectories`, Public.
2. Upload the 3 files above + the dataset-card README.
3. Copy the dataset URL; create a **dataset collection** containing it.
4. Paste the collection URL into Lexsi form pages 2-4; for the model
   collection field, leave blank or note "no fine-tuned model — dataset-only
   baseline submission" (do not invent a model link).
5. Submit the Lexsi form only with Umar's approval. Deadline Nov 14, 2026,
   23:59 AoE (= Nov 15, 03:59 PST); resubmission allowed, latest counts.

## Still open (user-only)
- Umar's **Discord username** (left blank at registration; optional on the
  form, but Lexsi reaches out there).
- HF account login to create the dataset + collection.
- Final approval before the form is submitted.
