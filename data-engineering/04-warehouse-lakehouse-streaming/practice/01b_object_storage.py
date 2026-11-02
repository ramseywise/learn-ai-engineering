"""Code from notes/01b-object-storage-and-the-data-lake.md, run against moto's S3 server.

Moto emulates the S3 API locally. Request counts and bytes come from real HTTP requests
made by boto3 and DuckDB, but latency, durability and scaling are not S3's.

Run from any folder (it writes only to a temporary directory):
    uv run --no-project --python 3.12 --with 'moto[server,s3]' --with boto3 --with duckdb \
        --with pyarrow --with numpy python 01b_object_storage.py
"""
import io, logging, os, tempfile, threading, time
os.chdir(tempfile.mkdtemp())
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# --- server ---
import boto3, duckdb, numpy as np, pyarrow as pa, pyarrow.compute as pc, pyarrow.parquet as pq
from botocore.exceptions import ClientError
from moto.server import DomainDispatcherApplication, create_backend_app
from werkzeug.serving import make_server

log = []                                                        # one (kind, bytes) per HTTP request

def counting(app):
    """WSGI wrapper: record the kind of every request and the bytes in every response."""
    def wrapped(environ, start_response):
        method, query = environ["REQUEST_METHOD"], environ.get("QUERY_STRING", "")
        kind = "LIST" if method == "GET" and "list-type" in query else method
        body = b"".join(app(environ, start_response))
        log.append((kind, len(body)))
        return [body]
    return wrapped

server = make_server("127.0.0.1", 0, counting(DomainDispatcherApplication(create_backend_app)))
threading.Thread(target=server.serve_forever, daemon=True).start()   # one request at a time
ENDPOINT = f"127.0.0.1:{server.server_port}"
s3 = boto3.client("s3", endpoint_url=f"http://{ENDPOINT}", region_name="us-east-1",
                  aws_access_key_id="test", aws_secret_access_key="test")
s3.create_bucket(Bucket="lake")

def requests_since_reset():
    """Summarise and clear the request log."""
    kinds = {}
    for kind, _ in log:
        kinds[kind] = kinds.get(kind, 0) + 1
    size = sum(b for _, b in log)
    log.clear()
    return kinds, size

# --- flat_keys ---
for key in ["trips/2024/06/a.parquet", "trips/2024/07/b.parquet", "zones.csv"]:
    s3.put_object(Bucket="lake", Key=key, Body=b"x")
print("every key   :", [o["Key"] for o in s3.list_objects_v2(Bucket="lake")["Contents"]])
top = s3.list_objects_v2(Bucket="lake", Delimiter="/")
print("delimiter / :", [p["Prefix"] for p in top["CommonPrefixes"]], [o["Key"] for o in top["Contents"]])
s3.put_object(Bucket="lake", Key="odd//name/./x", Body=b"x")     # a legal key, and not a path
print("odd key kept:", s3.head_object(Bucket="lake", Key="odd//name/./x")["ContentLength"], "byte")
print("no 'trips/' object:", "Contents" not in s3.list_objects_v2(Bucket="lake", Prefix="trips/", MaxKeys=0))

# --- rename ---
for i in range(2_500):
    s3.put_object(Bucket="lake", Key=f"old/part-{i:05d}", Body=b"x")
log.clear()
pages = s3.get_paginator("list_objects_v2").paginate(Bucket="lake", Prefix="old/")
keys = [o["Key"] for page in pages for o in page["Contents"]]
print(f"listed {len(keys):,} keys:", requests_since_reset()[0])
for key in keys:                                                 # there is no rename: copy, then delete
    s3.copy_object(Bucket="lake", Key=key.replace("old/", "new/"), CopySource={"Bucket": "lake", "Key": key})
    s3.delete_object(Bucket="lake", Key=key)
print("renamed the 'directory':", requests_since_reset()[0])

# --- conditional ---
def racers(n, work):
    threads = [threading.Thread(target=work, args=(i,)) for i in range(n)]
    [t.start() for t in threads]; [t.join() for t in threads]

outcomes = {}
def claim(i):
    try:
        s3.put_object(Bucket="lake", Key="_log/00000042.json", Body=f"writer {i}".encode(), IfNoneMatch="*")
        outcomes[i] = "won"
    except ClientError as e:
        outcomes[i] = e.response["ResponseMetadata"]["HTTPStatusCode"]
