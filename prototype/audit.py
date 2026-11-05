"""Minimal audit trail (AuditKIT-spirit, NOT the AuditKIT library).

Every tool call is appended as one JSON line: question, variant, tool, args,
row count, checks, and a short answer excerpt. This is the audit evidence
the evaluation harness and any submission demo can show. Real AuditKIT
integration (importing the library, running its checks on a model) is a
documented next step, not something this file claims.
"""
import json
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit_log.jsonl")


def log(question: str, variant: str, result, path: str = LOG_PATH) -> None:
    entry = {
        "question": question,
        "variant": variant,
        "tool_calls": [{"tool": t, "args": [str(a) for a in args]} for t, args in result.tool_calls],
        "sql": result.sql,
        "row_count": len(result.rows),
        "checks": result.checks,
        "answer_excerpt": result.answer[:200],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
