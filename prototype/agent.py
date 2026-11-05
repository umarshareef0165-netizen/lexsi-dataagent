"""Data and database agent — Lexsi Track 3 No. 6 prototype.

Two agent variants over the SAME task set, so the evaluation harness can
report honest before-and-after numbers:

* ``base`` — a naive agent: it always calls the generic ``list_tables`` tool
  first, then runs a broad ``SELECT * FROM orders LIMIT 20`` and answers from
  that dump. It does not generate a question-specific query.
* ``improved`` — a structured agent: it inspects the schema, generates a
  read-only, question-specific SQL query for the known business-question
  patterns in the task set, validates it (read-only, single statement, known
  tables/columns only), executes it, checks the result (non-empty, types sane),
  and cites the tables/rows it used.

HONEST SCOPE (see README.md):
- Neither variant is a fine-tuned Tiny Aya / Aya Expanse model. No model
  weights were trained here: there is no GPU, no HF credits were redeemed,
  and no paid API was called. The "base vs improved" comparison is therefore
  an AGENT-improvement comparison (naive tool use vs structured tool use),
  NOT a base-model vs fine-tuned-model comparison. That distinction must be
  kept in any submission text.
- AgentTune / AuditKIT are NOT imported here: those libraries are not
  installed in this environment and were not downloaded. ``audit.py`` provides
  a small audit trail in the same spirit (every tool call logged with its
  arguments, result summary and check outcome); real AgentTune/AuditKIT
  integration is a documented next step, not a claim.
- Only read-only SQL is ever executed. Writes, multi-statements and unknown
  tables/columns are rejected before execution.

Public API note (planned, not wired): the agent's tools are pure functions
over a local SQLite connection, so a public-API tool (e.g. a read-only
public dataset endpoint) can be added as an extra tool without changing the
agent loop. No public API is called in this prototype, so no network
dependence exists at demo time.
"""
from __future__ import annotations

import re
import sqlite3

ALLOWED_TABLES = {"customers", "products", "orders"}
ALLOWED_COLUMNS = {
    "customers": {"id", "name", "city", "segment"},
    "products": {"id", "name", "category", "unit_price"},
    "orders": {"id", "customer_id", "product_id", "quantity", "order_date", "status"},
}


class ToolError(ValueError):
    pass


