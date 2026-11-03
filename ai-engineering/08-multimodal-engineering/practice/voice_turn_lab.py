# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""A voice agent without audio, for notes/04: the latency budget as a distribution, barge-in with a tool in flight, and WER.

Run from this folder (a second or two, standard library only, downloads no data):
    uv run voice_turn_lab.py

Nothing here touches audio or a speech model. Stage latencies are random draws around the note's planning placeholders,
with a spread we assumed. The transcripts are generated from a seed with two made-up error profiles. The state machine,
the scoring and the arithmetic are real, and the numbers describe these assumptions, not any product.
"""
# %%
import math
import random
import re
import statistics

SEED, TURNS, TARGET_MS = 7, 20_000, 800
SPREAD = 0.45  # sigma of each stage's log latency, an assumption; each stage's p95 stays at the note's placeholder

STREAMING_P95 = {"network in": 40, "VAD end of speech": 300, "ASR partial": 60, "LLM to first token": 400,
                 "TTS first audio": 100, "network out": 40}


# %% 1. Stage p95s don't add up to the p95 of the turn
def percentile(values, p):
    return sorted(values)[int(p * (len(values) - 1))]


def draw(rng, p95):
    median = p95 / math.exp(1.645 * SPREAD)
    return rng.lognormvariate(math.log(median), SPREAD)


def latency_section():
    rng = random.Random(SEED)
    turns = [sum(draw(rng, p) for p in STREAMING_P95.values()) for _ in range(TURNS)]
    summed = sum(STREAMING_P95.values())
    print(f"1. Streaming cascade, {TURNS:,} simulated turns, sigma {SPREAD} per stage, independent stages")
    print(f"   sum of stage p95s  {summed:6.0f} ms   (the note's budget table)")
    print(f"   p95 of whole turn  {percentile(turns, 0.95):6.0f} ms")
    print(f"   p50 of whole turn  {percentile(turns, 0.50):6.0f} ms")
    print(f"   turns under {TARGET_MS} ms  {sum(t <= TARGET_MS for t in turns) / TURNS:6.1%}")
    # A shared slow spell makes stages move together, and then the gap closes.
    rng = random.Random(SEED)
    slow = []
    for _ in range(TURNS):
        load = rng.lognormvariate(0, SPREAD)
        slow.append(sum(p / math.exp(1.645 * SPREAD) * load for p in STREAMING_P95.values()))
    print(f"   p95 if every stage slows together  {percentile(slow, 0.95):6.0f} ms\n")


# %% 2. Barge-in with a tool in flight
class Turn:
    """The note's Turn, plus a tool call in flight. History holds what the caller heard and what really happened."""

    def __init__(self, keep_tool_outcome=True):
        self.state, self.spoken, self.queued, self.history = "listening", [], [], []
        self.pending_tool, self.keep_tool_outcome = None, keep_tool_outcome

    def call_tool(self, name):
        self.pending_tool, self.state = name, "tool"

    def tool_done(self, outcome, sentences):
        name, self.pending_tool = self.pending_tool, None
        if name is None:
            return
        if self.state == "listening" and not self.keep_tool_outcome:
            return  # the naive version: the caller interrupted, so it throws the result away
        self.history.append({"role": "tool", "name": name, "outcome": outcome})
        if self.state == "tool":
            self.reply(sentences)

    def reply(self, sentences):
        self.queued, self.state = list(sentences), "speaking"

    def tick(self):
        if self.state == "speaking" and self.queued:
            self.spoken.append(self.queued.pop(0))
            if not self.queued:
                self._commit(False)

    def barge_in(self):
        if self.state == "speaking":
            self.queued.clear()
            self._commit(True)
        elif self.state == "tool":
            self.state = "listening"  # nothing was spoken, but the tool is still running

    def _commit(self, interrupted):
        self.history.append({"role": "assistant", "text": " ".join(self.spoken), "interrupted": interrupted})
        self.spoken, self.state = [], "listening"


def replay(keep):
    t = Turn(keep_tool_outcome=keep)
    t.call_tool("issue_refund")
    t.barge_in()                                  # the caller talks over the silence
    t.tool_done("refund of 40 EUR issued", ["Your refund has gone through."])
    return t


def barge_in_section():
    print("2. Caller interrupts while issue_refund is running, and the refund then succeeds")
    for keep, label in [(False, "naive, drops the result"), (True, "keeps the outcome    ")]:
        t = replay(keep)
        knows = any(h.get("name") == "issue_refund" for h in t.history)
        print(f"   {label}  state={t.state}  next turn knows about the refund: {knows}  history={t.history}")
    print()


# %% 3. WER and critical terms on a generated corpus
TEMPLATES = ["you charged me {amt} euros on the {day} of april", "my order number is {num}", "please cancel the {day} payment",
             "i was told it would be {amt} euros and now the bill says something else entirely which is really not what we agreed on the phone last week",
             "can you check the invoice from the {day}", "the refund of {amt} euros has not arrived", "yes", "no thanks"]
WORD_SWAPS = {"charged": "charge", "payment": "payments", "invoice": "invoices", "agreed": "agree", "really": "very", "told": "sold"}


def make_corpus(rng, n=400):
    out = []
    for _ in range(n):
        amt, num, day = str(rng.randint(11, 99)), str(rng.randint(1000, 9999)), f"{rng.randint(1, 28)}th"
        text = rng.choice(TEMPLATES).format(amt=amt, num=num, day=day)
        critical = [w for w in text.split() if any(c.isdigit() for c in w)]
        out.append((text, critical))
    return out


def transcribe(rng, text, word_error, number_error):
    words = []
    for w in text.split():
        if any(c.isdigit() for c in w):
            words.append(str(rng.randint(11, 99)) if rng.random() < number_error else w)
        elif rng.random() < word_error:
            words.append(WORD_SWAPS.get(w, w + "s"))
        else:
            words.append(w)
    return " ".join(words)


def edits(ref, hyp):
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i]
        for j, h in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (r != h)))
        prev = cur
    return prev[-1]


def score(corpus, hyps):
    per_sentence, total_edits, total_words, hit, wanted = [], 0, 0, 0, 0
    for (text, critical), hyp in zip(corpus, hyps):
        ref_w, hyp_w = re.findall(r"\w+", text), re.findall(r"\w+", hyp)
        e = edits(ref_w, hyp_w)
        per_sentence.append(e / len(ref_w))
        total_edits += e
        total_words += len(ref_w)
        hit += sum(c in hyp_w for c in critical)
        wanted += len(critical)
    return statistics.mean(per_sentence), total_edits / total_words, hit / wanted


def wer_section():
    rng = random.Random(SEED)
    corpus = make_corpus(rng)
    engines = {"engine A, good on words, weak on numbers": (0.02, 0.20), "engine B, weak on words, good on numbers": (0.06, 0.02)}
    print(f"3. {len(corpus)} generated caller sentences, two made-up error profiles (word error, number error)")
    print(f"   {'':44}{'corpus WER':>11}{'mean per-sentence':>19}{'critical recall':>17}")
    for name, (we, ne) in engines.items():
        hyps = [transcribe(rng, text, we, ne) for text, _ in corpus]
        mean_wer, corpus_wer, recall = score(corpus, hyps)
        print(f"   {name:44}{corpus_wer:11.3f}{mean_wer:19.3f}{recall:17.3f}")


if __name__ == "__main__":
    latency_section()
    barge_in_section()
    wer_section()
