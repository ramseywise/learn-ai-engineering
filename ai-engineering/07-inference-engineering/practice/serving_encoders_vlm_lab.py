# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy", "pandas", "torch>=2.9", "transformers>=5", "peft>=0.20", "pillow", "num2words", "accelerate", "sentence-transformers>=5", "onnxruntime", "optimum[onnxruntime]"]
# ///
"""The numbers in notes/08b: where the time goes when you serve an encoder or a vision-language model.

Run from this folder. It downloads two small models, about 0.6 GB, on first use:
    uv run serving_encoders_vlm_lab.py

Everything runs in one process on one laptop, with no server and no network. Read the ratios, not the absolute numbers:
a datacentre GPU changes them, and the point of the lab is that you can take the same measurements on your own hardware.
"""
# %%
import io
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parents[2] / "08-multimodal-engineering" / "practice"))
from vlm_finetune import DEVICE, MODEL as VLM, PROMPT, TEXT_ONLY, add_lora, chat, clear, driver_gb, load_model, load_processor
from vlm_invoices import LAYOUTS, make

ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
pd.set_option("display.width", 170)
started = time.time()
print(f"device {DEVICE}, encoder {ENCODER}, VLM {VLM}")


def sync():
    if DEVICE == "mps":
        torch.mps.synchronize()


def timed(fn, repeats=3):
    """Median of the repeats, after one warm-up call, because the first call on MPS builds its graphs."""
    fn()
    sync()
    times = []
    for _ in range(repeats):
        tick = time.perf_counter()
        fn()
        sync()
        times.append(time.perf_counter() - tick)
    return float(np.median(times))


# %% Encoder: generated catalogue text, most of it short and a few long, like real product data
r = random.Random(0)
WORDS = "bolt flange steel zinc bearing seal housing valve stainless thread metric hex nut gasket washer bore pump shaft".split()


def text():
    return " ".join(r.choice(WORDS) for _ in range(min(250, max(3, int(r.lognormvariate(2.5, 1.0))))))


corpus = [text() for _ in range(3000)]
tok, encoder = AutoTokenizer.from_pretrained(ENCODER), AutoModel.from_pretrained(ENCODER).to(DEVICE).eval()
lengths = np.array([len(tok(t, truncation=True, max_length=256).input_ids) for t in corpus])
print(f"\n{len(corpus)} texts, tokens: median {np.median(lengths):.0f}, p90 {np.percentile(lengths, 90):.0f}, max {lengths.max()}")


def by_count(order, size):
    return [order[i:i + size] for i in range(0, len(order), size)]


def by_budget(order, budget):
    """A batch's cost is its longest text times its size, because shorter texts are padded to the longest."""
    out, batch, longest = [], [], 0
    for i in order:
        longest_now = max(longest, lengths[i])
        if batch and longest_now * (len(batch) + 1) > budget:
            out.append(batch)
            batch, longest_now = [], lengths[i]
        batch.append(i)
        longest = longest_now
    return out + [batch] if batch else out


@torch.inference_mode()
def embed(batches, model=encoder, dtype=None):
    """Mean pooling, then unit length. Returns vectors in corpus order, seconds, and the padded tokens computed."""
    vectors, padded = np.zeros((len(corpus), 384), dtype=np.float32), 0
    tick = time.perf_counter()
    for batch in batches:
        b = tok([corpus[i] for i in batch], padding=True, truncation=True, max_length=256, return_tensors="pt").to(DEVICE)
        padded += b["input_ids"].numel()
        with torch.autocast(DEVICE, dtype=dtype, enabled=dtype is not None):
            out = model(**b).last_hidden_state
        mask = b["attention_mask"].unsqueeze(-1).to(out.dtype)
        v = torch.nn.functional.normalize((out * mask).sum(1) / mask.sum(1), dim=1)
        vectors[batch] = v.float().cpu().numpy()
    sync()
    return vectors, time.perf_counter() - tick, padded


def top10_overlap(a, b, queries=300):
    """How much of fp32's top ten a cheaper encoder keeps, on the same corpus."""
    at, bt = a[:queries] @ a.T, b[:queries] @ b.T
    return float(np.mean([len(set(np.argsort(-x)[1:11]) & set(np.argsort(-y)[1:11])) / 10 for x, y in zip(at, bt)]))


arrival = list(range(len(corpus)))
longest_first = [int(i) for i in np.argsort(-lengths)]
embed(by_count(arrival, 32))  # warm-up, not reported
rows, reference = [], None
for name, batches in (("32 per batch, arrival order", by_count(arrival, 32)),
                      ("32 per batch, sorted by length", by_count(longest_first, 32)),
                      ("token budget 2048, arrival order", by_budget(arrival, 2048)),
                      ("token budget 2048, sorted by length", by_budget(longest_first, 2048))):
    vectors, seconds, padded = embed(batches)
    reference = vectors if reference is None else reference
    rows.append(dict(batching=name, batches=len(batches), texts_per_s=len(corpus) / seconds, padded_tokens=padded, padding_share=1 - lengths.sum() / padded))
