# Lexsi submission-fields DRAFT — NOT submitted

## Title
DataAgent: Reliable Business Answers from a Database, with Checked Queries and Cited Sources

## Problem statement (Track 3 No. 6 — Data and database agents)
Business users ask plain-language questions, but agents often guess, call the
wrong tool, or return unchecked numbers. DataAgent answers small, well-defined
business questions by querying a database, validating the query, checking the
result, and citing the sources it used — so every number can be traced.

## Solution approach
A Python agent over a local sample SQLite database: schema inspection, then a
read-only, question-specific SQL query (single statement, known tables/columns
only), execution, result checks (non-empty, types sane), and a cited answer
shown beside the generated query. A base (naive) variant and an improved
(structured) variant are evaluated on the SAME 12-task set, so the improvement
is measured, not asserted.

## Technologies used
Python 3.12 standard library only for the agent, server and harness
(sqlite3, http.server, unittest). The evaluation layer uses the real
AgentTune 1.1.3 (`Trajectory` schema) and AuditKIT 1.1.3 (`AgentEvalRunner`,
recorded mode) libraries, installed locally in the project venv. No paid
APIs, no external services, no credentials. Sample data is fully synthetic.

## Key features
- Read-only SQL validation: writes, multi-statements and unknown tables are
  rejected before execution (tested).
- Question-specific queries with cited tables/rows, shown in the demo UI.
- Audit trail: every tool call logged (question, variant, tool, args, checks).
- AgentTune trajectories: every run is exported as a real AgentTune
  `Trajectory` record (one Step per tool call, observation = returned rows,
  reward = task correctness) in `outputs/trajectories.jsonl`.
- AuditKIT scoring: the recorded trajectories are scored by AuditKIT's
  `AgentEvalRunner` in recorded mode (no live model call) — outcome oracle
  plus tool-call F1 / validity / permission / loop / redundancy diagnostics.
- Evaluation harness: task accuracy, tool-call accuracy, syntax correctness,
  efficiency (calls/task, approximate tokens/task), safety/robustness.

## Measured results (honest wording — use exactly this)
On a 12-task synthetic set, the structured agent scored task accuracy 1.000
and tool-call accuracy 1.000, vs 0.000 / 0.000 for the naive agent; syntax
correctness 1.000 for both. The structured agent used more calls (3.00 vs
2.00) and more approximate tokens (~72.6 vs ~39.2) per task, so no efficiency
win is claimed on this run. These are prototype measurements on synthetic
data, not a fine-tuned-model evaluation.

The same 24 runs (12 tasks × 2 variants), exported as AgentTune
trajectories and scored by the real AuditKIT runner in recorded mode:
verified success 12/24 — all 12 structured-agent runs, 0/12 naive runs;
tool-call F1 (name) 1.000 structured vs 0.800 naive; tool-call validity
1.000 and tool permission 1.000 for both; zero redundant calls; no loops
detected; trace coverage "full" on all 24 cases. These are scores of
recorded deterministic trajectories, not of a fine-tuned model.

## MUST-ADD before any real submission (do not submit without these)
- State plainly that no Tiny Aya fine-tuning has been done yet. AgentTune /
  AuditKIT library integration for evaluation IS done (see measured results
  above); fine-tuning itself is still not done and needs a GPU + Hugging
  Face credits decision.
- Public repo URL, demo video URL, and the submission form's exact fields
  (form link had not arrived at last check).
- Umar's separate final approval.
