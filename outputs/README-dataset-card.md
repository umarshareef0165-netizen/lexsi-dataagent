# Dataset Card: Lexsi DataAgent trajectories + eval logs

## Dataset Summary
The full recorded evidence for the Lexsi DataAgent (Track 3, Problem
Statement 6): 24 real AgentTune trajectories (12 tasks × base + improved
agent) plus the complete AgentTune/AuditKIT evaluation logs. Everything was
produced by running the public repo's own harness on a tiny synthetic
SQLite shop database (5 customers, 4 products, 10 orders; invented data).

## Files
- `trajectories.jsonl` — 24 rows. Each row: `trajectory_id`, `task`,
  `steps[]` (state/action/observation/thought/reward), `final_response`,
  `reward`, `metadata`. Real AgentTune `Trajectory` records.
- `eval_results.json` — AgentTune before/after: base 0/12 task accuracy,
  tool-call accuracy 0.0; improved 12/12, tool-call accuracy 1.000.
  Tool-call F1 0.800 → 1.000. Per-task SQL + answers included.
- `auditkit_eval.json` — AuditKIT `AgentEvalRunner` recorded-mode scores
  for all 24 cases: tool-call F1 (name), validity, redundant calls,
  loop detection, permission checks; trace coverage "full".

## What the numbers mean (honest reading)
These scores compare two DETERMINISTIC agent variants (naive tool use vs
structured tool use), not a base model vs a fine-tuned model. The improved
agent wins on accuracy, NOT on efficiency (3.00 vs 2.00 calls/task,
~72.6 vs ~39.2 approx. tokens/task). The fine-tuned-model comparison is a
separate experiment (see the model repo + `lexsi-dataagent-model-eval.json`
in the SFT dataset).

## License
MIT (same as the project repo).

## Reproducibility
Re-run from the public repo: `python -m pytest tests/` and the eval
harness in `prototype/eval.py`. Demo video:
https://youtu.be/yXklaZhqHs0
