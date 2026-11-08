---
origin: synthesis
sources:
  - https://arxiv.org/abs/2005.08100
  - https://arxiv.org/abs/2212.04356
  - https://arxiv.org/abs/2107.03312
  - https://arxiv.org/abs/2210.13438
  - https://arxiv.org/abs/2301.02111
  - https://arxiv.org/abs/2106.07447
  - https://arxiv.org/abs/2304.12995
  - https://arxiv.org/abs/2108.06209
  - https://arxiv.org/abs/2306.12925
  - https://arxiv.org/abs/2305.15255
  - https://arxiv.org/abs/2410.00037
  - https://github.com/QwenLM/Qwen2.5-Omni/blob/main/assets/Qwen2.5_Omni.pdf
  - https://github.com/MoonshotAI/Kimi-Audio/blob/master/assets/kimia_report.pdf
  - https://arxiv.org/abs/2305.17547
  - https://arxiv.org/abs/2308.15930
  - https://ai.meta.com/research/publications/omnilingual-asr-open-source-multilingual-speech-recognition-for-1600-languages/
confidence: medium
cleaned: 2026-11-01
---
# 4 — Speech and Voice Agents

> Speech gives the assistant a deadline. People expect a reply in a few hundred milliseconds and expect to interrupt it, so a voice agent's design starts from a latency budget and from what happens when the transcript is wrong.

The invoice assistant gets a phone line. A customer calls and says, "I think you charged me twice on the April invoice." The caller doesn't wait politely. They pause mid-sentence, cough, start talking over the reply, and the line drops a word. The text version of this assistant never had a clock on it, and this one has a hard one. Words that arrive three seconds late sound broken no matter how good they are. This chapter works through how speech gets recognised and produced, the two architectures for a voice agent, how to spend the latency budget, and how to measure a recogniser honestly. [The real-time agents note](../../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md) covers agent architecture for real-time systems, and this chapter stays with the engineering of the audio itself.

## Hearing: how speech recognition got robust

