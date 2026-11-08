---
origin: synthesis
sources:
  - "Phoenix & Taylor, Prompt Engineering for Generative AI (O'Reilly, 2024), ch. 7, 9"
  - https://arxiv.org/abs/2301.13188
  - https://arxiv.org/abs/2309.17421
  - https://huggingface.co/docs/diffusers
  - https://arxiv.org/abs/2410.00037
  - https://arxiv.org/abs/2410.13720
  - https://arxiv.org/abs/2304.08818
  - https://arxiv.org/abs/2307.04725
  - https://arxiv.org/abs/2010.02502
  - https://arxiv.org/abs/2205.11487
  - https://arxiv.org/abs/2102.12092
  - https://arxiv.org/abs/2206.10789
  - https://arxiv.org/abs/2105.05233
  - https://arxiv.org/abs/2207.12598
  - https://arxiv.org/abs/2112.10741
  - https://arxiv.org/abs/1809.11096
  - https://arxiv.org/abs/1706.08500
  - https://arxiv.org/abs/1606.03498
  - https://arxiv.org/abs/1801.03924
  - https://arxiv.org/abs/2204.03458
  - https://arxiv.org/abs/2308.16512
  - https://arxiv.org/abs/2601.20540
confidence: medium
cleaned: 2026-11-01
---
# 6 — Generating Images and Video

> An image model is a sampler you steer with a handful of numbers. Pin the seed, the sampler and the guidance scale, or you can't reproduce an image. Use masks and control images for edits. Fine-tune only when prompting can't name the subject. Treat any model you don't host as a dependency that can be withdrawn.

---

The invoice assistant's help pages need illustrations, and the first images looked good until someone asked for the same picture with one change. Nobody had recorded the seed, the model version had moved, and the original couldn't be reproduced. Image generation in production is mostly this kind of engineering: recording settings, editing without re-rolling, and deciding what you can rely on. [Chapter 5](05-how-image-generators-work.md) explains the mechanism. This chapter is about the controls.

## The controls

Every image API and local UI exposes some subset of these. Log all of them with every generated image.

| Control | What it does | Starting value (*Prompt Engineering for GenAI*, ch. 9) |
|---|---|---|
| **Seed** | Fixes the starting noise. Same seed + same settings + same model = same image | Any fixed integer. Reuse the seed of an image you liked when editing it |
| **Steps** | Number of denoising steps | 20–30 for most samplers; 50 in the diffusers example |
| **CFG scale** (`guidance_scale`) | How hard the denoiser follows the prompt instead of its own prior | 1 = no guidance, prompt followed loosely · 3 creative · **7 balanced** · 15 adhere · 30 strict |
| **Sampler** | The numerical method that walks from noise to image | DPM++ 2M Karras or UniPC at 20–30 steps for stable, reproducible output |
| **Negative prompt** | Concepts to steer away from | `lowres, bad anatomy, worst quality` and the like |
| **Denoising strength** (img2img, inpainting) | How far the output may move from the input image: 0 returns the input, 1 ignores it | 0.2–0.4 for small fixes; up to 0.8 to replace an element |

