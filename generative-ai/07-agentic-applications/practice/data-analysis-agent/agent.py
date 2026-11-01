"""A data-analysis agent: read-only SQL, charts, and a validator that recomputes each claim.

The tools are small on purpose. The agent sees schema and profiles first, queries through a
connection that cannot write, and can only end the task through submit_answer, which checks the
answer against an independent pandas computation before accepting it.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
MAX_ROWS = 25
MAX_CHART_BARS = 12
MAX_SQLITE_OPS = 2_000_000  # measured in thousands of VM steps by the progress handler below
SMALL_GROUP = 30


class ToolError(Exception):
    """A refused or failed call. The message tells the model what to do next."""


@dataclass(frozen=True)
class Metric:
    """A named definition a human signed off on. The agent may not swap in a similar number."""

    name: str
    table: str
    column: str
    per: str | None = None
    description: str = ""


def measure(frame: pd.DataFrame, column: str, per: str | None = None) -> pd.Series:
    return frame[column] / frame[per] if per else frame[column]


def bootstrap_difference(a: pd.Series, b: pd.Series, draws: int = 2000, seed: int = 7) -> tuple[float, float, float]:
    """Difference of means with a 95% percentile bootstrap interval."""
    rng = np.random.default_rng(seed)
    a_values, b_values = a.to_numpy(), b.to_numpy()
    differences = [
        rng.choice(a_values, a_values.size).mean() - rng.choice(b_values, b_values.size).mean()
        for _ in range(draws)
    ]
    low, high = np.percentile(differences, [2.5, 97.5])
    return float(a_values.mean() - b_values.mean()), float(low), float(high)


class Analyst:
    """Holds the data, the read-only connection, and everything the tools have shown the model."""

    def __init__(self, frames: dict[str, pd.DataFrame], metrics: list[Metric], out_dir: Path):
        self.frames = frames
        self.metrics = {metric.name: metric for metric in metrics}
        self.out_dir = out_dir
        self.evidence: set[float] = set()
        self.charts: list[str] = []
        self.answer: str | None = None

        self.conn = sqlite3.connect(":memory:")
        for name, frame in frames.items():
            frame.to_sql(name, self.conn, index=False)
        # Enforcement sits below the SQL text, so no clever query string can get round it.
        self.conn.set_authorizer(self._authorize)
        self._ticks = 0
        self.conn.set_progress_handler(self._tick, 1000)

    @staticmethod
    def _authorize(action, *_args) -> int:
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

    def _tick(self) -> int:
        self._ticks += 1
        return 1 if self._ticks * 1000 > MAX_SQLITE_OPS else 0

    def _note(self, text: str) -> str:
        """Remember every number the tools showed, so the validator can trace an answer's numbers."""
        self.evidence.update(float(x) for x in re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", text))
        return text

    def _query(self, query: str) -> pd.DataFrame:
        self._ticks = 0
        try:
            cursor = self.conn.execute(query)
            columns = [description[0] for description in cursor.description or []]
            return pd.DataFrame(cursor.fetchmany(MAX_ROWS + 1), columns=columns)
        except (sqlite3.Error, sqlite3.Warning) as err:
            raise ToolError(f"SQL refused: {err}. Only single SELECT statements over {sorted(self.frames)} run here.")

    # Tools --------------------------------------------------------------------------------

    def list_tables(self) -> str:
        tables = [f"{name}: {len(frame)} rows, columns {list(frame.columns)}" for name, frame in self.frames.items()]
        metrics = [f"{m.name} = {m.column}{'/' + m.per if m.per else ''} on {m.table}: {m.description}"
                   for m in self.metrics.values()]
        return self._note("Tables:\n  " + "\n  ".join(tables) + "\nMetrics:\n  " + "\n  ".join(metrics))

    def describe_table(self, table: str) -> str:
        if table not in self.frames:
            raise ToolError(f"No table {table!r}. Tables: {sorted(self.frames)}.")
        frame = self.frames[table]
        lines = [f"{table}: {len(frame)} rows"]
        for name in frame.columns:
            column = frame[name]
            span = (f"min {column.min():g}, max {column.max():g}" if pd.api.types.is_numeric_dtype(column)
                    else f"e.g. {list(column.dropna().unique()[:4])}")
            lines.append(f"  {name} ({column.dtype}): {column.isna().sum()} null, {column.nunique()} distinct, {span}")
        return self._note("\n".join(lines))

    def run_sql(self, query: str) -> str:
        rows = self._query(query)
        note = f"\n[only the first {MAX_ROWS} rows shown]" if len(rows) > MAX_ROWS else ""
        return self._note(rows.head(MAX_ROWS).round(4).to_csv(index=False).strip() + note)

    def compare_groups(self, metric: str, group_by: str, a: str, b: str) -> str:
        spec = self._metric(metric)
        frame = self.frames[spec.table].dropna(subset=[spec.column])
        values = measure(frame, spec.column, spec.per)
        diff, low, high = bootstrap_difference(values[frame[group_by] == a], values[frame[group_by] == b])
        return self._note(f"{a} minus {b} on {metric}: {diff:.4f}, 95% bootstrap interval [{low:.4f}, {high:.4f}]")

    def make_chart(self, query: str, title: str, highlight: str) -> str:
        rows = self._query(query)
        if rows.shape[1] != 2 or not pd.api.types.is_numeric_dtype(rows.iloc[:, 1]):
            raise ToolError("A chart query must return two columns: a label and a number.")
        if len(rows) > MAX_CHART_BARS:
            raise ToolError(f"More than {MAX_CHART_BARS} bars is not readable. Aggregate the query first.")
        rows = rows.sort_values(rows.columns[1])
        labels, values = rows.iloc[:, 0].astype(str), rows.iloc[:, 1]
        colors = ["#1E3A5F" if label == highlight else "#CBD5E1" for label in labels]
        fig, ax = plt.subplots(figsize=(6.4, 0.5 * len(rows) + 1.3), dpi=150)
        bars = ax.barh(labels, values, color=colors, height=0.62)
        ax.bar_label(bars, labels=[f"{v:.3g}" for v in values], padding=4, color="#334155", fontsize=9)
        ax.set_xlim(0, values.max() * 1.15)  # bars start at zero, or their lengths would lie
        ax.set_title(title, loc="left", fontsize=10.5, color="#0F172A")
        ax.spines[["top", "right", "bottom"]].set_visible(False)
        ax.tick_params(axis="x", bottom=False, labelbottom=False)
        ax.tick_params(axis="y", length=0, colors="#334155")
        fig.tight_layout()
        self.out_dir.mkdir(parents=True, exist_ok=True)
        path = self.out_dir / (re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] + ".png")
        fig.savefig(path)
        plt.close(fig)
        self.charts.append(str(path))
        self._note(rows.round(4).to_csv(index=False))
        return f"Saved {path.name}, {len(rows)} bars."

    def submit_answer(self, text: str, metric: str, group_by: str, group: str, value: float,
                      is_largest: bool = False) -> str:
        problems = validate(self, text, metric, group_by, group, value, is_largest)
        if problems:
            raise ToolError("Answer rejected:\n- " + "\n- ".join(problems))
        self.answer = text
        return "Accepted."

    def _metric(self, name: str) -> Metric:
        if name not in self.metrics:
            raise ToolError(f"No metric {name!r}. Agreed metrics: {sorted(self.metrics)}.")
        return self.metrics[name]


