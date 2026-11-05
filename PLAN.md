# Lexsi AI Safety Hackathon — Track 3 No. 6: Data and Database Agents

## Event (verified from official Tracks/Rules pages, read 2026-11-04)
- Lexsi AI Safety and Alignment Hackathon, Lexsi Labs + Cohere Labs + Hugging Face, online, Nov 1–21, 2026.
- Umar Shareef: registered solo, **Agentic Fine-tuning (Track 3)**.
- First-stage deadline: **Nov 14, 2026, 11:59 PM AoE = Nov 15, 3:59 AM PT**. Demo Day Nov 22 (per event pages).
- Track 3 toolkits: **AgentTune + AuditKIT** (main track toolkits). At least 2 relevant toolkits per submission in general.
- Models: **Tiny Aya (0.5B) / Aya Expanse (8B)**, unless dataset-only.
- Required metrics (Track 3): base vs post-training model, task accuracy, tool-call accuracy, syntax + argument correctness, efficiency (tool calls/task, tokens/task), safety/robustness.
- Code in a public repo; open-license/public data; no credentials or API keys committed. One submission per team; solo allowed.

## Project: DataAgent
A Python agent that answers small, well-defined business questions by querying a
database, checking the result, and citing its sources — with a UI showing the
question, the generated query, the checked result, and the cited source.

## Task set (the honest core)
12 tasks over a synthetic SQLite database (5 customers, 4 products, 10 orders,
all invented sample data — no real business data):
- revenue by product (delivered), top customer, order counts by status (×3),
  average order value, revenue in two date ranges, orders for two customers,
  plus 2 repeat tasks for stability.
- Expected answers were hand-verified against the seed data (two of my first
  arithmetic drafts were wrong — 980 not 840 for top customer, 1115/570 not
  1175/890 for date ranges — and were corrected before testing).

## Architecture
- `prototype/db.py` — seed SQLite schema + sample data.
- `prototype/agent.py` — tools (list_tables, describe_table, read-only run_query
  with validation), base vs improved agent variants, audit-friendly result object.
- `prototype/audit.py` — JSONL audit trail (AuditKIT-spirit, NOT the library).
- `prototype/eval.py` — harness on the same 12 tasks for both variants.
- `prototype/server.py` — stdlib demo UI (HTML in a Next.js-style layout; NOT a
  Next.js app — see README honesty section).
- `prototype/tasks.py` — task set + expected answers.

## Measured results (2026-11-04, verified by running the harness)
| metric | base | improved |
|---|---|---|
| task accuracy (12 tasks) | 0.000 | 1.000 |
| tool-call accuracy | 0.000 | 1.000 |
| syntax correctness | 1.000 | 1.000 |
| safety (no exception) | 1.000 | 1.000 |
| mean tool calls / task | 2.00 | 3.00 |
| mean tokens / task (chars/4 approx.) | ~39.2 | ~72.6 |

Honest reading: the improved agent wins on accuracy, NOT on efficiency —
it uses one extra tool call and roughly twice the (approximate) tokens per
task, because it inspects the schema and generates a specific query. Claiming
an efficiency win on these numbers would be false. A real efficiency story
needs the future step below (fewer, better-planned calls), not this run.

## What is NOT done (gaps, in priority order)
1. **No Tiny Aya fine-tuning was performed.** No GPU, no HF credits redeemed
   (redeeming needs a linked payment method — NOT done, needs his explicit
   decision), no model weights trained. The base-vs-improved numbers are an
   AGENT comparison, not a model fine-tuning comparison. To meet the track's
   letter, the next step is: run AgentTune on Tiny Aya over this task set
   (or a larger synthetic variant) with a real baseline, then re-run this
   harness against the fine-tuned model.
2. **No real AgentTune/AuditKIT library integration.** Neither library is
   installed here; `audit.py` is a local audit log, not AuditKIT. Next step:
   install the official toolkits (free, open-source) and wire their checks
   into the agent loop, then re-run the harness.
3. **No public API tool wired.** The design allows one, but the prototype calls
   no network service — deliberately, so the demo cannot fail on a service.
4. **No real Next.js frontend.** The demo UI is stdlib HTML in that layout.
   A Next.js app calling the same agent API is a next step.
5. **No public repo push, no demo video, no submission.** Submission form link
   is promised a day or two before the deadline and had not arrived at last
   check. Final submission needs Umar's separate approval.
6. **Task set is small and templated.** 12 tasks, 6 question patterns. A
   stronger submission needs a larger, held-out task set and unseen-question
   testing — the current patterns would not generalise to arbitrary questions,
   and that limit is stated in the submission draft.
