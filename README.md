# DataAgent — Lexsi Track 3 No. 6 (Data and Database Agents)

Solo project for Umar Shareef, Lexsi AI Safety and Alignment Hackathon,
Agentic Fine-tuning track. First-stage deadline Nov 14, 2026, 11:59 PM AoE
(Nov 15, 3:59 AM PT).

## What it does
Ask a small business question in plain language. The agent inspects the
schema, generates a read-only SQL query, validates it, runs it against a
local sample SQLite database, checks the result, and shows the question, the
generated query, the checked result, and the cited source tables.

## Run it (Python 3.12; core prototype is standard library only — nothing to install, nothing paid)
```bash
cd ~/workspace/lexsi-hackathon
python3 -m unittest discover -s tests -v   # 10/10 tests pass
python3 prototype/eval.py                  # base vs improved on 12 tasks
python3 prototype/server.py                # demo UI at http://127.0.0.1:8000
```
The AuditKIT / AgentTune evaluation needs the project venv (auditkit 1.1.3,
agenttune 1.1.3, torch, transformers, trl — installed locally, no paid API,
no network call at run time):
```bash
.venv/bin/python -m prototype.auditkit_eval  # writes outputs/trajectories.jsonl
                                             # and outputs/auditkit_eval.json
```

## Verified results
- Unit tests: **10/10 OK** (8 agent tests + 2 AuditKIT-integration tests).
- Server smoke test: `/health` → `{"ok": true}`; top-customer query returns
  Bilal Ahmed, 980.0, with the generated SQL and checks shown.
- Evaluation (12 tasks, same set for both variants):
  - base: task accuracy 0.000, tool-call accuracy 0.000
  - improved: task accuracy 1.000, tool-call accuracy 1.000, syntax 1.000
  - improved uses MORE calls (3.00 vs 2.00) and MORE approximate tokens
    (~72.6 vs ~39.2) per task — no efficiency win is claimed on this run.
- Real AuditKIT + AgentTune evaluation (`prototype/auditkit_eval.py`,
  recorded mode, no live model call): every run is exported as a genuine
  AgentTune `Trajectory` (`outputs/trajectories.jsonl`, 24 records) and
  scored by AuditKIT's `AgentEvalRunner` (`outputs/auditkit_eval.json`):
  verified success 12/24 — all 12 improved, 0/12 base; tool-call F1 (name)
  1.000 improved vs 0.800 base; tool-call validity 1.000 and tool
  permission 1.000 for both; no redundant calls; no loops detected; trace
  coverage "full" on all 24 cases. These are scores of RECORDED
  deterministic trajectories, not of a fine-tuned model.

## Honest limits — read before submitting anything
1. **No model was fine-tuned.** No Tiny Aya / Aya Expanse training ran here:
   no GPU, no Hugging Face credits redeemed (that needs a linked payment
   method, which was NOT linked — that decision is Umar's alone). "Base vs
   improved" here means naive agent vs structured agent, NOT base model vs
   fine-tuned model. Any submission text must keep that distinction.
2. **AgentTune / AuditKIT ARE integrated — for evaluation, not training.**
   `prototype/auditkit_eval.py` records every run as a real AgentTune
   `Trajectory` and scores the recorded trajectories with the real AuditKIT
   `AgentEvalRunner` (recorded mode). `prototype/audit.py` remains a local
   JSONL audit log alongside it. Neither library trained a model: there was
   no fine-tuning run, no GPU training, no HF credits redeemed. Library
   usage is not a fine-tuning claim.
3. **No paid API, no network call, no credentials.** The prototype runs
   fully offline on invented sample data (5 customers, 4 products, 10 orders).
   No real business data is used or claimed.
4. **The demo UI is not Next.js.** It is Python stdlib http.server serving
   HTML in a Next.js-style layout. A real Next.js frontend is a next step.
5. **The task set is narrow.** 12 tasks, 6 question patterns. Unseen,
   arbitrary questions will fall back to a total-count answer and be scored
   as misses — that is by design in the harness, and a larger held-out set
   is needed for a stronger submission.
6. **Nothing submitted, nothing paid, no score or win claimed.** The
   submission form link had not arrived at last check; final submission
   needs Umar's separate approval.
