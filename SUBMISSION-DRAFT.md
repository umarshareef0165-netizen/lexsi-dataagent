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
Python 3.12 standard library only (sqlite3, http.server, unittest). No paid
APIs, no external services, no credentials. Sample data is fully synthetic.

## Key features
- Read-only SQL validation: writes, multi-statements and unknown tables are
  rejected before execution (tested).
- Question-specific queries with cited tables/rows, shown in the demo UI.
- Audit trail: every tool call logged (question, variant, tool, args, checks).
- Evaluation harness: task accuracy, tool-call accuracy, syntax correctness,
  efficiency (calls/task, approximate tokens/task), safety/robustness.

## Measured results (honest wording — use exactly this)
On a 12-task synthetic set, the structured agent scored task accuracy 1.000
and tool-call accuracy 1.000, vs 0.000 / 0.000 for the naive agent; syntax
correctness 1.000 for both. The structured agent used more calls (3.00 vs
2.00) and more approximate tokens (~72.6 vs ~39.2) per task, so no efficiency
win is claimed on this run. These are prototype measurements on synthetic
data, not a fine-tuned-model evaluation.

## MUST-ADD before any real submission (do not submit without these)
- State plainly that no Tiny Aya fine-tuning has been done yet, and that
  AgentTune/AuditKIT library integration is planned, not present — OR complete
  those steps first and replace this paragraph with the real numbers.
- Public repo URL, demo video URL, and the submission form's exact fields
  (form link had not arrived at last check).
- Umar's separate final approval.