**What the CFG scale trades.** Guidance began as classifier guidance: push each denoising step along the gradient of a separate image classifier. On class-conditional ImageNet 256×256, raising the scale from 1 to 10 lifted precision from 0.82 to 0.88 but cut recall, the share of the real distribution the samples cover, from 0.52 to 0.32. FID worsened from 4.59 to 9.11 ([arXiv:2105.05233](https://arxiv.org/abs/2105.05233) (Dhariwal & Nichol, NeurIPS 2021), Table 4). Classifier-free guidance removes the classifier. Training drops the prompt 10–20% of the time, so one network learns both a conditional and an unconditional prediction. Sampling then extrapolates away from the unconditional one: ε̃ = (1 + w)·ε(z, c) − w·ε(z). On ImageNet 64×64 the best FID came at almost no guidance (w = 0.1, FID 1.55). Inception Score kept rising to w = 4, where FID had degraded to 26.2 ([arXiv:2207.12598](https://arxiv.org/abs/2207.12598) (Ho & Salimans, NeurIPS 2021 workshop, preprint), Table 1). diffusers' `guidance_scale` is 1 + w, so the usual 7 sits far past the FID optimum. **That is deliberate: text-to-image buys prompt adherence with diversity.** Three costs follow:

- **Each step runs the model twice**, once with the prompt and once without, which the CFG paper names as its main drawback. A guidance scale of 1 skips the second pass.
- **High scales oversaturate.** Imagen traced the burnt colors to predicted pixels leaving the training range, and clips them at each step (dynamic thresholding) ([arXiv:2205.11487](https://arxiv.org/abs/2205.11487), §2.3).
- **Guiding toward a scorer games the scorer.** GLIDE compared CLIP guidance with classifier-free guidance. CLIP guidance raised the CLIP score more, but human raters preferred classifier-free guidance for both photorealism and caption match. The authors read the gap as adversarial examples against CLIP ([arXiv:2112.10741](https://arxiv.org/abs/2112.10741) (Nichol et al., ICML 2022)). The same caution applies to any automatic score used to pick images (see [Sweep, don't guess](#sweep-dont-guess)).

The older GAN version of the same knob is BigGAN's truncation trick: resampling latent values above a threshold trades variety for fidelity ([arXiv:1809.11096](https://arxiv.org/abs/1809.11096) (Brock et al., ICLR 2019)).

**Don't write "no X" in the prompt.** Parti tends to draw whatever the prompt mentions. "A plate that has no bananas on it" came back with bananas. The paper's failure catalogue also lists color bleeding between objects and counting that holds up to about seven objects of one kind, then fails, and fails almost completely when the prompt counts several kinds ([arXiv:2206.10789](https://arxiv.org/abs/2206.10789), Limitations). Put exclusions in the negative prompt. In diffusers it takes the place of the unconditional pass, so guidance pushes away from it. Expect to fix counts and multi-object layouts with control images, not prompt wording.

**Ancestral samplers are not reproducible.** Samplers with an *a* in the name (Euler a and others) inject fresh noise at each step, so the image never converges and a fixed seed doesn't pin it (ch. 9). DDIM makes the split explicit with one parameter, η: η = 0 is deterministic and η = 1 is the stochastic DDPM sampler. Only the deterministic end is *consistent*: the same starting noise sampled with different step counts gives images with the same high-level features ([arXiv:2010.02502](https://arxiv.org/abs/2010.02502), §5.2). So you can preview a seed at 10 steps and render it at 50. If a pipeline needs to regenerate an asset exactly (a product shot, a test fixture), use a non-ancestral sampler and record the library version too.

A minimal self-hosted call with Hugging Face `diffusers`, with every control set explicitly:

```python
# illustrative: needs a CUDA GPU and downloaded SDXL weights
import torch
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16
).to("cuda")

image = pipe(
    prompt="an illustration of computers tied together, corporate memphis, white background",
    negative_prompt="lowres, blurry, text, watermark",
    num_inference_steps=30,
    guidance_scale=7.0,
    generator=torch.Generator("cuda").manual_seed(1024),  # the seed
).images[0]
image.save("out.png")
```

The book's version (ch. 9) pins `diffusers==0.11.1` and loads `CompVis/stable-diffusion-v1-4`. Both still illustrate the API, but neither is what you would deploy today.

### Prompt syntax in local UIs

AUTOMATIC1111 (and UIs that copied its syntax) parse weights out of the prompt (ch. 9):

- `(pirate)` multiplies the term's attention weight by 1.1, `((pirate))` by 1.21, `(pirate:1.5)` by 1.5. `[hat]` is 0.9.
- A down-weighted term is not a negative prompt. The term is still present, only weaker. Weights also work inside the negative prompt, to push a concept out harder.
- **Prompt editing** `[from:to:when]` switches prompts partway through sampling (`when` is a step count or a fraction). The early steps fix the shapes from `from`, and the late steps paint details from `to`.

This syntax belongs to the UI, not the model. Hosted APIs take a plain string, or a list of prompts with weights. The Stability v1 REST API took `text_prompts: [{text, weight}]`. Don't expect `(x:1.5)` to mean anything there.

The book suggests blending two celebrities with prompt editing so the result looks "vaguely familiar" without being recognizable, as a more ethical and legally sound option (ch. 9). Don't adopt that as policy. A blended likeness can still be recognizable, and right-of-publicity law doesn't care how you got there.

### Sweep, don't guess

The parameters interact: CFG and denoising strength, for example. The cheapest way to find good settings is a grid: fix the prompt and seed, vary two or three parameters, and render every combination (AUTOMATIC1111's X/Y/Z plot script, ch. 9). This is the image version of an eval sweep. It is only affordable when you host the model, or when per-image API prices are low enough to render a grid of dozens.

A vision-language model can do the first pass over the grid. GPT-4V rated prompt–image alignment on a 1–10 scale, giving 4 → 8 → 9 to three successively improved samples for "a parrot driving a car". It also caught misspelled text rendered on a cake ("Azuze Research" for "Azure Research"), and in a generate–critique–rewrite loop with SDXL it added the missing dog breed to the prompt ([arXiv:2309.17421](https://arxiv.org/abs/2309.17421) (Yang et al., 2023-09), §9.6, §10.3). These are hand-picked examples from an early GPT-4V, with no benchmark. Use a VLM judge to triage a grid and spot-check its scores before you trust them.

Generating many images and keeping the best is an old trick. DALL-E kept the best of 512 by CLIP score ([arXiv:2102.12092](https://arxiv.org/abs/2102.12092)). Parti's reranker helped with counting: for "five red apples", the top six images all had five apples, and further down the ranking the counts drifted from four to six ([arXiv:2206.10789](https://arxiv.org/abs/2206.10789)). Best-of-N costs N images, and as GLIDE showed, the more you select on a score, the more you select for the score's blind spots.

**Know what each automatic score measures.**

| Score | Measures | Use it for | Don't use it for |
|---|---|---|---|
| **FID** ([arXiv:1706.08500](https://arxiv.org/abs/1706.08500) (Heusel et al., NIPS 2017)) | Distance between the Inception-feature statistics (mean and covariance) of a generated set and a real set | Comparing models or settings over thousands of images | Scoring one image. It also misses compositional prompts: Imagen's encoders tied on COCO FID but split on DrawBench |
| **Inception Score** ([arXiv:1606.03498](https://arxiv.org/abs/1606.03498) (Salimans et al., NIPS 2016)) | Confident, varied ImageNet labels on generated images, with no comparison to real data | Legacy comparisons only. Its authors say it needs about 50k samples | Anything outside ImageNet-like objects |
| **CLIP score** | Image–text embedding similarity | Triage, at a scale where a model isn't being optimized against it | A target to guide or select hard on (see GLIDE above) |
| **LPIPS** ([arXiv:1801.03924](https://arxiv.org/abs/1801.03924) (Zhang et al., CVPR 2018)) | Perceptual distance between two images, from deep features | Checking that an edit or upscale didn't change too much | Prompt alignment |

LPIPS is the one that holds up against people. On its 2AFC similarity tests humans agreed with each other 73.9% of the time, and ImageNet-trained networks scored 67–69%. L2, SSIM and FSIM all came in around 63%, so don't gate an image pipeline on SSIM.

## Editing and customizing

Masks, control images, img2img, Segment Anything, LLM-driven editing, and the customization methods (DreamBooth, Textual Inversion, LoRA) moved to [6b — Editing and customizing images](06b-editing-and-customizing-images.md). The controls above are what you log; the editing tools there are how you change one region without a re-roll.

## Hosted API or self-hosted

| | Hosted API | Self-hosted (diffusers, a local UI) |
|---|---|---|
| Cost | Per image. The book's figure for Stability's API: 1,000 credits for $10, about 5,000 images (ch. 9). Check current prices | GPU time. Sweeps and grids are cheap once the hardware is paid for |
| Control | What the vendor exposes: usually prompt, size, steps, CFG, seed | Everything: samplers, ControlNet, LoRAs, prompt syntax, custom pipelines |
| Stability | **The model can be withdrawn.** Stability deprecated the more permissive SD 1.5 in favor of 2.0 and XL, and users who had tuned prompts and parameters to it lost them (ch. 9) | You pin the weights, so the model doesn't change unless you change it |
| Safety | The vendor filters prompts and outputs | You own filtering, and the legal exposure |

Two operational rules from the self-hosted side (ch. 9):

- **Load `.safetensors`, never untrusted `.ckpt`.** A `.ckpt` is a Python pickle and can execute code when loaded. Community model hubs are a supply chain; see [09-safety-and-security](../../09-safety-and-security/README.md).
- **Split composition and detail across models when quality matters.** SDXL's base model sets composition and an optional refiner adds detail. "Switch at 0.6" with 30 steps runs 18 base steps and then 12 refiner steps. The book's best results came from 0.6 at 30 steps, with 0.4–1.0 and 20–50 steps the usual range.

**SDXL size, clarified.** The book gives SDXL 1.0 as "6.6 billion parameters, compared to 0.98 billion for the v1.5 model" (ch. 7, 9). Stability's 6.6B figure is the base-plus-refiner ensemble. The base model alone is about 3.5B, so compare 3.5B with 0.98B when choosing hardware.

## Provenance and training-data risk

**Metadata is the cheapest provenance, and the most fragile.** AUTOMATIC1111 writes the prompt and every setting into each PNG's metadata. That makes an image reproducible, but the metadata survives only until a site strips it on upload (ch. 9). Store generation parameters in your own database keyed by image hash; don't rely on the file. Signed manifests such as C2PA Content Credentials (not covered in the book) are the industry route for marking output as AI-generated. Invisible watermarks in the pixels or samples are weaker than they look. Moshi's authors found that an AudioSeal mark on 10-second clips, detected at 0.9999, dropped to 0.08 after one pass through their Mimi audio codec, which is no different from unmarked audio (0.09). They also note that removing the watermark from Stable Diffusion's open-source code took commenting out one line ([arXiv:2410.00037](https://arxiv.org/abs/2410.00037) (Défossez et al., 2024-09), §6.4). Re-encoding the media erases the mark, so treat a watermark as a hint, never as proof of origin.

**Memorization is rare, but not zero.** The book cites Carlini et al. to argue that a diffusion model is not a collage tool: of 350,000 training images the researchers tried to reproduce from Stable Diffusion, they succeeded with 109 (ch. 7; [arXiv:2301.13188](https://arxiv.org/abs/2301.13188), Carlini et al., 2023-01). The paper chose those 350,000 as the *most duplicated* images in the training set, where memorization is likeliest, so 109 is a floor for heavily duplicated content, not a rate for typical images. The engineering reading is that output can occasionally reproduce a training image nearly exactly, most likely for famous artworks, logos and stock photos, and that a rare copy is still a copy. Prompts that name a living artist or a trademark raise the odds.

**Mitigating bias is part of the product, and clumsy fixes backfire.** DALL-E 2 was found to silently append words like "black" or "female" to prompts such as "a photo of a doctor", to offset a skew in its training data. Google's Gemini image generation drew criticism in early 2024 for a similarly clumsy attempt (ch. 7). If your system rewrites prompts, log the rewritten prompt next to the user's, so you can audit what the model was actually asked.

The labs' own first answer was to withhold the model or filter its training data. Google didn't release Imagen. Its paper reports a bias toward lighter skin tones and Western gender stereotypes for professions, and weaker photorealism on people: raters preferred Imagen over real COCO images 39.2% of the time overall, and 43.6% once images of people were removed ([arXiv:2205.11487](https://arxiv.org/abs/2205.11487), human evaluation and limitations). OpenAI released only a small 300M GLIDE trained on data with all people, and some violent images and hate symbols, filtered out ([arXiv:2112.10741](https://arxiv.org/abs/2112.10741), Safety Considerations). Filtering removes a capability as well as a risk, so expect a model released this way to be weak on whatever was filtered out.

### Record it or lose it

Most of the checklist below reduces to storing a provenance record next to every image, and refusing to call an image reproducible unless the record supports that. The sketch below stores a sidecar and computes a key that changes when any setting that affects pixels changes.

```python
import hashlib, json

PIXEL_FIELDS = ["model_id", "weights_sha256", "seed", "sampler", "steps", "cfg",
                "width", "height", "prompt", "negative_prompt"]
ANCESTRAL = {"euler a", "dpm2 a", "dpm++ 2s a"}

def provenance_key(rec):
    payload = json.dumps({k: rec.get(k) for k in PIXEL_FIELDS}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def reproducibility_problems(rec):
    problems = [f"missing {k}" for k in PIXEL_FIELDS if rec.get(k) in (None, "")]
    if rec.get("sampler", "").lower() in ANCESTRAL:
        problems.append("ancestral sampler: treat exact regeneration as unsupported")
    if rec.get("rewritten_prompt") and rec["rewritten_prompt"] != rec.get("prompt"):
        problems.append("hosted API rewrote the prompt: store and regenerate from the rewrite")
    return problems

rec = {"model_id": "sdxl-base-1.0", "weights_sha256": "31e35c80", "seed": 1024,
       "sampler": "DPM++ 2M", "steps": 30, "cfg": 7.0, "width": 1024, "height": 1024,
       "prompt": "an illustration of computers tied together",
       "negative_prompt": "lowres, blurry"}
print("key            :", provenance_key(rec))
print("problems       :", reproducibility_problems(rec))
print("one step more  :", provenance_key(dict(rec, steps=31)))
print("ancestral run  :", reproducibility_problems(dict(rec, sampler="Euler a")))
print("hosted rewrite :", reproducibility_problems(dict(rec, rewritten_prompt="a vivid illustration of computers")))
print("no seed stored :", reproducibility_problems({k: v for k, v in rec.items() if k != "seed"}))
```

Output:

```text
key            : 1569d5aeba09ac46
problems       : []
one step more  : 5641469badee7b81
ancestral run  : ['ancestral sampler: treat exact regeneration as unsupported']
hosted rewrite : ['hosted API rewrote the prompt: store and regenerate from the rewrite']
no seed stored : ['missing seed']
```


Use the key to deduplicate and cache, and run the problems check when an image is stored, not when someone later asks for a variation. By then it is too late.

## Video

The book doesn't cover video prompting. It records the timeline up to early 2024: RunwayML's Gen-2, AnimateDiff in the open-source community, Stable Video Diffusion (November 2023), and OpenAI's Sora (February 2024). It claims everything about image prompting carries over (ch. 7). The controls above do carry over: seed, steps, guidance, and an image as a conditioning input (image-to-video). What doesn't carry over is cost, since each second of video is many frames, and consistency between frames, which no single-image setting controls.

Video diffusion began as image diffusion with a time axis. Video Diffusion Models factorized a 3D U-Net into spatial layers, applied per frame, and temporal attention across frames. It trained on 16 frames at a time ([arXiv:2204.03458](https://arxiv.org/abs/2204.03458) (Ho et al., NeurIPS 2022)). Three of its findings still shape video tools:

- **Images help video.** Adding 8 independent images per 16-frame clip cut FVD from 202.28 to 57.84 on 16×64×64 text-to-video. Captioned images are far more plentiful than captioned clips.
- **Guidance trades the same way it does for images.** At guidance weight 5 the per-frame Inception Score rose, but FVD rose from 41.65 to 163.74, so the video got worse as a whole.
- **Long clips are extended, not generated in one pass.** Conditioning each new block of frames by simply copying in the previous block lost temporal coherence (FVD 451.45 for 64 frames). Reconstruction guidance, which steers the new block toward agreeing with the old one, scored 136.22. Each extension is conditioned only on the frames before it, so check coherence across block boundaries, not just within a clip.

The open video models of 2023 started from a frozen image model and trained only new temporal layers. Video LDM inserts temporal attention and 3D-convolution layers between Stable Diffusion's frozen spatial layers and fine-tunes the autoencoder's decoder on video. Without that decoder fine-tune, reconstruction FVD on driving footage is 390.88; with it, 32.94 ([arXiv:2304.08818](https://arxiv.org/abs/2304.08818) (Blattmann et al., 2023-04)). Because the image layers stay frozen, the temporal layers drop into a DreamBooth-personalized checkpoint without retraining. Its zero-shot UCF-101 FVD of 550.61 still trailed Make-A-Video's 367.23. AnimateDiff turned this into the community workflow: a motion module trained once on SD 1.5 plugs into any personalized SD 1.5 checkpoint, and a MotionLoRA of about 30 MB learns a camera move from 20–50 reference clips in 1–2 hours ([arXiv:2307.04725](https://arxiv.org/abs/2307.04725) (Guo et al., 2023-07)). Its quantitative evidence is thin: a user ranking and CLIP scores against two adapted baselines, on prompts the authors chose.

The same reshaping of attention carries image models to 3D. Text-to-3D methods descended from DreamFusion fit a 3D model so that every rendered view scores well under a 2D diffusion model. That model sees one view at a time, so it keeps redrawing the prompt's subject on every side, as in the "Janus" horse with two faces. MVDream fine-tunes Stable Diffusion 2.1 to generate four views at once ([arXiv:2308.16512](https://arxiv.org/abs/2308.16512) (Shi et al., ICLR 2024)). It reshapes the existing self-attention so all views attend to each other, adds a camera embedding, and trains on renders of about 350K Objaverse objects mixed 70/30 with LAION images. In its ablation, a single-view camera-conditioned model still made Janus faces, and four views all but removed them. Used as the prior for 3D fitting, 78% of 914 user votes preferred it over four re-implemented baselines. There is no quantitative 3D metric, the output is 256×256, and the textures look like the rendered training set.

Meta's Movie Gen shows what frame count costs at scale. It is a 30B transformer trained with flow matching on video latents compressed 8×8×8, and a 16-second 768px clip at 16 fps fills a context of about 73K tokens ([arXiv:2410.13720](https://arxiv.org/abs/2410.13720) (Polyak et al., 2024-10)). In Meta's own human evaluation its net win rate on overall quality was +35.0 against Runway Gen3, +8.2 against Sora, and +3.9 against Kling 1.5, which the paper counts as on par. Sora could only be judged on the videos OpenAI chose to publish, so Meta compared them with a hand-picked best of five from Movie Gen.

A video model that responds to controls while it generates is a **world model**. LingBot-World starts from the open Wan2.2 image-to-video model, adds adapters for camera pose and WASD keys, and trains on clips that grow from 5 to 60 seconds ([arXiv:2601.20540](https://arxiv.org/abs/2601.20540) (Robbyant Team, 2026-01, preprint)). For real-time use it switches to block-causal attention with a KV cache, the decoding setup of a language model, and distils to a few denoising steps. The distilled version runs at 16 fps at 480p with under 1 s of latency on one GPU node. On VBench over 100 videos longer than 30 s it beat two open world models on imaging quality (0.668 against 0.584 and 0.651) but not on smoothness or flicker. Genie 3 appears only as a feature checklist, with no numbers. The weights are open; the training data and compute are not described. Its memory is only the context window, so scenes drift over long runs.

## What has dated

The chapters were written in 2023 for a 2024 book. Still sound: the controls table, the editing workflow, the customization trade-offs and the self-host vs. API comparison. Dated:

- The model lineup (DALL-E 2/3, Midjourney v5, SD 1.5/2/XL) and Stability's credit prices.
- "LoRA is experimental", as in [6b](06b-editing-and-customizing-images.md#customizing-a-model).
- The diffusers version, and the `CompVis/stable-diffusion-v1-4` and `runwayml/stable-diffusion-v1-5` model IDs.
- AUTOMATIC1111 as the default power-user UI.

## Checklist

- [ ] Every generated image is stored with its model ID and version, seed, sampler, steps, CFG, prompt and negative prompt, and any rewritten prompt.
- [ ] Pipelines that must regenerate an image exactly use a non-ancestral sampler.
- [ ] Self-hosted weights are `.safetensors`, pinned by hash.
- [ ] A hosted model's deprecation would not break the product: prompts and settings are versioned per model.
- [ ] Prompts naming living artists, trademarks or real people are filtered or reviewed.

## Pitfalls

- **Storing the image without its settings.** You can't produce a small variation later, and you can't answer where a picture came from.
- **Pinning a model name without pinning weights.** A hosted model can change under the same name. Self-hosted weights should be pinned by hash.
- **Scoring with one metric.** Each metric in the table above misses something. CLIP score in particular stops being useful once you select on it hard.
- **Treating training-data risk as a legal footnote.** Generators can reproduce memorised images, and prompts naming real people need review before an image ships.

## Try it

1. Add `control_image_sha256` and `lora_sha256` to `PIXEL_FIELDS`. Why must a missing optional field not count as a problem, and how would you express that?
2. You must regenerate an image made six months ago by a hosted API. Which fields in the record can you actually rely on, and what is your fallback?
3. Write a sweep plan for three guidance values and three step counts that uses the seed correctly. How many images do you need for a fair comparison with four seeds?

<details><summary>Answers</summary>

1. Most images don't use a LoRA or control image, so absence is legitimate. Keep required and optional lists separately, and hash both while checking only the required ones. The optional fields still belong in the key, because they change the pixels.
2. You can rely on the prompt, the seed if the API returned it, and your own stored image. You can't rely on the model staying available, so the realistic fallback is to edit the stored image with a mask or img2img, not to regenerate it.
3. Use the same four seeds in every cell, so that seed variation doesn't look like a setting effect: `3 × 3 × 4 = 36` images. Change only guidance and steps, and compare within a seed.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Which settings must you store to reproduce an image? | Model and exact weights, seed, sampler, steps, guidance, size, prompt and negative prompt, plus any rewritten prompt or extra weights and control inputs. |
| Why do ancestral samplers break reproducibility work? | They inject fresh noise at each step, so the image never converges and small changes in settings move it unpredictably. |
| API or self-hosted? | API for low volume and fast start, self-hosted for control, privacy, pinned weights and high volume. A hosted model is a dependency that can be withdrawn. |
| How do you evaluate generated images? | Combine a distribution metric such as FID for model comparison, CLIP-style scores for triage, and structured prompt-adherence checks and human review for what users will actually see. |

## Next

[Chapter 6b — Editing and customizing images](06b-editing-and-customizing-images.md) covers the edits and the customization methods this chapter points to. Then [chapter 7 — Evaluating multimodal systems](07-evaluating-multimodal-systems.md) gathers the measurement ideas from this pillar and adds the tests that stop a model scoring well for the wrong reasons.
