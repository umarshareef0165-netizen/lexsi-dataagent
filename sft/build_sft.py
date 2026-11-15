"""Build the Lexsi DataAgent SFT dataset (train + held-out eval) from the
verified prototype.

Every training example's SQL is EXECUTED against the seeded SQLite database
and its result checked before the example is kept. Nothing is invented:
questions come from the prototype's own task patterns, SQL comes from the
improved agent's verified templates with literal values substituted, and
expected answers are computed from the database itself.

Design (honest split):
- TRAIN: expanded variants only — different date ranges, other customers,
  and paraphrases. The 12 original eval questions appear NOWHERE in train.
- EVAL: the 12 original tasks verbatim (T01..T12), with the improved
  agent's SQL as reference and the tasks.py must_contain checks.
So the eval measures generalisation to unseen wordings/values within the
same six patterns — not memorisation of the eval set.

Run:  python3 sft/build_sft.py   (stdlib only; run from lexsi-hackathon/)
Outputs: sft/lexsi-dataagent-sft-train.jsonl, sft/lexsi-dataagent-sft-eval.json
"""
from __future__ import annotations

import itertools
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from prototype import agent as AG  # noqa: E402
from prototype import db as DB  # noqa: E402
from prototype.tasks import TASKS  # noqa: E402

SCHEMA_TEXT = (
    "customers(id, name, city, segment)\n"
    "products(id, name, category, unit_price)\n"
    "orders(id, customer_id, product_id, quantity, order_date, status)"
)

PROMPT_TEMPLATE = (
    "Write a read-only SQL query for the question below using this schema.\n\n"
    "Schema:\n{schema}\n\nQuestion: {question}\nSQL:"
)


def make_prompt(question: str) -> str:
    return PROMPT_TEMPLATE.format(schema=SCHEMA_TEXT, question=question)


# SQL templates from the improved agent (verified in eval_results.json),
# with literal values substituted for training.
SQL_REVENUE_BY_PRODUCT = (
    "SELECT p.name AS product, SUM(o.quantity * p.unit_price) AS revenue "
    "FROM orders o JOIN products p ON p.id = o.product_id "
    "WHERE o.status = 'delivered' GROUP BY p.name ORDER BY revenue DESC"
)
SQL_TOP_CUSTOMER = (
    "SELECT c.name AS customer, SUM(o.quantity * p.unit_price) AS total "
    "FROM orders o JOIN customers c ON c.id = o.customer_id "
    "JOIN products p ON p.id = o.product_id "
    "WHERE o.status = 'delivered' GROUP BY c.name ORDER BY total DESC LIMIT 1"
)
SQL_AVG_VALUE = (
    "SELECT AVG(o.quantity * p.unit_price) AS avg_value FROM orders o "
    "JOIN products p ON p.id = o.product_id WHERE o.status = 'delivered'"
)


def sql_count_status(status: str) -> str:
    return f"SELECT COUNT(*) AS n FROM orders WHERE status = '{status}'"


def sql_revenue_range(d1: str, d2: str) -> str:
    return (
        "SELECT SUM(o.quantity * p.unit_price) AS revenue FROM orders o "
        "JOIN products p ON p.id = o.product_id "
        f"WHERE o.status = 'delivered' AND o.order_date BETWEEN '{d1}' AND '{d2}'"
    )


def sql_orders_for_customer(name: str) -> str:
    return (
        "SELECT o.id, p.name AS product, o.quantity, o.order_date, o.status "
        "FROM orders o JOIN products p ON p.id = o.product_id "
        "JOIN customers c ON c.id = o.customer_id "
        f"WHERE c.name = '{name}'"
    )


def verify_and_add(rows: list, conn, question: str, sql: str, pattern: str,
                   source: str) -> None:
    """Execute the SQL; keep the example only if it runs and returns rows
    (or a non-null aggregate) — otherwise raise so a bad example is loud."""
    AG.validate_readonly_sql(sql)
    out = AG.run_query(conn, sql)
    assert out, f"empty result for {question!r} / {sql!r}"
    first = out[0]
    if "revenue" in first:
        assert first["revenue"] is not None, f"null revenue: {question!r}"
    rows.append({
        "prompt": make_prompt(question),
        "completion": " " + sql,
        "question": question,
        "sql": sql,
        "pattern": pattern,
        "source": source,
        "verified_by_execution": True,
    })


