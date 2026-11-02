"""DataOps: the runnable code of notes/06-dataops.md

Run from any folder (it writes only to a temporary directory):
    uv run --with dbt-duckdb python data-engineering/05-quality-and-observability/practice/06_dataops.py

dbt and DuckDB run for real. Airflow, Terraform, a CRM and any cloud do not: the DAG
checks parse source text, the infrastructure section is a small model of what
Terraform does, and the CRM is a Python class.
"""
import os, tempfile
os.chdir(tempfile.mkdtemp())

# --- project ---
import contextlib, io, json, pathlib, shutil, duckdb
from dbt.cli.main import dbtRunner

def write(path, text):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

write("dbt_project.yml", """
name: shop
version: "1.0"
profile: shop
models:
  shop:
    +materialized: table
    stg_orders: {+materialized: view}
""")
# One warehouse file, one schema per environment. Nothing in the models names a schema.
write("profiles.yml", """
shop:
  target: dev
  outputs:
    prod: {type: duckdb, path: wh.duckdb, schema: prod, threads: 2}
    ci:   {type: duckdb, path: wh.duckdb, schema: "{{ env_var('CI_SCHEMA') }}", threads: 2}
""")
write("seeds/raw_orders.csv", "order_id,customer_id,status,amount,ordered_on\n" + "".join(
    f"{i},{i % 40},{'refunded' if i % 10 == 0 else 'paid'},{10 + i % 90},2026-10-{1 + i % 28:02d}\n"
    for i in range(1, 2001)))
write("seeds/raw_products.csv", "product_id,name\n1,Kettle\n2,Toaster\n")
write("models/stg_orders.sql", "select order_id, customer_id, status, amount, ordered_on from {{ ref('raw_orders') }}")
write("models/daily_revenue.sql", """
select ordered_on, sum(amount) as revenue
from {{ ref('stg_orders') }}
group by ordered_on
""")
write("models/customer_value.sql", """
select customer_id, sum(amount) as lifetime_value
from {{ ref('stg_orders') }}
group by customer_id
""")
write("models/revenue_by_month.sql", """
select date_trunc('month', ordered_on) as month, sum(revenue) as revenue
from {{ ref('daily_revenue') }}
group by 1
""")
write("models/dim_products.sql", "select product_id, name from {{ ref('raw_products') }}")
write("models/schema.yml", """
models:
  - name: daily_revenue
    description: Revenue per day
    meta: {owner: finance-data}
    columns:
      - name: ordered_on
        data_tests: [unique, not_null]
  - name: customer_value
    description: Lifetime spend per customer
    meta: {owner: growth-data}
    columns:
      - name: customer_id
        data_tests: [unique, not_null]
  - name: revenue_by_month
    meta: {owner: finance-data}
  - name: dim_products
exposures:
  - name: weekly_revenue_dashboard
    type: dashboard
    url: https://bi.example.com/dashboards/1
    depends_on: [ref('revenue_by_month')]
    owner: {name: Finance data, email: finance-data@example.com}
""")

QUIET = ["--project-dir", ".", "--profiles-dir", ".", "--log-level", "none", "--no-use-colors"]

def dbt(*args, target="prod"):
    """Run dbt in this process. Return whether it succeeded, printing one line per node."""
    res = dbtRunner().invoke([*args, "--target", target, *QUIET])
    if res.exception:
        raise res.exception
    for r in res.result.results:
        print(f"  {r.status!s:9}{r.node.resource_type!s:10}{r.node.name}")
    return res

def ls(*args):
    """Names of the nodes dbt selects, in order."""
    with contextlib.redirect_stdout(io.StringIO()):
        res = dbtRunner().invoke(["ls", *args, "--output", "name", "--target", "prod", *QUIET])
    if res.exception:
        raise res.exception
    return sorted(str(n).split(".")[-1] for n in res.result)

def sql(query):
    with duckdb.connect("wh.duckdb") as con:
        return con.execute(query).fetchall()

def tables_in(schema):
    return sorted(r[0] for r in sql(f"select table_name from information_schema.tables where table_schema = '{schema}'"))

print("project written; models:", sorted(p.stem for p in pathlib.Path("models").glob("*.sql")))

