"""Usage report for LLM calls. Run monthly. Don't touch unless you have to."""
import json
import sys

# prices per 1k tokens (updated last week)
OUT = "report_out.txt"
seen = []
TOTAL = 0


def report(path, mode="full", show_cost=True, write=False, dedupe=True, by_tenant=False):
    global TOTAL
    d = {}
    lat = []
    n = 0
    f = open(path)
    for l in f:
        try:
            r = json.loads(l)
        except:
            continue
        # skip dupes
        if dedupe:
            if r["id"] in seen:
                continue
            seen.append(r["id"])
        if r.get("status") != "ok":
            continue
        m = r["model"]
        p = r["prompt_tokens"]
        c = r["completion_tokens"]
        h = r.get("cached_tokens", 0)
        if m == "atlas-large":
            x = (p - h + h * 0.1) / 1000 * 0.015 + c / 1000 * 0.075
        elif m == "atlas-medium":
            x = (p - h + h * 0.1) / 1000 * 0.003 + c / 1000 * 0.015
        elif m == "atlas-small" or m == "atlas-small-2":
            x = (p - h + h * 0.1) / 1000 * 0.0008 + c / 1000 * 0.004
        else:
            x = (p - h + h * 0.1) / 1000 * 0.001 + c / 1000 * 0.002
        if by_tenant:
            g = r.get("tenant", "unknown")
        else:
            g = m
        if g not in d:
            d[g] = [0, 0, 0, 0.0]
        d[g][0] = d[g][0] + 1
        d[g][1] = d[g][1] + p
        d[g][2] = d[g][2] + c
        d[g][3] = d[g][3] + x
        TOTAL = TOTAL + x
        lat.append(r["latency_ms"])
        n = n + 1
    f.close()
    lat.sort()
    if len(lat) > 0:
        p95 = lat[int(len(lat) * 0.95)]
    else:
        p95 = 0
    if mode == "full":
        if by_tenant:
            print("tenant           calls   prompt   compl     cost")
        else:
            print("model            calls   prompt   compl     cost")
        for k in sorted(d, key=lambda k: -d[k][3]):
            v = d[k]
            if show_cost:
                print("%-15s %6d %8d %7d %8.4f" % (k, v[0], v[1], v[2], v[3]))
            else:
                print("%-15s %6d %8d %7d" % (k, v[0], v[1], v[2]))
        print("calls: %d" % n)
        print("p95 latency: %d ms" % p95)
        if show_cost:
            print("total: %.4f" % TOTAL)
    elif mode == "summary":
        if show_cost:
            print("calls: %d total: %.4f" % (n, TOTAL))
        else:
            print("calls: %d" % n)
    else:
        print("bad mode", file=sys.stderr)
        return None
    if write:
        o = open(OUT, "w")
        if mode == "full":
            if by_tenant:
                o.write("tenant           calls   prompt   compl     cost\n")
            else:
                o.write("model            calls   prompt   compl     cost\n")
            for k in sorted(d, key=lambda k: -d[k][3]):
                v = d[k]
                if show_cost:
                    o.write("%-15s %6d %8d %7d %8.4f\n" % (k, v[0], v[1], v[2], v[3]))
                else:
                    o.write("%-15s %6d %8d %7d\n" % (k, v[0], v[1], v[2]))
            o.write("calls: %d\n" % n)
            o.write("p95 latency: %d ms\n" % p95)
            if show_cost:
                o.write("total: %.4f\n" % TOTAL)
        else:
            if show_cost:
                o.write("calls: %d total: %.4f\n" % (n, TOTAL))
            else:
                o.write("calls: %d\n" % n)
        o.close()
    return round(TOTAL, 4)
