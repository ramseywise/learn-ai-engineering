"""Code from notes/07-consistency-and-consensus.md.

Run from any folder (it writes only to a temporary directory):
    uv run --no-project --python 3.12 --with pgserver --with 'psycopg[binary]' python 07_consistency_and_consensus.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- linear_checker ---
def linearizable(history, initial=0):
    """history: (client, 'w'|'r', value, start, end). True if some total order of the operations
    respects real time (an op that ended before another began comes first) and every read sees
    the latest write before it. Searches every order, so it is only for small histories."""
    def search(remaining, value, order):
        if not remaining:
            return order
        for op in remaining:
            if any(other[4] < op[3] for other in remaining if other is not op):
                continue                             # something had to finish before this began
            client, kind, v, *_ = op
            if kind == "r" and v != value:
                continue
            rest = [o for o in remaining if o is not op]
            found = search(rest, v, order + [f"{client}:{kind}({v})"])
            if found:
                return found
        return None
    found = search(list(history), initial, [])
    return (True, " -> ".join(found)) if found else (False, "no valid order exists")

# A writer sets x=1 from t=0 to t=10, overlapping both reads.
fine   = [("W", "w", 1, 0, 10), ("A", "r", 0, 1, 2), ("B", "r", 1, 3, 4)]
# Same, but A reads the new value, and then B, starting later, reads the old one.
broken = [("W", "w", 1, 0, 10), ("A", "r", 1, 1, 2), ("B", "r", 0, 3, 4)]
print("old then new, during the write:", linearizable(fine))
print("new then old, during the write:", linearizable(broken))
print("--- linear_checker done")

# --- quorum_history ---
import random

class Replica:
    def __init__(self):
        self.value, self.version = 0, 0

def run_quorum(n, r, seed, reads_between=2):
    """A write (to all n) reaches replicas one at a time while reads run. Each read asks r
    replicas and keeps the highest version. Returns a history for the checker."""
    rng = random.Random(seed)
    replicas = [Replica() for _ in range(n)]
    history, t = [], 0
    for step, target in enumerate(rng.sample(range(n), n)):
        replicas[target].value, replicas[target].version = 1, 1      # one more replica has it
        if step < n - 1:                                             # write still in flight
            for i in range(reads_between):
                best = max(rng.sample(replicas, r), key=lambda x: x.version)
                history.append((f"R{t}", "r", best.value, t, t + 0.5))
                t += 1
    return [("W", "w", 1, -1, t + 1)] + history

def share_non_linearizable(n, r, runs=5000):
    return sum(not linearizable(run_quorum(n, r, seed))[0] for seed in range(runs)) / runs

for n, r in [(3, 2), (5, 3)]:
    print(f"n={n} w={n} r={r} (w + r > n): {share_non_linearizable(n, r):.0%} of runs not linearizable")
example = next(h for h in (run_quorum(3, 2, s) for s in range(100)) if not linearizable(h)[0])
print("example:", [(c, k, v) for c, k, v, *_ in example])

def single_leader_history(seed):
    """All reads go to one node, which switches once from the old value to the new."""
    switch, history = random.Random(seed).randrange(5), []
    for t in range(5):
        history.append((f"R{t}", "r", int(t >= switch), t, t + 0.5))
    return [("W", "w", 1, -1, 6)] + history

print("reading from a single leader:",
      sum(not linearizable(single_leader_history(s))[0] for s in range(5000)), "of 5000 not linearizable")
print("--- quorum_history done")

# --- lamport ---
class Node:
    def __init__(self, name):
        self.name, self.counter = name, 0
    def event(self):
        self.counter += 1
        return (self.counter, self.name)
    def send(self):
        return self.event()
    def receive(self, stamp):
        self.counter = max(self.counter, stamp[0])
        return self.event()

a, b, c = Node("A"), Node("B"), Node("C")
log = []
def record(label, stamp): log.append((stamp, label))

record("A: rider requests trip", a.event())
m = a.send(); record("A: sends request", m)
record("B: driver accepts", b.receive(m))
record("B: driver sends arrival", (m2 := b.send()))
record("C: unrelated trip elsewhere", c.event())
record("C: payment on arrival", c.receive(m2))
for stamp, label in sorted(log):
    print(stamp, label)
print("--- lamport done")

# --- username ---
def claim_with_lamport():
    """Two nodes each accept a username claim, then later compare timestamps."""
    a, b = Node("A"), Node("B")
    sa, sb = a.event(), b.event()
    winner = min((sa, "Rae"), (sb, "Sam"))
    print(f"each node said yes at once, without waiting: A stamped {sa}, B stamped {sb}")
    print(f"after they exchange stamps the winner is {winner[1]}, so the other's success was premature")

claim_with_lamport()
print("--- username done")

# --- tob ---
class Log:
    """Total order broadcast: a single sequence that every consumer applies in the same order."""
    def __init__(self):
        self.entries = []
    def append(self, msg):
        self.entries.append(msg)
        return len(self.entries) - 1

def apply(log, upto=None):
    owners = {}
    for i, (kind, key, who) in enumerate(log.entries[:upto]):
        if kind == "claim" and key not in owners:
            owners[key] = who
    return owners

def claim(log, key, who):
    position = log.append(("claim", key, who))         # 1. append a tentative claim
    owners = apply(log, position + 1)                  # 2. read the log up to our own message
    return owners[key] == who                          # 3. did ours come first?

log = Log()
print("Rae claims vehicle-9:", claim(log, "vehicle-9", "Rae"))
print("Sam claims vehicle-9:", claim(log, "vehicle-9", "Sam"))
print("Sam claims vehicle-3:", claim(log, "vehicle-3", "Sam"))
print("two replicas replaying the log agree:", apply(log) == apply(log), apply(log))
print("--- tob done")

# --- twopc ---
class Participant:
    def __init__(self, name, will_vote=True):
        self.name, self.will_vote, self.state, self.locks = name, will_vote, "active", True
    def prepare(self):
        self.state = "prepared" if self.will_vote else "aborted"
        if not self.will_vote:
            self.locks = False
        return self.will_vote
    def finish(self, decision):
        self.state, self.locks = decision, False

def two_phase_commit(participants, coordinator_crash=None):
    """coordinator_crash: None, 'before_decision' or 'after_one_commit'."""
    votes = [p.prepare() for p in participants]
    decision = "committed" if all(votes) else "aborted"
    if coordinator_crash == "before_decision":
        return None
    for i, p in enumerate(participants):
        if coordinator_crash == "after_one_commit" and i == 1:
            return decision
        if p.state == "prepared" or decision == "aborted":
            p.finish(decision)
    return decision

def show(label, crash=None, votes=(True, True, True)):
    ps = [Participant(n, v) for n, v in zip(("warehouse", "ledger", "queue"), votes)]
    two_phase_commit(ps, crash)
    print(f"{label:<34}", {p.name: p.state + ("*" if p.locks else "") for p in ps})

print("* = still holding locks")
show("all vote yes")
show("ledger votes no", votes=(True, False, True))
show("coordinator dies before deciding", "before_decision")
show("coordinator dies mid-commit", "after_one_commit")
print("--- twopc done")

# --- pg_2pc ---
import sys, tempfile, time
try:
    import pgserver, psycopg
except ImportError:
    pgserver = None
    print("skipped: needs --python 3.12 --with pgserver --with 'psycopg[binary]'")
if pgserver:
    data = tempfile.mkdtemp()
    pg = pgserver.get_server(data)
    with psycopg.connect(pg.get_uri(), autocommit=True) as c:
        c.execute("alter system set max_prepared_transactions = 10")
    pg.cleanup()                                   # the setting needs a restart
    pg = pgserver.get_server(data)
    uri = pg.get_uri()
    with psycopg.connect(uri, autocommit=True) as c:
        c.execute("create table payout(driver int primary key, cents int)")
        c.execute("insert into payout values (7, 0)")

    # A participant does its work and votes yes, then the client disappears.
    client = psycopg.connect(uri, autocommit=True)
    client.execute("begin")
    client.execute("update payout set cents = 2000 where driver = 7")
    client.execute("prepare transaction 'trip-42'")
    client.close()                                 # coordinator gone, no decision delivered

    with psycopg.connect(uri, autocommit=True) as c:
        print("in doubt:", c.execute("select gid, prepared::time(0) is not null from pg_prepared_xacts").fetchall())
        print("visible value:", c.execute("select cents from payout").fetchone()[0])
        c.execute("set lock_timeout = '200ms'")
        try:
            c.execute("update payout set cents = 1 where driver = 7")
        except psycopg.errors.LockNotAvailable as e:
            print("another writer:", str(e).splitlines()[0])

    pg.cleanup()                                   # restart the database: does the promise survive?
    pg = pgserver.get_server(data)
    with psycopg.connect(pg.get_uri(), autocommit=True) as c:
        print("after a restart, still in doubt:", c.execute("select gid from pg_prepared_xacts").fetchall())
        c.execute("commit prepared 'trip-42'")     # a human or recovery tool plays coordinator
        print("after commit prepared:", c.execute("select cents from payout").fetchone()[0])
    pg.cleanup()
print("--- pg_2pc done")

# --- consensus ---
class ConsensusNode:
    def __init__(self, id):
        self.id, self.term, self.voted_for = id, 0, None
        self.log = []          # entries of (term, value)
        self.committed = 0

def up_to_date(cand_log, voter_log):
    last = lambda log: (log[-1][0], len(log)) if log else (0, 0)
    return last(cand_log) >= last(voter_log)

class Cluster:
    """A small Raft-shaped consensus: terms, one vote per term, majority to win and to commit."""
    def __init__(self, n, seed):
        self.nodes = [ConsensusNode(i) for i in range(n)]
        self.majority = n // 2 + 1
        self.rng = random.Random(seed)
        self.reachable = {i: set(range(n)) for i in range(n)}
        self.leaders = {}      # term -> leader id
        self.acked = []        # (value, term, index) the client was told succeeded

    def can_talk(self, a, b):
        return b in self.reachable[a]

    def partition(self):
        ids = list(range(len(self.nodes)))
        self.rng.shuffle(ids)
        cut = self.rng.randrange(1, len(ids))
        left, right = set(ids[:cut]), set(ids[cut:])
        for i in left:
            self.reachable[i] = left
        for i in right:
            self.reachable[i] = right

    def heal(self):
        self.reachable = {i: set(range(len(self.nodes))) for i in range(len(self.nodes))}

    def elect(self, cand_id):
        cand = self.nodes[cand_id]
        cand.term += 1
        cand.voted_for = cand_id
        votes = 1
        for n in self.nodes:
            if n.id == cand_id or not self.can_talk(cand_id, n.id):
                continue
            if cand.term > n.term:
                n.term, n.voted_for = cand.term, None
            if n.term == cand.term and n.voted_for is None and up_to_date(cand.log, n.log):
                n.voted_for = cand_id
                votes += 1
        if votes >= self.majority:
            assert self.leaders.get(cand.term, cand_id) == cand_id, "two leaders in one term"
            self.leaders[cand.term] = cand_id
            return True
        return False

    def replicate(self, leader_id, value):
        """A leader appends and copies to whoever it can reach. Stale leaders get refused."""
        leader = self.nodes[leader_id]
        if self.leaders.get(leader.term) != leader_id:
            return False
        entry = (leader.term, value)
        leader.log.append(entry)
        acks = 1
        for n in self.nodes:
            if n.id == leader_id or not self.can_talk(leader_id, n.id):
                continue
            if n.term > leader.term:                    # a follower has seen a newer term: refuse
                continue
            n.term = leader.term
            n.log = list(leader.log)                    # simplification: follower adopts the leader's log
            acks += 1
        if acks >= self.majority:
            self.acked.append((value, leader.term, len(leader.log) - 1))
            return True
        return False

def run_trial(seed, n=5, steps=60):
    cluster = Cluster(n, seed)
    rng = random.Random(seed + 1)
    leader, stale_rejected, value = None, 0, 0
    for _ in range(steps):
        event = rng.random()
        if event < 0.15:
            cluster.partition()
        elif event < 0.30:
            cluster.heal()
        elif event < 0.55 or leader is None:
            candidate = rng.randrange(n)
            if cluster.elect(candidate):
                leader = candidate
        else:
            value += 1
            target = leader if rng.random() < 0.8 else rng.randrange(n)
            cluster.replicate(target, value)
        for v, term, index in cluster.acked:
            # Safety: any later leader's log must still contain every acknowledged entry.
            newest = max(cluster.leaders, default=0)
            if newest and term <= newest:
                log = cluster.nodes[cluster.leaders[newest]].log
                assert index < len(log) and log[index] == (term, v), f"lost acked write {v}"
    return len(cluster.leaders), len(cluster.acked)

trials = 3000
terms = acked = 0
for seed in range(trials):
    t, a = run_trial(seed)
    terms += t
    acked += a
print(f"{trials} random runs with partitions: {terms} leaders elected, {acked} writes acknowledged")
print("invariants checked after every step: at most one leader per term, no acknowledged write lost")
print("--- consensus done")

# --- consensus_scenario ---
c = Cluster(5, seed=0)
print("node 0 elected:", c.elect(0), "term", c.nodes[0].term)
print("write a, all reachable:", c.replicate(0, "a"))
c.reachable = {0: {0, 1}, 1: {0, 1}, 2: {2, 3, 4}, 3: {2, 3, 4}, 4: {2, 3, 4}}
print("partition {0,1} | {2,3,4}")
print("old leader writes b, reaches 2 of 5:", c.replicate(0, "b"), "(not acknowledged)")
print("node 2 elected on the majority side:", c.elect(2), "term", c.nodes[2].term)
print("node 2 writes c:", c.replicate(2, "c"))
c.heal()
print("healed; old leader tries d in term", c.nodes[0].term, ":", c.replicate(0, "d"))
print("logs:", {n.id: [v for _, v in n.log] for n in c.nodes})
print("node 2 writes e:", c.replicate(2, "e"))
print("logs:", {n.id: [v for _, v in n.log] for n in c.nodes})
print("--- consensus_scenario done")

# --- broken_quorum ---
def run_trial_minority(seed, n=5, steps=60):
    """The same protocol, but with a 'majority' of only 2 of 5."""
    cluster = Cluster(n, seed)
    cluster.majority = 2
    rng = random.Random(seed + 1)
    leader, value = None, 0
    try:
        for _ in range(steps):
            event = rng.random()
            if event < 0.15:
                cluster.partition()
            elif event < 0.30:
                cluster.heal()
            elif event < 0.55 or leader is None:
                candidate = rng.randrange(n)
                if cluster.elect(candidate):
                    leader = candidate
            else:
                value += 1
                cluster.replicate(leader, value)
            for v, term, index in cluster.acked:
                newest = max(cluster.leaders, default=0)
                if newest and term <= newest:
                    log = cluster.nodes[cluster.leaders[newest]].log
                    assert index < len(log) and log[index] == (term, v), "lost"
    except AssertionError as e:
        return str(e)
    return None

failures = [run_trial_minority(s) for s in range(1000)]
print(f"quorum of 2 of 5: {sum(f is not None for f in failures)} of 1000 runs broke an invariant")
print("--- broken_quorum done")
