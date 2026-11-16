# DataAgent: Reliable Business Answers from a Database, with Checked Queries and Cited Sources

**One-line claim:** A read-only data agent that turns plain-language business
questions into verified SQL — and a Tiny Aya LoRA that learns to do the
same — measured before and after on the same 12 tasks.

> STATUS: Model-eval numbers filled Nov 16, 2026 from the Kaggle fine-tune
> run (`notebook/lexsi-tiny-aya-lora.ipynb`, Version #1): base 0/12, LoRA
> 3/12. All numbers in this article were actually run and verified.

## Tracks + problem statements covered
- **Track 3 — Agentic Fine-tuning**, Problem Statement **6: Data and
  database agents** (train an agent that answers business questions by
  querying databases, rewarded on verified results).
- No other track. Solo team: Umar Shareef.

## Abstract (under 500 words)
Lexsi DataAgent is a read-only data agent that answers small, well-defined
business questions — for example, "Who is the top customer by delivered
spend?" — by writing a single read-only SQL query, checking the result, and
answering with cited rows. It never writes to the database and never shows
an un-cited number.

We evaluated it honestly, before and after, with the track's own toolkits:
AgentTune and AuditKIT. Over 12 tasks on a synthetic shop database, the
base agent (a generic SQL dump) succeeded on 0 of 12; the improved agent —
better tool selection, a verification step, and a strict read-only rule —
succeeded on 12 of 12. Tool-call F1 rose from 0.800 to 1.000; validity and
permission compliance stayed at 1.000 for both. Every trajectory is recorded
as a real AgentTune Trajectory object, and the full evaluation is
reproducible from the public repo.

We then transferred the same pipeline to a trained model: a LoRA adapter
(r=16) on Tiny Aya Global, fine-tuned on 26 verified question→SQL examples
whose SQL was executed against the seed database before training. Base Tiny Aya scored 0/12; the LoRA scored 3/12 on the 12 held-out task questions (exact eval questions never appear in training). No
fine-tuning is claimed beyond this prototype-scale adapter, and the
agent-level and model-level evaluations are kept separate throughout.

**Headline before → after (agent level, measured):** task accuracy 0.000 →
1.000; tool-call accuracy 0.000 → 1.000 (12 tasks).
**Headline before → after (model level):** base 0.000 → LoRA 0.250 (3/12; correct tasks T02, T06, T12).

**Base model + method in one line:** CohereLabs Tiny Aya Global (3.35B),
LoRA r=16, 4-bit NF4, SFT on 26 execution-verified question→SQL examples.

## Problem statement and approach
Business users ask plain-language questions, but agents often guess, call
the wrong tool, or return unchecked numbers. DataAgent answers small,
well-defined business questions by querying a database, validating the
query, checking the result, and citing the sources it used — so every
number can be traced.

**Why this problem / real use case:** every small business runs on the same
questions (revenue by product, top customer, order counts, averages, date
ranges, per-customer orders). A wrong number in an answer is worse than no
answer, so the design rule is: one read-only, question-specific query,
validated before execution, with the result checked and cited. The same
rule is what the LoRA is trained to follow: emit one valid SELECT, nothing
else.

**Approach:** (1) a deterministic prototype agent over a local synthetic
SQLite database, with a naive and a structured variant evaluated on the same
12-task set; (2) AgentTune trajectories + AuditKIT recorded-mode scoring of
both variants; (3) a LoRA fine-tune of Tiny Aya on execution-verified
question→SQL pairs derived from the structured agent's correct queries;
(4) base-vs-LoRA evaluation on the same 12 tasks, scored by executing the
generated SQL.

## Hackathon repos (kits) used
| Repo | Version | Used for | Features |
|---|---|---|---|
| AgentTune | 1.1.3 | Trajectories + agent evaluation | Real `Trajectory` schema (one Step per tool call, observation = returned rows, reward = task correctness); trajectories exported to `outputs/trajectories.jsonl` |
| AuditKIT | 1.1.3 | Scoring the recorded trajectories | `AgentEvalRunner`, recorded mode (no live model call): tool-call F1 (name), tool-call validity, redundant calls, loop detection, tool permission; outcome oracle |

**How the repos connect:** the agent loop (prototype) produces one AgentTune
`Trajectory` per run → the trajectories are scored by AuditKIT's runner in
recorded mode → the scores drive the before/after comparison → the correct
structured-agent queries become the verified SFT data for the LoRA → the
LoRA is evaluated by the same execute-and-check scoring. CuratorKIT,
SafeTune, CircuitKIT and AlignTune were NOT used; no curation filtering,
safety repair, circuit work or AlignTune training was performed, and none
is claimed. (Track 3's toolkits are AgentTune + AuditKIT; both are used.)

## Models and licenses
| Model | Role | Version | Licence |
|---|---|---|---|
| CohereLabs/tiny-aya-global | Base model for the LoRA | 3.35B params; revision as downloaded by the notebook (recorded in `BASE_MODEL.txt`) | CC-BY-NC-4.0 (+ Cohere Labs Acceptable Use Policy) |
| CohereLabs/tiny-aya-base | Fallback base if the gated global model cannot be downloaded | 3.35B params | CC-BY-NC-4.0 |
| `umarshareef0165/lexsi-dataagent-tiny-aya-lora` | The trained adapter (this submission) | LoRA r=16, alpha 32 | CC-BY-NC-4.0 (inherited from the base model) |

No teacher model was used. No closed model was used anywhere in the
pipeline. No LLM was used as a judge.

## Datasets, benchmarks and licenses
**Source of data:** everything is synthetic and built for this project. The
database is a hand-written seed (5 customers, 4 products, 10 orders;
invented names, prices and dates — no real business or personal data).
No third-party dataset is used.

| Dataset | Contents | Licence |
|---|---|---|
| `lexsi-dataagent-trajectories` | 24 AgentTune trajectories + `eval_results.json` + `auditkit_eval.json` (in the GitHub repo `outputs/`; HF repo created but empty at write-up time, upload pending) | MIT |
| `lexsi-dataagent-sft` | 26 SFT train examples + 12 held-out eval tasks + (after the Kaggle run) `lexsi-dataagent-model-eval.json` | MIT |

**Languages covered:** English only (questions, SQL, answers).

**Train / test splits, leak check:** SFT train = 26 examples (12 date-range
variants, 3 other-customer variants, 11 paraphrases). Eval = the 12 original
task questions verbatim. The eval questions appear NOWHERE in train —
verified by an exact-match check in `sft/build_sft.py` (0 leaked). So the
model eval measures generalisation to unseen wordings/values within the
same six patterns, not memorisation. No embedding/MinHash leak check was
needed beyond the exact-match check because train and eval are disjoint by
construction (different parameter values and wordings).

**CuratorKIT filtering:** not used — the SFT data was verified by execution
instead (each SQL run against the seed database; only examples returning a
correct, non-null result were kept).

**Safety benchmark:** no external safety benchmark was run. The safety
property measured is the read-only rule: every generated SQL is validated
(SELECT-only, single statement, known tables/columns) before execution, and
the eval reports how many generated queries pass validation and execute.
**General capability benchmark:** none was run; the eval is task-specific by
design, and that limit is stated.

## Metrics, and why these
| Metric | Higher/lower better | Why |
|---|---|---|
| Task accuracy (12 tasks) | higher | The headline: did the answer match the verified expected answer? |
| Tool-call accuracy | higher | Did the agent/model call the right tool / emit a question-specific query? |
| Syntax correctness | higher | Is the SQL valid? |
| Tool-call F1 (name) | higher | AuditKIT: precision/recall of the tool calls |
| Tool-call validity / permission | higher | AuditKIT: calls well-formed and allowed |
| Redundant calls / loops | lower | AuditKIT: efficiency and runaway-loop diagnostics |
| Mean calls/task, approx. tokens/task | reported | Efficiency — reported honestly, no win claimed where there is none |

**Metrics for what should not get worse:** validity and permission stayed at
1.000 for both agent variants; the model eval reports the same checks for
base vs LoRA (validation-pass rate and execution-success rate per task).

## Method / experiments
**Agent experiment (measured Nov 4–6):** naive vs structured agent, same 12
tasks, same database, deterministic (no sampling). Harness:
`prototype/eval.py`; tests: `tests/` (pytest).

**Model experiment (Kaggle notebook):**
- Base: Tiny Aya Global, 4-bit NF4, `device_map="auto"`, fp16 compute.
- Method: LoRA r=16, alpha 32, dropout 0.05, all linear projections;
  TRL 0.12.0 SFTTrainer, prompt-completion data, prompt masked;
  lr 2e-4, 3 epochs, per-device batch 1 × grad-accum 8 (effective batch 8),
  max length 512, seed 42. (TRL 1.18's fused loss kernel crashed on the
  T4, so the run used TRL 0.12.0; batch 4 OOMed the T4 on the 256k-vocab
  logits, hence batch 1.)
- Hardware: Kaggle free GPU (T4 x2). Training time 87s.
- Eval: greedy decoding (temperature 0), max 120 new tokens, same prompt
  format as training; SQL extracted with a regex; executed against the
  seed database; scored with the tasks' `must_contain` checks (same logic
  as the prototype harness). Base evaluated BEFORE training; LoRA evaluated
  by reloading the saved adapter on a fresh base.
- Seeds: 42 (training); eval is greedy/deterministic.
- Ablations: none (time-boxed; see "With more credits").

## Results
**Agent level — same model before vs after (table, measured):**

| metric | base (naive) | improved (structured) |
|---|---|---|
| task accuracy (12 tasks) | 0.000 | 1.000 |
| tool-call accuracy | 0.000 | 1.000 |
| syntax correctness | 1.000 | 1.000 |
| safety (no exception) | 1.000 | 1.000 |
| tool-call F1 (name) | 0.800 | 1.000 |
| tool-call validity | 1.000 | 1.000 |
| tool permission | 1.000 | 1.000 |
| redundant calls / loops | 0 / none | 0 / none |
| mean tool calls / task | 2.00 | 3.00 |
| mean approx. tokens / task | ~39.2 | ~72.6 |

**Model level — base vs LoRA (table, measured Nov 16, 2026):**

| task | base correct? | LoRA correct? |
|---|---|---|
| T01 | No | No |
| T02 | No | Yes |
| T03 | No | No |
| T04 | No | No |
| T05 | No | No |
| T06 | No | Yes |
| T07 | No | No |
| T08 | No | No |
| T09 | No | No |
| T10 | No | No |
| T11 | No | No |
| T12 | No | Yes |
| **accuracy** | **0.000 (0/12)** | **0.250 (3/12)** |

Per-task generated SQL: `lexsi-dataagent-model-eval.json` in the public SFT dataset repo (`umarshareef0165/lexsi-dataagent-sft`).

**Findings (agent level):** the structured agent wins on accuracy, NOT on
efficiency — it uses one extra tool call and roughly twice the (approximate)
tokens per task, because it inspects the schema and generates a specific
query. No efficiency win is claimed on these numbers.

**What didn't work / negative results:** the LoRA failed 9 of 12 tasks (T01, T03, T04, T05, T07, T08, T09, T10, T11); each generated SQL is recorded in `lexsi-dataagent-model-eval.json`, but the per-task failure modes were not individually diagnosed. The likely causes at this scale are the tiny training set (26 examples) and unseen pattern variants. Known in advance: the eval is small (12 tasks) and the training set is tiny (26 examples); a failure on an unseen pattern variant is expected, not hidden.

**Sample inputs and outputs:**
- Input: "What is the total revenue by product for delivered orders?"
  Reference SQL: `SELECT p.name AS product, SUM(o.quantity * p.unit_price)
  AS revenue FROM orders o JOIN products p ON p.id = o.product_id WHERE
  o.status = 'delivered' GROUP BY p.name ORDER BY revenue DESC` →
  Office Chair: 960.0, Desk Lamp: 350.0, Notebook Pack: 240.0, Laptop
  Stand: 135.0.
- Input: "Who is the top customer by delivered spend?" → Bilal Ahmed
  (980.0).
- Full per-task SQL + answers: `outputs/eval_results.json`; model
  generations: `lexsi-dataagent-model-eval.json` (after the Kaggle run).

## Limitations
- Tiny and narrow: 26 SFT examples, six question patterns, one 10-order
  database. The adapter is a prototype-scale proof, not a general
  text-to-SQL model.
- Eval is 12 tasks; no confidence intervals are meaningful at this size,
  so none are claimed.
- No external safety or general-capability benchmark was run.
- No efficiency win: the structured agent uses more calls/tokens than the
  naive one; the LoRA's efficiency is not yet measured against a
  token-count baseline.
- The demo UI is a stdlib HTML page, not a production app.

## With more credits
**Planned approach:** expand the SFT set to ~500 examples by generating
verified variants across more databases (different schemas, more rows,
more statuses/date ranges), add a held-out database (unseen schema) as the
real generalisation test, train 3–5 epochs with a small sweep over LoRA
rank (8/16/32) and learning rate, and add an over-refusal/validation
check (the model must refuse or flag questions about unknown tables
instead of hallucinating SQL).
**Expected before / after:** with ~500 verified examples and a held-out
schema, we would expect the LoRA to hold its seen-pattern accuracy and
gain partial accuracy on the unseen schema (roughly 40–60% as a first
estimate — a forecast, not a result), while the base model would stay near
its current level.

## Artifacts
- **HF datasets collection:** `Lexsi DataAgent — datasets`
  (https://huggingface.co/collections/umarshareef0165/lexsi-dataagent-datasets)
  — public. Contains `umarshareef0165/lexsi-dataagent-sft` (26 train
  examples, 12 eval tasks, model-eval JSON) and
  `umarshareef0165/lexsi-dataagent-trajectories` (repo created; empty on
  HF at write-up time — the trajectory files live in the GitHub repo
  `outputs/`; HF upload pending).
- **HF models collection:** `Lexsi DataAgent — models`
  (https://huggingface.co/collections/umarshareef0165/lexsi-dataagent-models)
  — public. Contains `umarshareef0165/lexsi-dataagent-tiny-aya-lora`.
- **GitHub repo:** https://github.com/umarshareef0165-netizen/lexsi-dataagent
  (public; prototype, tests, SFT builder, notebook, this article).
- **Demo video:** https://youtu.be/yXklaZhqHs0 (public; before/after on a
  real question with the real numbers on screen).
- **Demo / Space:** none (the demo is the video + repo; no HF Space was
  built in the time available).

## Documentation and reproduction
**Repo layout:**
```
lexsi-dataagent/
  prototype/   db.py (seed DB) · agent.py (tools + variants) · eval.py (harness)
               server.py (demo UI) · auditkit_eval.py (AgentTune/AuditKIT wiring)
  tests/       pytest suite for the agent + eval wiring
  outputs/     trajectories.jsonl · eval_results.json · auditkit_eval.json
  sft/         build_sft.py · lexsi-dataagent-sft-train.jsonl · lexsi-dataagent-sft-eval.json
  notebook/    lexsi-tiny-aya-lora.ipynb (Kaggle, T4)
  WRITEUP-ARTICLE.md (this article)
```
**Run instructions:**
1. Agent eval: `python -m pytest tests/` then the harness in
   `prototype/eval.py` (stdlib + AgentTune/AuditKIT in the repo venv).
2. SFT data: `python3 sft/build_sft.py` (stdlib only; re-verifies every
   example by execution).
3. Fine-tune + model eval: open `notebook/lexsi-tiny-aya-lora.ipynb` on
   Kaggle with GPU T4, add the `HF_TOKEN` secret, Run All.
4. Environment: Python 3.12; `torch`, `transformers`, `trl`, `peft`,
   `datasets`, `bitsandbytes`, `accelerate`, `agenttune==1.1.3`,
   `auditkit==1.1.3`. No paid APIs, no external services, no credentials
   committed.
**Declaration of work done outside the hackathon:** none. The prototype,
evals, SFT data, notebook and this article were all produced Nov 4–15,
2026, during the hackathon window.
**LLM usage statement:** code and write-up were drafted with AI assistance
(and every result in this article was actually run and verified — no
number is asserted without a run behind it).

## Teammates tagged
Solo — Umar Shareef (all work: prototype, evals, SFT data, notebook,
write-up, video).

## Acknowledgements
Lexsi Labs for the toolkits and the hackathon; Cohere Labs for Tiny Aya;
Hugging Face for hosting; Kaggle for the free GPU used for the fine-tune.

## References
- Lexsi hackathon: https://hackathon.lexsi.ai (rules, tracks, submit page)
- AgentTune / AuditKIT: Lexsi Labs open-source stack (GitHub)
- Tiny Aya Global: https://huggingface.co/CohereLabs/tiny-aya-global
  (CC-BY-NC-4.0)
- SafetyPulse (Track 2b) for the LoRA-on-T4 recipe reference:
  https://huggingface.co/blog/purvansh01/safetypulse-safety-drift-monitor
- Repo: https://github.com/umarshareef0165-netizen/lexsi-dataagent
