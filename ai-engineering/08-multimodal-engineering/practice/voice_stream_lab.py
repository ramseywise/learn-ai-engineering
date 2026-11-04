# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy"]
# ///
"""A voice agent's real-time loop on audio samples, for notes/04: VAD, endpointing, and barge-in by task cancellation.

Run from this folder (under a minute on a laptop CPU, no API key, downloads no data):
    uv run voice_stream_lab.py
    uv run voice_stream_lab.py --silence-ms 250 --hangover-ms 60 --barge-confirm-ms 100   # move a knob, watch the tables move

The checks about what the default setup shows are asserts at the defaults. Move a knob and they print as warnings, because
a moved knob is allowed to break them. Checks that hold for any setting, such as history matching what was played, stay asserts.

Optional, off by default, downloads a Whisper model (about 75 MB) and a public speech clip into ~/.cache:
    uv run --with faster-whisper voice_stream_lab.py --asr              # a short public clip of real speech
    uv run --with faster-whisper voice_stream_lab.py --asr my_clip.wav  # or your own WAV file

voice_turn_lab.py draws stage latencies and never touches audio. This lab builds on it and processes sample arrays,
20 ms at a time.

What is real: the samples are numpy arrays read frame by frame. The VAD, the endpointer and the asyncio pipeline with its
queues and task cancellation run as written, and end-of-speech-to-first-audio is measured off the running loop.
What is generated: the audio. The waveforms are built from a seed and ARE NOT SPEECH. They are harmonic stacks with a
syllable-rate envelope, plus noise bursts that stand in for coughs and pink noise at a chosen SNR. Pause lengths are our
assumption, not measured from callers.
What is a stub: STT, LLM, TTS and the refund backend. They consume and produce real streams, but their timing is a draw
around the note's planning placeholders and their text is scripted.
What is left out: echo. Every barge-in here assumes the agent's own voice has been removed from the caller's channel.

Sections 1 to 5 run on a virtual clock: a real asyncio loop whose clock jumps to the next timer, so hundreds of calls take
seconds and the output repeats exactly for a seed. Section 6 runs on the wall clock, so its numbers vary by machine.
Every number describes these assumptions, not any product.
"""
# %%
import argparse
import asyncio
import math
import random
import re
import selectors
import statistics
import sys
import time
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from voice_turn_lab import SPREAD, STREAMING_P95, TARGET_MS, draw, edits, percentile

SEED = 7
SR, FRAME_MS = 16_000, 20
FRAME = SR * FRAME_MS // 1000
SPEECH_DB = -20.0     # active speech level of a nominal caller, in dB relative to full scale
GAIN_SPREAD_DB = 6.0  # handsets differ: each call's level moves by up to this much either way
FIXED_DB = -38.0      # the naive VAD's threshold, chosen by looking at one quiet recording
MARGIN_DB = 7.0       # the adaptive VAD fires this far above its noise floor
FLOOR_WINDOW_MS = 2000  # longer than a phrase, so speech doesn't become the floor
HANGOVER_MS = 120     # how long the VAD stays "speech" after energy drops
ONSET_MS = 60         # energy needed before it says "speech" at all
MIN_SPEECH_MS = 160   # a shorter blip reaches the endpointer but gets no reply
SILENCE_MS = 400      # the endpointer's window, counted after the hangover has run out
BARGE_CONFIRM_MS = 160
MAX_TURN_S = 6.0      # a real system's backstop when the endpointer never fires
SNRS = (30, 20, 10, 5, 0)

# The note's placeholders. STREAMING_P95 comes from voice_turn_lab; the batch lines are the note's other budget row.
BATCH_P95 = {"ASR final": 300, "LLM to first token": 500, "LLM full reply": 900, "TTS full audio": 400}
TOKEN_S, WORD_S = 0.03, 0.30  # assumed: time per generated word, and how long one word takes to play


AT_DEFAULTS = True  # main() clears this when a knob moves


def claim(holds, message):
    """A check on what the default setup shows: an assert at the defaults, a printed warning once a knob has moved."""
    if holds:
        return
    if AT_DEFAULTS:
        raise AssertionError(message)
    print(f"   warning, with the knobs moved: {message}")


def median_of(values):
    return statistics.median(values) if values else math.nan


# %% Generated audio. These waveforms are not speech.
def db_rms(samples):
    return 10 * math.log10(float(samples.dot(samples)) / len(samples) + 1e-12)


def burst(rng, seconds):
    """A harmonic stack with a wandering pitch and a syllable-rate envelope. It has speech's energy shape and no words."""
    n = max(FRAME, int(seconds * SR))
    t = np.arange(n) / SR
    f0 = rng.uniform(100, 220) * (1 + 0.04 * np.sin(2 * np.pi * rng.uniform(0.5, 1.5) * t + rng.uniform(0, 6)))
    phase = 2 * np.pi * np.cumsum(f0) / SR
    wave = sum(np.sin(k * phase) / k for k in range(1, 13))
    envelope = 0.5 * (1 + np.sin(2 * np.pi * rng.uniform(3, 6) * t + rng.uniform(0, 6)))
    edge = np.minimum(1, np.minimum(np.arange(n), np.arange(n)[::-1]) / (0.015 * SR))
    out = wave * envelope * edge
    return out / np.sqrt(np.mean(out * out))


def cough(rng, seconds):
    """Broadband noise with a sharp attack and a fast decay. An energy detector has no way to tell this from a word."""
    n = max(FRAME, int(seconds * SR))
    out = rng.standard_normal(n) * np.exp(-3.0 * np.arange(n) / n)
    return out / np.sqrt(np.mean(out * out))


def pink(rng, n):
    size = 2 ** math.ceil(math.log2(max(n, 2)))  # a power of two keeps the FFT fast
    spectrum = np.fft.rfft(rng.standard_normal(size))
    spectrum[1:] /= np.sqrt(np.arange(1, len(spectrum)))
    spectrum[0] = 0
    out = np.fft.irfft(spectrum, size)[:n]
    return out / np.sqrt(np.mean(out * out))


