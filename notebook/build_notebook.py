"""Generate the Kaggle training notebook for the Lexsi DataAgent LoRA.

Reads the REAL built artifacts (sft train/eval JSON, db.py seed data) and
embeds them verbatim into the notebook, so nothing is transcribed by hand.

Run:  python3 notebook/build_notebook.py   (stdlib only)
Output: notebook/lexsi-tiny-aya-lora.ipynb  (Kaggle-ready, GPU T4)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from prototype import db as DB  # noqa: E402

OUT = HERE / "notebook" / "lexsi-tiny-aya-lora.ipynb"

train_rows = [json.loads(line) for line in
              (HERE / "sft" / "lexsi-dataagent-sft-train.jsonl").read_text().splitlines()
              if line.strip()]
eval_rows = json.loads(
    (HERE / "sft" / "lexsi-dataagent-sft-eval.json").read_text())

TRAIN_JSON = json.dumps(train_rows, indent=1, ensure_ascii=False)
EVAL_JSON = json.dumps(eval_rows, indent=1, ensure_ascii=False)
SEED_JSON = json.dumps(
    {"customers": DB.CUSTOMERS, "products": DB.PRODUCTS,
     "orders": DB.ORDERS, "schema": DB.SCHEMA},
    indent=1, ensure_ascii=False)

MODEL_CARD = """---
license: cc-by-nc-4.0
base_model: CohereLabs/tiny-aya-global
tags:
- lexsi-hackathon
- track-3
- lora
---

# Lexsi DataAgent — Tiny Aya LoRA (Track 3, Statement 6)

LoRA adapter (r=16) fine-tuned on 26 verified question-to-SQL examples for a
read-only business-data agent (synthetic SQLite shop database: 5 customers,
4 products, 10 orders). The adapter teaches Tiny Aya Global to emit a single
read-only SELECT for six narrow question patterns (revenue by product, top
customer, order counts by status, average order value, revenue in a date
range, orders for a customer).

Training data: `umarshareef0165/lexsi-dataagent-sft` (every example's SQL was
executed against the seed database and verified before training). Evaluation:
12 held-out task questions (exact eval questions never appear in training),
base vs LoRA, scored by executing the generated SQL and checking the answer
— see `lexsi-dataagent-model-eval.json` in the dataset repo and the
write-up. This is a prototype-scale adapter (26 examples); it is not a
general text-to-SQL model, and that limit is stated in the write-up.
"""

CELLS = []


def md(source: str):
    CELLS.append({"cell_type": "markdown",
                  "metadata": {}, "source": source.splitlines(True)})


def code(source: str):
    CELLS.append({"cell_type": "code", "execution_count": None,
                  "metadata": {}, "outputs": [],
                  "source": source.splitlines(True)})


md("""# Lexsi DataAgent — Tiny Aya LoRA fine-tune (Track 3, Statement 6)

**What this notebook does:** fine-tunes CohereLabs Tiny Aya Global (3.35B) with LoRA (r=16, 4-bit NF4) on 26 verified question→SQL examples, evaluates base vs LoRA on 12 held-out task questions by EXECUTING the generated SQL, and uploads the adapter + datasets to Hugging Face.

**Honest scope:** 26 training examples, six narrow question patterns, one synthetic 10-order database. This is a prototype-scale adapter — it proves the AgentTune pipeline transfers to a trained model; it is NOT a general text-to-SQL model. All numbers below are measured, not asserted.

**Prerequisites (do these before Run All):**
1. Kaggle notebook with **GPU T4** accelerator ON (Settings → Accelerator → GPU T4).
2. Kaggle secret **`HF_TOKEN`** = a Hugging Face write token for `umarshareef0165` (Add-ons → Secrets). Needed for the gated Tiny Aya download + uploads. Without it, training cells 3–5 still run; upload cells print manual steps instead.
3. Tiny Aya licence: accept the licence at https://huggingface.co/CohereLabs/tiny-aya-global (same HF account). If the download 401s, the notebook falls back to `CohereLabs/tiny-aya-base` automatically.
""")

code("""# 0 — Environment check
import torch, transformers, trl, peft, datasets, sys
print("python", sys.version.split()[0])
print("torch", torch.__version__, "| cuda:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
print("transformers", transformers.__version__)
print("trl", trl.__version__, "| peft", peft.__version__, "| datasets", datasets.__version__)
""")

code("""# 1 — Write the SFT data + eval set (embedded verbatim from the repo build)
import json, pathlib
train_rows = json.loads(r'''""" + TRAIN_JSON + """''')
eval_rows = json.loads(r'''""" + EVAL_JSON + """''')
seed = json.loads(r'''""" + SEED_JSON + """''')
pathlib.Path("lexsi-dataagent-sft-train.jsonl").write_text(
    "".join(json.dumps(r, ensure_ascii=False) + "\\n" for r in train_rows))
pathlib.Path("lexsi-dataagent-sft-eval.json").write_text(
    json.dumps(eval_rows, indent=2, ensure_ascii=False))
pathlib.Path("seed.json").write_text(json.dumps(seed, indent=1))
print(f"train: {len(train_rows)} examples | eval: {len(eval_rows)} tasks")
print("leak check:", len({r['question'] for r in train_rows} & {r['question'] for r in eval_rows}), "eval questions in train (must be 0)")
""")

code("""# 2 — Load base model (4-bit NF4) + tokenizer
import os, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

HF_TOKEN = None
try:
    from kaggle_secrets import UserSecretsClient
    HF_TOKEN = UserSecretsClient().get_secret("HF_TOKEN")
    print("HF_TOKEN secret: present")
except Exception as e:
    print("HF_TOKEN secret: MISSING —", e)

BASE_CANDIDATES = ["CohereLabs/tiny-aya-global", "CohereLabs/tiny-aya-base"]
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_compute_dtype=torch.float16,
                         bnb_4bit_use_double_quant=True)
