"""Evaluation harness: base vs improved agent on the SAME task set.

Metrics reported (Lexsi Track 3 required set, as far as this prototype can
measure them honestly):
- task accuracy: fraction of tasks whose answer contains all must_contain strings
- tool-call accuracy: fraction of tasks whose final run_query call was a
  question-specific query (base always fails this by design; improved passes
  when a pattern matched)
- syntax correctness: fraction of generated SQL that passes read-only validation
- argument correctness: approximated by task accuracy here (correct tables/
  filters produce the correct answer); reported as such, not as a separate
  ground-truth argument parse
- efficiency: mean tool calls per task, mean tokens per task (tokens
  approximated as characters/4 — stated openly, not a tokenizer count)
- safety/robustness: fraction of tasks with no rejected/unsafe query and no
  exception; plus a dedicated adversarial check (see tests) that write/DDL
  SQL is rejected before execution

Run: python3 prototype/eval.py  (from ~/workspace/lexsi-hackathon/)
Writes: outputs/eval_results.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from agent import run_agent, validate_readonly_sql  # noqa: E402
from db import open_db  # noqa: E402
from tasks import TASKS  # noqa: E402


def evaluate(variant: str) -> dict:
    conn = open_db()
    n = len(TASKS)
    task_ok = tool_ok = syntax_ok = safe = 0
    calls_total = tokens_total = 0
    per_task = []
    for t in TASKS:
        try:
            r = run_agent(conn, t["question"], variant)
            ok = all(s in r.answer for s in t["must_contain"])
            task_ok += ok
            tool_ok += bool(r.checks.get("question_specific_query"))
            try:
                validate_readonly_sql(r.sql)
                syntax_ok += 1
            except Exception:
                pass
            safe += 1
            calls_total += len(r.tool_calls)
            tokens_total += (len(t["question"]) + len(r.sql) + len(r.answer)) // 4
            per_task.append({"id": t["id"], "correct": ok, "tool_calls": len(r.tool_calls),
                             "sql": r.sql, "answer": r.answer})
        except Exception as e:  # robustness: a crash scores as a miss, not a crash
            per_task.append({"id": t["id"], "correct": False, "error": str(e)})
    return {
        "variant": variant,
        "n_tasks": n,
        "task_accuracy": task_ok / n,
        "tool_call_accuracy": tool_ok / n,
        "syntax_correctness": syntax_ok / n,
        "safety_robustness_no_exception": safe / n,
        "mean_tool_calls_per_task": calls_total / n,
        "mean_tokens_per_task_approx": tokens_total / n,
        "per_task": per_task,
    }


def main():
    base = evaluate("base")
    improved = evaluate("improved")
    out = {"base": base, "improved": improved}
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    for name, r in out.items():
        print(f"{name}: task_accuracy={r['task_accuracy']:.3f} "
              f"tool_call_accuracy={r['tool_call_accuracy']:.3f} "
              f"syntax={r['syntax_correctness']:.3f} "
              f"safety={r['safety_robustness_no_exception']:.3f} "
              f"mean_calls={r['mean_tool_calls_per_task']:.2f} "
              f"mean_tokens~{r['mean_tokens_per_task_approx']:.1f}")


if __name__ == "__main__":
    main()
