"""Evaluation task set: 12 small, well-defined business questions.

Each task carries the exact expected answer computed from the seeded sample
data, plus the expected tool behaviour (a question-specific read-only query
over the right tables). The harness scores BOTH variants on the SAME tasks,
so before/after numbers are comparable. Tasks are deliberately narrow: the
point is measurable tool-use reliability, not open-ended chat.
"""
# expected values computed from db.py seed data (delivered orders only
# where the question says delivered / revenue).
TASKS = [
    {"id": "T01", "question": "What is the total revenue by product for delivered orders?",
     "expected": "Office Chair: 960.0, Desk Lamp: 350.0, Laptop Stand: 135.0, Notebook Pack: 240.0",
     "must_contain": ["Office Chair", "960"]},
    {"id": "T02", "question": "Who is the top customer by delivered spend?",
     "expected": "Bilal Ahmed (980.0: 600 + 140 + 240)",
     "must_contain": ["Bilal Ahmed", "980"]},
    {"id": "T03", "question": "How many orders have status pending?",
     "expected": "2", "must_contain": ["Count: 2"]},
    {"id": "T04", "question": "How many orders have status delivered?",
     "expected": "7", "must_contain": ["Count: 7"]},
    {"id": "T05", "question": "How many orders have status cancelled?",
     "expected": "1", "must_contain": ["Count: 1"]},
    {"id": "T06", "question": "What is the average order value for delivered orders?",
     "expected": "240.71", "must_contain": ["240.71"]},
    {"id": "T07", "question": "What is the revenue between 2026-10-05 and 2026-10-09 for delivered orders?",
     "expected": "1115.0 (240 + 600 + 135 + 140)",
     "must_contain": ["1115"]},
    {"id": "T08", "question": "List orders for Bilal Ahmed.",
     "expected": "3 orders (ids 2, 5, 9)",
     "must_contain": ["Notebook Pack"]},
    {"id": "T09", "question": "List orders for Ayesha Khan.",
     "expected": "3 orders (ids 1, 3, 10)",
     "must_contain": ["Office Chair"]},
    {"id": "T10", "question": "What is the total revenue by product for delivered orders?",
     "expected": "same as T01 (repeat for stability)",
     "must_contain": ["Office Chair", "960"]},
    {"id": "T11", "question": "What is the revenue between 2026-10-10 and 2026-10-13 for delivered orders?",
     "expected": "570.0 (120 + 210 + 240; cancelled order excluded)",
     "must_contain": ["570"]},
    {"id": "T12", "question": "Who is the top customer by delivered spend?",
     "expected": "same as T02 (repeat for stability)",
     "must_contain": ["Bilal Ahmed", "980"]},
]
