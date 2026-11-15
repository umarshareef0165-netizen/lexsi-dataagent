# Dataset Card: Lexsi DataAgent SFT data

## Dataset Summary
26 verified question→SQL instruction-tuning examples + 12 held-out eval
tasks for a read-only business-data agent over a tiny synthetic SQLite shop
database (5 customers, 4 products, 10 orders; all invented sample data).
Built for the Lexsi AI Safety & Alignment Hackathon, Track 3 (Agentic
Fine-tuning), Problem Statement 6 (Data and database agents).

## Files
- `lexsi-dataagent-sft-train.jsonl` — 26 examples, fields `prompt`,
  `completion`, `question`, `sql`, `pattern`, `source`,
  `verified_by_execution`. Prompt = schema + question; completion = one
  read-only SELECT statement.
- `lexsi-dataagent-sft-eval.json` — the 12 original eval tasks verbatim,
  fields `id`, `prompt`, `question`, `reference_sql`, `expected`,
  `must_contain`.

## How it was built (and verified)
Every training example's SQL was EXECUTED against the seeded database and
its result checked before the example was kept (see `sft/build_sft.py` in
the repo). Train contains expanded variants ONLY — different date ranges
(12), the three customers not used in eval (3), and paraphrases of the
fixed-answer patterns (11). The 12 eval questions appear nowhere in train
(leak check: 0). So eval measures generalisation to unseen wordings/values
within the same six patterns, not memorisation.

Patterns (6): revenue by product (delivered), top customer by delivered
spend, order counts by status, average order value (delivered), revenue in
a date range (delivered), orders for a customer.

## Splits
- train: 26 examples (12 revenue_in_range, 3 orders_for_customer,
  3 revenue_by_product, 3 top_customer, 3 avg_order_value, 2 count_by_status)
- eval: 12 tasks (T01–T12)

## Limitations
Tiny and narrow by design: 26 examples, six patterns, one 10-order
database. This teaches a small adapter to emit read-only SQL for these
patterns; it is NOT a general text-to-SQL dataset, and no such claim is
made. All data is synthetic; no real business data, no personal data.

## License
MIT (same as the project repo). Base-model outputs are not included here;
the fine-tuned adapter built from this data inherits the Tiny Aya
CC-BY-NC-4.0 licence (see the model card).
