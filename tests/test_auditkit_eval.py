"""Tests for the real AuditKIT + AgentTune integration (prototype/auditkit_eval.py).

These tests check the integration itself, not the agent logic (covered by
test_agent.py):
- every run is recorded as a real AgentTune Trajectory (schema fields,
  one Step per tool call, reward = harness correctness);
- the real AuditKIT recorded-mode run over those trajectories agrees with
  the existing harness (improved 12/12 success, base 0/12) and reports the
  expected tool-call F1 gap.

The AuditKIT test takes a few seconds (library import); that is the real
library being exercised, not a mock.
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "prototype"))
from auditkit_eval import build_trajectories, run_auditkit, write_trajectories  # noqa: E402
from eval import evaluate  # noqa: E402
from tasks import TASKS  # noqa: E402


class TestAuditKitEval(unittest.TestCase):
    def test_trajectories_are_agenttune_records(self):
        records = build_trajectories()
        self.assertEqual(len(records), 2 * len(TASKS))
        ids = [r["trajectory_id"] for r in records]
        expected_ids = [f"{t['id']}-{v}" for t in TASKS for v in ("base", "improved")]
        self.assertEqual(ids, expected_ids)
        for rec in records:
            # AgentTune Trajectory.to_dict() schema.
            self.assertIn("task", rec)
            self.assertIn("steps", rec)
            self.assertIn("final_response", rec)
            self.assertIn("reward", rec)
            self.assertIn("trajectory_id", rec)
            self.assertTrue(rec["steps"])
            for step in rec["steps"]:
                self.assertIn("name", step["action"])
                self.assertIn("arguments", step["action"])
                self.assertIn("observation", step)
            self.assertIn(rec["reward"], (0.0, 1.0))
            # Reward matches the harness correctness rule for this task.
            task = next(t for t in TASKS if t["id"] == rec["metadata"]["task_id"])
            correct = all(s in rec["final_response"] for s in task["must_contain"])
            self.assertEqual(rec["reward"], 1.0 if correct else 0.0)

    def test_auditkit_agrees_with_harness(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "trajectories.jsonl")
            write_trajectories(path)
            with open(path, encoding="utf-8") as f:
                self.assertEqual(sum(1 for _ in f), 24)
            out = run_auditkit(path)
        self.assertEqual(out["mode"], "recorded")
        self.assertEqual(out["n_cases"], 24)
        verdicts = {}
        f1 = {}
        for row in out["rows"]:
            self.assertEqual(row["status"], "completed")
            self.assertEqual(row["errors"], [])
            variant = row["case_id"].rsplit("-", 1)[1]
            verdicts.setdefault(variant, []).append(row["outcome"]["verdict"])
            f1.setdefault(variant, set()).add(
                str(row["diagnostics"]["tool_call_f1_name"]["value"]))
            # Full trace coverage: names, arguments and results all observed.
            self.assertEqual(row["coverage_label"], "full")
        self.assertEqual(verdicts["improved"], ["success"] * 12)
        self.assertEqual(verdicts["base"], ["failure"] * 12)
        self.assertEqual(f1["improved"], {"1.0"})
        self.assertEqual(f1["base"], {"0.8"})
        # Cross-check against the harness numbers themselves.
        self.assertEqual(evaluate("base")["task_accuracy"], 0.0)
        self.assertEqual(evaluate("improved")["task_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