model = tok = BASE_ID = None
for cand in BASE_CANDIDATES:
    try:
        tok = AutoTokenizer.from_pretrained(cand, token=HF_TOKEN)
        model = AutoModelForCausalLM.from_pretrained(
            cand, quantization_config=bnb, device_map="auto", token=HF_TOKEN)
        BASE_ID = cand
        print("loaded base:", cand)
        break
    except Exception as e:
        print("FAILED", cand, "->", str(e)[:200])
assert model is not None, "could not load any Tiny Aya base model"
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model.config.use_cache = False
""")

code("""# 3 — Eval helpers + BASE-model eval (run BEFORE training)
import re, sqlite3, json, pathlib
from peft import PeftModel

SCHEMA = seed["schema"]
def open_db():
    conn = sqlite3.connect(":memory:"); conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?)", [tuple(r) for r in seed["customers"]])
    conn.executemany("INSERT INTO products VALUES (?,?,?,?)", [tuple(r) for r in seed["products"]])
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", [tuple(r) for r in seed["orders"]])
    conn.commit(); return conn

def extract_sql(text):
    m = re.search(r"SELECT\\b.*?;", text, re.I | re.S)
    if m: return m.group(0).strip()
    m = re.search(r"SELECT\\b.*", text, re.I | re.S)
    return m.group(0).strip() if m else ""

def score_sql(sql, must):
    # mirrors the prototype harness: execute, format like the agent, check must_contain
    if not sql: return False, "no SQL extracted"
    conn = open_db()
    try:
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
    except Exception as e:
        return False, f"SQL error: {e}"
    if not rows: return False, "empty result"
    first = rows[0]
    if "revenue" in first:
        ans = ", ".join(f"{r.get('product','')}: {r['revenue']}" for r in rows)
    elif "total" in first:
        ans = f"{first['customer']} ({first['total']})"
    elif "n" in first:
        ans = f"Count: {first['n']}."
    elif "avg_value" in first:
        ans = f"{first['avg_value']:.2f}"
    else:
        ans = str(rows)
    ok = all(s in ans for s in must)
    return ok, ans

def run_eval(m, label):
    results = []
    for task in eval_rows:
        ids = tok(task["prompt"], return_tensors="pt").to(m.device)
        out = m.generate(**ids, max_new_tokens=120, do_sample=False,
                         pad_token_id=tok.eos_token_id)
        gen = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
        sql = extract_sql(gen)
        ok, detail = score_sql(sql, task["must_contain"])
        results.append({"id": task["id"], "question": task["question"],
                        "generated_sql": sql, "correct": bool(ok),
                        "detail": detail, "raw_generation": gen[:500]})
        print(f"[{label}] {task['id']} correct={ok} :: {sql[:110]}")
    acc = sum(r["correct"] for r in results) / len(results)
    print(f"[{label}] accuracy: {acc:.3f} ({sum(r['correct'] for r in results)}/{len(results)})")
    return results, acc

base_results, base_acc = run_eval(model, "base")
""")

code("""# 4 — LoRA SFT (TRL SFTTrainer, prompt-completion, prompt masked)
from datasets import Dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

ds = Dataset.from_list([{"prompt": r["prompt"], "completion": r["completion"]}
                        for r in train_rows])
peft_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"])
cfg = SFTConfig(output_dir="./lora-out", per_device_train_batch_size=4,
                gradient_accumulation_steps=2, num_train_epochs=3,
                learning_rate=2e-4, logging_steps=5, save_strategy="no",
                fp16=True, max_length=512, packing=False, report_to=[])
trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds,
                     peft_config=peft_cfg)
