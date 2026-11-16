# Lexsi DataAgent — demo video notes

Video: `demo-video/lexsi-demo.mp4` — **2:01 (120.9s), 1280×720, H.264 + AAC narration** (max 3:00).
Captions: `demo-video/captions.srt`. Raw screen recording: `demo-video/lexsi-demo-raw.mp4` (118.9s).
Narration segments: `demo-video/narration/seg1–seg6.mp3` (TTS voiceover; the video shows the REAL agent running live).

## What the video shows (all real, nothing staged)
1. **0:00–0:12 — The problem.** DataAgent UI (Lexsi Track 3, Statement 6): business questions over a
   sample SQLite database. Sample data only, no real business data.
2. **0:12–0:38 — Improved agent, live.** Question "Who is the top customer by delivered spend?" →
   generated read-only SQL (JOIN orders/customers/products, delivered only) → answer
   "Bilal Ahmed (980.0)" with cited rows and all checks true (non-empty, question-specific query,
   read-only validated).
3. **0:38–1:01 — Base agent, same question (before).** Generic `SELECT * FROM orders LIMIT 20` dump,
   answer "See the raw orders dump (base agent does not generate a question-specific query)."
4. **1:01–1:42 — Verified before/after numbers** (from `outputs/auditkit_eval.json`, re-run live
   2026-11-06): 12 tasks each variant, recorded as real AgentTune Trajectories, scored by the real
   AuditKIT AgentEvalRunner (recorded mode).
5. **1:42–2:01 — Honest scope + repo.** `github.com/umarshareef0165-netizen/lexsi-dataagent`.

## Verified metrics (re-run live 2026-11-06; do not alter)
| Metric (12 tasks) | Base agent | Improved agent |
|---|---|---|
| Tasks answered correctly | 0 / 12 | **12 / 12** |
| Task accuracy | 0.000 | **1.000** |
| Tool-call accuracy | 0.000 | **1.000** |
| Tool-call F1 | 0.800 | **1.000** |
| Tool-call validity / permission | 1.000 | 1.000 |
| Unit tests | 10 / 10 pass (`python -m unittest discover -s tests`) |

Evidence files: `outputs/trajectories.jsonl` (24 records), `outputs/auditkit_eval.json` (24 cases:
base 12/12 failure, improved 12/12 success), `outputs/eval_results.json`.

## Honest scope (must stay in any submission text)
- This is an **agent** comparison (naive tool use vs structured tool use) scored on recorded
  trajectories. **No fine-tuning was done**: no Tiny Aya / Aya Expanse weights were trained, no GPU,
  no Hugging Face credits redeemed, no paid API called.
- The AuditKIT run is in recorded mode; no live model call and no judge scorer was used.

## Remaining before first-stage submission (deadline Nov 14, 2026, 23:59 AoE)
- [ ] **Fine-tuning decision — Umar's call.** Tiny Aya / Aya Expanse fine-tuning needs Hugging Face
      credits, which need a payment method linked to HF. NOT decided; do not decide for him.
- [ ] **Submission form link** — not arrived yet (promised a day or two before the deadline).
- [ ] **Upload video to YouTube** (browser step — NOT done here) and **final approval from Umar**
      before any submission. Nothing has been submitted.
