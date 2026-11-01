"""Note 05: a real langsmith Client that keeps runs in memory instead of posting them."""
from langsmith import Client


class CaptureClient(Client):
    """The SDK builds real run payloads; only the two network calls are replaced."""

    def __init__(self):
        super().__init__(api_key="offline", api_url="http://localhost:1", auto_batch_tracing=False)
        self.captured: dict[str, dict] = {}

    def create_run(self, name, inputs, run_type, **kwargs):
        run_id = str(kwargs.get("id"))
        self.captured[run_id] = {"name": name, "run_type": run_type, "inputs": inputs, **kwargs}

    def update_run(self, run_id, **kwargs):
        self.captured.setdefault(str(run_id), {}).update(kwargs)


def print_tree(client: CaptureClient) -> None:
    """Print the captured runs as an indented tree, in the order they started."""
    runs = sorted(client.captured.values(), key=lambda r: r["dotted_order"])
    for run in runs:
        depth = run["dotted_order"].count(".")
        print(f"{'  ' * depth}{run['name']} [{run['run_type']}]")