Modern recognisers combine local and global patterns in sound. Conformer put convolution and self-attention together in one block, and on LibriSpeech it reached 2.1% word error rate on test-clean with no language model, with a small 10M-parameter version at 2.7% ([arXiv:2005.08100](https://arxiv.org/abs/2005.08100) (Gulati et al., Interspeech 2020)). That is a clean-audio benchmark of people reading books. Your callers aren't reading books.

Whisper attacked robustness through data. It trained on about 680,000 hours of web audio, weakly supervised by whatever transcripts came with it, and it splits audio into 30-second segments. On clean LibriSpeech its score was unremarkable, at 2.5 WER, but it held up much better on harder sets such as CHiME-6 and TED talks ([arXiv:2212.04356](https://arxiv.org/abs/2212.04356) (Radford et al., ICML 2023)). Its decoder also predicts a `<|nospeech|>` token, trained on segments with no speech in them, so a model that outputs one can double as a rough voice activity signal. The authors found that WER across languages tracked training hours closely, with an r² of 0.83, which is a good warning for any language you are about to launch in: check how much audio trained the model in that language.

Coverage has continued to expand. Meta's Omnilingual ASR reports open models for over 1,600 languages, more than 500 of them not served by earlier systems, from 300M to 7B parameters ([Omnilingual ASR](https://ai.meta.com/research/publications/omnilingual-asr-open-source-multilingual-speech-recognition-for-1600-languages/) (Meta, 2025)). Kimi-Audio is an example of a current audio foundation model, trained on 13 million hours ([Kimi-Audio report](https://github.com/MoonshotAI/Kimi-Audio/blob/master/assets/kimia_report.pdf) (Moonshot AI, 2025)).

## Speaking: audio as tokens

Producing speech with a language model needs a compact sequence of discrete tokens that can stand in for audio. Neural codecs provide this. SoundStream compresses audio with an encoder, a residual vector quantizer and a decoder, and one model covers 3 to 18 kbps ([arXiv:2107.03312](https://arxiv.org/abs/2107.03312) (Zeghidour et al., IEEE/ACM TASLP 2022)). EnCodec does the same in real time, with a streaming architecture ([arXiv:2210.13438](https://arxiv.org/abs/2210.13438) (Défossez et al., TMLR 2023)). VALL-E showed that once speech is codec tokens, a language model can do text-to-speech with zero-shot voice cloning from a three-second sample ([arXiv:2301.02111](https://arxiv.org/abs/2301.02111) (Wang et al., 2023-01, preprint)). That power brings a real risk, which is covered in [chapter 9.1](../../09-safety-and-security/notes/01-threat-model.md).

Codec tokens are built to rebuild the waveform. A second kind of token comes from self-supervised recognisers and is built to predict what was said. HuBERT makes its targets offline. It clusters MFCC frames into 100 groups with k-means, trains a model to predict the cluster of each masked frame, then re-clusters that model's own layer-6 features into 500 groups and trains again. Each round gave better units. With 500 clusters each time, the share of phone uncertainty that the cluster label removes rose from 0.276 (MFCC) to 0.637 (round-1 layer 6) to 0.704 (round-2 layer 9), and dev-other word error fell from 18.40 to 10.75 (100k pre-training steps, 10-hour fine-tune). Putting the loss only on masked frames is what made noisy targets usable: on unmasked frames alone, training failed at 96.37 WER ([arXiv:2106.07447](https://arxiv.org/abs/2106.07447) (Hsu et al., IEEE/ACM TASLP 2021)). w2v-BERT learns its token IDs and predicts them in one pass, with a contrastive loss to keep the codebook alive. Without that loss, masked prediction collapsed every time they tried it. Pretrained on 60,000 hours of Libri-Light, the 0.6B model reached 1.5/2.9 WER on LibriSpeech test/test-other with no language model, and pretrained instead on 34,300 hours of English voice-search audio it cut WER from 8.9 to 6.2 against a matched contrastive baseline ([arXiv:2108.06209](https://arxiv.org/abs/2108.06209) (Chung et al., ASRU 2021)). Both papers test recognition only, on English. Neither generates speech from its units, and HuBERT lists generation as future work, so when a later speech model calls units like these its "semantic tokens", check its own evidence for that.

The token rate explains why this suits streaming. Kyutai's Mimi codec, used by Moshi, runs at 12.5 frames per second with 8 codebooks of 2,048 entries, which you can check directly:

```python
import math

frames_per_second = 12.5
codebooks = 8
codebook_size = 2048

bits_per_token = math.log2(codebook_size)
tokens_per_second = frames_per_second * codebooks
bitrate = tokens_per_second * bits_per_token

print(f"{tokens_per_second:.0f} tokens per second")
print(f"{bitrate / 1000:.1f} kbps")
print(f"one frame lasts {1000 / frames_per_second:.0f} ms")
print(f"raw 16-bit 24 kHz audio is {16 * 24000 / 1000:.0f} kbps, ratio {16 * 24000 / bitrate:.0f}x")
```

Output:

```text
100 tokens per second
1.1 kbps
one frame lasts 80 ms
raw 16-bit 24 kHz audio is 384 kbps, ratio 349x
```


A frame of 80 ms sets a floor on how quickly such a system can react, and 1.1 kbps is low enough to stream on nearly any connection. Multimodal models like AudioPaLM ([arXiv:2306.12925](https://arxiv.org/abs/2306.12925) (Rubenstein et al., 2023-06, preprint)) and Spectron ([arXiv:2305.15255](https://arxiv.org/abs/2305.15255) (Nachmani et al., ICLR 2024)) train language models directly on audio representations, which leads to the second architecture below.

## Two architectures

```mermaid
flowchart TD
    subgraph Cascade
      A1[Mic audio] --> B1[Voice activity detection]
      B1 --> C1[Speech to text]
      C1 --> D1[Language model and tools]
      D1 --> E1[Text to speech]
      E1 --> F1[Speaker]
    end
    subgraph Speech-to-speech
      A2[Mic audio] --> B2[Audio tokens]
      B2 --> C2[One multimodal model]
      C2 --> D2[Audio tokens]
      D2 --> F2[Speaker]
    end
```

**The cascade.** VAD finds speech, ASR writes it down, a language model thinks, TTS speaks. You can pick the best model for each stage, the transcript is text you can log and audit, and every existing text tool, including guardrails, works unchanged. The cost is latency, which accumulates at every stage, and the loss of anything that isn't words: tone, hesitation, a laugh. AudioGPT is the extreme case of a cascade: gpt-3.5-turbo reads the transcript, picks from the existing audio models behind its 15 supported tasks (Whisper, FastSpeech 2, a source separator, a talking-head generator) and passes files between them by name. The paper reports no scores. It shows a 12-round demo dialogue, and its own limits are prompt-writing effort, the context length and its dependence on each tool's accuracy ([arXiv:2304.12995](https://arxiv.org/abs/2304.12995) (Huang et al., AAAI 2024)).

**Speech-to-speech.** One model takes audio in and sends audio out. Moshi argues the case directly: compositional systems take several seconds where natural conversation needs a few hundred milliseconds, they lose non-linguistic information, and turn-based design ignores the 10 to 20% of spoken time that people overlap. Its model listens and talks in parallel streams at a theoretical 160 ms and about 200 ms in practice, on the authors' hardware. Its Inner Monologue method prefixes the audio output with its text transcript, which they report helps with both recognition and speech ([arXiv:2410.00037](https://arxiv.org/abs/2410.00037) (Défossez et al., 2024-10, preprint)). Qwen2.5-Omni's Thinker-Talker splits the same model into a reasoning part and a part that turns its hidden states into streaming audio, and reports that speech-instruction performance comes close to text on benchmarks like MMLU and GSM8K ([Qwen2.5-Omni report](https://github.com/QwenLM/Qwen2.5-Omni/blob/main/assets/Qwen2.5_Omni.pdf) (Qwen Team, 2025-03)).

Translation is the task where speech-to-speech first had to prove itself against the cascade. Translatotron 3 trains a direct Spanish-English model from monolingual speech only, with a masked autoencoder, an embedding-mapping loss and back-translation. On a proprietary synthesized conversational set it beat a weak unsupervised ASR+MT+TTS cascade by **13.27 BLEU (En→Es) and 18.14 (Es→En)**, and it carried the speaker's voice over (speaker-embedding similarity about 0.6, against about 0.16 for the cascade's random voices). The result is much thinner on real speech: on Common Voice Spanish to English it scored 10.67 BLEU against 9.92 for the cascade (the paper's Table 2 says 10.76), well behind supervised systems from other papers on Es→En (14.25 against 18.2 to 29.0 on the synthesized Common Voice 11 set). Every score is measured offline on short utterances, and the paper has no latency or streaming result ([arXiv:2305.17547](https://arxiv.org/abs/2305.17547) (Nachmani et al., 2023-05, preprint)).

A middle design keeps a recogniser's encoder and skips its transcript. LLaSM puts a Whisper encoder and a small trained adaptor in front of Chinese-LLAMA2-7B and replaces placeholder tokens in the prompt with the audio embeddings, in the way LLaVA does for images. Stage one trains only the adaptor on public ASR data, with Whisper and the LLM frozen. Stage two trains the adaptor and the LLM on 508k samples (199k conversations; 428k English, 80k Chinese) whose human turns were voiced with Azure text-to-speech. The authors argue this removes the ASR step and its errors. The paper reports no word error rate, benchmark or cascade baseline, only example conversations, and its speech inputs are synthetic, so the efficiency claim is untested. It also gives no learning rate, batch size or compute, and its output is text ([arXiv:2308.15930](https://arxiv.org/abs/2308.15930) (Shu et al., 2023-08, preprint)).

| | Cascade | Speech-to-speech |
|---|---|---|
| Latency | Sum of the stages | Low, can be full-duplex |
| Audit trail | Transcript at every step | You need to add one, such as a text track |
| Tone and emotion | Lost at ASR | Kept |
| Swapping a part | Replace one stage | Replace the model |
| Tool calls and business logic | Natural | Depends on the model's support |
| Guardrails | Standard text guards | Must work on audio or on a parallel transcript |

For a regulated use such as disputing a charge, the audit trail and tool calling usually decide it: a cascade today, with streaming in every stage. A companion or a tutor might go the other way. The decision also changes with time, since models with audio input and output keep gaining tool support, so re-check before you commit.

## Spending the latency budget

Treat response latency as a budget in milliseconds and write it down for each stage, with the figure measured at the 95th percentile. The numbers below are planning placeholders, not measurements of any product, so replace them with your own:

```python
budgets = {
    "cascade, batch stages": {
        "network in": 40, "VAD end of speech": 500, "ASR final": 300,
        "LLM to first token": 500, "LLM full reply": 900, "TTS full audio": 400, "network out": 40},
    "cascade, streaming": {
        "network in": 40, "VAD end of speech": 300, "ASR partial": 60,
        "LLM to first token": 400, "TTS first audio": 100, "network out": 40},
    "speech-to-speech": {
        "network in": 40, "model first audio": 200, "network out": 40},
}
TARGET = 800
for name, stages in budgets.items():
    total = sum(stages.values())
    worst = max(stages, key=stages.get)
    verdict = "within" if total <= TARGET else "over"
    print(f"{name:<24}{total:>6} ms  {verdict} {TARGET} ms  largest: {worst} ({stages[worst]} ms)")
```

Output:

```text
cascade, batch stages     2680 ms  over 800 ms  largest: LLM full reply (900 ms)
cascade, streaming         940 ms  over 800 ms  largest: LLM to first token (400 ms)
speech-to-speech           280 ms  within 800 ms  largest: model first audio (200 ms)
```


Two things stand out when you lay it out this way. Moving to streaming saves far more than a faster model would, because the listener only needs the first syllable, not the full reply. And even the streaming cascade is over target with these placeholders, with deciding that the person has finished as one of its largest lines, which isn't a model speed problem at all. Cut the VAD silence window too far and you interrupt people, so test this value on real callers. The remaining options are a smaller model for simple turns and a short spoken acknowledgement while a slower step runs.

## Finding the end of speech

The budget has a line called "VAD end of speech", and a faster server can't shrink it, because it waits on the caller. Here is what sits behind that line.

An energy VAD works on frames of about 20 ms. It computes each frame's level in decibels and calls the frame speech when that level clears the background noise by some margin. The naive version compares against a fixed threshold, so a quiet caller falls below it and a noisy line stays above it for a whole call. The better version tracks the floor, for example as the quietest smoothed level of the last two seconds, which is long enough that speech doesn't become the floor. Frame decisions flicker, because words have quiet stops inside them. So the detector asks for a few loud frames before it turns on, and a **hangover** keeps it on for about 120 ms after the level drops.

The **endpointer** sits on top of the VAD. It counts silence once the VAD has turned off, and when the count reaches the silence window it declares the turn finished. So the caller waits for the hangover plus the window. A short window replies sooner and cuts people off whenever they pause. A long window hears them out and adds silence to every turn. [`practice/voice_stream_lab.py`](../practice/voice_stream_lab.py) runs this on sample arrays. The audio is generated and isn't speech, with pause lengths we assumed, so read the shape of this table and not its values (300 generated calls of each kind at 20 dB SNR, hangover 120 ms):

| Silence window | Cut off, open talk | Cut off, digit strings | Added wait, p50 |
|---|---|---|---|
| 100 ms | 87.0% | 100.0% | 219 ms |
| 300 ms | 34.3% | 100.0% | 421 ms |
| 400 ms | 15.7% | 95.7% | 521 ms |
| 800 ms | 0.7% | 28.7% | 921 ms |
| 1200 ms | 0.3% | 7.0% | 1321 ms |

No single window serves a caller chatting and a caller reading out an account number with pauses between the groups. The dialogue knows which question it just asked, so let it choose. In the same setup, using 300 ms normally and 900 ms after asking for digits leaves open talk where it was, at 421 ms and 34.3% cut off, and cuts digit strings off 21.0% of the time, where a fixed 300 ms cut them off every time. The cost lands only on the digit question, which waits 1022 ms at the median.

The budget's 300 ms placeholder looks hopeful next to this. In the lab's full loop (200 generated calls, SNR mixed over 10, 20 and 30 dB, stage stubs drawn around the placeholders above), a 400 ms window gives a median wait of 540 ms and a median of 876 ms from end of speech to first audio, with a p95 of 1451 ms. Halving the window brings the median to 675 ms, and first audio within 800 ms goes from 19.5% of calls to 74.5%. But the agent talks over the caller on 24.5% of calls instead of 8.0%, and it makes 1.90 language model calls per call instead of 1.20, because every false endpoint starts a reply that then gets cancelled. On one more call (0.5%), the only reply began before the caller had finished. A shorter window buys its speed with those costs.

Energy has limits. It fires on coughs at every SNR in that test, and at 0 dB the detector with hangover misses 65.7% of speech frames. A trained VAD is the usual next step, and [the real-time agents note](../../../generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents.md#streaming-voice-perception-replacing-vad--asr) looks at replacing silence detection altogether. Test on real audio as well. An earlier floor tracker in this lab passed everything on generated audio, then stuck at the digital silence that opens a real clip and stayed on for 99% of its frames.

## Interruption is a state machine

People interrupt, and a voice agent that keeps talking feels broken. Handling this means stopping playback, discarding unspoken text, and telling the language model what the user actually heard, because its context otherwise claims it said everything it generated. Getting this wrong has real consequences. The agent can believe it read out a refund policy that the caller never heard. A small explicit state machine makes the behaviour testable:

```python
class Turn:
    def __init__(self):
        self.state = "listening"
        self.spoken = []
        self.queued = []
        self.history = []

    def reply(self, sentences):
        self.queued = list(sentences)
        self.state = "speaking"

    def tick(self):
        """One sentence finishes playing."""
        if self.state == "speaking" and self.queued:
            self.spoken.append(self.queued.pop(0))
            if not self.queued:
                self._commit(interrupted=False)

    def barge_in(self):
        if self.state == "speaking":
            self.queued.clear()
            self._commit(interrupted=True)

    def _commit(self, interrupted):
        text = " ".join(self.spoken)
        self.history.append({"role": "assistant", "text": text, "interrupted": interrupted})
        self.spoken = []
        self.state = "listening"

t = Turn()
t.reply(["I can see two charges on April.", "The second is a refund hold.", "It clears in five days."])
t.tick()
t.barge_in()  # caller talks over the second sentence
print(t.state)
print(t.history)
```

Output:

```text
listening
[{'role': 'assistant', 'text': 'I can see two charges on April.', 'interrupted': True}]
```


The history holds only what the caller heard, with a flag the model can see. A real implementation works on word timestamps from the TTS engine and not on whole sentences, but the invariant is the same, and you can write regression tests against it.

Two things sit outside that class. The first is deciding that a sound is an interruption at all. Stopping on the first loud frame lets every cough silence the agent, so the detector waits for a confirmation window, and energy alone can't tell a cough from a short "no". On generated events at 20 dB SNR, a 160 ms confirmation lets 91.0% of coughs stop the agent and misses 1.0% of short replies, while 320 ms lets through 34.0% of coughs and misses 77.5% of replies. Pausing at onset and resuming if the burst doesn't confirm is one way out. All of this assumes the agent's own voice has been removed from the caller's channel, since otherwise it interrupts itself. The lab assumes that too and doesn't model it.

The second is what cancellation reaches. In an asyncio loop, one reply can be a task group holding the LLM, TTS and playback tasks, so a barge-in cancels the group, and generation stops along with the audio. A tool call isn't part of the reply. Cancelling your side of a request doesn't undo what the server has already done, so a tool belongs to the call and outlives the turn that started it. The lab replays this with a refund in flight (40 generated calls, the tool takes an assumed 3 to 6 s, the money moves at 40% of that, and the LLM stub retries if history shows no refund):

| Version | Tokens generated after barge-in | Tokens in history the caller never heard | Refunds per call | Calls that re-issue it | Calls where the caller heard the outcome |
|---|---|---|---|---|---|
| Mute the speaker only | 21.1 | 34.5 | 1.00 | 0% | 92% |
| Cancel everything | 0.0 | 0.0 | 2.12 | 100% | 95% |
| Cancel everything, tool has an idempotency key | 0.0 | 0.0 | 1.00 | 100% | 100% |
| Cancel the turn, tool survives | 0.0 | 0.0 | 1.00 | 0% | 100% |

All four stop the audio at the same median, 215 ms after the caller starts, so that number can't tell them apart. The last column counts a caller as told only when the whole outcome sentence played. An agent that commits only what was heard can see a cut-off outcome and say it again. Muting can't, because its history says the sentence was spoken. Keep the key anyway, as [the tool design note](../../03-harness-engineering/notes/03-tool-design.md#write-operation-safety) says, because a line can drop and a retry can come from anywhere. And keep the loop itself free. In one wall-clock run of 8 calls on one loop, an LLM stub that blocked the loop instead of awaiting moved the median first audio from 898 ms to 2165 ms and left a microphone frame 831 ms late at worst. Those two numbers vary by machine.

## Measuring recognition honestly

Word error rate is substitutions, insertions and deletions over reference words. It looks simple, but small choices about text move it a lot. The Whisper authors built a text normaliser by inspecting failures, and found it could drop WER by up to 50% on some datasets because of quirks in reference transcripts, while warning that the same normaliser could end up tuned to their model's habits ([arXiv:2212.04356](https://arxiv.org/abs/2212.04356)). So compare systems with one shared normaliser, and report which one it was.

```python
import re

def normalise(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    for a, b in {"twenty": "20", "two": "2", "euros": "eur"}.items():
        text = re.sub(rf"\b{a}\b", b, text)
    return text.split()

def wer(ref, hyp):
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i]
        for j, h in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (r != h)))
        prev = cur
    return prev[-1] / max(1, len(ref))

ref = "You charged me twenty euros twice on the April invoice."
hyp_style = "you charged me 20 EUR twice on the april invoice"
hyp_wrong = "you charged me 70 euros twice on the april invoice"

raw = lambda s: s.split()
print("raw WER, style difference only :", round(wer(raw(ref), raw(hyp_style)), 3))
print("norm WER, style difference only:", round(wer(normalise(ref), normalise(hyp_style)), 3))
print("norm WER, wrong amount         :", round(wer(normalise(ref), normalise(hyp_wrong)), 3))

critical = {"20", "2"}
missed = critical & set(normalise(ref)) - set(normalise(hyp_wrong))
print("critical terms missed          :", missed)
```

Output:

```text
raw WER, style difference only : 0.5
norm WER, style difference only: 0.0
norm WER, wrong amount         : 0.1
critical terms missed          : {'20'}
```


The wrong-amount transcript scores about 10% WER, which might pass a threshold, while being the worst possible error for this product. So alongside WER, track recall on critical terms: amounts, dates, names, account numbers. Test across accents, handsets and noise, and report each group separately, since an average can hide a group the system fails.

For the agent as a whole, measure things the caller feels: time to first audio, how often it talks over people, how often it is interrupted, task completion, and how often callers repeat themselves. Repeats are a good proxy for recognition failure on live traffic without any reference transcripts.

If something downstream reads the transcript, such as a model that scores the call, recognition error becomes its input. Evaluate that step on the recogniser's output as well as on a clean transcript, and compare the two on the same calls, split by accent and channel.

## Pitfalls

- **Benchmarking on read speech.** Clean audiobook WER predicts little about a call centre. Build a test set from your own channel.
- **Confirming nothing.** A misheard amount becomes a real action. Read back any value you will act on, and confirm it before calling the tool.
- **Telling the model it said what it never said.** Commit only spoken text to history, as the state machine above does.
- **Treating the VAD threshold as a detail.** It decides both responsiveness and how often you cut people off.
- **Assuming a voice is proof of identity.** Short samples can clone a voice. Use a real authentication factor for account actions.
- **Forgetting audio retention rules.** Voice is often regulated personal data. Decide what is stored, where, and for how long, before you record.

## Try it

1. Change the Mimi numbers to 25 frames per second and 4 codebooks. What happens to the bit rate and the reaction floor, and what do you gain?
2. Add a "tool call in flight" state to `Turn`. What should `barge_in` do if the agent has already called a refund tool?
3. Compute WER on two reference sentences where one is 50 words and one is 5, each with one error. Why is averaging per-sentence WER misleading, and what should you do instead?
4. Run [`practice/voice_turn_lab.py`](../practice/voice_turn_lab.py). Why is the p95 of a whole turn lower than the sum of the stage p95s, and when does that stop being true? In its barge-in replay, what goes wrong in the version that drops the tool result? Which of its two made-up engines would you pick for a billing line?
5. Run [`practice/voice_stream_lab.py`](../practice/voice_stream_lab.py), which takes under a minute. In section 4, what did halving the silence window buy and what did it cost? In section 5, all four versions stop the audio equally fast, so why does "cancel everything" pay out about twice, and what does an idempotency key still leave wrong?

<details><summary>Answers</summary>

1. The bit rate is unchanged at 1.1 kbps (`25 × 4 × 11` bits), while the frame falls to 40 ms, halving the reaction floor. The cost is that each frame has fewer codebooks and so fewer bits, so audio quality is likely to suffer at the same rate, and the model must produce more frames per second.
2. Stop speaking, but don't discard the tool's outcome. The action may have happened, so record the tool result in history and tell the caller the true state on the next turn. Consequential actions should normally need confirmation before this point.
3. Per-sentence WERs are 2% and 20%, averaging to 11%, while the corpus WER is `2/55`, about 3.6%. Averaging over-weights short sentences, so divide total errors by total reference words across the corpus.
4. Independent stages rarely peak in the same turn: with our assumed spread the stage p95s add up to 940 ms while the turn's p95 is about 733 ms. If a shared slow spell moves every stage together, the turn's p95 is about 945 ms, so don't count on the gap. The naive version keeps listening with an empty history, so the next reply knows nothing about a refund that went through. For billing, take engine B: its corpus WER is worse (0.051 against 0.035), but it recalls critical terms at 0.98 against 0.82.
5. Going from 400 ms to 200 ms moved median first audio from 876 ms to 675 ms and first audio within 800 ms from 19.5% to 74.5%. It raised calls where the agent talked over the caller from 8.0% to 24.5%, and language model calls from 1.20 to 1.90 per call, and on 0.5% of calls the only reply began before the caller finished. "Cancel everything" cancels the client, but the refund has usually gone through on the server, and nothing in history says so, so the model tries again: 2.12 refunds per call. A key holds that to 1.00, yet the agent still sent the request again in 100% of calls, because it lost track of the first one. Of the versions that cancel the turn, only the one where the tool survives gets 1.00 refunds and 0% re-issued.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Cascade or speech-to-speech for a banking agent? | Usually a cascade with streaming, because of the transcript for audit, standard guardrails and mature tool calling, accepting more latency. Revisit as speech-to-speech models improve on those points. |
| Where does cascade latency go? | End-of-speech detection, the time to the LLM's first token, and the first TTS audio. Streaming every stage helps more than a faster model, since only the first audio matters for perceived speed. |
| What is a neural codec's role in a voice model? | It turns audio into a compact sequence of discrete tokens a language model can predict, at low bit rates. Its frame length sets a floor on reaction time. |
| Why is WER not enough? | It weights every word equally, so a wrong amount looks like a wrong article. Add recall on critical terms, and break results down by accent and channel. |
| How should a text normaliser be handled? | Use one shared normaliser for all compared systems and report it. It can change WER by a large margin, and it can be fit, even by accident, to one model's habits. |
| What must happen on barge-in? | Stop playback, drop the unspoken text, record only what was heard, and preserve any tool result already obtained, so that the model's context matches reality. |
| How do you set the silence window? | By dialogue state and by measurement. It trades cut-off callers against added wait, one value can't serve open talk and read-out digits, and a short window also wastes LLM calls on false endpoints. |
| Does cancelling a task on barge-in cancel the tool call? | It shouldn't, and it can't undo the server anyway. Cancel the turn's tasks, let the call own the tool, record the outcome, and use an idempotency key against retries. |

## Next

[Chapter 5 — How image generators work](05-how-image-generators-work.md) turns from understanding media to making it, starting with how a diffusion model gets from noise to a picture.