print("\n--- batching, same encoder and texts, on the GPU")
print(pd.DataFrame(rows).round(3).to_string(index=False))

rows = []
sorted_batches = by_count(longest_first, 32)
for name, dtype in (("fp32", None), ("bf16 autocast", torch.bfloat16), ("fp16 autocast", torch.float16)):
    vectors, seconds, _ = embed(sorted_batches, dtype=dtype)
    rows.append(dict(precision=name, texts_per_s=len(corpus) / seconds, top10_kept_of_fp32=top10_overlap(reference, vectors)))
print("\n--- precision on the GPU, sorted batches of 32")
print(pd.DataFrame(rows).round(3).to_string(index=False))
del encoder
clear()

rows = []
sample = corpus[:600]
base = None
for name, kw in (("PyTorch fp32", dict(backend="torch")),
                 ("ONNX fp32", dict(backend="onnx")),
                 ("ONNX int8", dict(backend="onnx", model_kwargs=dict(file_name="onnx/model_qint8_arm64.onnx")))):
    st = SentenceTransformer(ENCODER, device="cpu", **kw)
    st.encode(sample[:32], batch_size=32, show_progress_bar=False)
    tick = time.perf_counter()
    v = st.encode(sample, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
    seconds = time.perf_counter() - tick
    base = v if base is None else base
    rows.append(dict(backend=name, texts_per_s=len(sample) / seconds, top10_kept_of_fp32=top10_overlap(base, v, 100)))
    del st
print("\n--- on the CPU, 600 texts")
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% Dynamic batching: how long to wait for a batch. Service times are measured here; only the queue is simulated.
encoder = AutoModel.from_pretrained(ENCODER).to(DEVICE).eval()
one = {n: timed(lambda n=n: embed([list(range(n))], encoder), repeats=5) for n in (1, 4, 16, 32, 64)}
print("\n--- measured seconds for one batch of the first n texts: " + ", ".join(f"{n}: {s * 1000:.0f} ms" for n, s in one.items()))
del encoder
clear()
sizes = np.array(list(one))
service = lambda n: float(np.interp(n, sizes, list(one.values())))


def queue(rate, wait, cap=64, n=20_000, seed=0):
    """A single worker. A batch leaves when it is full, or when its oldest request has waited `wait`, or as soon as the worker frees up after that."""
    rng = np.random.default_rng(seed)
    arrive = np.cumsum(rng.exponential(1 / rate, n))
    done, i, free = np.zeros(n), 0, 0.0
    while i < n:
        leave = max(arrive[i] + wait, free)
        j = int(np.searchsorted(arrive, leave, side="right"))
        j = min(j, i + cap, n)
        finish = leave + service(j - i)
        done[i:j] = finish
        free, i = finish, j
    late = done - arrive
    return float(np.percentile(late, 50) * 1000), float(np.percentile(late, 99) * 1000), n / (done[-1] - arrive[0])


capacity = 64 / service(64)
rows = []
for share in (.1, .5, .9):
    for wait in (0, .002, .010, .050):
        p50, p99, _ = queue(capacity * share, wait)
        rows.append(dict(load=f"{share:.0%} of capacity", wait_ms=wait * 1000, p50_ms=p50, p99_ms=p99))
print(f"\n--- a simulated queue over those service times; capacity {capacity:.0f} requests/s at batch 64")
print(pd.DataFrame(rows).pivot(index="load", columns="wait_ms", values=["p50_ms", "p99_ms"]).round(1).to_string())

# %% VLM: where one page's time goes
pages = make(16, 0, LAYOUTS[:3])
png = []
for image, _ in pages:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    png.append(buffer.getvalue())
print(f"\nPNG pages {np.mean([len(b) for b in png]) / 1e6:.2f} MB on average, {pages[0][0].size[0]}x{pages[0][0].size[1]} px")
model = load_model().eval()
rows = []
for edge in (512, 1024, 2048):
    proc = load_processor(edge)
    prompt = proc.apply_chat_template(chat(), add_generation_prompt=True, tokenize=False)
    image = Image.open(io.BytesIO(png[0])).convert("RGB")
    decode = timed(lambda: Image.open(io.BytesIO(png[0])).convert("RGB").load(), 5)
    prepare = timed(lambda: proc(text=prompt, images=[[image]], return_tensors="pt"), 5)
    b = proc(text=prompt, images=[[image]], return_tensors="pt")
    b = {k: v.to(DEVICE, dtype=torch.bfloat16) if k == "pixel_values" else v.to(DEVICE) for k, v in b.items()}
    with torch.inference_mode():
        encode = timed(lambda: model.model.get_image_features(pixel_values=b["pixel_values"], pixel_attention_mask=b.get("pixel_attention_mask")), 5)
        whole = timed(lambda: model.generate(**b, min_new_tokens=50, max_new_tokens=50, do_sample=False), 3)
    rows.append(dict(edge=edge, tiles=b["pixel_values"].shape[1], prompt_tokens=b["input_ids"].shape[1], decode_ms=decode * 1000, prepare_ms=prepare * 1000, encode_ms=encode * 1000,
                     generate_rest_ms=(whole - encode) * 1000, whole_ms=(whole + decode + prepare) * 1000, cpu_share=(decode + prepare) / (whole + decode + prepare), driver_gb=driver_gb()))
print("\n--- one page, 50 tokens out, GPU encoder and decoder, CPU decode and prepare")
print(pd.DataFrame(rows).round(3).to_string(index=False))

# %% Can the CPU keep the GPU fed? Pages per second from the preparing threads, against what the GPU can take
images = [Image.open(io.BytesIO(b)).convert("RGB") for b in png]
rows = []
for edge in (512, 1024, 2048):
    proc = load_processor(edge)
    prompt = proc.apply_chat_template(chat(), add_generation_prompt=True, tokenize=False)
    for threads in (1, 2, 4, 8):
        work = (png * 3)
        def prepare_one(b):
            return proc(text=prompt, images=[[Image.open(io.BytesIO(b)).convert("RGB")]], return_tensors="pt")
        tick = time.perf_counter()
        with ThreadPoolExecutor(threads) as pool:
            list(pool.map(prepare_one, work))
        rows.append(dict(edge=edge, threads=threads, pages_per_s=len(work) / (time.perf_counter() - tick)))
print("\n--- CPU decode and prepare, pages per second by thread count")
print(pd.DataFrame(rows).pivot(index="edge", columns="threads", values="pages_per_s").round(1).to_string())

# %% Batching a VLM, and asking a second question of the same page
proc = load_processor(512)
proc.tokenizer.padding_side = "left"
prompt = proc.apply_chat_template(chat(), add_generation_prompt=True, tokenize=False)
rows = []
for size in (1, 2, 4, 8):
    b = proc(text=[prompt] * size, images=[[images[i]] for i in range(size)], return_tensors="pt", padding=True)
    b = {k: v.to(DEVICE, dtype=torch.bfloat16) if k == "pixel_values" else v.to(DEVICE) for k, v in b.items()}
    with torch.inference_mode():
        seconds = timed(lambda: model.generate(**b, min_new_tokens=50, max_new_tokens=50, do_sample=False), 3)
    rows.append(dict(pages_in_batch=size, seconds=seconds, pages_per_s=size / seconds, driver_gb=driver_gb()))
print("\n--- batched generation, one 512 px tile, 50 tokens out")
print(pd.DataFrame(rows).round(3).to_string(index=False))

b = proc(text=prompt, images=[[images[0]]], return_tensors="pt")
b = {k: v.to(DEVICE, dtype=torch.bfloat16) if k == "pixel_values" else v.to(DEVICE) for k, v in b.items()}
with torch.inference_mode():
    features = model.model.get_image_features(pixel_values=b["pixel_values"], pixel_attention_mask=b.get("pixel_attention_mask"))
    features = getattr(features, "pooler_output", features)
    rest = {k: v for k, v in b.items() if k not in ("pixel_values", "pixel_attention_mask")}
    fresh = timed(lambda: model.generate(**b, min_new_tokens=50, max_new_tokens=50, do_sample=False), 5)
    cached = timed(lambda: model.generate(**rest, image_hidden_states=features, min_new_tokens=50, max_new_tokens=50, do_sample=False), 5)
    same = model.generate(**b, max_new_tokens=50, do_sample=False).tolist() == model.generate(**rest, image_hidden_states=features, max_new_tokens=50, do_sample=False).tolist()
print(f"\n--- the same page again: {fresh * 1000:.0f} ms encoding it fresh, {cached * 1000:.0f} ms from cached image features, same reply: {same}")
del model
clear()

# %% An adapter at serving time. Untrained weights: this measures speed only, and an r=8 adapter costs the same trained or not
base = load_model().eval()
b = proc(text=prompt, images=[[images[0]]], return_tensors="pt")
b = {k: v.to(DEVICE, dtype=torch.bfloat16) if k == "pixel_values" else v.to(DEVICE) for k, v in b.items()}
with torch.inference_mode():
    plain = timed(lambda: base.generate(**b, min_new_tokens=50, max_new_tokens=50, do_sample=False), 5)
wrapped = add_lora(base, TEXT_ONLY).eval()
wrapped.config.use_cache = True
wrapped.base_model.model.config.use_cache = True
with torch.inference_mode():
    attached = timed(lambda: wrapped.generate(**b, min_new_tokens=50, max_new_tokens=50, do_sample=False, use_cache=True), 5)
merged = wrapped.merge_and_unload().eval()
with torch.inference_mode():
    folded = timed(lambda: merged.generate(**b, min_new_tokens=50, max_new_tokens=50, do_sample=False, use_cache=True), 5)
print(f"\n--- one page, 50 tokens: base {plain * 1000:.0f} ms, adapter attached {attached * 1000:.0f} ms, adapter merged {folded * 1000:.0f} ms")
print(f"\nall done, {time.time() - started:.0f}s")
