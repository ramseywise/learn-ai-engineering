"""Code from notes/04-data-contracts.md. The validate_contract step fetches the ODCS JSON Schema, so it needs a network connection.

Run from any folder (it writes only to a temporary directory):
    uv run --with duckdb --with pyarrow --with numpy --with pyyaml --with jsonschema python 04_data_contracts.py
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- contract ---
ODCS_URL = "https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/schema/odcs-json-schema-latest.json"
import yaml, json, urllib.request, jsonschema, duckdb, numpy as np, pyarrow as pa

CONTRACT = """
apiVersion: v3.1.0
kind: DataContract
id: 6a1f7ab2-0b3e-4c5e-9f50-3bb9d8a7e101
name: trips
version: 1.0.0
status: active
description:
  purpose: One row per completed taxi trip, for finance and pricing.
schema:
  - name: trips
    physicalName: raw_trips
    logicalType: object
    dataGranularityDescription: One row per completed trip
    properties:
      - {name: trip_id, logicalType: integer, physicalType: BIGINT, primaryKey: true, required: true, unique: true}
      - {name: pickup_at, logicalType: timestamp, physicalType: TIMESTAMP, required: true}
      - {name: zone_id, logicalType: integer, physicalType: INTEGER, required: true}
      - name: fare_usd
        logicalType: number
        physicalType: DOUBLE
        required: true
        description: Fare in US dollars, before tip.
        quality:
          - {type: sql, description: fares are dollars and plausible,
             query: "SELECT count(*) FROM raw_trips WHERE fare_usd < 0 OR fare_usd > 500",
             mustBe: 0}
          - {type: sql, description: median fare looks like dollars not cents,
             query: "SELECT median(fare_usd) FROM raw_trips",
             mustBeBetween: [5, 40]}
slaProperties:
  - {property: freshness, value: 2, unit: h, element: trips.pickup_at}