@dataclass
class Call:
    audio: np.ndarray
    speech: np.ndarray  # one bool per frame, the generator's ground truth
    coughs: np.ndarray
    true_end: float     # when the last speech segment ends, in seconds
    bursts: list = field(default_factory=list)  # (kind, start, end) in seconds


def render(segments, rng, snr_db):
    """Mix ("speech"|"cough"|"pause", seconds) segments over pink noise, at snr_db below this call's speech level."""
    level = 10 ** ((SPEECH_DB + rng.uniform(-GAIN_SPREAD_DB, GAIN_SPREAD_DB)) / 20)
    n = int(sum(sec for _, sec in segments) * SR)
    clean, speech, coughs, spans, at = np.zeros(n), np.zeros(n, bool), np.zeros(n, bool), [], 0
    for kind, sec in segments:
        part = int(sec * SR)
        if kind == "speech":
            clean[at:at + part] = burst(rng, sec)[:part] * level
            speech[at:at + part] = True
        elif kind == "cough":
            clean[at:at + part] = cough(rng, sec)[:part] * level * 2  # a cough is louder than the talker
            coughs[at:at + part] = True
        if kind != "pause":
            spans.append((kind, at / SR, (at + part) / SR))
        at += part
    audio = clean + pink(rng, n) * level / 10 ** (snr_db / 20)
    frames = n // FRAME
    true_end = max((end for kind, _, end in spans if kind == "speech"), default=0.0)
    return Call(audio, speech[:frames * FRAME].reshape(frames, FRAME).any(axis=1),
                coughs[:frames * FRAME].reshape(frames, FRAME).any(axis=1), true_end, spans)


def conversation(rng, cough_p=0.15, tail=2.5):
    """Two to four phrases with hesitation pauses. The pause distribution is our assumption."""
    segments = [("pause", 0.6)]
    phrases = rng.integers(2, 5)
    for i in range(phrases):
        segments.append(("speech", rng.uniform(0.5, 1.4)))
        if i < phrases - 1:
            segments.append(("pause", min(1.5, rng.lognormal(math.log(0.22), 0.55))))
    if rng.random() < cough_p:  # just after the caller stops, which restarts the silence count
        segments += [("pause", rng.uniform(0.1, 0.3)), ("cough", rng.uniform(0.12, 0.4))]
    return segments + [("pause", tail)]


def digits(rng, tail=2.5):
    """Someone reading out a number in groups, with long gaps. Also an assumed distribution."""
    segments = [("pause", 0.6)]
    groups = rng.integers(5, 9)
    for i in range(groups):
        segments.append(("speech", rng.uniform(0.25, 0.45)))
        if i < groups - 1:
            segments.append(("pause", min(1.6, rng.lognormal(math.log(0.45), 0.45))))
    return segments + [("pause", tail)]


# %% The VAD and the endpointer: one frame in, one decision out
class FixedVad:
    """The naive version: one absolute threshold, no memory. Fine in the room it was tuned in."""
    onset = 1

    def step(self, frame):
        return db_rms(frame) > FIXED_DB