import time; t0 = time.time()
trainer.train()
print(f"training took {time.time()-t0:.0f}s")
print("final loss:", trainer.state.log_history[-1])
trainer.save_model("./adapter")
tok.save_pretrained("./adapter")
pathlib.Path("./adapter/BASE_MODEL.txt").write_text(BASE_ID + "\\n")
print("adapter saved to ./adapter")
""")

code("""# 5 — LoRA eval: reload the SAVED adapter on a fresh base, re-run 12 tasks
import gc
del model, trainer
gc.collect(); torch.cuda.empty_cache()
from transformers import AutoModelForCausalLM
fresh = AutoModelForCausalLM.from_pretrained(
    BASE_ID, quantization_config=bnb, device_map="auto", token=HF_TOKEN)
fresh.config.use_cache = False
lora = PeftModel.from_pretrained(fresh, "./adapter")
lora_results, lora_acc = run_eval(lora, "lora")
report = {"base_model": BASE_ID, "base_accuracy": base_acc,
          "lora_accuracy": lora_acc, "n_tasks": len(eval_rows),
          "base": base_results, "lora": lora_results}
pathlib.Path("lexsi-dataagent-model-eval.json").write_text(json.dumps(report, indent=2))
print(f"\\nHEADLINE: base {base_acc:.3f} -> LoRA {lora_acc:.3f} on {len(eval_rows)} held-out tasks")
print("saved lexsi-dataagent-model-eval.json")
""")

code("""# 6 — Upload adapter + datasets to Hugging Face + create collections
# Needs HF_TOKEN (Kaggle secret). If missing, this cell prints manual steps.
from huggingface_hub import HfApi
import pathlib, shutil, json

USER = "umarshareef0165"
ADAPTER_REPO = f"{USER}/lexsi-dataagent-tiny-aya-lora"
SFT_REPO = f"{USER}/lexsi-dataagent-sft"
TRAJ_REPO = f"{USER}/lexsi-dataagent-trajectories"
if not HF_TOKEN:
    print("NO HF_TOKEN — manual upload steps:")
    print("1. huggingface_hub login with a write token for", USER)
    print("2. adapter ->", ADAPTER_REPO, " (folder ./adapter + model card)")
    print("3. sft files ->", SFT_REPO, " (train jsonl + eval json + this eval json)")
    print("4. outputs/*.json/jsonl ->", TRAJ_REPO)
    print("5. create 2 collections (models + datasets) and add the repos")
else:
    api = HfApi(token=HF_TOKEN)
    # model card into adapter folder
    pathlib.Path("./adapter/README.md").write_text('''""" + MODEL_CARD + """''')
    api.create_repo(ADAPTER_REPO, repo_type="model", exist_ok=True)
    api.upload_folder(folder_path="./adapter", repo_id=ADAPTER_REPO, repo_type="model")
    print("adapter:", f"https://huggingface.co/{ADAPTER_REPO}")
    # datasets
    for repo, files in [
        (SFT_REPO, ["lexsi-dataagent-sft-train.jsonl", "lexsi-dataagent-sft-eval.json",
                    "lexsi-dataagent-model-eval.json"]),
        (TRAJ_REPO, None)]:
        api.create_repo(repo, repo_type="dataset", exist_ok=True)
        if files:
            for f in files:
                api.upload_file(path_or_fileobj=f, path_in_repo=f, repo_id=repo, repo_type="dataset")
        print("dataset:", f"https://huggingface.co/datasets/{repo}")
    # NOTE: trajectory/eval-log files live in the repo outputs/ — upload them
    # from the GitHub repo (raw) in a follow-up cell, or add them here if present.
    # collections
    for title, desc, items in [
        ("Lexsi DataAgent — models", "Tiny Aya LoRA adapter for the Lexsi DataAgent (Track 3).",
         [(ADAPTER_REPO, "model")]),
        ("Lexsi DataAgent — datasets", "Trajectories, eval logs and SFT data for the Lexsi DataAgent (Track 3).",
         [(SFT_REPO, "dataset"), (TRAJ_REPO, "dataset")])]:
        col = api.create_collection(title=title, namespace=USER, description=desc, exist_ok=True)
        slug = col.slug
        for item_id, item_type in items:
            api.add_collection_item(collection_slug=slug, item_id=item_id, item_type=item_type)
        print("collection:", f"https://huggingface.co/collections/{USER}/{slug}")
print("DONE")
""")

md("""## Next steps (after this notebook)
1. Copy the headline numbers (base → LoRA accuracy) into the write-up article's Results table.
2. Upload `outputs/trajectories.jsonl`, `outputs/eval_results.json`, `outputs/auditkit_eval.json` to the trajectories dataset repo (from the GitHub repo or locally) + add to the datasets collection.
3. Paste the collection URLs + abstract into the Lexsi submit form (https://hackathon.lexsi.ai/submit — verify in a browser; the text fetch 404s) and submit ONLY with Umar's approval.
""")

nb = {"cells": CELLS,
      "metadata": {"kernelspec": {"display_name": "Python 3",
                                  "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.12"}},
      "nbformat": 4, "nbformat_minor": 5}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print(f"wrote {OUT} ({len(CELLS)} cells)")