# --- prod ---
os.environ["CI_SCHEMA"] = "pr_42"
dbt("build")                               # a deploy from main
shutil.copytree("target", "prod-artifacts")  # the manifest of what prod is now
print("prod has:", tables_in("prod"))

# --- state ---
# The pull request: daily revenue should not count refunded orders.
write("models/daily_revenue.sql", """
select ordered_on, sum(amount) as revenue
from {{ ref('stg_orders') }}
where status <> 'refunded'
group by ordered_on
""")
print("all resources:", len(ls()))
print("state:modified:", ls("--select", "state:modified", "--state", "prod-artifacts"))
print("state:modified+:", ls("--select", "state:modified+", "--state", "prod-artifacts"))

# --- slim_ci ---
ok = dbt("build", "--select", "state:modified+", "--defer", "--state", "prod-artifacts", target="ci")
print("green:", ok.success)
print("pr_42 has:", tables_in("pr_42"))
compiled = pathlib.Path("target/run/shop/models/daily_revenue.sql").read_text()
print("reads from:", [l.strip() for l in compiled.splitlines() if "stg_orders" in l])
print("prod total:", sql("select sum(revenue) from prod.daily_revenue")[0][0],
      " pr total:", sql("select sum(revenue) from pr_42.daily_revenue")[0][0])
sql("drop schema pr_42 cascade")           # the PR closed
print("after close:", tables_in("pr_42"))

# --- broken_pr ---
# A second PR groups by one column too many, so a day now has two rows. The test should stop it.
write("models/daily_revenue.sql", """
select ordered_on, status, sum(amount) as revenue
from {{ ref('stg_orders') }}
group by ordered_on, status
""")
ok = dbt("build", "--select", "state:modified+", "--defer", "--state", "prod-artifacts", target="ci")
print("green:", ok.success, " exit code a CI runner would see:", 0 if ok.success else 1)
print("prod untouched:", sql("select count(*) from prod.daily_revenue")[0][0], "rows")
sql("drop schema pr_42 cascade")
write("models/daily_revenue.sql", """
select ordered_on, sum(amount) as revenue
from {{ ref('stg_orders') }}
where status <> 'refunded'
group by ordered_on
""")

# --- dag_checks ---
import ast, graphlib

GOOD_DAG = """
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
with DAG("nightly", schedule="@daily") as dag:
    extract = BashOperator(task_id="extract", bash_command="extract.sh")
    build = BashOperator(task_id="build", bash_command="dbt build")
    extract >> build
"""
BAD_DAG = """
import requests
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
tables = requests.get("https://internal/tables").json()
with DAG("nightly", schedule="@daily") as dag:
    a = BashOperator(task_id="a", bash_command="a.sh")
    b = BashOperator(task_id="b", bash_command="b.sh")
    a >> b >> a
"""

def edges(node):
    """Pairs from `a >> b >> c`, read from the syntax tree."""
    found = []
    for n in ast.walk(node):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.RShift) and isinstance(n.right, ast.Name):
            left = n.left.right if isinstance(n.left, ast.BinOp) else n.left
            found.append((left.id, n.right.id))
    return found

def check_dag(source):
    """Problems a pull request can find without Airflow installed or a scheduler running."""
    tree, problems = ast.parse(source), []
    for stmt in tree.body:
        if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.With, ast.FunctionDef)):
            continue
        calls = [c for c in ast.walk(stmt) if isinstance(c, ast.Call)]
        if calls:
            problems.append(f"line {stmt.lineno}: work at the top level runs on every parse")
    graph = {}
    for a, b in edges(tree):
        graph.setdefault(b, set()).add(a)
    try:
        list(graphlib.TopologicalSorter(graph).static_order())
    except graphlib.CycleError as e:
        problems.append(f"cycle: {' -> '.join(e.args[1])}")
    return problems

print("good dag:", check_dag(GOOD_DAG))
for p in check_dag(BAD_DAG):
    print("bad dag: ", p)

# --- secrets ---
import re