class EnergyVad:
    """Adaptive noise floor, a leaky onset counter, and a hangover. hangover_ms=0 shows what the hangover buys."""

    def __init__(self, hangover_ms=HANGOVER_MS, onset_ms=ONSET_MS, margin_db=MARGIN_DB):
        self.hangover = hangover_ms // FRAME_MS
        self.onset = max(1, onset_ms // FRAME_MS)
        self.margin, self.count, self.hold, self.on = margin_db, 0, 0, False
        self.recent, self.smooth = deque(maxlen=FLOOR_WINDOW_MS // FRAME_MS), None

    def step(self, frame):
        level = db_rms(frame)
        # The floor is the quietest smoothed level of the last couple of seconds. A slow-rising average looked fine on
        # generated audio and stuck at -120 dB on a real clip that opens with digital silence, so --asr caught it.
        self.smooth = level if self.smooth is None else 0.7 * self.smooth + 0.3 * level
        self.recent.append(self.smooth)
        loud = level > min(self.recent) + self.margin
        self.count = min(self.onset, self.count + 1) if loud else max(0, self.count - 1)
        if loud and self.on:
            self.hold = self.hangover
        elif self.count >= self.onset:
            self.on, self.hold = True, self.hangover
        elif self.on:
            self.hold -= 1
            self.on = self.hold >= 0
        return self.on


class Endpointer:
    """Turns VAD decisions into start and end events. The window is counted after the VAD's hangover has run out."""

    def __init__(self, silence_ms=SILENCE_MS):
        self.window = max(1, silence_ms // FRAME_MS)
        self.talking, self.quiet = False, 0

    def step(self, is_speech):
        if is_speech:
            started = not self.talking
            self.talking, self.quiet = True, 0
            return "start" if started else None
        if self.talking:
            self.quiet += 1
            if self.quiet >= self.window:
                self.talking = False
                return "end"
        return None


def frames_of(audio):
    return (audio[i:i + FRAME] for i in range(0, len(audio) - FRAME + 1, FRAME))


def vad_section(n_calls, hangover_ms):
    print("1. VAD, frame by frame, on generated audio that is NOT speech (bursts, coughs, pink noise)")
    print(f"   {n_calls} generated calls per SNR, level varies {GAIN_SPREAD_DB:.0f} dB either way per call, {FRAME_MS} ms frames")
    print(f"   {'':30}{'SNR dB':>7}{'false alarm':>13}{'miss':>8}{'on-runs per phrase':>20}{'fires on coughs':>17}")
    arms = [("fixed threshold, no hangover", FixedVad),
            ("adaptive floor, no hangover", lambda: EnergyVad(hangover_ms=0)),
            ("adaptive floor, hangover", lambda: EnergyVad(hangover_ms=hangover_ms))]
    results = {}
    for label, make in arms:
        for snr in SNRS:
            rng = np.random.default_rng([SEED, 1, snr])
            fa, miss, nonspeech, speech, runs, phrases, hit, coughs = 0, 0, 0, 0, 0, 0, 0, 0
            for _ in range(n_calls):
                call = render(conversation(rng, cough_p=0.5), rng, snr)
                vad, previous, fired = make(), False, False
                for i, frame in enumerate(frames_of(call.audio)):
                    on = vad.step(frame)
                    runs += on and not previous
                    previous = on
                    if call.coughs[i]:
                        fired = fired or on
                    elif call.speech[i]:
                        speech += 1
                        miss += not on
                    else:
                        nonspeech += 1
                        fa += on
                phrases += sum(kind == "speech" for kind, _, _ in call.bursts)
                has_cough = call.coughs.any()
                coughs += has_cough
                hit += has_cough and fired
            row = fa / nonspeech, miss / speech, runs / phrases, hit / max(1, coughs)
            results[label, snr] = row
            print(f"   {label:30}{snr:>7}{row[0]:>13.1%}{row[1]:>8.1%}{row[2]:>20.1f}{row[3]:>17.0%}")
    # The invariants this section exists to show.
    claim(results["adaptive floor, hangover", 20][2] < results["adaptive floor, no hangover", 20][2], "the hangover should merge runs")
    assert results["fixed threshold, no hangover", 10][0] > 0.5, "noise above a fixed threshold reads as speech"
    claim(results["adaptive floor, hangover", 10][0] < results["fixed threshold, no hangover", 10][0], "adaptive should false-alarm less than fixed at 10 dB")
    print("   The hangover's false alarms are its tails: the price of not flipping off inside every word. Energy alone fires on")
    print("   coughs at every SNR, and at 0 dB it has little left to work with. A trained VAD is the next step.\n")


# %% Endpointing: a window too short cuts people off, too long adds dead air
def endpoints(call, make_vad, silence_ms):
    vad, ep, fired = make_vad(), Endpointer(silence_ms), []
    for i, frame in enumerate(frames_of(call.audio)):
        if ep.step(vad.step(frame)) == "end":
            fired.append((i + 1) * FRAME / SR)
    return fired


def endpoint_stats(calls, make_vad, silence_ms):
    cut, hung, delays = 0, 0, []
    for call in calls:
        fired = endpoints(call, make_vad, silence_ms)
        cut += any(t < call.true_end for t in fired)
        after = [t for t in fired if t >= call.true_end]
        if after:
            delays.append((after[0] - call.true_end) * 1000)
        else:
            hung += 1
    return cut / len(calls), hung / len(calls), delays


def endpoint_section(n_calls, hangover_ms):
    make_vad = lambda: EnergyVad(hangover_ms=hangover_ms)
    rng = np.random.default_rng([SEED, 2])
    talk = [render(conversation(rng), rng, 20) for _ in range(n_calls)]
    nums = [render(digits(rng), rng, 20) for _ in range(n_calls)]
    print(f"2. Endpointing trade-off, {n_calls} generated calls per kind at 20 dB SNR, adaptive VAD, hangover {hangover_ms} ms")
    print(f"   {'silence window':>16}{'cut off, talk':>15}{'cut off, digits':>17}{'added wait p50':>16}{'added wait p95':>16}")
    rows = {}
    for silence in (100, 200, 300, 400, 600, 800, 1200):
        cut_t, _, delays = endpoint_stats(talk, make_vad, silence)
        cut_d, _, delays_d = endpoint_stats(nums, make_vad, silence)
        rows[silence] = cut_t, cut_d, delays, delays_d
        p95 = percentile(delays, 0.95) if delays else math.nan
        print(f"   {silence:>13} ms{cut_t:>15.1%}{cut_d:>17.1%}{median_of(delays):>13.0f} ms{p95:>13.0f} ms")
    claim(rows[100][0] > rows[1200][0] and median_of(rows[100][2]) < median_of(rows[1200][2]), "a short window should cut off more and wait less than a long one")

    short, long = 300, 900
    cut_short_t, _, delay_short_t = endpoint_stats(talk, make_vad, short)
    cut_short_d, _, delay_short_d = endpoint_stats(nums, make_vad, short)
    cut_long_t, _, delay_long_t = endpoint_stats(talk, make_vad, long)
    cut_long_d, _, delay_long_d = endpoint_stats(nums, make_vad, long)
    print(f"\n   One window can't serve both. The dialogue knows which question it just asked, so let it choose:")
    print(f"   {'':34}{'cut off, talk':>15}{'cut off, digits':>17}{'wait p50, talk':>16}{'wait p50, digits':>18}")
    for label, a, b, c, d in [(f"fixed {short} ms", cut_short_t, cut_short_d, delay_short_t, delay_short_d),
                              (f"fixed {long} ms", cut_long_t, cut_long_d, delay_long_t, delay_long_d),
                              (f"{short} ms, or {long} ms after asking digits", cut_short_t, cut_long_d, delay_short_t, delay_long_d)]:
        print(f"   {label:34}{a:>15.1%}{b:>17.1%}{median_of(c):>13.0f} ms{median_of(d):>15.0f} ms")

    print(f"\n   Naive against adaptive at a {SILENCE_MS} ms window, by SNR. A hung turn never ends without the {MAX_TURN_S:.0f} s backstop:")
    print(f"   {'SNR dB':>9}{'fixed: hung':>14}{'adaptive: hung':>16}{'adaptive wait p50':>19}{'adaptive cut off':>18}")
    hung_fixed_10 = hung_adaptive_10 = 0
    for snr in SNRS:
        rng = np.random.default_rng([SEED, 3, snr])
        calls = [render(conversation(rng), rng, snr) for _ in range(n_calls // 2)]
        _, hung_fixed, _ = endpoint_stats(calls, FixedVad, SILENCE_MS)
        cut, hung, delays = endpoint_stats(calls, make_vad, SILENCE_MS)
        if snr == 10:
            hung_fixed_10, hung_adaptive_10 = hung_fixed, hung
        wait = f"{statistics.median(delays):.0f} ms" if delays else "none"
        print(f"   {snr:>9}{hung_fixed:>14.1%}{hung:>16.1%}{wait:>19}{cut:>18.1%}")
    claim(hung_fixed_10 > hung_adaptive_10, "a fixed threshold in noise should hang more turns than the adaptive VAD")
    print()


# %% Barge-in confirmation: the same trade-off, while the agent is talking
def barge_section(n_calls, hangover_ms):
    rng = np.random.default_rng([SEED, 4])
    pre = ("pause", 0.8)
    coughs_ = [render([pre, ("cough", rng.uniform(0.12, 0.4)), ("pause", 0.8)], rng, 20) for _ in range(n_calls)]
    short = [render([pre, ("speech", rng.uniform(0.25, 0.5)), ("pause", 0.8)], rng, 20) for _ in range(n_calls)]
    full = [render([pre, ("speech", rng.uniform(1.0, 2.0)), ("pause", 0.8)], rng, 20) for _ in range(n_calls)]

    def fired_at(call, confirm_ms):
        vad = EnergyVad(hangover_ms=hangover_ms, onset_ms=confirm_ms)
        for i, frame in enumerate(frames_of(call.audio)):
            if vad.step(frame):
                return (i + 1) * FRAME / SR
        return None

    print(f"3. Barge-in confirmation, {n_calls} generated events of each kind at 20 dB SNR, while the agent is speaking")
    print(f"   {'confirm':>11}{'coughs that stop the agent':>28}{'short replies missed':>22}{'reaction p50, long':>20}")
    rows = {}
    for confirm in (20, 60, 100, 160, 240, 320, 480):
        false_stop = sum(fired_at(c, confirm) is not None for c in coughs_) / n_calls
        missed = sum(fired_at(c, confirm) is None for c in short) / n_calls
        react = [(t - c.bursts[0][1]) * 1000 for c in full if (t := fired_at(c, confirm)) is not None]
        rows[confirm] = false_stop, missed, median_of(react)
        print(f"   {confirm:>8} ms{false_stop:>28.1%}{missed:>22.1%}{rows[confirm][2]:>17.0f} ms")
    claim(rows[20][0] > rows[480][0] and rows[20][1] < rows[480][1] and rows[20][2] < rows[480][2], "a longer confirmation should stop fewer coughs, miss more replies and react later")
    print("   No setting wins, because energy can't tell a cough from a short 'no'. Pausing at onset and resuming if the burst\n"
          "   doesn't confirm is one way out. It is not built here.\n")


# %% A real asyncio loop on a virtual clock
class _JumpSelector(selectors.DefaultSelector):
    """When the loop would sleep, jump the clock instead. Everything else about the loop is ordinary asyncio."""
    loop = None

    def select(self, timeout=None):
        if timeout is None:
            raise RuntimeError("the loop would wait forever: nothing is scheduled")
        if timeout > 0:
            self.loop.now += timeout
        return []  # nothing in this lab waits on real I/O


class VirtualLoop(asyncio.SelectorEventLoop):
    def __init__(self):
        selector = _JumpSelector()
        super().__init__(selector)
        selector.loop = self
        self.now = 0.0

    def time(self):
        return self.now


def run_virtual(coro):
    loop = VirtualLoop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# %% The cascade: frames in, STT, LLM, TTS and playback as tasks joined by bounded queues
ACK = ("I can see the second charge on your April invoice. I am issuing the refund of 40 euros now and that can take a few "
       "seconds. While it runs I can go through what else the invoice shows for the month.").split()
PLAIN = "I can see the charge you mean on the April invoice, and here is what it was for.".split()
GONE_THROUGH = "Your refund of 40 euros has gone through.".split()
STILL_RUNNING = "That refund is still running and I will tell you when it lands.".split()
REISSUE = "Let me issue that refund for you now.".split()


class Backend:
    """The refund service. It lives on the far side of a network, so cancelling the client doesn't stop it."""

    def __init__(self):
        self.applied, self.seen = [], {}

    async def handle(self, key, seconds):
        if key is not None and key in self.seen:  # an idempotency key turns a retry into a lookup
            return await asyncio.shield(self.seen[key])
        task = asyncio.ensure_future(self._apply(seconds))
        if key is not None:
            self.seen[key] = task
        return await asyncio.shield(task)

    async def _apply(self, seconds):
        await asyncio.sleep(seconds * 0.4)
        self.applied.append("refund of 40 EUR")  # the money has moved, whoever is still listening
        await asyncio.sleep(seconds * 0.6)
        return "refund of 40 EUR issued"


@dataclass
class Config:
    name: str = ""
    streaming: bool = True
    make_vad: object = EnergyVad
    silence_ms: int = SILENCE_MS
    barge_confirm_ms: int = BARGE_CONFIRM_MS
    barge: str = "correct"             # correct | mute | cancel_all
    idempotency_key: bool = False
    block_the_loop: bool = False       # a synchronous call inside a coroutine


@dataclass
class Reply:
    words: list = field(default_factory=list)
    generated: list = field(default_factory=list)
    heard: list = field(default_factory=list)
    muted: bool = False
    interrupted: bool = False
    first_audio: float | None = None
    last_audible: float | None = None
    tokens_after_barge: int = 0
    finished: bool = False
    said: list = field(default_factory=list)


class VoiceCall:
    def __init__(self, cfg, draws, call, stop_at_first_audio=False, backend=None, tool_seconds=0.0, seed=0):
        self.cfg, self.d, self.call = cfg, draws, call
        self.stop_at_first_audio, self.backend, self.tool_seconds = stop_at_first_audio, backend, tool_seconds
        self.rng = np.random.default_rng([SEED, 5, seed])
        self.vad, self.ep = cfg.make_vad(), Endpointer(cfg.silence_ms)
        self.history, self.replies, self.tool_tasks = [], [], set()
        self.reply_tasks, self.stt_task = [], None
        self.frames, self.text = asyncio.Queue(), asyncio.Queue()
        self.done = asyncio.Event()
        self.user_turns = self.llm_calls = self.talk_overs = 0
        self.t_start = self.first_audio_after_end = self.t_endpoint = self.t_barge = None
        self.frame_lateness, self.want_announce, self.told, self.history_says_told = [], False, False, False
        self.plans, self.duplicate_call, self.speech_frames, self.answer_owed = 0, False, 0, False
        self.vad_tail_ms = getattr(self.vad, "hangover", 0) * FRAME_MS

    # ---- what the language model would decide, reduced to a rule that reads the history
    def plan(self):
        self.plans += 1
        if self.backend is None:
            return PLAIN, False
        if self.plans == 1:
            return ACK, True
        if any(h["role"] == "tool" for h in self.history):
            return GONE_THROUGH, False
        if self.tool_tasks:
            return STILL_RUNNING, False
        self.duplicate_call = True  # no record of the refund, so a sensible model tries again
        return REISSUE, True

    # ---- the call-scoped tool task
    async def run_tool(self):
        key = "call:refund:april" if self.cfg.idempotency_key else None
        outcome = await self.backend.handle(key, self.tool_seconds)
        self.history.append({"role": "tool", "name": "issue_refund", "outcome": outcome})
        self.want_announce = True

    def start_tool(self, group):
        if self.cfg.barge == "cancel_all":
            group.create_task(self.run_tool())  # a child of the turn, so it dies with the turn
        else:  # a child of the call, so it outlives any one turn
            task = asyncio.ensure_future(self.run_tool())
            self.tool_tasks.add(task)
            task.add_done_callback(self.tool_tasks.discard)

    # ---- STT: consumes frames, emits a final transcript after the endpoint
    async def stt(self, frames, text):
        partials = 0
        while (frame := await frames.get()) is not None:
            partials += 1  # a streaming recogniser would be emitting partials here
        await asyncio.sleep(self.d["ASR partial"] if self.cfg.streaming else self.d["ASR final"])
        await text.put(f"<transcript of {partials} frames>")

    # ---- LLM: consumes the transcript, streams words; may start a tool
    async def llm(self, text, out, reply, group, announce):
        if not announce:
            await text.get()
        self.llm_calls += 1
        first = self.d["LLM to first token"] if self.cfg.streaming else self.d["LLM to first token batch"] + self.d["LLM full reply"]
        if self.cfg.block_the_loop:
            time.sleep(first)  # the bug: every other call on this loop stops too
        else:
            await asyncio.sleep(first)
        words, use_tool = (GONE_THROUGH, False) if announce else self.plan()
        if use_tool:
            self.start_tool(group)
        for word in words:
            if self.cfg.streaming:
                await asyncio.sleep(TOKEN_S)
            reply.generated.append(word)
            if self.t_barge is not None and not reply.finished:
                reply.tokens_after_barge += 1
            await out.put(word)
        await out.put(None)

    # ---- TTS: consumes words, produces real sample frames, each tagged with the word it finishes
    async def tts(self, words, out):
        if not self.cfg.streaming:
            batch = []
            while (word := await words.get()) is not None:
                batch.append(word)
            await asyncio.sleep(self.d["TTS full audio"])
            for word in batch:
                await self._synth(word, out)
        else:
            first = True
            while (word := await words.get()) is not None:
                if first:
                    await asyncio.sleep(self.d["TTS first audio"])
                    first = False
                await self._synth(word, out)
        await out.put(None)

    async def _synth(self, word, out):
        samples = burst(self.rng, WORD_S)
        count = len(samples) // FRAME
        for i in range(count):
            await out.put((samples[i * FRAME:(i + 1) * FRAME], word if i == count - 1 else None))

    # ---- playback: one frame every 20 ms; only here does a word become something the caller heard
    async def playback(self, audio, reply):
        loop = asyncio.get_running_loop()
        while (item := await audio.get()) is not None:
            frame, word = item
            if reply.first_audio is None:
                reply.first_audio = loop.time() + self.d["network out"]
                self._note_first_audio(reply)
            await asyncio.sleep(FRAME / SR)
            if not reply.muted:
                reply.last_audible = loop.time()
                if word is not None:
                    reply.heard.append(word)

    def _note_first_audio(self, reply):
        self.answer_owed = False
        if self.t_start is None or reply.first_audio < self.t_start + self.call.true_end:
            return  # started before the caller finished: that is talking over them, not a reply
        self.first_audio_after_end = reply.first_audio
        if self.stop_at_first_audio:
            self.done.set()

    # ---- one reply is a TaskGroup, so cancelling the turn cancels exactly its children
    async def reply(self, reply, text, announce=False):
        words, audio = asyncio.Queue(maxsize=8), asyncio.Queue(maxsize=50)  # bounded: playback paces generation
        try:
            async with asyncio.TaskGroup() as group:
                group.create_task(self.llm(text, words, reply, group, announce))
                group.create_task(self.tts(words, audio))
                group.create_task(self.playback(audio, reply))
        except asyncio.CancelledError:
            reply.interrupted = True
            raise
        finally:
            reply.finished = True
            # The fix and the bug are this one line: what goes into history, what was heard or what was generated.
            reply.said = reply.generated if self.cfg.barge == "mute" else reply.heard
            self.history.append({"role": "assistant", "text": " ".join(reply.said), "interrupted": reply.interrupted or reply.muted})
            # The caller knows only what played. The agent knows only what history says, and retries on that.
            self.told = self.told or reply.heard == GONE_THROUGH
            self.history_says_told = self.history_says_told or reply.said == GONE_THROUGH
            if any(h["role"] == "tool" for h in self.history) and not self.history_says_told:
                self.want_announce = True

    def start_reply(self, text=None, announce=False):
        reply = Reply()
        self.replies.append(reply)
        self.reply_tasks.append(asyncio.ensure_future(self.reply(reply, text, announce)))
        return reply

    def reply_active(self):
        return bool(self.reply_tasks) and not self.reply_tasks[-1].done()

    def audible(self):
        return self.reply_active() and self.replies[-1].first_audio is not None and not self.replies[-1].muted

    def caller_resumed(self, now):
        """Speech started while a reply is under way. This is either a false endpoint or a barge-in."""
        if self.audible():
            self.talk_overs += now < self.t_start + self.call.true_end
            if self.t_barge is None:
                self.t_barge = now
        if self.reply_active():
            if self.cfg.barge == "mute" and self.audible():
                self.replies[-1].muted = True  # the speaker goes quiet; LLM and TTS keep running and billing
            else:
                self.reply_tasks[-1].cancel()
        self.restart_stt()

    def restart_stt(self):
        if self.stt_task is not None:
            self.stt_task.cancel()
        self.frames, self.text = asyncio.Queue(), asyncio.Queue()
        self.stt_task = asyncio.ensure_future(self.stt(self.frames, self.text))

    # ---- the mic: real samples, one frame at a time, paced by the clock
    async def mic(self):
        loop = asyncio.get_running_loop()
        self.t_start = loop.time()
        arrive = self.t_start + self.d["network in"]
        started_at = None
        for i, frame in enumerate(frames_of(self.call.audio)):
            due = arrive + (i + 1) * FRAME / SR
            await asyncio.sleep(max(0.0, due - loop.time()))
            now = loop.time()
            self.frame_lateness.append(now - due)
            self.vad.onset = max(1, (self.cfg.barge_confirm_ms if self.reply_active() else ONSET_MS) // FRAME_MS)
            is_speech = self.vad.step(frame)
            event = self.ep.step(is_speech)
            if event == "start":
                started_at = started_at or now
                self.caller_resumed(now)
            if is_speech and self.frames is not None:
                self.frames.put_nowait(frame)
                self.speech_frames += 1
            forced = self.ep.talking and started_at is not None and now - started_at >= MAX_TURN_S
            if forced:
                self.ep.talking = False
            long_enough = self.speech_frames * FRAME_MS >= MIN_SPEECH_MS + self.vad_tail_ms
            if (event == "end" or forced) and (long_enough or self.answer_owed):  # a cough can't cancel an answer for good
                self.answer_owed = True
                self.t_endpoint = now
                self.frames.put_nowait(None)
                self.start_reply(self.text)
                self.user_turns += 1
            if event == "end" or forced:
                started_at, self.speech_frames = None, 0
            if self.want_announce and not self.reply_active() and not self.ep.talking:
                self.want_announce = False
                if not self.history_says_told:
                    self.start_reply(announce=True)
            if self.done.is_set():
                return
            if self.backend is not None and self.scenario_over():
                self.done.set()
                return

    def started_early(self):
        """The only reply began before the caller finished and was still playing when they did. Answered, but over them."""
        end = self.t_start + self.call.true_end
        return self.first_audio_after_end is None and any(
            r.first_audio is not None and r.last_audible is not None and r.last_audible >= end for r in self.replies)

    def scenario_over(self):
        return (self.user_turns >= 2 and not self.reply_active() and not self.tool_tasks and not self.want_announce
                and not self.ep.talking and all(r.finished for r in self.replies))

    async def run(self):
        mic = asyncio.ensure_future(self.mic())
        waiter = asyncio.ensure_future(self.done.wait())
        await asyncio.wait({mic, waiter}, return_when=asyncio.FIRST_COMPLETED)
        tasks = [mic, waiter, *self.reply_tasks, self.stt_task, *self.tool_tasks]
        for task in filter(None, tasks):
            task.cancel()
        results = await asyncio.gather(*filter(None, tasks), return_exceptions=True)
        for result in results:
            if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                raise result
        return self


# %% End-of-speech to first audio, off the running loop
def stage_draws(seed):
    rng = random.Random(seed)
    # The same seed gives each arm the same draws for a call, so arms differ only by what they do.
    out = {name: draw(rng, p) / 1000 for name, p in STREAMING_P95.items()}
    out["LLM to first token batch"] = draw(rng, BATCH_P95["LLM to first token"]) / 1000
    for name in ("ASR final", "LLM full reply", "TTS full audio"):
        out[name] = draw(rng, BATCH_P95[name]) / 1000
    return out


def latency_stats(results):
    """One latency per call in ms. A call with no reply that waited for the caller to finish counts as infinite, so it can't
    flatter the percentiles. That covers no reply at all and a reply that started early; the table counts the two apart."""
    return [math.inf if c.first_audio_after_end is None else (c.first_audio_after_end - c.t_start - c.call.true_end) * 1000
            for c in results]


async def latency_arm(cfg, calls):
    done = []
    for i, call in enumerate(calls):
        voice = VoiceCall(cfg, stage_draws(SEED * 1000 + i), call, stop_at_first_audio=True, seed=i)
        done.append(await voice.run())
        leftover = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        assert not leftover, f"tasks leaked after a call: {leftover}"
    return done


def latency_section(n_turns, silence_ms, hangover_ms, confirm_ms):
    rng = np.random.default_rng([SEED, 6])
    mix = [30, 20, 20, 10]
    calls = [render(conversation(rng, tail=MAX_TURN_S + 1.5), rng, mix[i % len(mix)]) for i in range(n_turns)]
    adaptive = lambda: EnergyVad(hangover_ms=hangover_ms)
    common = dict(make_vad=adaptive, silence_ms=silence_ms, barge_confirm_ms=confirm_ms)
    arms = [Config("batch stages, adaptive VAD", streaming=False, **common),
            Config("streaming, fixed-threshold VAD", **{**common, "make_vad": FixedVad}),
            Config("streaming, adaptive VAD", **common),
            Config("streaming, shorter window", **{**common, "silence_ms": max(FRAME_MS, silence_ms // 2)})]
    print(f"4. End of speech to first audio, measured on the running loop. {n_turns} generated calls, SNR mixed over {sorted(set(mix))} dB")
    print(f"   Real samples and a real VAD set the wait; the note's placeholders drive the stubs, sigma {SPREAD}, paired draws per call")
    print(f"   {'':32}{'window':>9}{'wait p50':>10}{'p50':>8}{'p95':>8}{'p99':>8}{f'<= {TARGET_MS} ms':>11}{'no reply':>10}{'began early':>13}{'talked over':>13}{'LLM calls/call':>16}")
    show = lambda x: "never" if math.isinf(x) else f"{x:.0f}"
    out = {}
    for cfg in arms:
        done = run_virtual(latency_arm(cfg, calls))
        lat = latency_stats(done)
        over = sum(c.talk_overs > 0 for c in done) / len(done)
        llm = sum(c.llm_calls for c in done) / len(done)
        p50, p95, p99 = percentile(lat, .5), percentile(lat, .95), percentile(lat, .99)
        waits = [(c.t_endpoint - c.t_start - c.call.true_end) * 1000 for c in done if c.first_audio_after_end is not None]
        early = sum(c.started_early() for c in done) / len(done)
        no_reply = sum(math.isinf(x) for x in lat) / len(lat) - early
        out[cfg.name] = p50, p95, no_reply, median_of(waits)
        print(f"   {cfg.name:32}{cfg.silence_ms:>6} ms{median_of(waits):>10.0f}{show(p50):>8}{show(p95):>8}{show(p99):>8}"
              f"{sum(x <= TARGET_MS for x in lat) / len(lat):>11.1%}{no_reply:>10.1%}{early:>13.1%}{over:>13.1%}{llm:>16.2f}")
    claim(out["streaming, adaptive VAD"][0] < out["batch stages, adaptive VAD"][0], "streaming should lower time to first audio")
    claim(out["streaming, adaptive VAD"][2] == 0, "the adaptive VAD should leave no caller without a reply")
    claim(out["streaming, fixed-threshold VAD"][2] > 0, "a fixed threshold that can't see silence should leave some callers without a reply")
    print(f"   The note's streaming budget adds up to {sum(STREAMING_P95.values())} ms with a {STREAMING_P95['VAD end of speech']} ms placeholder for the VAD line. Here that line is")
    print(f"   measured: {out['streaming, adaptive VAD'][3]:.0f} ms at the median, the wait column, from the audio. A fixed threshold in noise keeps hearing 'speech', so it")
    print("   cancels its own replies and some callers never get an answer.\n")


# %% Barge-in with a refund in flight
def barge_call(rng):
    """Caller asks for a refund, the agent starts talking, the caller talks over it, and then waits."""
    gap = rng.uniform(2.2, 3.2)
    segments = [("pause", 0.6), ("speech", rng.uniform(1.2, 2.0)), ("pause", gap), ("speech", rng.uniform(1.0, 1.6)), ("pause", 18.0)]
    return render(segments, rng, 20)


def tool_trial(cfg, call, i):
    async def go():
        tool_seconds = random.Random(SEED * 31 + i).uniform(3.0, 6.0)
        voice = VoiceCall(cfg, stage_draws(SEED * 2000 + i), call, backend=Backend(), tool_seconds=tool_seconds, seed=i)
        await voice.run()
        leftover = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in leftover:  # the refund service outlives the call by design; let it finish
            await task
        return voice
    return run_virtual(go())


def barge_tool_section(n_trials, hangover_ms, confirm_ms):
    rng = np.random.default_rng([SEED, 7])
    calls = [barge_call(rng) for _ in range(n_trials)]
    common = dict(make_vad=lambda: EnergyVad(hangover_ms=hangover_ms), barge_confirm_ms=confirm_ms)
    arms = [Config("mute the speaker only", barge="mute", **common),
            Config("cancel everything", barge="cancel_all", **common),
            Config("cancel everything, keyed tool", barge="cancel_all", idempotency_key=True, **common),
            Config("cancel turn, tool survives", barge="correct", idempotency_key=True, **common)]
    print(f"5. Barge-in with issue_refund in flight, {n_trials} generated calls, tool takes 3 to 6 s (assumed), the money moves at 40% of that")
    print("   The LLM stub follows one rule: if history has no record of the refund and none is running, it tries again.")
    print(f"   {'':31}{'stop audio p50':>15}{'tokens after':>14}{'claimed, unheard':>18}{'refunds':>9}{'re-issued':>11}{'caller told':>13}")
    example, results = None, {}
    for cfg in arms:
        stop, tokens, unheard, refunds, retried, told = [], [], [], [], [], []
        failed = {}

        def check(holds, message):
            failed[message] = failed.get(message, 0) + (not holds)

        for i, call in enumerate(calls):
            voice = tool_trial(cfg, call, i)
            first = voice.replies[0] if voice.replies else Reply()
            barge_onset = voice.t_start + call.bursts[1][1]
            check(voice.t_barge is not None, "the caller should talk over the reply")
            if voice.t_barge is not None and first.last_audible is not None:  # otherwise no audio was there to stop
                stop.append((first.last_audible - barge_onset) * 1000)
            tokens.append(first.tokens_after_barge)
            said = first.said
            unheard.append(len(said) - len(first.heard))
            refunds.append(len(voice.backend.applied))
            retried.append(voice.duplicate_call)
            told.append(voice.told)
            if cfg.barge == "correct":
                # The invariants: what history says is what was heard, the refund happened once, and the caller found out.
                assert said == first.heard, "history must hold only what was played"
                check(len(voice.backend.applied) == 1, "the refund should happen once")
                check(not voice.duplicate_call, "a surviving tool should never be sent again")
                check(voice.told, "the caller should hear the whole outcome")
                check(any(h["role"] == "tool" for h in voice.history), "the tool outcome should survive the barge-in")
                check(first.interrupted, "the first reply should be cancelled")
                check(voice.t_barge is None or first.last_audible is None or first.last_audible <= voice.t_barge + 0.05, "no audio after the cancel")
                example = example or voice
        for message, count in failed.items():
            claim(count == 0, f"{cfg.name}: {message}, fails on {count} of {n_trials} calls")
        results[cfg.name] = statistics.mean(refunds), statistics.mean(unheard)
        print(f"   {cfg.name:31}{median_of(stop):>12.0f} ms{statistics.mean(tokens):>14.1f}{statistics.mean(unheard):>18.1f}"
              f"{statistics.mean(refunds):>9.2f}{statistics.mean(retried):>11.0%}{statistics.mean(told):>13.0%}")
    print("   Caller told means the whole outcome sentence played. Muting has no retry: its history says the sentence was spoken.")
    claim(results["cancel everything"][0] > 1.5, "cancelling the client doesn't undo the server, so a retry should pay twice")
    claim(results["cancel everything, keyed tool"][0] == 1, "the key should hold a retry to one refund")
    claim(results["mute the speaker only"][1] > 0, "muting should leave words in history that the caller never heard")
    print("\n   One history from the last arm, in commit order. A reply commits when it ends, so the outcome can land while a stale")
    print("   'still running' is being spoken. The next reply corrects it, because the outcome is in history:")
    for entry in example.history:
        print(f"     {entry}")
    print()


# %% The wall clock, where a blocking call costs every other caller
def wall_section():
    rng = np.random.default_rng([SEED, 8])
    calls = [render([("pause", 0.3), ("speech", rng.uniform(0.8, 1.4)), ("pause", 7.0)], rng, 20) for _ in range(8)]

    async def arm(cfg):
        voices = [VoiceCall(cfg, stage_draws(SEED * 3000 + i), c, stop_at_first_audio=True, seed=i) for i, c in enumerate(calls)]
        await asyncio.gather(*(v.run() for v in voices))
        return voices

    def summary(voices):
        lat = latency_stats(voices)
        late = [x * 1000 for v in voices for x in v.frame_lateness]
        assert not any(math.isinf(x) for x in lat), "every call on the wall clock must get an answer"
        return statistics.median(lat), max(late), statistics.median(late)

    print("6. Same code on the wall clock, 8 calls on one loop. These numbers vary by machine.")
    print(f"   {'':34}{'first audio p50':>17}{'late mic frame, p50':>21}{'worst':>10}")
    virtual = summary(run_virtual(arm(Config())))
    real = summary(asyncio.run(arm(Config())))
    blocked = summary(asyncio.run(arm(Config(block_the_loop=True))))
    for label, row in [("virtual clock", virtual), ("wall clock", real), ("wall clock, LLM stub blocks the loop", blocked)]:
        print(f"   {label:37}{row[0]:>11.0f} ms{row[2]:>18.1f} ms{row[1]:>7.0f} ms")
    assert blocked[1] > real[1] + 200, "a synchronous call stalls every call sharing the loop"
    print()


# %% Optional: a real speech model on a real clip
CLIP_URL = "https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/samples/jfk.wav"
CLIP_REFERENCE = "and so my fellow americans ask not what your country can do for you ask what you can do for your country"


def load_wav(path):
    import wave
    with wave.open(str(path), "rb") as handle:
        rate, channels, width = handle.getframerate(), handle.getnchannels(), handle.getsampwidth()
        raw = handle.readframes(handle.getnframes())
    if width != 2:
        sys.exit(f"--asr reads 16-bit WAV files; {path} has {8 * width}-bit samples")
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    if rate != SR:
        samples = np.interp(np.arange(0, len(samples) * SR / rate) * rate / SR, np.arange(len(samples)), samples)
    return samples


def asr_section(source):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("--asr needs the model package: uv run --with faster-whisper voice_stream_lab.py --asr")
    from pathlib import Path
    reference = None
    if source == "default":
        import urllib.request
        path = Path.home() / ".cache" / "voice_stream_lab" / "jfk.wav"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"downloading {CLIP_URL}")
            urllib.request.urlretrieve(CLIP_URL, path)
        reference = CLIP_REFERENCE
    else:
        path = Path(source)
    clip = load_wav(path)
    speech_level = np.percentile([db_rms(f) for f in frames_of(clip)], 90)
    print(f"7. Real audio and a real model, whisper tiny.en on CPU. {path.name}, {len(clip) / SR:.1f} s. This is speech, unlike the sections above.")
    print("   The VAD runs on the real samples, frame by frame; the noise added below is generated pink noise.")
    vad, runs, previous, on_frames = EnergyVad(), 0, False, 0
    total = 0
    for frame in frames_of(clip):
        on = vad.step(frame)
        runs += on and not previous
        previous, on_frames, total = on, on_frames + on, total + 1
    print(f"   energy VAD on the clip: {runs} speech runs, on for {on_frames / max(1, total):.0%} of frames")
    for silence in (100, 300, 600, 1000):
        fired = endpoints(Call(clip, None, None, 0.0), EnergyVad, silence)
        print(f"   silence window {silence:>5} ms: endpoint fires {len(fired)} time(s), at {[round(t, 1) for t in fired][:8]} s")
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    rng = np.random.default_rng([SEED, 9])
    print(f"   {'added noise':>13}{'seconds to transcribe':>23}{'times real time':>17}{'WER':>7}   transcript")
    for snr in (None, 20, 10, 5, 0):
        noisy = clip if snr is None else clip + pink(rng, len(clip)) * 10 ** ((speech_level - snr) / 20)
        began = time.perf_counter()
        segments, _ = model.transcribe(noisy.astype(np.float32), language="en", beam_size=1)
        text = " ".join(segment.text.strip() for segment in segments)
        spent = time.perf_counter() - began
        hyp = re.findall(r"[a-z']+", text.lower())
        wer = f"{edits(reference.split(), hyp) / len(reference.split()):.2f}" if reference else "n/a"
        print(f"   {'none' if snr is None else f'{snr} dB':>13}{spent:>23.2f}{len(clip) / SR / spent:>17.1f}{wer:>7}   {text[:90]}")
    print("   One clip and one speaker: a check that the plumbing is real, not a benchmark of the model.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--silence-ms", type=int, default=SILENCE_MS, help="endpointing window for section 4")
    parser.add_argument("--hangover-ms", type=int, default=HANGOVER_MS, help="VAD hangover for sections 1 to 5")
    parser.add_argument("--barge-confirm-ms", type=int, default=BARGE_CONFIRM_MS, help="speech needed to stop the agent in sections 4 and 5")
    parser.add_argument("--turns", type=int, default=200, help="calls per arm in section 4")
    parser.add_argument("--skip-wall", action="store_true", help="skip section 6, which is the only one that varies between runs")
    parser.add_argument("--asr", nargs="?", const="default", metavar="WAV", help="also run a real speech model (downloads a model)")
    args = parser.parse_args()
    global AT_DEFAULTS
    AT_DEFAULTS = (args.silence_ms, args.hangover_ms, args.barge_confirm_ms, args.turns) == (SILENCE_MS, HANGOVER_MS, BARGE_CONFIRM_MS, 200)
    vad_section(40, args.hangover_ms)
    endpoint_section(300, args.hangover_ms)
    barge_section(200, args.hangover_ms)
    latency_section(args.turns, args.silence_ms, args.hangover_ms, args.barge_confirm_ms)
    barge_tool_section(40, args.hangover_ms, args.barge_confirm_ms)
    if not args.skip_wall:
        wall_section()
    if args.asr:
        asr_section(args.asr)


if __name__ == "__main__":
    main()