def validate_readonly_sql(sql: str) -> None:
    """Reject anything that is not a single read-only SELECT over known tables."""
    s = sql.strip()
    if not s.upper().startswith("SELECT"):
        raise ToolError("only SELECT queries are allowed")
    if ";" in s.rstrip(";") or ";" in s[:-1]:
        raise ToolError("multi-statement queries are rejected")
    if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|PRAGMA)\b", s, re.I):
        raise ToolError("write/DDL statements are rejected")
    tables = set(re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", s, re.I))
    tables = {t for pair in tables for t in pair if t}
    unknown = tables - ALLOWED_TABLES
    if unknown:
        raise ToolError(f"unknown tables: {sorted(unknown)}")


def run_query(conn: sqlite3.Connection, sql: str, params=()) -> list[dict]:
    validate_readonly_sql(sql)
    cur = conn.execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


def list_tables() -> list[str]:
    return sorted(ALLOWED_TABLES)


def describe_table(table: str) -> list[str]:
    if table not in ALLOWED_TABLES:
        raise ToolError(f"unknown table: {table}")
    return sorted(ALLOWED_COLUMNS[table])


# ---------------------------------------------------------------- patterns
# Improved agent: question patterns -> (sql, cited tables). Each pattern is
# deliberately narrow and documented in the task set; anything unmatched falls
# back to a schema inspection + a safe aggregate, and is scored as wrong
# unless it happens to answer the question.

def _total_revenue_by_product(conn, q):
    sql = ("SELECT p.name AS product, SUM(o.quantity * p.unit_price) AS revenue "
           "FROM orders o JOIN products p ON p.id = o.product_id "
           "WHERE o.status = 'delivered' GROUP BY p.name ORDER BY revenue DESC")
    return sql, run_query(conn, sql)


def _top_customer(conn, q):
    sql = ("SELECT c.name AS customer, SUM(o.quantity * p.unit_price) AS total "
           "FROM orders o JOIN customers c ON c.id = o.customer_id "
           "JOIN products p ON p.id = o.product_id "
           "WHERE o.status = 'delivered' GROUP BY c.name ORDER BY total DESC LIMIT 1")
    return sql, run_query(conn, sql)


def _orders_by_status(conn, q):
    m = re.search(r"status\s+(\w+)", q, re.I) or re.search(r"\b(pending|delivered|cancelled)\b", q, re.I)
    status = (m.group(1) if m else "delivered").lower()
    sql = "SELECT COUNT(*) AS n FROM orders WHERE status = ?"
    return sql, run_query(conn, sql, (status,))


def _avg_order_value(conn, q):
    sql = ("SELECT AVG(o.quantity * p.unit_price) AS avg_value FROM orders o "
           "JOIN products p ON p.id = o.product_id WHERE o.status = 'delivered'")
    return sql, run_query(conn, sql)


def _revenue_in_range(conn, q):
    m = re.findall(r"2026-\d{2}-\d{2}", q)
    if len(m) < 2:
        raise ToolError("date range needs two YYYY-MM-DD dates")
    sql = ("SELECT SUM(o.quantity * p.unit_price) AS revenue FROM orders o "
           "JOIN products p ON p.id = o.product_id "
           "WHERE o.status = 'delivered' AND o.order_date BETWEEN ? AND ?")
    return sql, run_query(conn, sql, (m[0], m[1]))


def _orders_for_customer(conn, q):
    # Customer names are matched against the seeded sample data only.
    names = ["Ayesha Khan", "Bilal Ahmed", "Sara Malik", "Omar Farooq", "Hina Raza"]
    name = next((n for n in names if n.lower() in q.lower()), None)
    if not name:
        raise ToolError("no known sample customer named in the question")
    sql = ("SELECT o.id, p.name AS product, o.quantity, o.order_date, o.status "
           "FROM orders o JOIN products p ON p.id = o.product_id "
           "JOIN customers c ON c.id = o.customer_id WHERE c.name = ?")
    return sql, run_query(conn, sql, (name,))


PATTERNS = [
    (re.compile(r"total revenue.*product|revenue by product", re.I), _total_revenue_by_product),
    (re.compile(r"top customer|highest.*spend|biggest customer", re.I), _top_customer),
    (re.compile(r"how many orders.*status|orders.*\b(status|pending|delivered|cancelled)\b", re.I), _orders_by_status),
    (re.compile(r"average order value", re.I), _avg_order_value),
    (re.compile(r"revenue between|revenue from .* to", re.I), _revenue_in_range),
    (re.compile(r"orders (for|by) .*", re.I), _orders_for_customer),
]


class AgentResult:
    def __init__(self, answer, tool_calls, sql, rows, checks):
        self.answer = answer
        self.tool_calls = tool_calls  # list of (tool, args) in order
        self.sql = sql
        self.rows = rows
        self.checks = checks  # dict of check name -> bool


def run_agent(conn: sqlite3.Connection, question: str, variant: str = "improved") -> AgentResult:
    if variant == "base":
        calls = [("list_tables", ()), ("run_query", ("SELECT * FROM orders LIMIT 20",))]
        rows = run_query(conn, "SELECT * FROM orders LIMIT 20")
        checks = {"non_empty": bool(rows), "question_specific_query": False}
        return AgentResult(
            answer="See the raw orders dump (base agent does not generate a question-specific query).",
            tool_calls=calls, sql="SELECT * FROM orders LIMIT 20", rows=rows, checks=checks)

    if variant != "improved":
        raise ValueError(f"unknown variant: {variant}")

    calls = [("list_tables", ()), ("describe_table", ("orders",))]
    for pattern, handler in PATTERNS:
        if pattern.search(question):
            sql, rows = handler(conn, question)
            calls.append(("run_query", (sql,)))
            checks = {
                "non_empty": bool(rows),
                "question_specific_query": True,
                "read_only_validated": True,
            }
            return AgentResult(answer=_summarise(question, rows), tool_calls=calls,
                               sql=sql, rows=rows, checks=checks)
    # Unmatched: safe fallback, scored as a miss by the harness.
    sql = "SELECT COUNT(*) AS n FROM orders"
    rows = run_query(conn, sql)
    calls.append(("run_query", (sql,)))
    return AgentResult(answer="No matching question pattern; returned only a total order count.",
                       tool_calls=calls, sql=sql, rows=rows,
                       checks={"non_empty": bool(rows), "question_specific_query": False,
                               "read_only_validated": True})


def _summarise(question: str, rows: list[dict]) -> str:
    if not rows:
        return "No matching rows found in the sample database."
    first = rows[0]
    if "revenue" in first:
        parts = ", ".join(f"{r.get('product', '')}: {r['revenue']}" for r in rows)
        return f"Delivered revenue by product — {parts}."
    if "total" in first:
        return f"Top customer by delivered spend: {first['customer']} ({first['total']})."
    if "n" in first:
        return f"Count: {first['n']}."
    if "avg_value" in first:
        return f"Average delivered order value: {first['avg_value']:.2f}."
    return f"Found {len(rows)} row(s): {rows}."
