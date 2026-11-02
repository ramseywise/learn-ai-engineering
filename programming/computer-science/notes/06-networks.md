---
origin: synthesis
sources:
  - "RFC 9293, Transmission Control Protocol — https://www.rfc-editor.org/rfc/rfc9293"
  - "RFC 6298, Computing TCP's Retransmission Timer — https://www.rfc-editor.org/rfc/rfc6298"
  - "RFC 5681, TCP Congestion Control — https://www.rfc-editor.org/rfc/rfc5681"
  - "RFC 6928, Increasing TCP's Initial Window — https://www.rfc-editor.org/rfc/rfc6928"
  - "RFC 1034 and RFC 1035, Domain Names — https://www.rfc-editor.org/rfc/rfc1035"
  - "RFC 8305, Happy Eyeballs Version 2 — https://www.rfc-editor.org/rfc/rfc8305"
  - "RFC 9110 and RFC 9112, HTTP Semantics and HTTP/1.1 — https://www.rfc-editor.org/rfc/rfc9112"
  - "RFC 9113, HTTP/2; RFC 9114, HTTP/3; RFC 9000, QUIC — https://www.rfc-editor.org/rfc/rfc9114"
  - "RFC 8446, TLS 1.3; RFC 6066, TLS Extensions — https://www.rfc-editor.org/rfc/rfc8446"
  - "Python docs: socket, ssl, http.client — https://docs.python.org/3.14/library/socket.html"
concepts: [tcp, three-way-handshake, time-wait, retransmission-timeout, bandwidth-delay-product, slow-start, aimd, dns, http-1-1, chunked-encoding, keep-alive, http-2, quic, tls-1-3, sni, cold-request-budget]
confidence: high
cleaned: 2026-11-02
---
# 6 — Networks

> A cold HTTPS request cost me 317 ms in this chapter, and a second one on the same connection cost 21 ms. No amount of Python optimisation can touch that 15-fold gap. It comes from round trips: one for TCP, one for TLS, more for slow start, and DNS on top. Once you can count those, you can explain why connection pools matter, why a small response gets to you in one round trip while a large one takes several, and why retries can double-charge a customer unless you think about idempotency. This chapter goes through each layer using its RFC and a working Python socket, including building a DNS query and reading TLS flights by hand. Most blocks run on loopback, so they work anywhere. The two marked blocks use the real network, and only run with `bash check.sh network`.

---

## TCP is a stream, not messages

