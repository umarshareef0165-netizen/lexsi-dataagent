# Lexsi DataAgent — Submission Abstract (DRAFT, under 500 words)

**Track:** 3 — Agentic Fine-tuning
**Problem statement:** No. 6 — Data and database agents
**Repo:** https://github.com/umarshareef0165-netizen/lexsi-dataagent
**Demo video:** https://youtu.be/yXklaZhqHs0

## Abstract (target ~200 words)

Lexsi DataAgent is a read-only data agent that answers small, well-defined business questions — for example, "Who is the top customer by delivered spend?" — by writing a single read-only SQL query, checking the result, and answering with cited rows. It never writes to the database and never shows an un-cited number.

We evaluated it honestly, before and after, with the track's own toolkits: AgentTune and AuditKIT. Over 12 tasks, the base agent (a generic SQL dump) succeeded on 0 of 12; the improved agent — better tool selection, a verification step, and a strict read-only rule — succeeded on 12 of 12. Tool-call F1 rose from 0.800 to 1.000; validity and permission compliance stayed at 1.000 for both. Every trajectory is recorded as a real AgentTune Trajectory object, and the full evaluation is reproducible from the public repo.

No fine-tuning is claimed: this submission measures what better tool use and verification achieve before any training, and it gives the fine-tuning stage a clean, measured baseline to improve on. The demo video shows the before/after side by side on a real question, with the real numbers on screen.

## Submission checklist status
- [x] GitHub repo (public): https://github.com/umarshareef0165-netizen/lexsi-dataagent
- [x] Demo video (public): https://youtu.be/yXklaZhqHs0
- [x] Before/after metrics: AgentTune + AuditKIT, 12 tasks, multiple metrics
- [ ] Abstract — this draft (needs Umar's approval before pasting)
- [ ] Discord username — needed (optional field on the form, but Lexsi reaches out there)
- [ ] Hugging Face model collection — OPEN QUESTION: no fine-tuned model exists (no GPU/HF credits); check whether the submission can be dataset-only (trajectories + eval logs as a public HF dataset collection)
- [ ] Hugging Face dataset collection — trajectories.jsonl + auditkit_eval.json exist locally and can be uploaded
- [ ] Write-up/article — GitHub README exists; HF article if accessible
- [ ] Form pages 2–4 — not yet enumerated (advancing past page 1 needs the email + abstract entered)

## Deadlines
- Submission: Nov 14, 2026, 23:59 AoE (= Nov 15, 03:59 PST). Resubmission allowed; latest counts.
- Demo Day teams announced: Nov 16. Demo Day: Nov 22.
- Registration closes: ~Nov 6, 4:00 PM PST (Nov 5 EOD AoE + 12h extension) — no change needed (Track 3, solo already set).