PATTERNS = {
    "aws access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "password value": re.compile(r"""(?i)\b(password|passwd|token|secret)\b\s*[:=]\s*["']?(?!\{\{)[^\s"'{]{4,}"""),
}

def scan(files):
    return [(path, n, name) for path, text in files.items()
            for n, line in enumerate(text.splitlines(), 1)
            for name, rx in PATTERNS.items() if rx.search(line)]

fake_key = "AKIA" + "IOSFODNN7EXAMPLE"     # AWS's documented example key, split so scanners ignore this file
repo = {
    "profiles.yml": "password: {{ env_var('DBT_PASSWORD') }}\nuser: {{ env_var('DBT_USER') }}\n",
    "old_profiles.yml": "user: analytics\npassword: hunter2hunter2\n",
    "scripts/load.py": f'client = boto3.client("s3", aws_access_key_id="{fake_key}")\n',
    "dags/nightly.py": 'schedule = "@daily"\n',
}
for hit in scan(repo):
    print("found:", hit)
print("clean files:", sorted(set(repo) - {h[0] for h in scan(repo)}))

# --- iac ---
def plan(desired, state, cloud):
    """A model of `terraform plan`: refresh what exists, then diff it against the config."""
    refreshed = {k: dict(cloud[k]) for k in state if k in cloud}
    drifted = sorted(k for k in refreshed if refreshed[k] != state[k])
    changes = []
    for k in sorted(desired.keys() | refreshed.keys()):
        if k not in refreshed:
            changes.append(("create", k, desired[k]))
        elif k not in desired:
            changes.append(("destroy", k, refreshed[k]))
        elif desired[k] != refreshed[k]:
            immutable = desired[k].get("region") != refreshed[k].get("region")
            changes.append(("REPLACE" if immutable else "update", k, desired[k]))
    return drifted, changes

def apply(changes, state, cloud):
    for action, k, spec in changes:
        if action == "destroy":
            cloud.pop(k), state.pop(k)
        else:
            cloud[k] = dict(spec)
            state[k] = dict(spec)

def show(title, result):
    drifted, changes = result
    print(f"{title}: drift={drifted}", [f"{a} {k}" for a, k, _ in changes] or "no changes")

desired = {"bucket.raw": {"region": "eu-west-1", "versioning": True},
           "warehouse.etl": {"size": "S", "auto_suspend": 60}}
state, cloud = {}, {}
show("first plan", plan(desired, state, cloud))
apply(plan(desired, state, cloud)[1], state, cloud)
show("second plan", plan(desired, state, cloud))

cloud["warehouse.etl"]["size"] = "XL"      # someone resized it in the console during an incident
show("after console edit", plan(desired, state, cloud))
apply(plan(desired, state, cloud)[1], state, cloud)
print("size after apply:", cloud["warehouse.etl"]["size"])

desired["bucket.raw"]["region"] = "us-east-1"  # looks like a one-word edit
show("after region edit", plan(desired, state, cloud))
desired["bucket.raw"]["region"] = "eu-west-1"

# --- blue_green ---
import time

with duckdb.connect("wh.duckdb") as con:
    con.execute("create schema serving")
    con.execute("create schema build_1")
    con.execute("create table build_1.daily_revenue as select * from prod.daily_revenue")
    con.execute("create view serving.daily_revenue as select * from build_1.daily_revenue")
    read = lambda: con.execute("select round(sum(revenue)) from serving.daily_revenue").fetchone()[0]
    print("live, build_1:", read())

    con.execute("create schema build_2")   # blue stays live while green builds
    con.execute("""create table build_2.daily_revenue as
                   select ordered_on, revenue * 0.9 as revenue from build_1.daily_revenue""")
    audit = con.execute("""select count(*), count(*) filter (where revenue < 0)
                           from build_2.daily_revenue""").fetchone()
    print("audit build_2 (rows, negative):", audit)

    t = time.perf_counter()
    con.execute("create or replace view serving.daily_revenue as select * from build_2.daily_revenue")
    print(f"live, build_2: {read()}  (swap took {(time.perf_counter() - t) * 1000:.1f} ms)")

    t = time.perf_counter()
    con.execute("create or replace view serving.daily_revenue as select * from build_1.daily_revenue")
    print(f"rolled back: {read()}  (took {(time.perf_counter() - t) * 1000:.1f} ms)")

# --- slo ---
import random

def simulate(seed=7, days=28, slo_minutes=30):
    """An hourly batch for four weeks: delays, task failures that retries absorb, one real outage."""
    rng = random.Random(seed)
    runs = []
    for hour in range(days * 24):
        delay = rng.lognormvariate(2.5, 0.35)        # typically about 12 minutes
        task_failures = 0
        while rng.random() < 0.04:                   # a transient failure, then a retry
            task_failures += 1
            delay += 5
        if 17 * 24 + 3 <= hour < 17 * 24 + 8:        # day 17: an upstream outage for five hours
            delay += 300
        runs.append({"hour": hour, "delay": delay, "failures": task_failures, "good": delay <= slo_minutes})
    return runs

runs = simulate()
target = 0.99
bad = [r for r in runs if not r["good"]]
budget = (1 - target) * len(runs)
print(f"batches: {len(runs)}  SLI: {1 - len(bad) / len(runs):.2%}  target: {target:.0%}")
print(f"budget: {budget:.2f} late batches  spent: {len(bad)}  ({len(bad) / budget:.0%})")
outage = [r for r in bad if 17 * 24 + 3 <= r["hour"] < 17 * 24 + 8]
print(f"of which the outage: {len(outage)}  scattered: {len(bad) - len(outage)}")

# --- paging ---
def cause_pages(runs):
    """Page on every task failure: the cause-based alert."""
    return [r["hour"] for r in runs if r["failures"]]

def symptom_pages(runs, window=6, late=2):
    """Page when 2 of the last 6 batches were late, and at most once per incident."""
    pages, in_incident = [], False
    for i in range(len(runs)):
        recent = runs[max(0, i - window + 1):i + 1]
        firing = sum(not r["good"] for r in recent) >= late
        if firing and not in_incident:
            pages.append(runs[i]["hour"])
        in_incident = firing
    return pages

a, b = cause_pages(runs), symptom_pages(runs)
hit = lambda pages: any(17 * 24 + 3 <= h < 17 * 24 + 8 for h in pages)
print(f"page on any task failure: {len(a)} pages, {len(a) / 28:.1f} a day")
print(f"page on the symptom:      {len(b)} pages, {len(b) / 28:.2f} a day")
print("symptom page at hour:", b, " outage began at hour:", 17 * 24 + 3)
print("each batch is", f"{1 / budget:.0%}", "of the budget")

# --- semantic ---
sql("""create or replace table prod.orders_fact as
       select order_id, customer_id, status, amount, ordered_on from prod.raw_orders""")
print("finance dashboard:", sql("select sum(amount) from prod.orders_fact where status = 'paid'")[0][0])
print("growth dashboard: ", sql("select sum(amount) from prod.orders_fact")[0][0])

METRICS = {"revenue": {"expr": "sum(amount)", "from": "prod.orders_fact",
                       "filter": "status = 'paid'", "owner": "finance-data"}}

def metric_sql(name, by=None):
    """Compile a metric to SQL: the idea underneath a semantic layer, in a few lines."""
    m = METRICS[name]
    dims = f"{by}, " if by else ""
    group = f" group by {by} order by {by}" if by else ""
    return f"select {dims}{m['expr']} as {name} from {m['from']} where {m['filter']}{group}"

print("both dashboards now:", sql(metric_sql("revenue"))[0][0])
print(metric_sql("revenue", by="customer_id"))
print("impact of revenue_by_month:", ls("--select", "revenue_by_month+"))
print("upstream of the dashboard:", ls("--select", "+exposure:weekly_revenue_dashboard"))

# --- catalog ---
manifest = json.loads(pathlib.Path("prod-artifacts/manifest.json").read_text())
models = [n for n in manifest["nodes"].values() if n["resource_type"] == "model"]
print(f"{'model':18}{'owner':14}{'documented':12}columns tested")
tests = [n for n in manifest["nodes"].values() if n["resource_type"] == "test"]
for m in sorted(models, key=lambda m: m["name"]):
    tested = sorted({t["column_name"] for t in tests if m["unique_id"] in t["depends_on"]["nodes"]})
    print(f"{m['name']:18}{m['config']['meta'].get('owner', '-'):14}{'yes' if m['description'] else 'NO':12}{tested}")
unowned = sorted(m["name"] for m in models if not m["config"]["meta"].get("owner"))
print("CI gate, models with no owner:", unowned)

# --- reverse_etl ---
import hashlib

class FakeCRM:
    """The destination: upserts by external id, counted, and it can fail partway."""
    def __init__(self):
        self.contacts, self.calls, self.fail_after = {}, 0, None
    def upsert(self, external_id, fields):
        if self.fail_after is not None and self.calls >= self.fail_after:
            raise ConnectionError("503 from CRM")
        self.calls += 1
        self.contacts[external_id] = fields

def fingerprint(fields):
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()

def sync(con, crm):
    """Send only what changed since the last successful send of each record."""
    rows = con.execute("select customer_id, tier, lifetime_value from audience").fetchall()
    done = dict(con.execute("select customer_id, fp from synced").fetchall())
    sent = 0
    for customer_id, tier, value in rows:
        fields = {"tier": tier, "ltv": float(value)}
        fp = fingerprint(fields)
        if done.get(customer_id) == fp:
            continue
        crm.upsert(customer_id, fields)    # the send first, the record of it second
        con.execute("insert or replace into synced values (?, ?)", [customer_id, fp])
        sent += 1
    return sent

con = duckdb.connect()
con.execute("""create table audience as
               select i as customer_id, case when i % 10 = 0 then 'gold' else 'std' end as tier,
                      (i % 500)::double as lifetime_value
               from range(1000) t(i)""")
con.execute("create table synced (customer_id bigint primary key, fp varchar)")
crm = FakeCRM()
print("first sync sent:", sync(con, crm))
print("no changes, sent:", sync(con, crm))

con.execute("update audience set tier = 'gold' where customer_id between 100 and 136 and tier <> 'gold'")
changed = con.execute("select count(*) from audience where tier = 'gold'").fetchone()[0] - 100
print("tier changes in the warehouse:", changed)
crm.fail_after = crm.calls + 10
try:
    sync(con, crm)
except ConnectionError as e:
    print("crash partway:", e, "after", crm.calls - 1000, "sends")
crm.fail_after = None
print("rerun sent:", sync(con, crm), " total calls:", crm.calls)
truth = dict(con.execute("select customer_id, tier from audience").fetchall())
print("CRM matches warehouse:", all(crm.contacts[k]["tier"] == v for k, v in truth.items()))

# --- tryit ---
# 1. A change to the model everything reads.
original = pathlib.Path("models/stg_orders.sql").read_text()
write("models/stg_orders.sql", original + " where amount > 0")
print("1. state:modified+:", ls("--select", "state:modified+", "--state", "prod-artifacts"))
write("models/stg_orders.sql", original)

# 2. Budget at a stricter target.
for t in (0.99, 0.999):
    print(f"2. target {t:.1%}: budget {(1 - t) * 672:.2f} late batches in four weeks")

# 3. Record the send before making it.
def sync_state_first(con, crm):
    rows = con.execute("select customer_id, tier, lifetime_value from audience").fetchall()
    done = dict(con.execute("select customer_id, fp from synced").fetchall())
    for customer_id, tier, value in rows:
        fields = {"tier": tier, "ltv": float(value)}
        fp = fingerprint(fields)
        if done.get(customer_id) == fp:
            continue
        con.execute("insert or replace into synced values (?, ?)", [customer_id, fp])
        crm.upsert(customer_id, fields)

con.execute("update audience set tier = 'silver' where customer_id < 20")
before = crm.calls
crm.fail_after = crm.calls + 5
try:
    sync_state_first(con, crm)
except ConnectionError:
    pass
crm.fail_after = None
sync_state_first(con, crm)
truth = dict(con.execute("select customer_id, tier from audience").fetchall())
wrong = sum(crm.contacts[k]["tier"] != v for k, v in truth.items())
print("3. rerun sends:", crm.calls - before - 5, " records wrong in the CRM for good:", wrong)

# 4. Lose the state file.
show("4. state lost", plan(desired, {}, cloud))
