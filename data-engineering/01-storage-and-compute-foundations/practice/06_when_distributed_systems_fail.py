"""Code from notes/06-when-distributed-systems-fail.md.

Run from any folder (it writes only to a temporary directory):
    uv run --with numpy python 06_when_distributed_systems_fail.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- outcomes ---
import random

def call(rng, p_lost_request=0.02, p_lost_reply=0.02, p_slow=0.02, p_crash=0.01):
    """One request over an unreliable network. Returns (applied on server?, client saw reply?)."""
    if rng.random() < p_lost_request:
        return False, False                   # request never arrived
    if rng.random() < p_crash:
        return False, False                   # server died before doing the work
    applied = True
    if rng.random() < p_lost_reply:
        return applied, False                 # work done, reply lost
    if rng.random() < p_slow:
        return applied, False                 # work done, reply later than the timeout
    return applied, True

rng = random.Random(1)
applied_after_timeout = timed_out = ok = 0
for _ in range(100_000):
    applied, replied = call(rng)
    if replied:
        ok += 1
    else:
        timed_out += 1
        applied_after_timeout += applied
print(f"replies {ok:,}, timeouts {timed_out:,}")
print(f"of the timeouts, the write HAD been applied in {applied_after_timeout / timed_out:.0%}")
print("--- outcomes done")

# --- retries ---
def charge_all(rng, requests, max_tries, idempotent):
    """Client retries on timeout. The ledger is what the server actually recorded."""
    ledger, seen, gave_up = [], set(), 0
    for request_id in range(requests):
        for _ in range(max_tries):
            applied, replied = call(rng)
            if applied and not (idempotent and request_id in seen):
                ledger.append(request_id)
                seen.add(request_id)
            if replied:
                break
        else:
            gave_up += 1
    charged = len(ledger)
    distinct = len(set(ledger))
    return charged, distinct, gave_up

N = 100_000
for label, tries, idem in [("no retry", 1, False), ("retry 3x", 3, False), ("retry 3x, request id", 3, True)]:
    charged, distinct, gave_up = charge_all(random.Random(2), N, tries, idem)
    print(f"{label:<22} charges {charged:>7,}  duplicates {charged - distinct:>6,}"
          f"  never charged {N - distinct:>6,}  client gave up {gave_up:>5,}")
print("--- retries done")

# --- timeouts ---
import numpy as np
rng = np.random.default_rng(3)

# Round trip times for a healthy node: a lognormal body plus rare queueing spikes.
n = 1_000_000
rtt = rng.lognormal(np.log(5), 0.5, n)
spike = rng.random(n) < 0.001
rtt[spike] += rng.exponential(400, spike.sum())
print(f"healthy rtt  p50={np.percentile(rtt,50):5.1f} ms  p99={np.percentile(rtt,99):5.1f}"
      f"  p99.9={np.percentile(rtt,99.9):6.1f}  max={rtt.max():7.1f}")
print("timeout   healthy node wrongly declared dead, per 10,000 checks")
for timeout in (10, 25, 100, 500, 2000):
    print(f"{timeout:>5} ms   {(rtt > timeout).mean() * 10_000:>8.1f}")
print("--- timeouts done")

# --- clocks ---
import time
wall_a, mono_a = time.time(), time.monotonic()
time.sleep(0.05)
print(f"elapsed by wall clock {time.time() - wall_a:.4f} s, by monotonic clock {time.monotonic() - mono_a:.4f} s")
print("wall clock now      ", round(time.time(), 1), " seconds since 1970: comparable between machines, can jump")
print("monotonic clock now ", round(time.monotonic(), 1), " since some arbitrary point: meaningless on another machine")

drift_ppm = 200
print(f"{drift_ppm} ppm drift: {drift_ppm * 1e-6 * 30 * 1000:.0f} ms per 30 s, {drift_ppm * 1e-6 * 86400:.1f} s per day")
print("--- clocks done")

# --- lww ---
def lww_run(skew_ms, seed, writes=100_000):
    """Two nodes take turns accepting writes to one key, one every `gap` ms.
    B's clock runs skew_ms behind. Last-write-wins keeps the highest timestamp."""
    rng = random.Random(seed)
    lost, t, winner_ts, winner = 0, 0.0, -1, None
    for i in range(writes):
        t += rng.expovariate(1 / 10)              # a write every 10 ms on average
        node = rng.choice("AB")
        stamp = t if node == "A" else t - skew_ms
        if stamp > winner_ts:
            winner_ts, winner = stamp, i
        else:
            lost += 1                             # acknowledged, then silently discarded
    return lost / writes