"""
contract = yaml.safe_load(CONTRACT)
print(contract["name"], contract["version"], [p["name"] for p in contract["schema"][0]["properties"]])
print("--- contract done")

# --- validate_contract ---
schema = json.load(urllib.request.urlopen(ODCS_URL))
errors = list(jsonschema.Draft201909Validator(schema).iter_errors(contract))
print("schema errors:", [e.message[:80] for e in errors])
print("--- validate_contract done")

# --- batches ---
def make_batch(n=20_000, seed=7, **change):
    rng = np.random.default_rng(seed)
    miles = rng.gamma(2.0, 1.6, n) + .1
    cols = {
        "trip_id": np.arange(1, n + 1),
        "pickup_at": pa.array((np.datetime64("2026-01-15T00:00:00") + rng.integers(0, 86400, n) * np.timedelta64(1, "s")).astype("datetime64[s]")),
        "zone_id": rng.integers(1, 261, n).astype("int32"),
        "fare_usd": np.round(3 + miles * 2.5, 2),
    }
    if change.get("cents"):       cols["fare_usd"] = np.round(cols["fare_usd"] * 100, 0)
    if change.get("rename"):      cols["fare_amount"] = cols.pop("fare_usd")
    if change.get("string_zone"): cols["zone_id"] = pa.array([str(z) for z in cols["zone_id"]])
    if change.get("nulls"):       cols["zone_id"] = pa.array(cols["zone_id"], mask=rng.random(n) < .03)
    if change.get("dupes"):       cols["trip_id"][:50] = 1
    return pa.table(cols)

TYPES = {"BIGINT": "int64", "TIMESTAMP": "timestamp[s]", "INTEGER": "int32", "DOUBLE": "double"}
print("--- batches done")

# --- check ---
def check(contract, batch):
    """Return every breach. Structure first, since a missing column makes later checks meaningless."""
    con = duckdb.connect()
    con.register("raw_trips", batch)
    breaches, props = [], contract["schema"][0]["properties"]
    for p in props:
        if p["name"] not in batch.schema.names:
            breaches.append(f"missing column {p['name']}")
        elif str(batch.schema.field(p["name"]).type) != TYPES[p["physicalType"]]:
            breaches.append(f"{p['name']} is {batch.schema.field(p['name']).type}, promised {TYPES[p['physicalType']]}")
    if breaches:
        return breaches
    for p in props:
        c = p["name"]
        if p.get("required") and (n := con.execute(f"SELECT count(*) FROM raw_trips WHERE {c} IS NULL").fetchall()[0][0]):
            breaches.append(f"{c}: {n} nulls")
        if p.get("unique") and (n := con.execute(f"SELECT count(*) - count(DISTINCT {c}) FROM raw_trips").fetchall()[0][0]):
            breaches.append(f"{c}: {n} duplicates")
        for q in p.get("quality", []):
            v = con.execute(q["query"]).fetchall()[0][0]
            ok = v == q["mustBe"] if "mustBe" in q else q["mustBeBetween"][0] <= v <= q["mustBeBetween"][1]
            if not ok:
                breaches.append(f"{c}: {q['description']} (got {v})")
    return breaches

cases = {"good": {}, "renamed": {"rename": 1}, "zone as string": {"string_zone": 1},
         "3% null zones": {"nulls": 1}, "duplicate ids": {"dupes": 1}, "cents": {"cents": 1}}
for name, change in cases.items():
    print(f"{name:15s}", check(contract, make_batch(**change)) or "ok")
print("--- check done")

# --- silent ---
for name, change in {"good": {}, "cents": {"cents": 1}}.items():
    b = make_batch(**change)
    print(name, "dbt-style schema test passes:", "fare_usd" in b.schema.names,
          "| mean fare", round(duckdb.sql("SELECT avg(fare_usd) FROM b").fetchall()[0][0], 2))
print("--- silent done")

# --- quarantine ---
def split(batch):
    """Row-level failures go aside with a reason. The good rows carry on."""
    con = duckdb.connect()
    con.register("b", batch)
    bad = con.sql("""SELECT *, CASE WHEN zone_id IS NULL THEN 'null zone' ELSE 'fare out of range' END AS reason
        FROM b WHERE zone_id IS NULL OR fare_usd NOT BETWEEN 0 AND 500""").to_arrow_table()
    good = con.sql("SELECT * FROM b WHERE zone_id IS NOT NULL AND fare_usd BETWEEN 0 AND 500").to_arrow_table()
    return good, bad

good, bad = split(make_batch(nulls=1))
print("good", good.num_rows, "quarantined", bad.num_rows, "share", round(bad.num_rows / 20000, 3))
THRESHOLD = 0.01
print("stop the load" if bad.num_rows / 20000 > THRESHOLD else "load good rows, alert the owner")
print("--- quarantine done")

# --- diff ---
import copy

def breaking_changes(old, new):
    """Compare two contract versions, as a producer's CI job would before merging."""
    props = lambda c: {p["name"]: p for p in c["schema"][0]["properties"]}
    o, n, out = props(old), props(new), []
    for name, p in o.items():
        if name not in n:
            out.append(f"BREAKING removed {name}")
        elif n[name]["physicalType"] != p["physicalType"]:
            out.append(f"BREAKING {name} type {p['physicalType']} -> {n[name]['physicalType']}")
        elif n[name].get("required") and not p.get("required"):
            out.append(f"BREAKING {name} now required")
    for name, p in n.items():
        if name not in o:
            out.append(("BREAKING" if p.get("required") else "safe") + f" added {name}")
    return out

v2 = copy.deepcopy(contract)
v2["schema"][0]["properties"][2]["physicalType"] = "VARCHAR"
v2["schema"][0]["properties"].append({"name": "tip_usd", "logicalType": "number", "physicalType": "DOUBLE"})
print(breaking_changes(contract, v2))
print("--- diff done")

# --- expand_contract ---
def add_field(c, name, **kw):
    c = copy.deepcopy(c)
    c["schema"][0]["properties"].append({"name": name, **kw})
    return c

v2 = add_field(contract, "fare_cents", logicalType="integer", physicalType="BIGINT")
print("step 1, add the new column:", breaking_changes(contract, v2))
v3 = copy.deepcopy(v2)
v3["schema"][0]["properties"] = [p for p in v3["schema"][0]["properties"] if p["name"] != "fare_usd"]
print("step 3, drop the old one:  ", breaking_changes(v2, v3))
print("--- expand_contract done")