racers(8, claim)
print("eight writers claim one key:", sorted(outcomes.values(), key=str))
print("the object holds            :", s3.get_object(Bucket="lake", Key="_log/00000042.json")["Body"].read().decode())

def run_counter(key, safe):
    s3.put_object(Bucket="lake", Key=key, Body=b"0")
    retries = [0]
    def add(_):
        for _ in range(25):
            while True:
                got = s3.get_object(Bucket="lake", Key=key)
                value = int(got["Body"].read()) + 1
                extra = {"IfMatch": got["ETag"]} if safe else {}
                try:
                    s3.put_object(Bucket="lake", Key=key, Body=str(value).encode(), **extra)
                    break
                except ClientError:
                    retries[0] += 1
    racers(8, add)
    return int(s3.get_object(Bucket="lake", Key=key)["Body"].read()), retries[0]
print("8 writers, 25 increments each, 200 expected")
print("  blind read-modify-write: count %d, %d retries" % run_counter("count-blind", False))
print("  If-Match on the ETag   : count %d, %d retries" % run_counter("count-safe", True))

# --- many_keys ---
def parquet_bytes(table):
    buf = io.BytesIO(); pq.write_table(table, buf); return buf.getvalue()

duck = duckdb.connect()
duck.execute("INSTALL httpfs; LOAD httpfs")
duck.execute(f"""SET s3_endpoint='{ENDPOINT}'; SET s3_use_ssl=false; SET s3_url_style='path';
                 SET s3_access_key_id='test'; SET s3_secret_access_key='test'; SET s3_region='us-east-1';
                 SET enable_external_file_cache=false""")     # so each query shows its own requests

for part in range(4):                                            # the live table: 4 files, 1,000 rows each
    s3.put_object(Bucket="lake", Key=f"sales/part-{part}.parquet",
                  Body=parquet_bytes(pa.table({"amount": [1] * 1_000})))
total = lambda: duck.execute("SELECT sum(amount) FROM 's3://lake/sales/*.parquet'").fetchall()[0][0]
print("before the overwrite:", total())
new = [f"sales/new-{part}.parquet" for part in range(4)]
for key in new[:2]:                                              # a job rewrites the table, and dies halfway
    s3.put_object(Bucket="lake", Key=key, Body=parquet_bytes(pa.table({"amount": [1] * 1_000})))
print("job dies after 2 of 4 new files, reader sees:", total())
s3.delete_object(Bucket="lake", Key="sales/part-0.parquet")
s3.delete_object(Bucket="lake", Key="sales/part-1.parquet")
print("cleanup removes 2 old files, reader sees    :", total())

# --- multipart ---
upload = s3.create_multipart_upload(Bucket="lake", Key="big/huge.parquet")
s3.upload_part(Bucket="lake", Key="big/huge.parquet", UploadId=upload["UploadId"], PartNumber=1, Body=b"x" * 5_242_880)
print("objects under big/    :", s3.list_objects_v2(Bucket="lake", Prefix="big/")["KeyCount"])
pending = s3.list_multipart_uploads(Bucket="lake")["Uploads"]
print("incomplete uploads    :", [u["Key"] for u in pending], "still billed, invisible to the list above")
s3.abort_multipart_upload(Bucket="lake", Key="big/huge.parquet", UploadId=upload["UploadId"])
print("after abort           :", len(s3.list_multipart_uploads(Bucket="lake").get("Uploads", [])))

# --- small_files ---
rng = np.random.default_rng(7)
n = 1_000_000
day = rng.integers(0, 366, n)
trips = pa.table({"day": pa.array(day.astype("int32")),
                  "zone": pa.array(rng.integers(1, 266, n).astype("int32")),
                  "total": pa.array(np.round(4 + rng.exponential(19.0, n), 2)),
                  "note": pa.array(rng.integers(0, 2**62, n).astype(str))})

def load(prefix, files):
    """Split the table into equal files and upload them. Returns total bytes stored."""
    step, stored = n // files, 0
    for i in range(files):
        body = parquet_bytes(trips.slice(i * step, step))
        s3.put_object(Bucket="lake", Key=f"{prefix}/part-{i:05d}.parquet", Body=body)
        stored += len(body)
    return stored

def measure(sql):
    log.clear()
    t = time.perf_counter()
    answer = duck.execute(sql).fetchall()[0][0]
    took = time.perf_counter() - t
    kinds, size = requests_since_reset()
    return answer, kinds, size, took