CAUSAL = re.compile(r"\b(because|caused?|causes|due to|leads? to|makes? (people|customers))\b", re.I)
HEDGE = re.compile(r"\b(not distinguishable|cannot tell|too close|inconclusive)\b", re.I)


def traced(number: str, percent: bool, evidence: set[float]) -> bool:
    """True if the number, at the precision written, rounds from something a tool returned."""
    decimals = len(number.split(".")[1]) if "." in number else 0
    value = float(number)
    tolerance = 0.5 * 10 ** -decimals + 1e-9
    return any(abs(seen - value) <= tolerance or (percent and abs(seen * 100 - value) <= tolerance)
               for seen in evidence)


def validate(session: Analyst, text: str, metric: str, group_by: str, group: str, value: float,
             is_largest: bool) -> list[str]:
    """Recompute the claim in pandas, on the source data, without touching the agent's SQL."""
    spec = session.metrics.get(metric)
    if spec is None:
        return [f"{metric!r} is not an agreed metric. Use one of {sorted(session.metrics)}."]
    frame = session.frames[spec.table]
    if group_by not in frame or group not in set(frame[group_by].astype(str)):
        return [f"{group_by}={group!r} does not exist in {spec.table}."]

    usable = frame.dropna(subset=[spec.column])
    keyed = usable.assign(_value=measure(usable, spec.column, spec.per), _group=usable[group_by].astype(str))
    table = keyed.groupby("_group")["_value"].agg(["mean", "size"]).sort_values("mean", ascending=False)
    session.evidence.update(float(x) for x in table["mean"])
    session.evidence.update(float(x) for x in table["size"])
    session.evidence.update([float(len(frame)), float(len(usable))])

    problems = []
    actual = table.loc[group, "mean"]
    if abs(actual - value) > max(0.005 * abs(actual), 5e-4):
        problems.append(f"Recomputed {metric} for {group} is {actual:.4f}, you claimed {value:.4f}.")
    if is_largest and table.index[0] != group:
        problems.append(f"{group} is not the largest: {table.index[0]} is ({table['mean'].iloc[0]:.4f}).")

    n = int(table.loc[group, "size"])
    if n < SMALL_GROUP and not re.search(rf"\b{n}\b", text):
        problems.append(f"{group} has only {n} rows. State that sample size in the answer.")

    if usable.shape[0] < frame.shape[0] and str(len(usable)) not in text:
        problems.append(f"{spec.column} is null in {len(frame) - len(usable)} of {len(frame)} rows. "
                        f"Say the answer covers {len(usable)} of {len(frame)}.")

    if is_largest and len(table) > 1:
        runner_up = table.index[1]
        _, low, high = bootstrap_difference(keyed.loc[keyed._group == group, "_value"],
                                            keyed.loc[keyed._group == runner_up, "_value"])
        if low <= 0 <= high and not HEDGE.search(text):
            problems.append(f"The gap to {runner_up} has a 95% interval of [{low:.4f}, {high:.4f}], which includes 0. "
                            "Say the two are not distinguishable.")

    for number, percent in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)(%?)", text):
        if not traced(number, bool(percent), session.evidence):
            problems.append(f"The number {number}{percent} did not come from any tool result.")

    if CAUSAL.search(text):
        problems.append("This data is observational. Describe the association, not a cause.")
    return problems


