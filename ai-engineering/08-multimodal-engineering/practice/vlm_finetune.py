"""Training and scoring helpers for vlm_finetune_lab.py: the collator, LoRA set-up, the loop and field accuracy."""
import gc
import json
import random
import resource
import time

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

from vlm_invoices import FIELDS, answer

MODEL = "HuggingFaceTB/SmolVLM-256M-Instruct"
DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
PROMPT = "Read this invoice. Return JSON with the keys vendor, number, issued and total, and nothing else."
SHOWN = PROMPT + ' Use exactly this shape: {"vendor": "Acme Print Ltd", "number": "123456", "issued": "2026-01-31", "total": "1234.50"}'
SUFFIXES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
TEXT_ONLY = r".*text_model.*\.(" + "|".join(SUFFIXES) + ")"


def load_processor(edge=512):
    proc = AutoProcessor.from_pretrained(MODEL)
    proc.image_processor.size = {"longest_edge": edge}
    proc.image_processor.max_image_size = {"longest_edge": 512}
    return proc


def load_model(bits=None):
    if bits == 4:
        config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
        return AutoModelForImageTextToText.from_pretrained(MODEL, quantization_config=config, device_map={"": DEVICE})
    return AutoModelForImageTextToText.from_pretrained(MODEL, dtype=torch.bfloat16).to(DEVICE)


def add_lora(model, targets=TEXT_ONLY, r=8, quantized=False):
    if quantized:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=False)  # freezes the base, casts its norms to float32
    model = get_peft_model(model, LoraConfig(r=r, lora_alpha=r, target_modules=targets, task_type="CAUSAL_LM"))
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs=dict(use_reentrant=False))
    model.config.use_cache = False
    return model


def chat(with_answer=None, prompt=PROMPT):
    messages = [dict(role="user", content=[dict(type="image"), dict(type="text", text=prompt)])]
    if with_answer is not None:
        messages.append(dict(role="assistant", content=[dict(type="text", text=with_answer)]))
    return messages


def collate(proc, docs, mask="answer only"):
    """Turn (image, doc) pairs into a batch. Labels of -100 are left out of the loss."""
    texts = [proc.apply_chat_template(chat(answer(d)), tokenize=False) for _, d in docs]
    batch = proc(text=texts, images=[[im] for im, _ in docs], return_tensors="pt", padding=True, pad_to_multiple_of=32)
    labels = batch["input_ids"].clone()
    labels[batch["attention_mask"] == 0] = -100
    if mask == "padding and image tokens":
        labels[labels == proc.tokenizer.convert_tokens_to_ids("<image>")] = -100
    if mask == "answer only":
        start = proc.tokenizer("Assistant:", add_special_tokens=False).input_ids
        for row in labels:
            ids, at = row.tolist(), -1
            for i in range(len(ids) - len(start), -1, -1):
                if ids[i:i + len(start)] == start:
                    at = i + len(start)
                    break
            assert at > 0, "no assistant turn found"
            row[:at] = -100
    batch["labels"] = labels
    return {k: v.to(DEVICE, dtype=torch.bfloat16) if k == "pixel_values" else v.to(DEVICE) for k, v in batch.items()}


def train(model, proc, docs, steps, seed, batch=4, lr=2e-4, mask="answer only", log=None, every=None, val=None, curve=None):
    random.seed(seed)
    torch.manual_seed(seed)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    model.train()
    started, losses = time.time(), []
    for step in range(steps):
        with torch.autocast(DEVICE, dtype=torch.bfloat16):  # a 4-bit base mixes bf16 layers with float32 norms
            loss = model(**collate(proc, random.sample(docs, min(batch, len(docs))), mask)).loss
        loss.backward()
        opt.step()
        opt.zero_grad()
        losses.append(loss.item())
        if every and (step + 1) % every == 0:
            curve.append(dict(step=step + 1, train_loss=sum(losses[-every:]) / every, **{k: v for k, v in score(model, proc, val)[0].items() if k in ("field_accuracy", "parses")}))
            model.train()
        if log and (step + 1) % log == 0:
            print(f"  step {step + 1} loss {sum(losses[-log:]) / log:.3f}, {(time.time() - started) / (step + 1):.2f} s/step, {driver_gb():.2f} GB", flush=True)
    return (time.time() - started) / steps


def clear():
    """Between runs: without this the driver keeps the last run's pool and every arm reports the same memory."""
    gc.collect()
    if DEVICE == "mps":
        torch.mps.empty_cache()


def weights_gb():
    return torch.mps.current_allocated_memory() / 1e9 if DEVICE == "mps" else 0.0


def driver_gb():
    return torch.mps.driver_allocated_memory() / 1e9 if DEVICE == "mps" else resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


@torch.no_grad()
def read(model, proc, image, prompt=PROMPT, max_new_tokens=70):
    model.eval()
    b = proc(text=proc.apply_chat_template(chat(prompt=prompt), add_generation_prompt=True, tokenize=False), images=[[image]], return_tensors="pt")
    b = {k: v.to(DEVICE, dtype=torch.bfloat16) if k == "pixel_values" else v.to(DEVICE) for k, v in b.items()}
    was_cached, model.config.use_cache = model.config.use_cache, True
    out = model.generate(**b, max_new_tokens=max_new_tokens, do_sample=False)
    model.config.use_cache = was_cached
    return proc.tokenizer.decode(out[0, b["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def score(model, proc, docs, prompt=PROMPT):
    """Exact match per field, values found anywhere in the reply under any key, and how many replies parse as JSON at all."""
    hits, parsed, found, replies = {f: 0 for f in FIELDS}, 0, 0, []
    for image, doc in docs:
        text = read(model, proc, image, prompt)
        replies.append(text)
        found += sum(doc[f] in text for f in FIELDS)
        try:
            got = json.loads(text)
            parsed += isinstance(got, dict)
        except json.JSONDecodeError:
            got = {}
        got = got if isinstance(got, dict) else {}
        for f in FIELDS:
            hits[f] += str(got.get(f, "")).strip() == doc[f]
    n = len(docs)
    return dict(field_accuracy=sum(hits.values()) / (n * len(FIELDS)), values_found=found / (n * len(FIELDS)), parses=parsed / n, **{f: hits[f] / n for f in FIELDS}), replies