GET = 0.0004 / 1000                                               # S3 Standard, GET and other reads, per request
print(f"{'files':>6} {'stored MB':>9} {'LIST':>5} {'HEAD':>5} {'GET':>6} {'MB read':>8} {'query s':>8} {'answer':>12}")
for files in [1, 10, 100, 1_000]:
    stored = load(f"t{files}", files)
    answer, kinds, size, took = measure(f"SELECT sum(total) FROM 's3://lake/t{files}/*.parquet'")
    print(f"{files:>6,} {stored / 1e6:>9.1f} {kinds.get('LIST', 0):>5} {kinds.get('HEAD', 0):>5} {kinds.get('GET', 0):>6,} "
          f"{size / 1e6:>8.1f} {took:>8.2f} {answer:>12,.0f}")

# --- pruning ---
for month in range(12):                                           # one prefix per month, hive style
    rows = trips.filter(pc.equal(pa.array((day // 31).astype("int32")), month))
    s3.put_object(Bucket="lake", Key=f"hive/month={month:02d}/data.parquet", Body=parquet_bytes(rows))
for label, sql in [
    ("every month, all columns", "SELECT count(note) + sum(total) + sum(zone) FROM 's3://lake/hive/*/*.parquet'"),
    ("every month, one column ", "SELECT sum(total) FROM 's3://lake/hive/*/*.parquet'"),
    ("one month,   one column ", "SELECT sum(total) FROM read_parquet('s3://lake/hive/*/*.parquet', hive_partitioning=true) WHERE month = 5"),
]:
    _, kinds, size, took = measure(sql)
    print(f"{label}: {kinds.get('LIST', 0)} LIST, {kinds.get('GET', 0):>3} GET, {size / 1e6:6.1f} MB read")

# --- request_cost ---
PUT_LIST = 0.005 / 1000                                           # S3 Standard, PUT, COPY, POST and LIST, per request
def monthly_ops(files, gets_per_file, runs_per_day):
    """Request cost of one recurring scan, for 30 days of runs."""
    runs = runs_per_day * 30
    return runs * (files * gets_per_file * GET + (files // 1000 + 1) * PUT_LIST)
for files in [10, 1_000, 100_000]:
    print(f"{files:>8,} files, 2 GETs each, 96 runs a day: ${monthly_ops(files, 2, 96):>8,.2f} a month in requests")
print(f"rewrite 100,000 small files as 100 big ones  : ${100_000 * 2 * GET + 100 * PUT_LIST:>8,.2f} once (deletes are free)")
print(f"scan 100,000 files at 5,500 GET/s, 2 GETs each: {100_000 * 2 / 5_500:.0f} s on one prefix")

# --- tiers ---
PRICE = {"Standard": .023, "Standard-IA": .0125, "Glacier IR": .004}     # USD per GB-month, first tier, us-east-1
RETRIEVAL = {"Standard": 0, "Standard-IA": .01, "Glacier IR": .03}       # USD per GB read
TRANSITION = {"Standard-IA": .01 / 1000, "Glacier IR": .02 / 1000}       # USD per object moved by lifecycle rule
print("1,000 GB for a year, by reads a month (full scans), in USD")
print(f"{'':12s} " + " ".join(f"{r:>7d}x" for r in [0, 1, 2, 5]))
for tier in PRICE:
    costs = [12 * 1000 * (PRICE[tier] + r * RETRIEVAL[tier]) for r in [0, 1, 2, 5]]
    print(f"{tier:12s} " + " ".join(f"{c:>8,.0f}" for c in costs))
print("Moving 1,000 GB from Standard to Glacier IR: what the one-off transition costs")
for size_kb in [1_000_000, 10_000, 256]:
    objects = 1000 * 1e6 / size_kb
    fee = objects * TRANSITION["Glacier IR"]
    saved = 1000 * (PRICE["Standard"] - PRICE["Glacier IR"])
    print(f"  {size_kb:>9,} KB objects: {objects:>10,.0f} objects, ${fee:>8,.2f} fee, paid back in {fee / saved:5.1f} months")
print("A 10 KB object in Standard-IA is billed as 128 KB:", f"{128 / 10:.1f}x its size,",
      f"so it costs {128 / 10 * PRICE['Standard-IA'] / PRICE['Standard']:.1f}x what Standard charges for it")
duck.close()
server.shutdown()