print("clock skew   acknowledged writes silently dropped by LWW")
for skew in (0, 1, 3, 10, 35, 100, 1000):
    print(f"{skew:>6} ms   {lww_run(skew, 4):7.2%}")
print("--- lww done")

# --- order_inversion ---
def inverted_share(skew_ms, gap_low=5, gap_high=50, trips=100_000, seed=5):
    """The drop-off service emits an event, then payment emits one 5-50 ms later.
    Payment's clock runs skew_ms behind. How often does payment look like it came first?"""
    rng = random.Random(seed)
    return sum(rng.uniform(gap_low, gap_high) < skew_ms for _ in range(trips)) / trips

print("clock skew   payment stamped before the drop-off that caused it")
for skew in (0, 5, 10, 20, 35, 80):
    print(f"{skew:>6} ms   {inverted_share(skew):7.2%}")
print("--- order_inversion done")

# --- pause ---
import os, signal, subprocess, sys
child_code = """
import time, sys
last = time.monotonic()
worst = 0.0
end = last + 2.0
while time.monotonic() < end:
    now = time.monotonic()
    worst = max(worst, now - last)
    last = now
    time.sleep(0.001)
print(f"{worst:.3f}")
"""
def worst_gap(pause_for):
    child = subprocess.Popen([sys.executable, "-c", child_code], stdout=subprocess.PIPE, text=True)
    time.sleep(0.5)
    if pause_for:
        os.kill(child.pid, signal.SIGSTOP)        # a stop-the-world pause the process cannot see coming
        time.sleep(pause_for)
        os.kill(child.pid, signal.SIGCONT)
    return float(child.communicate()[0])

print(f"worst gap between heartbeats, undisturbed   {worst_gap(0):6.3f} s")
print(f"worst gap between heartbeats, paused 0.8 s  {worst_gap(0.8):6.3f} s")
print("--- pause done")

# --- majority ---
def can_decide(nodes, reachable):
    return reachable > nodes // 2

print("nodes  majority  tolerates")
for n in (1, 2, 3, 4, 5, 7):
    print(f"{n:>5}  {n // 2 + 1:>8}  {(n - 1) // 2:>9}")

# A 5-node cluster splits. Which side may act?
for left, right in ((3, 2), (4, 1), (2, 2)):
    total = left + right
    print(f"split {left}|{right} of {total}: left can decide={can_decide(total, left)}, right can decide={can_decide(total, right)}")
print("--- majority done")

# --- lease ---
class Storage:
    def __init__(self, fence):
        self.fence, self.highest, self.rows = fence, -1, []
    def write(self, who, token, row):
        if self.fence and token < self.highest:
            return f"{who} (token {token}): REJECTED, already saw {self.highest}"
        self.highest = max(self.highest, token)
        self.rows.append((who, row))
        return f"{who} (token {token}): wrote {row}"

class LockService:
    """Grants a lease; each grant carries a higher token."""
    def __init__(self):
        self.token, self.expires = 0, -1
    def acquire(self, now, ttl=10):
        if now < self.expires:
            return None
        self.token += 1
        self.expires = now + ttl
        return self.token

for fence in (False, True):
    locks, store = LockService(), Storage(fence)
    print("fencing on" if fence else "fencing off")
    a = locks.acquire(now=0)                       # worker A gets the lease at t=0
    print(" ", store.write("A", a, "part-1"))      # and writes
    # A pauses for 15 s, which it cannot detect. The lease lapses at t=10.
    b = locks.acquire(now=12)                      # worker B gets it at t=12
    print(" ", store.write("B", b, "part-1-rerun"))
    print(" ", store.write("A", a, "part-2-from-stale-worker"))   # A wakes, still believes
    print("  final rows:", store.rows)
print("--- lease done")

# --- checksum ---
import zlib
def flip(data, rng):
    i = rng.randrange(len(data))
    out = bytearray(data); out[i] ^= 1 << rng.randrange(8)
    return bytes(out)

rng = random.Random(6)
block = b"trip_id=1,fare=1200;" * 200
caught_len = caught_crc = 0
trials = 20_000
for _ in range(trials):
    bad = flip(block, rng)
    caught_len += len(bad) != len(block)
    caught_crc += zlib.crc32(bad) != zlib.crc32(block)
print(f"{trials:,} single-bit corruptions: length check caught {caught_len:,}, crc32 caught {caught_crc:,}")

# The value still parses, so without a checksum it flows downstream as a real number.
good = int(b"1200"); bad = int(bytes([b"1200"[0] ^ 8]) + b"200")
print(f"a flipped bit in fare: {good} becomes {bad}")
print("--- checksum done")
