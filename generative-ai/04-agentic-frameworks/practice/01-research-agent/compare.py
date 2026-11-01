"""Note 06: measure what each framework costs on the same scripted agent.

The model is a stub, so these numbers measure framework overhead only: no network,
no inference. Run it with `--isolated` dependencies if you want clean package counts.
"""
import asyncio
import statistics
import subprocess
import sys
import time
from pathlib import Path

from research_lab import QUESTION

RUNS = 200
HERE = Path(__file__).parent
COLD_START = {
    "no framework": "import agent_scratch as a; a.query(a.search.__doc__[:20], verbose=False)",
    "langgraph": "import agent_langgraph as a; a.build_agent().invoke({'messages': [('user', 'loops')]})",
    "google-adk": "import asyncio, agent_adk as a; asyncio.run(a.ask(a.build_agent(), 'loops'))",
}


def cold_start_seconds(statement: str, repeats: int = 3) -> float:
    """Median wall time of a fresh interpreter importing the agent and running it once."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        subprocess.run([sys.executable, "-c", statement], cwd=HERE, check=True, capture_output=True)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def per_run_ms(call, runs: int = RUNS) -> float:
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        call()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples) * 1000


def code_lines(path: str) -> int:
    """Non-blank, non-comment lines in one agent file."""
    lines = (HERE / path).read_text().splitlines()
    return sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))


def main() -> None:
    import agent_adk
    import agent_langgraph
    import agent_scratch

    graph = agent_langgraph.build_agent()
    adk = agent_adk.build_agent()
    calls = {
        "no framework": lambda: agent_scratch.query(QUESTION, verbose=False),
        "langgraph": lambda: graph.invoke({"messages": [("user", QUESTION)]}),
        "google-adk": lambda: asyncio.run(agent_adk.ask(adk, QUESTION)),
    }
    files = {"no framework": "agent_scratch.py", "langgraph": "agent_langgraph.py", "google-adk": "agent_adk.py"}
    print(f"{'':14}{'cold s':>10}{'ms/run':>10}{'lines':>8}")
    for name, call in calls.items():
        print(f"{name:14}{cold_start_seconds(COLD_START[name]):>10.2f}{per_run_ms(call):>10.2f}{code_lines(files[name]):>8}")


if __name__ == "__main__":
    main()