TOOLS = [
    {"name": "list_tables", "description": "List tables, their columns, and the agreed metric definitions.",
     "input_schema": {"type": "object", "additionalProperties": False, "properties": {}}},
    {"name": "describe_table", "description": "Profile a table: type, nulls, distinct values and range per column.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["table"],
                      "properties": {"table": {"type": "string"}}}},
    {"name": "run_sql", "description": f"Run one read-only SQLite SELECT. Returns at most {MAX_ROWS} rows as CSV.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["query"],
                      "properties": {"query": {"type": "string"}}}},
    {"name": "compare_groups", "description": "Difference between two groups on a metric, with a 95% bootstrap interval.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["metric", "group_by", "a", "b"],
                      "properties": {"metric": {"type": "string"}, "group_by": {"type": "string"},
                                     "a": {"type": "string"}, "b": {"type": "string"}}}},
    {"name": "make_chart", "description": "Bar chart from a SELECT returning label and number. Highlights one label.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["query", "title", "highlight"],
                      "properties": {"query": {"type": "string"}, "title": {"type": "string"},
                                     "highlight": {"type": "string"}}}},
    {"name": "submit_answer", "description": "End the task. The claim is recomputed; a mismatch is rejected with reasons.",
     "input_schema": {"type": "object", "additionalProperties": False,
                      "required": ["text", "metric", "group_by", "group", "value"],
                      "properties": {"text": {"type": "string"}, "metric": {"type": "string"},
                                     "group_by": {"type": "string"}, "group": {"type": "string"},
                                     "value": {"type": "number"}, "is_largest": {"type": "boolean"}}}},
]
TOOL_NAMES = {tool["name"] for tool in TOOLS}


@dataclass
class Result:
    status: str
    steps: int
    rejected: int = 0
    log: list[dict] = field(default_factory=list)


def run_agent(model, session: Analyst, question: str, max_steps: int = 14, trace=print) -> Result:
    messages = [{"role": "user", "content": question}]
    result = Result(status="step_limit", steps=0)
    for step in range(1, max_steps + 1):
        result.steps = step
        response = model.create(messages=messages, tools=TOOLS)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            result.status = f"stopped_without_answer:{response.stop_reason}"
            return result
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                if block.name not in TOOL_NAMES:
                    raise ToolError(f"There is no tool called {block.name}.")
                output, is_error = getattr(session, block.name)(**block.input), False
            except (ToolError, TypeError) as err:
                output, is_error = str(err), True
                result.rejected += 1
            trace(f"{step:>2}  {block.name}  {'REFUSED' if is_error else 'ok'}\n" +
                  "\n".join(f"      {line[:104]}" for line in output.splitlines()[:9]))
            result.log.append({"tool": block.name, "input": block.input, "is_error": is_error, "output": output})
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": tool_results})
        if session.answer is not None:
            result.status = "answered"
            return result
    return result