def main() -> None:
    conn = DB.open_db()
    train: list[dict] = []

    # --- 1. Date-range variants (exclude the two eval ranges) ----------
    eval_ranges = {("2026-10-05", "2026-10-09"), ("2026-10-10", "2026-10-13")}
    dates = sorted({o[4] for o in DB.ORDERS})
    ranges = [(a, b) for a, b in itertools.combinations(dates, 2)
              if (a, b) not in eval_ranges]
    # Spread across short, medium and long spans; take 12.
    picked = [ranges[i] for i in (0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33)
              if i < len(ranges)]
    for d1, d2 in picked:
        q = (f"What is the revenue between {d1} and {d2} "
             "for delivered orders?")
        verify_and_add(train, conn, q, sql_revenue_range(d1, d2),
                       "revenue_in_range", "expanded-date-range")

    # --- 2. Other customers (eval uses Bilal Ahmed + Ayesha Khan) ------
    for name in ("Sara Malik", "Omar Farooq", "Hina Raza"):
        q = f"List orders for {name}."
        verify_and_add(train, conn, q, sql_orders_for_customer(name),
                       "orders_for_customer", "expanded-customer")

    # --- 3. Paraphrases of the fixed-answer patterns -------------------
    paraphrases = [
        ("Show delivered revenue grouped by product.",
         SQL_REVENUE_BY_PRODUCT, "revenue_by_product"),
        ("How much revenue did each product bring in from delivered orders?",
         SQL_REVENUE_BY_PRODUCT, "revenue_by_product"),
        ("Break down delivered revenue by product.",
         SQL_REVENUE_BY_PRODUCT, "revenue_by_product"),
        ("Which customer spent the most on delivered orders?",
         SQL_TOP_CUSTOMER, "top_customer"),
        ("Who is our biggest customer by delivered revenue?",
         SQL_TOP_CUSTOMER, "top_customer"),
        ("Name the customer with the highest delivered spend.",
         SQL_TOP_CUSTOMER, "top_customer"),
        ("What is the mean value of a delivered order?",
         SQL_AVG_VALUE, "avg_order_value"),
        ("On average, how much is a delivered order worth?",
         SQL_AVG_VALUE, "avg_order_value"),
        ("Compute the average delivered order value.",
         SQL_AVG_VALUE, "avg_order_value"),
        ("How many pending orders are there?",
         sql_count_status("pending"), "count_by_status"),
        ("Count the delivered orders.",
         sql_count_status("delivered"), "count_by_status"),
    ]
    for q, sql, pattern in paraphrases:
        verify_and_add(train, conn, q, sql, pattern, "paraphrase")

    # --- 4. Eval set: the 12 original tasks verbatim -------------------
    # Reference SQL = improved agent's SQL with literals substituted.
    ref_sql = {}
    improved = json.loads(
        (HERE / "outputs" / "eval_results.json").read_text())["improved"]
    for per in improved["per_task"]:
        ref_sql[per["id"]] = per["sql"]
    # Substitute the parameters the agent binds at runtime.
    subs = {
        "T03": ("?", "'pending'"), "T04": ("?", "'delivered'"),
        "T05": ("?", "'cancelled'"),
        "T07": (("?", "?"), ("'2026-10-05'", "'2026-10-09'")),
        "T11": (("?", "?"), ("'2026-10-10'", "'2026-10-13'")),
        "T08": ("?", "'Bilal Ahmed'"), "T09": ("?", "'Ayesha Khan'"),
    }
    eval_rows = []
    for t in TASKS:
        sql = ref_sql[t["id"]]
        if t["id"] in subs:
            old, new = subs[t["id"]]
            if isinstance(old, tuple):
                for o, n in zip(old, new):
                    sql = sql.replace(o, n, 1)
            else:
                sql = sql.replace(old, new, 1)
        AG.validate_readonly_sql(sql)
        out = AG.run_query(conn, sql)
        assert out, f"eval {t['id']} produced no rows"
        eval_rows.append({
            "id": t["id"],
            "prompt": make_prompt(t["question"]),
            "question": t["question"],
            "reference_sql": sql,
            "expected": t["expected"],
            "must_contain": t["must_contain"],
        })

    # --- 5. Leakage check: no eval question verbatim in train ----------
    eval_qs = {r["question"] for r in eval_rows}
    leaked = [r for r in train if r["question"] in eval_qs]
    assert not leaked, f"LEAKED eval questions in train: {leaked}"

    out_dir = HERE / "sft"
    out_dir.mkdir(exist_ok=True)
    train_path = out_dir / "lexsi-dataagent-sft-train.jsonl"
    eval_path = out_dir / "lexsi-dataagent-sft-eval.json"
    train_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in train))
    eval_path.write_text(json.dumps(eval_rows, indent=2, ensure_ascii=False))

    from collections import Counter
    print(f"train examples: {len(train)}")
    print("by pattern:", dict(Counter(r['pattern'] for r in train)))
    print(f"eval tasks: {len(eval_rows)} (T01..T12, verbatim)")
    print(f"leak check: 0 eval questions in train")
    print(f"wrote {train_path}")
    print(f"wrote {eval_path}")


if __name__ == "__main__":
    main()