TCP gives you an ordered, reliable stream of bytes between two endpoints ([RFC 9293](https://www.rfc-editor.org/rfc/rfc9293)). The first thing to absorb is what it doesn't give you, which is message boundaries:

```python
import socket
import threading
import time


def pair():
    listener = socket.create_server(("127.0.0.1", 0))
    client = socket.create_connection(listener.getsockname())
    server, _ = listener.accept()
    listener.close()
    return client, server


client, server = pair()
for msg in (b"first", b"second", b"third"):
    client.sendall(msg)
time.sleep(0.05)
print("3 sends, 1 recv:", server.recv(1024))

big = bytes(4_000_000)
sender = threading.Thread(target=client.sendall, args=(big,))
sender.start()
sizes = []
while sum(sizes) < len(big):
    sizes.append(len(server.recv(1 << 20)))
sender.join()
print(f"1 send of {len(big):,} bytes, {len(sizes)} recvs, sizes from {min(sizes):,} to {max(sizes):,}")
client.close()
server.close()
```

<!-- measured -->

```text
3 sends, 1 recv: b'firstsecondthird'
1 send of 4,000,000 bytes, 54 recvs, sizes from 416 to 433,604
```

Three `send`s came out as one `recv`, and one 4 MB `send` came out as 54 pieces of varying size. `recv` returns whatever has arrived so far, and that's all it promises. Code that assumes `recv` returns one message passes on loopback with small messages and fails in production. It's the most common networking bug there is.

So every protocol on top of TCP has to mark its own boundaries, using either a length prefix or a delimiter. You'll write a 4-byte big-endian length-prefix decoder in the [lab](../practice/README.md), and the test cuts the stream at every possible byte position. Multi-byte integers on the wire are big-endian by convention, the byte order from [chapter 4](04-numbers-and-memory.md#bits-youll-actually-use).

## Opening and closing a connection

[Section 3.5 of RFC 9293](https://www.rfc-editor.org/rfc/rfc9293#section-3.5) sets out the three-way handshake. Each side picks a starting sequence number and has it acknowledged, and that takes SYN, SYN-ACK and ACK. The client can send data with its ACK, so the handshake costs one round trip before the first byte of the request goes out:

```text
client                                   server
  |  -------- SYN seq=x ------------->     |
  |  <------- SYN-ACK seq=y ack=x+1 --     |   1 RTT before the client may send
  |  -------- ACK, then request ----->     |
  |  <------- response ---------------     |   1 more RTT for the first byte back
  |  -------- FIN ------------------->     |
  |  <------- ACK, FIN ---------------     |
  |  -------- ACK ------------------->     |   the side that closed first waits in
  |          TIME-WAIT, 2 x MSL            |   TIME-WAIT
```

Closing is separate in each direction, so one side can finish sending and keep receiving, which is called a half-close ([Section 3.6.1](https://www.rfc-editor.org/rfc/rfc9293#section-3.6.1)). The side that closes first then stays in TIME-WAIT for 2 × MSL, the maximum segment lifetime, so a delayed segment can't turn up in a later connection using the same address and ports, and so that its last ACK can be resent if lost. The RFC takes MSL to be 2 minutes, an engineering choice, and implementations vary. Here's that state showing up in practice, along with what a new connection costs even with no network in between:

```python
import socket
import threading
import time


def echo_server(listener, stop):
    def handle(conn):
        with conn:
            while data := conn.recv(64):
                conn.sendall(data)

    listener.settimeout(0.1)
    while not stop.is_set():
        try:
            conn, _ = listener.accept()
        except TimeoutError:
            continue
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


listener = socket.create_server(("127.0.0.1", 0), backlog=128)
addr = listener.getsockname()
stop = threading.Event()
threading.Thread(target=echo_server, args=(listener, stop), daemon=True).start()
n = 2_000

start = time.perf_counter()
for _ in range(n):
    with socket.create_connection(addr) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.sendall(b"x")
        s.recv(64)
fresh = (time.perf_counter() - start) / n

with socket.create_connection(addr) as s:
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    start = time.perf_counter()
    for _ in range(n):
        s.sendall(b"x")
        s.recv(64)
    reused = (time.perf_counter() - start) / n
stop.set()
print(f"loopback, new connection each time: {fresh * 1e6:7.1f} us per request")
print(f"loopback, reused connection:        {reused * 1e6:7.1f} us per request")

import shutil
import subprocess

time.sleep(0.2)
if shutil.which("netstat"):
    out = subprocess.run(["netstat", "-an", "-p", "tcp"], capture_output=True, text=True).stdout
    port = str(addr[1])
    waiting = [l for l in out.splitlines() if "TIME_WAIT" in l and port in l]
    print(f"sockets in TIME_WAIT for this port: {len(waiting):,}")
```

<!-- measured -->

```text
loopback, new connection each time:    88.0 us per request
loopback, reused connection:           17.4 us per request
sockets in TIME_WAIT for this port: 2,001
```

Opening a connection per request is 5 times slower on loopback, where the round trip is near zero. Over a real network the ratio is far larger. It also left 2,001 sockets in TIME-WAIT, and each one holds a client port for a while. Under enough load, a service that doesn't reuse connections runs out of ports, with an error about addresses that doesn't explain itself. That's the case for connection pools.

There's another classic latency trap here. Nagle's algorithm ([Section 3.7.4](https://www.rfc-editor.org/rfc/rfc9293#section-3.7.4)) holds back small segments while earlier data is unacknowledged, and combined with delayed ACKs it can stall a write-write-read pattern. I tried to reproduce the stall on macOS loopback and couldn't: 0.03 ms with `TCP_NODELAY` and 0.05 ms without, so I'm not showing it as a measured effect. Setting `TCP_NODELAY` on request-response connections is still normal.

## How long to wait before resending

TCP detects loss by missing acknowledgements, and it has to decide how long to wait. Too short and it sends needless duplicates. Too long and a lost packet stalls everything. [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298) keeps a smoothed average of round-trip time and of its variation, and waits for the average plus four times the variation:

```python
class RtoEstimator:
    """RFC 6298, section 2. Times in seconds; G is the clock granularity."""

    def __init__(self, g=0.001, floor=1.0):
        self.g, self.floor = g, floor
        self.srtt = self.rttvar = None
        self.rto = 1.0

    def sample(self, r):
        if self.srtt is None:
            self.srtt, self.rttvar = r, r / 2
        else:
            self.rttvar = 0.75 * self.rttvar + 0.25 * abs(self.srtt - r)  # uses the old srtt
            self.srtt = 0.875 * self.srtt + 0.125 * r
        self.rto = max(self.floor, self.srtt + max(self.g, 4 * self.rttvar))
        return self.rto


for label, samples in [("steady", [0.1] * 6), ("spike ", [0.1, 0.1, 0.1, 0.5, 0.1, 0.1])]:
    e = RtoEstimator(floor=0.0)  # floor off, to see the estimator itself
    print(label, [round(e.sample(s), 3) for s in samples])
print("with the 1 s floor:", round(RtoEstimator().sample(0.1), 3))
```

```text
steady [0.3, 0.25, 0.213, 0.184, 0.163, 0.147]
spike  [0.3, 0.25, 0.213, 0.634, 0.557, 0.492]
with the 1 s floor: 1.0
```

With steady samples, the timeout falls towards the real RTT as the variance term decays. One 500 ms spike more than doubles it, and it comes down slowly, which is deliberate: after a surprise, TCP is cautious. The last line shows the [1 second floor](https://www.rfc-editor.org/rfc/rfc6298#section-2) that the RFC specifies, and in practice that floor dominates on fast links: a lost packet on a 1 ms link can still stall for a second. After each timeout it doubles the wait (rule 5.5), with an allowed maximum of at least 60 seconds.

You'll write this in the [lab](../practice/README.md), and the order of the two update lines matters, since `RTTVAR` has to use the old `SRTT`. A test catches this.

The same shape, exponential backoff with a bound and an estimate of normal latency, is what your own retry code should have. See [when distributed systems fail](../../../data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail.md).

## Windows and the bandwidth-delay product

A sender can only have so many unacknowledged bytes in flight, and it's limited by the window. Throughput is therefore at most one window per round trip, and to use a link fully, the window has to be as large as the bandwidth times the delay. That product is how many bytes fit in the pipe:

```python
def bdp_bytes(mbps, rtt_ms):
    return mbps * 1e6 / 8 * rtt_ms / 1e3


print(f"{'link':>9} {'RTT':>6} {'BDP':>10}   max rate with a 64 KiB window")
for mbps, rtt in [(100, 1), (100, 20), (1_000, 20), (1_000, 100), (10_000, 100)]:
    limit = 65_536 * 8 / (rtt / 1e3) / 1e6
    print(f"{mbps:>6}Mbit {rtt:>4}ms {bdp_bytes(mbps, rtt) / 1e6:>8.3f}MB   {min(limit, mbps):>8.1f} Mbit/s")


def rounds_to_send(total, mss=1460):
    """Round trips of pure slow start with no loss: the window doubles each round."""
    sent, cwnd, rounds = 0, min(10 * mss, max(2 * mss, 14_600)), 0  # RFC 6928's initial window
    while sent < total:
        sent += cwnd
        cwnd *= 2
        rounds += 1
    return rounds


print(f"\n{'response':>10} {'rounds':>7} {'at 50 ms RTT':>13}")
for size in (1_000, 14_000, 15_000, 100_000, 1_000_000, 10_000_000):
    r = rounds_to_send(size)
    print(f"{size:>10,} {r:>7} {r * 50:>10} ms")


def aimd(rounds, capacity=100):
    """Two senders on one link: add one segment per round trip, halve both on a loss."""
    a, b, gaps = 80.0, 10.0, [70.0]
    for _ in range(rounds):
        if a + b > capacity:
            a, b = a / 2, b / 2
            gaps.append(a - b)
        else:
            a, b = a + 1, b + 1
    return a, b, gaps


a, b, gaps = aimd(300)
print("\nAIMD, gap between two flows after each loss:", [round(g, 1) for g in gaps[:6]], f"after {len(gaps) - 1} losses: {gaps[-1]:.4f}")
```

```text
     link    RTT        BDP   max rate with a 64 KiB window
   100Mbit    1ms    0.013MB      100.0 Mbit/s
   100Mbit   20ms    0.250MB       26.2 Mbit/s
  1000Mbit   20ms    2.500MB       26.2 Mbit/s
  1000Mbit  100ms   12.500MB        5.2 Mbit/s
 10000Mbit  100ms  125.000MB        5.2 Mbit/s

  response  rounds  at 50 ms RTT
     1,000       1         50 ms
    14,000       1         50 ms
    15,000       2        100 ms
   100,000       3        150 ms
 1,000,000       7        350 ms
10,000,000      10        500 ms

AIMD, gap between two flows after each loss: [70.0, 35.0, 17.5, 8.8, 4.4, 2.2] after 12 losses: 0.0171
```

The top table is the point: a 64 KiB window, the most that the 16-bit header field can express without the window-scale option, caps you at 26 Mbit/s at 20 ms, however fast the link. At 100 ms it's 5 Mbit/s even on a 10 Gbit link. RFC 9293 mentions the option, and I've not read its own RFC. The lesson for you is that "the network is 10 Gbit" doesn't tell you the throughput of one connection across an ocean. Latency and window size do.

## Slow start: why small responses are special

A new connection doesn't know how fast the path is, so it starts small and probes. Under [RFC 5681](https://www.rfc-editor.org/rfc/rfc5681#section-3.1), the congestion window grows by up to one segment per ACK during slow start, and that doubles it every round trip. [RFC 6928](https://www.rfc-editor.org/rfc/rfc6928) set the initial window at up to 10 segments, about 14,600 bytes. The second table in the block above works through the rounds, in a simple model that has no loss and ignores receive limits.

Two consequences follow. A response under about 14 KB arrives in one round trip, so trimming a 15 KB response down to 14 KB saves a whole RTT, and it's the only case where a small byte saving matters so much. And a long connection that's already warmed up doesn't pay any of this, which is another argument for pools. A 1 MB response needs 7 round trips at first: at 50 ms RTT that's 350 ms, however fast the link, and it's a big part of why a cold first request is so slow.

## Sharing a link: AIMD

Nothing assigns bandwidth centrally. Each sender infers congestion from loss. On loss, the RFC 5681 sender cuts its threshold to half of what's in flight (`ssthresh = max(FlightSize / 2, 2 * SMSS)`), and between losses it adds about one segment per round trip. That's additive increase and multiplicative decrease.

The last line of the block above shows why that's a good rule. It's a simulation I wrote, with two senders on one link, and not a measurement of real TCP. Adding one to both leaves the gap between them unchanged, while halving both halves the gap. After 12 losses, a 70-segment gap is about 0.02. So senders that don't communicate converge on a fair share. It's why a long download doesn't starve your other connections, and it also means that loss is a normal signal in TCP and not a failure: a throughput graph looks like a sawtooth by design.

## DNS: a small protocol worth reading once

Before any of this, a name has to become an address. [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035) has a compact binary format, and you can build a query in about ten lines:

```python
import socket
import struct


def encode_name(name):
    out = b""
    for label in name.rstrip(".").split("."):
        out += bytes([len(label)]) + label.encode("ascii")
    return out + b"\x00"


def build_query(name, qid=0x1234, qtype=1):
    flags = 0x0100  # RD: please recurse for me
    header = struct.pack(">HHHHHH", qid, flags, 1, 0, 0, 0)
    return header + encode_name(name) + struct.pack(">HH", qtype, 1)


def read_name(msg, at):
    """Returns (name, offset after it). Follows compression pointers, refuses loops."""
    labels, jumped, end, seen = [], False, at, set()
    while True:
        length = msg[at]
        if length & 0xC0 == 0xC0:  # top two bits set: a 14-bit offset to earlier in the message
            target = struct.unpack(">H", msg[at:at + 2])[0] & 0x3FFF
            if target in seen:
                raise ValueError("compression loop")
            seen.add(target)
            if not jumped:
                end, jumped = at + 2, True
            at = target
        elif length == 0:
            return ".".join(labels), (end if jumped else at + 1)
        else:
            labels.append(msg[at + 1:at + 1 + length].decode("ascii"))
            at += 1 + length


def parse_response(msg):
    qid, flags, qd, an, _, _ = struct.unpack(">HHHHHH", msg[:12])
    at = 12
    for _ in range(qd):
        _, at = read_name(msg, at)
        at += 4
    answers = []
    for _ in range(an):
        name, at = read_name(msg, at)
        rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", msg[at:at + 10])
        at += 10
        rdata = msg[at:at + rdlength]
        answers.append((name, rtype, ttl, socket.inet_ntoa(rdata) if rtype == 1 else rdata.hex()))
        at += rdlength
    return {"id": qid, "qr": flags >> 15, "rcode": flags & 0xF, "answers": answers}


query = build_query("example.com")
print(query.hex(" "))
print(len(query), "bytes")

# A response built by hand. 0xC00C is a pointer to offset 12, where the question's name starts.
answer = struct.pack(">HHHIH", 0xC00C, 1, 1, 300, 4) + socket.inet_aton("192.0.2.1")  # RFC 5737 address
canned = struct.pack(">HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0) + query[12:] + answer
print(parse_response(canned))
print("name repeated uncompressed would cost", len(encode_name("example.com")), "bytes; the pointer costs 2")
```

```text
12 34 01 00 00 01 00 00 00 00 00 00 07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01
29 bytes
{'id': 4660, 'qr': 1, 'rcode': 0, 'answers': [('example.com', 1, 300, '192.0.2.1')]}
name repeated uncompressed would cost 13 bytes; the pointer costs 2
```

Read the hex against [Section 4.1.1](https://www.rfc-editor.org/rfc/rfc1035#section-4.1.1): a 2-byte id, flags `0100` with the "recursion desired" bit, one question and no other records. The name follows as length-prefixed labels, `07 example 03 com 00`, then type A and class IN. Compression ([Section 4.1.4](https://www.rfc-editor.org/rfc/rfc1035#section-4.1.4)) lets a later name point back at an earlier one in 2 bytes, with the top two bits set, which matters because [plain UDP messages are limited to 512 bytes](https://www.rfc-editor.org/rfc/rfc1035#section-4.2.1) and longer answers get truncated with the `TC` bit. A parser that follows pointers has to refuse loops, and this one does, since a malicious response could otherwise spin it forever.

Your stub resolver asks a recursive resolver to do the walking from the root down, and each answer has a TTL that says how long it can be cached ([RFC 1034](https://www.rfc-editor.org/rfc/rfc1034)). Here's the real thing, sending the same bytes to a public resolver:

<!-- requires: network -->
```python
import struct
import socket
import time
def encode_name(name):
    out = b""
    for label in name.rstrip(".").split("."):
        out += bytes([len(label)]) + label.encode("ascii")
    return out + b"\x00"


def build_query(name, qid=0x1234, qtype=1):
    flags = 0x0100  # RD: please recurse for me
    header = struct.pack(">HHHHHH", qid, flags, 1, 0, 0, 0)
    return header + encode_name(name) + struct.pack(">HH", qtype, 1)


def read_name(msg, at):
    """Returns (name, offset after it). Follows compression pointers, refuses loops."""
    labels, jumped, end, seen = [], False, at, set()
    while True:
        length = msg[at]
        if length & 0xC0 == 0xC0:  # top two bits set: a 14-bit offset to earlier in the message
            target = struct.unpack(">H", msg[at:at + 2])[0] & 0x3FFF
            if target in seen:
                raise ValueError("compression loop")
            seen.add(target)
            if not jumped:
                end, jumped = at + 2, True
            at = target
        elif length == 0:
            return ".".join(labels), (end if jumped else at + 1)
        else:
            labels.append(msg[at + 1:at + 1 + length].decode("ascii"))
            at += 1 + length


def parse_response(msg):
    qid, flags, qd, an, _, _ = struct.unpack(">HHHHHH", msg[:12])
    at = 12
    for _ in range(qd):
        _, at = read_name(msg, at)
        at += 4
    answers = []
    for _ in range(an):
        name, at = read_name(msg, at)
        rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", msg[at:at + 10])
        at += 10
        rdata = msg[at:at + rdlength]
        answers.append((name, rtype, ttl, socket.inet_ntoa(rdata) if rtype == 1 else rdata.hex()))
        at += rdlength
    return {"id": qid, "qr": flags >> 15, "rcode": flags & 0xF, "answers": answers}



with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(3)
    query = build_query("example.com", qid=0x4242)
    start = time.perf_counter()
    s.sendto(query, ("1.1.1.1", 53))
    reply, _ = s.recvfrom(512)
    ms = (time.perf_counter() - start) * 1e3
r = parse_response(reply)
print(f"{ms:.1f} ms, {len(reply)} bytes, id match {r['id'] == 0x4242}, rcode {r['rcode']}")
for name, rtype, ttl, data in r["answers"]:
    print(f"  {name} type {rtype} ttl {ttl}s {data}")

for attempt in range(3):
    start = time.perf_counter()
    infos = socket.getaddrinfo("example.com", 443, type=socket.SOCK_STREAM)
    print(f"getaddrinfo #{attempt + 1}: {(time.perf_counter() - start) * 1e3:7.2f} ms, {len(infos)} addresses, families {sorted({i[0].name for i in infos})}")
```

<!-- measured -->

```text
89.6 ms, 61 bytes, id match True, rcode 0
  example.com type 1 ttl 255s 104.20.23.154
  example.com type 1 ttl 255s 172.66.147.243
getaddrinfo #1:  102.90 ms, 4 addresses, families ['AF_INET', 'AF_INET6']
getaddrinfo #2:    0.96 ms, 4 addresses, families ['AF_INET', 'AF_INET6']
getaddrinfo #3:    0.81 ms, 4 addresses, families ['AF_INET', 'AF_INET6']
```

The first `getaddrinfo` takes 103 ms and the next ones under 1 ms, as the OS resolver has cached the answer. So DNS is either almost free or is the worst part of a request, and a cold service sees the bad case. There's also a design problem to consider: `getaddrinfo` is a blocking call, so it's exactly what mustn't be called directly [on an event loop](05-processes-threads-and-io.md#the-event-loop-many-waits-one-thread).

Note the 4 addresses across two families. [`socket.create_connection`](https://docs.python.org/3.14/library/socket.html#socket.create_connection) tries them in turn, so an unreachable first address can mean a long connect timeout before the next is tried. [RFC 8305](https://www.rfc-editor.org/rfc/rfc8305), Happy Eyeballs, races them instead, starting the next attempt after a delay, with 250 ms as its recommended default. Set explicit connect timeouts, and remember that the timeout may apply per address.

## HTTP/1.1 on top of TCP

HTTP/1.1 is text framing on the stream. It solves the same boundary problem: [Section 6.3 of RFC 9112](https://www.rfc-editor.org/rfc/rfc9112#section-6.3) gives the rules for finding a body's end, by `Content-Length`, by chunked coding, or by the connection closing. Chunked coding ([Section 7.1](https://www.rfc-editor.org/rfc/rfc9112#section-7.1)) is how a server streams a body of unknown length, each piece preceded by its size in hex, and that's what's under an LLM token stream:

```python
import http.client
import socket
import threading
import time

BODY = b'{"ok": true}'


def handle(conn):
    with conn:
        buffer = b""
        while True:
            while b"\r\n\r\n" not in buffer:
                data = conn.recv(4096)
                if not data:
                    return
                buffer += data
            head, buffer = buffer.split(b"\r\n\r\n", 1)
            target = head.split(b" ")[1]
            if target == b"/stream":
                conn.sendall(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n")
                for piece in (b"data: Hel\n\n", b"data: lo\n\n"):
                    conn.sendall(f"{len(piece):x}\r\n".encode() + piece + b"\r\n")
                conn.sendall(b"0\r\n\r\n")
            else:
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%b" % (len(BODY), BODY))


listener = socket.create_server(("127.0.0.1", 0), backlog=128)
host, port = listener.getsockname()


def serve():
    while True:
        conn, _ = listener.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


threading.Thread(target=serve, daemon=True).start()

# Raw bytes first: what chunked framing looks like on the wire.
with socket.create_connection((host, port)) as s:
    s.sendall(b"GET /stream HTTP/1.1\r\nHost: x\r\n\r\n")
    raw = b""
    while not raw.endswith(b"0\r\n\r\n"):
        raw += s.recv(4096)
print(raw)

# Then the same request through http.client, which decodes the framing.
conn = http.client.HTTPConnection(host, port)
conn.request("GET", "/stream")
print(conn.getresponse().read())

n = 2_000
start = time.perf_counter()
for _ in range(n):
    c = http.client.HTTPConnection(host, port)
    c.request("GET", "/")
    c.getresponse().read()
    c.close()
fresh = (time.perf_counter() - start) / n
c = http.client.HTTPConnection(host, port)
start = time.perf_counter()
for _ in range(n):
    c.request("GET", "/")
    c.getresponse().read()
reuse = (time.perf_counter() - start) / n
print(f"http.client on loopback: new connection {fresh * 1e6:.0f} us, keep-alive {reuse * 1e6:.0f} us per request")
```

<!-- measured -->

```text
b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\nb\r\ndata: Hel\n\n\r\na\r\ndata: lo\n\n\r\n0\r\n\r\n'
b'data: Hel\n\ndata: lo\n\n'
http.client on loopback: new connection 128 us, keep-alive 38 us per request
```

The raw bytes show the frames: `b\r\n` is 11 bytes in hex, then the piece, and `0\r\n\r\n` ends it. `http.client` removes the framing. Note that chunk boundaries don't have to line up with application events: if you're parsing server-sent events, an event can be split across chunks, and this is the `recv` lesson again, so buffer until you've got a complete event.

The second result is keep-alive: 128 µs against 38 µs on loopback, for the same reason as before. HTTP/1.1 connections are [persistent by default](https://www.rfc-editor.org/rfc/rfc9112#section-9.3). A library's `Session` or `Client` object is what holds that pool, so creating a new one per request throws it away, and that's the single most common HTTP performance bug in Python services.

A connection can handle only one response at a time. [Pipelining](https://www.rfc-editor.org/rfc/rfc9112#section-9.3.2) allows sending requests ahead but responses must come back in order, so one slow response holds up the rest, and that's why clients open several connections.

Retries depend on the semantics in [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#section-9.2.2): idempotent methods have the same effect however many times they're applied, so a client can resend one after a dropped connection. A POST isn't, and if the connection dies mid-request you can't tell whether it took effect. That's why LLM and payment APIs offer idempotency keys.

## HTTP/2 and HTTP/3

[HTTP/2](https://www.rfc-editor.org/rfc/rfc9113) keeps the semantics and changes the framing: binary frames carrying many concurrent streams over one TCP connection, so one slow response no longer holds up the others at the HTTP layer. The RFC is plain that this doesn't fix TCP-level head-of-line blocking. TCP delivers in order, so one lost packet stalls every stream on that connection until the retransmission arrives, even those streams whose data has turned up.

[HTTP/3](https://www.rfc-editor.org/rfc/rfc9114) moves to [QUIC](https://www.rfc-editor.org/rfc/rfc9000), which runs over UDP and puts streams in the transport, so a loss delays only the stream it belongs to. QUIC also folds the transport and TLS handshakes together. That isn't free in code complexity, and I haven't measured it here since Python's standard library has no HTTP/2 or HTTP/3 client.

## TLS 1.3: one more round trip

TLS adds encryption and authentication on top of the stream. [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446#section-2) shows the full handshake in its Figure 1, and it takes one round trip: the client sends its key share up front, and the server responds with its own, a certificate and a signature, already encrypted. This uses an in-memory pair of TLS objects so that I can count what would go on the wire, with a throwaway certificate created at run time:

<!-- requires: openssl -->
```python
import os
import ssl
import subprocess
import tempfile
import time


def make_cert(directory, name="service.test"):
    """A throwaway self-signed certificate, created at run time and never stored."""
    key, cert = os.path.join(directory, "key.pem"), os.path.join(directory, "cert.pem")
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1",
         "-keyout", key, "-out", cert, "-days", "1", "-nodes", "-subj", f"/CN={name}",
         "-addext", f"subjectAltName=DNS:{name}"],
        check=True, capture_output=True,
    )
    return key, cert


def handshake(client_ctx, server_ctx, hostname):
    """Run a TLS handshake over two in-memory pipes; count flights and bytes."""
    c_in, c_out, s_in, s_out = ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO()
    client = client_ctx.wrap_bio(c_in, c_out, server_hostname=hostname)
    server = server_ctx.wrap_bio(s_in, s_out, server_side=True)
    flights = []
    done = {"client": False, "server": False}
    for side, obj in [("client", client), ("server", server)] * 5:
        if not done[side]:
            try:
                obj.do_handshake()
                done[side] = True
            except ssl.SSLWantReadError:
                pass
        out, into = (c_out, s_in) if side == "client" else (s_out, c_in)
        data = out.read()
        if data:
            flights.append((side, len(data)))
            into.write(data)
    return client, server, flights


with tempfile.TemporaryDirectory() as d:
    key, cert = make_cert(d)
    server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_ctx.load_cert_chain(cert, key)
    client_ctx = ssl.create_default_context(cafile=cert)
    print("hostname check on:", client_ctx.check_hostname, " verify mode:", client_ctx.verify_mode.name)

    client, server, flights = handshake(client_ctx, server_ctx, "service.test")
    print(client.version(), client.cipher()[0])
    print("flights:", flights)

    n = 200
    start = time.perf_counter()
    for _ in range(n):
        handshake(client_ctx, server_ctx, "service.test")
    print(f"full handshake CPU, both sides: {(time.perf_counter() - start) / n * 1e3:.2f} ms")

    try:
        handshake(client_ctx, server_ctx, "other.test")
    except ssl.SSLCertVerificationError as e:
        print("wrong name:", e.verify_message)
```

<!-- measured -->

```text
hostname check on: True  verify mode: CERT_REQUIRED
TLSv1.3 TLS_AES_256_GCM_SHA384
flights: [('client', 1517), ('server', 1874), ('client', 80), ('server', 510)]
full handshake CPU, both sides: 0.33 ms
wrong name: Hostname mismatch, certificate is not valid for 'other.test'.
```

The flights match the RFC's shape. The client's opening 1,517 bytes contain the key shares, and I haven't broken down the rest. The server's reply has the certificate and signature. The client answers with its 80-byte Finished, and the last 510 bytes are the server's [session tickets](https://www.rfc-editor.org/rfc/rfc8446#section-4.6.1), for later resumption.

The cost surprise is that the crypto is cheap: 0.33 ms of CPU for both sides together. So when someone says "TLS is slow", what's slow is the round trip, not the arithmetic. The handshake took 40 ms on the real network below, more than 100 times this CPU cost.

The last line is the part that actually protects you. [`ssl.create_default_context`](https://docs.python.org/3.14/library/ssl.html#ssl.create_default_context) turns on certificate and hostname checks. If you've ever turned them off with `verify=False` to silence an error, you've removed the authentication and left the encryption, which means you may well be encrypting to an attacker. The `server_hostname` argument is doing two jobs: it's what gets checked, and it's sent as the [SNI extension](https://www.rfc-editor.org/rfc/rfc6066#section-3), so a server hosting many names can present the right certificate.

Resumption can send data in the first flight (0-RTT), but [Section 2.3](https://www.rfc-editor.org/rfc/rfc8446#section-2.3) warns that it isn't protected against replay, as [Appendix E.5](https://www.rfc-editor.org/rfc/rfc8446#appendix-E.5) expands on. So it's for idempotent requests only, and it's the same reasoning as for retries.

## A budget for a cold request

Here's where the time goes on one real connection, measured from this machine to `example.com`:

<!-- requires: network -->
```python
import socket
import ssl
import time

HOST = "example.com"
t0 = time.perf_counter()
family, kind, proto, _, addr = socket.getaddrinfo(HOST, 443, type=socket.SOCK_STREAM)[0]
t1 = time.perf_counter()
raw = socket.socket(family, kind, proto)
raw.settimeout(5)
raw.connect(addr)
t2 = time.perf_counter()
tls = ssl.create_default_context().wrap_socket(raw, server_hostname=HOST)
t3 = time.perf_counter()
tls.sendall(f"HEAD / HTTP/1.1\r\nHost: {HOST}\r\nConnection: keep-alive\r\n\r\n".encode())
first = tls.recv(4096)
t4 = time.perf_counter()
print(f"{tls.version()}, {first.split(b'\r\n', 1)[0].decode()}")
print(f"DNS    {(t1 - t0) * 1e3:7.1f} ms")
print(f"TCP    {(t2 - t1) * 1e3:7.1f} ms")
print(f"TLS    {(t3 - t2) * 1e3:7.1f} ms")
print(f"HTTP   {(t4 - t3) * 1e3:7.1f} ms")
print(f"total  {(t4 - t0) * 1e3:7.1f} ms")
t5 = time.perf_counter()
tls.sendall(f"HEAD / HTTP/1.1\r\nHost: {HOST}\r\nConnection: close\r\n\r\n".encode())
tls.recv(4096)
print(f"second request on the same connection {(time.perf_counter() - t5) * 1e3:7.1f} ms")
tls.close()
```

<!-- measured -->

```text
TLSv1.3, HTTP/1.1 200 OK
DNS        2.9 ms
TCP       61.9 ms
TLS       40.4 ms
HTTP     211.8 ms
total    316.9 ms
second request on the same connection    21.2 ms
```

And laid out as round trips, on a path where the RTT is about 50 ms:

```text
                                RTTs  this run   avoided by
DNS (cached here)                0-1      3 ms   OS cache, DNS TTL
TCP handshake                      1     62 ms   connection pool
TLS 1.3 handshake                  1     40 ms   connection pool, resumption
Request, server time, 1st byte    1+    212 ms   server's own work and caching
                                       ------
Cold total                               317 ms
Same request, connection reused   1+     21 ms
```

The second request is 15 times faster, and it's the same code. Note that the "HTTP" row includes the server's own work and the path to wherever that request went, while the handshake rows are mostly raw round trips. Networks vary a lot, so run this from your own location before quoting these numbers: I got them from one run.

This is the arithmetic I'd do before optimising a slow API call. Count the round trips, multiply by the RTT, and compare with what you measured. If a service has a 500 ms budget and calls a dependency 50 ms away, a cold connection spends 100 ms on handshakes before it sends anything, and a response over 14 KB adds more round trips. Then check for per-request connections, which is the highest-yield fix and costs one line. Compare that with the [time budget for one request in chapter 1](01-cost-models-and-big-o.md#a-budget-for-one-request): the network often dwarfs everything your Python code does.

## Pitfalls

- **Assuming one `recv` is one message.** Symptom: it works locally and corrupts under load or on a slow link. Use a length prefix or a delimiter, and loop.
- **A new HTTP client per request.** Symptom: every call pays for TCP and TLS, p50 sits at several RTTs, and the server shows many TIME-WAIT sockets on the closing side.
- **No timeouts.** Symptom: a thread hangs forever on a dead peer. Set connect and read timeouts, remembering that connect may be per address.
- **Retrying a POST blindly.** Symptom: double charges or double sends. Use idempotency keys.
- **`verify=False`.** Symptom: none, until someone's intercepting your traffic. Install the correct CA instead.
- **Blocking DNS on an event loop.** Symptom: rare stalls of 100 ms and more that hit all clients.
- **Parsing a stream by chunk.** Symptom: a JSON error once in a while, when an event is split across chunks.
- **Caching DNS forever.** Symptom: traffic still goes to an old address after a failover. Respect TTLs.
- **Blaming bandwidth for slowness over distance.** Symptom: an upgrade changes nothing. Compute the BDP and check RTT and window first.

## Try it

1. Implement `FrameDecoder` in the [lab](../practice/README.md). Why does it check the header's length before buffering the body?
2. Implement `RtoEstimator`. What's the RTO after samples of 100 ms and then 300 ms, with no floor?
3. How many round trips does a 200 KB response take in pure slow start with an initial window of 14,600 bytes? How does this change on a warm connection whose window is already 1 MB?
4. Using the DNS block's `parse_response`, craft a response with a compression pointer pointing to itself. What should happen?

<details>
<summary>Answers</summary>

1. A peer can send a header claiming 4 GB. Rejecting it before you buffer means a short message can't make you allocate memory. `test_decoder_rejects_oversized_header_before_buffering` covers this.
2. First sample: `SRTT = 0.1`, `RTTVAR = 0.05`. Second: `RTTVAR = 0.75 × 0.05 + 0.25 × |0.1 - 0.3| = 0.0875`, `SRTT = 0.125`. So `RTO = 0.125 + 4 × 0.0875 = 0.475` seconds. Using the new `SRTT` for `RTTVAR` is the bug the test catches.
3. 14,600 × (2^r − 1) ≥ 200,000 gives `r = 4`. On the warm connection it's 1 round trip.
4. `read_name` should raise `ValueError("compression loop")`, thanks to its `seen` set. Without that set, a single short packet would hang the parser forever, so this is a real denial-of-service case.

</details>

## Interview checklist

| Question | Answer |
|---|---|
| Why does TCP need framing on top? | It's a byte stream. `recv` boundaries don't relate to `send` boundaries. |
| What's the three-way handshake, and what does it cost? | SYN, SYN-ACK, ACK. It synchronises sequence numbers, and costs 1 RTT before the first request byte. |
| What's TIME-WAIT? | The closer waits 2 × MSL so old segments can't reach a new connection using those ports. Too many of these exhaust ports. |
| How's the retransmission timeout set? | `SRTT + 4 × RTTVAR`, with a floor of 1 s in the RFC, doubling on each timeout. |
| What's the bandwidth-delay product? | Bytes in flight needed to fill the link: bandwidth × RTT. Throughput is capped at window / RTT. |
| What's slow start? | Starting at about 10 segments and doubling each RTT, so small responses take one RTT and large ones several. |
| Why AIMD? | Adding equally and halving proportionally shrinks the difference between flows, so they converge on a fair share. |
| Walk through DNS. | Stub to recursive resolver over UDP, with caching by TTL. Falls back to TCP when truncated. |
| How does HTTP/1.1 find the end of a message? | `Content-Length`, chunked coding, or connection close. |
| HTTP/2 versus HTTP/3? | HTTP/2 multiplexes on one TCP connection, so TCP loss stalls all streams. HTTP/3 uses QUIC, where loss only stalls one stream. |
| What does TLS 1.3 add to latency? | One RTT on a new connection. The CPU cost is small. |
| Why is 0-RTT limited? | First-flight data can be replayed, so use it only for idempotent requests. |
| Which methods are safe to retry? | Idempotent ones, such as GET, PUT and DELETE. POST needs an idempotency key. |

## Next

Next track: [Software design](../../software-design/README.md), which applies the same habit of measuring first to the structure of the code itself. For where this chapter's failures go at larger scale, read [when distributed systems fail](../../../data-engineering/01-storage-and-compute-foundations/notes/06-when-distributed-systems-fail.md).
