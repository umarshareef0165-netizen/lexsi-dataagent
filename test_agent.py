import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "prototype"))
from agent import ToolError, run_agent, run_query, validate_readonly_sql  # noqa: E402
from db import open_db  # noqa: E402
from eval import evaluate  # noqa: E402
from tasks import TASKS  # noqa: E402


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.conn = open_db()

    def test_improved_answers_top_customer(self):
        r = run_agent(self.conn, "Who is the top customer by delivered spend?", "improved")
        self.assertIn("Bilal Ahmed", r.answer)
        self.assertIn("980", r.answer)

    def test_improved_revenue_by_product(self):
        r = run_agent(self.conn, "What is the total revenue by product for delivered orders?", "improved")
        self.assertIn("Office Chair", r.answer)
        self.assertIn("960", r.answer)

    def test_improved_counts(self):
        self.assertIn("Count: 2", run_agent(self.conn, "How many orders have status pending?", "improved").answer)
        self.assertIn("Count: 7", run_agent(self.conn, "How many orders have status delivered?", "improved").answer)

    def test_base_does_not_answer_specifically(self):
        r = run_agent(self.conn, "Who is the top customer by delivered spend?", "base")
        self.assertFalse(r.checks["question_specific_query"])
        self.assertNotIn("Bilal Ahmed", r.answer)

    def test_write_sql_rejected(self):
        for bad in ["DELETE FROM orders", "DROP TABLE orders",
                    "SELECT * FROM orders; DELETE FROM orders",
                    "SELECT * FROM secrets"]:
            with self.assertRaises(ToolError):
                validate_readonly_sql(bad)

    def test_write_never_executes(self):
        with self.assertRaises(ToolError):
            run_query(self.conn, "UPDATE orders SET status='x'")
        n = run_query(self.conn, "SELECT COUNT(*) AS n FROM orders")[0]["n"]
        self.assertEqual(n, 10)

    def test_eval_improved_beats_base(self):
        base = evaluate("base")
        improved = evaluate("improved")
        self.assertEqual(base["n_tasks"], 12)
        self.assertEqual(improved["task_accuracy"], 1.0)
        self.assertGreater(improved["task_accuracy"], base["task_accuracy"])
        self.assertGreater(improved["tool_call_accuracy"], base["tool_call_accuracy"])
        self.assertEqual(improved["syntax_correctness"], 1.0)

    def test_all_tasks_have_expected(self):
        self.assertEqual(len(TASKS), 12)
        for t in TASKS:
            self.assertTrue(t["must_contain"])


if __name__ == "__main__":
    unittest.main()
