# LEXSI Stage 1 — feasibility verdict + handoff (Sun Nov 15, ~16:30 PT)

## VERDICT: FEASIBLE — but only via Kaggle free GPU + Umar's HF token
**Deadline: Mon Nov 16, 03:59 AM PT** (Nov 15, 11:59 PM AoE). ~11.5h left.
**NOT feasible on this VM:** no GPU, 559 MB RAM free, Tiny Aya is 3.35B
params (both `tiny-aya-global` and `tiny-aya-base` are 3,349,227,520 params
— the "0.5B" note in the old PLAN.md is wrong), no HF token cached.
**Feasible route (officially endorsed by Lexsi: "use free GPUs from Colab
or Kaggle"):** Kaggle free GPU (T4) + LoRA r=16 on Tiny Aya Global.
Umar HAS a Kaggle account (username `umarshareef0165zxq7`, used for Gemma 4
+ Memecoins). Training on 26 short examples takes minutes on a T4; the
SafetyPulse team ran the identical recipe (Tiny Aya Global, LoRA r=16,
T4) for this same hackathon.

## What already exists (verified today)
- Track 3, Statement 6, solo, REGISTERED (confirmed by Ram's email today).
- Public repo: https://github.com/umarshareef0165-netizen/lexsi-dataagent
- Public demo video: https://youtu.be/yXklaZhqHs0 (oEmbed verified)
- Real AgentTune 1.1.3 + AuditKIT 1.1.3 evals: base 0/12 → improved 12/12,
  tool-call F1 0.800 → 1.000 (`outputs/`)
- HF username confirmed: `umarshareef0165` (from his email, not guessed)

## What I built today (all under ~/workspace/lexsi-hackathon/)
1. `sft/build_sft.py` + `sft/lexsi-dataagent-sft-train.jsonl` (26 examples)
   + `sft/lexsi-dataagent-sft-eval.json` (12 tasks) — every SQL executed
   against the seed DB and verified; 0 eval questions leaked into train.
2. `sft/README.md` — dataset card for the SFT dataset.
3. `outputs/README-dataset-card.md` — dataset card for trajectories/logs.
4. `notebook/build_notebook.py` → `notebook/lexsi-tiny-aya-lora.ipynb`
   (9 cells, Kaggle T4): env check → data (embedded verbatim) → load base
   (global, fallback base) → BASE eval → LoRA SFT (r=16, lr 2e-4, 3 ep)
   → LoRA eval (reloads saved adapter) → HF upload + collections.
   Embedded data re-parsed and verified after generation.
5. `WRITEUP-ARTICLE.md` — full write-up per the official checklist
   (title, abstract <500w, repos, models, datasets, metrics, method,
   results, limitations, artifacts, reproduction). Model-eval numbers are
   marked **[TO FILL]** — they come from the Kaggle run only.
6. This handoff.

## Remaining steps (owner + time)
| # | Step | Owner | Time |
|---|------|-------|------|
| 1 | Push `sft/`, `notebook/`, `WRITEUP-ARTICLE.md`, dataset cards to the public repo (or confirm already pushed by subagent) | parent (GitHub) | ~15 min |
| 2 | Get Umar's **HF write token** via Secure Vault card (account `umarshareef0165`). NEVER ask in chat. Without it, no HF upload is possible. | parent → user | ~10 min of his time |
| 3 | Run the Kaggle notebook on T4 with `HF_TOKEN` secret set; confirm Tiny Aya licence accepted on HF (else fallback to `tiny-aya-base` is automatic) | parent browser task OR user on his device | ~60–90 min incl. setup |
| 4 | Upload trajectories dataset files (from repo `outputs/`) to the trajectories repo + verify BOTH collections are public | Kaggle notebook cell 6 does most; verify by opening the collection URLs | ~15 min |
| 5 | Paste the REAL model-eval numbers into `WRITEUP-ARTICLE.md` Results table + abstract; push updated article to the repo | parent | ~20 min |
| 6 | Submit the Lexsi form with his FINAL approval (never without it) | parent browser + user approval | ~15 min |

## Submit form
- URL from Ram's Nov 13 email: **https://hackathon.lexsi.ai/submit**
  (text-fetch 404s — the page is JS-rendered; open it in the live browser
  to read the exact fields). Also: https://hackathon.lexsi.ai/submission/
  (same, JS-rendered). Form needs: registered email, abstract <500 words,
  HF model collection URL, HF dataset collection URL, write-up link,
  GitHub repo, track/problem statements, repos + models used.
- Resubmission allowed; latest counts.

## Risks (honest)
- **Biggest risk: the Kaggle run.** If Kaggle GPU is unavailable / the
  notebook hits a version snag, the fallback is Google Colab (same
  notebook, T4) — also browser-driven. No local fallback exists.
- **HF token is the gating his-step.** If he won't provide it, NOTHING can
  be uploaded and the submission cannot qualify. The $20 HF-credits coupon
  is NOT a substitute: redeeming it requires linking a payment method
  (his decision, not made; card is empty).
- **Tiny model, tiny data.** 26 examples / 12 tasks is prototype-scale.
  The LoRA may score modestly (even 6–8/12). The write-up reports the real
  numbers either way; a modest-but-real adapter still qualifies (both
  collections public + write-up + before/after metrics), it just won't win.
- **Tiny Aya Global is gated** (`gated: auto`) — the licence must be
  accepted on HF under his account or the download 401s. Fallback to
  ungated `tiny-aya-base` is built into the notebook.
- **Time.** The plan leaves ~5h of buffer before 03:59 PT, but every
  his-step (token, Kaggle, approval) eats into it. If the Kaggle run has
  not STARTED by ~21:00 PT, the risk of missing the deadline rises fast.

## What was NOT done (and must not be claimed)
- No fine-tune has run yet. No adapter, model, or dataset exists on HF yet.
- Nothing has been submitted to LEXSI. No accounts created, nothing paid.
- No results invented: every number in the write-up draft is either from
  the Nov 4–6 measured evals or marked [TO FILL].
