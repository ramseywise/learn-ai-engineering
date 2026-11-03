"""Structural checks on the Kubernetes manifests and CI workflow. Offline: nothing is deployed or run."""
import sys
from pathlib import Path

import yaml

here = Path(__file__).parent
docs = {d["kind"]: d for d in yaml.safe_load_all((here / "k8s/deployment.yaml").read_text())}
assert set(docs) == {"Deployment", "HorizontalPodAutoscaler", "PodDisruptionBudget"}, set(docs)

deployment = docs["Deployment"]["spec"]
pod = deployment["template"]["spec"]
container = pod["containers"][0]
checks = {
    "selector matches pod labels": deployment["selector"]["matchLabels"] == deployment["template"]["metadata"]["labels"],
    "budget selects the same pods": docs["PodDisruptionBudget"]["spec"]["selector"]["matchLabels"] == deployment["selector"]["matchLabels"],
    "autoscaler targets this deployment": docs["HorizontalPodAutoscaler"]["spec"]["scaleTargetRef"]["name"] == docs["Deployment"]["metadata"]["name"],
    "all three probes set": all(p in container for p in ("startupProbe", "livenessProbe", "readinessProbe")),
    "readiness and liveness differ": container["livenessProbe"]["httpGet"]["path"] != container["readinessProbe"]["httpGet"]["path"],
    "cpu and memory requests set": set(container["resources"]["requests"]) == {"cpu", "memory"},
    "memory limit set": "memory" in container["resources"]["limits"],
    "image pinned, not latest": not container["image"].endswith(":latest") and ":" in container["image"],
    "runs as non-root": pod["securityContext"]["runAsNonRoot"] is True,
    "read-only root filesystem": container["securityContext"]["readOnlyRootFilesystem"] is True,
    "capabilities dropped": container["securityContext"]["capabilities"]["drop"] == ["ALL"],
    "grace period exceeds drain": pod["terminationGracePeriodSeconds"] > int(container["env"][0]["value"]),
}
workflow = yaml.safe_load((here / "ci/ci.yml").read_text())
checks["workflow has jobs and needs order"] = workflow["jobs"]["image"]["needs"] == "test"
checks["workflow token is read-only"] = workflow["permissions"] == {"contents": "read"}

failed = [name for name, passed in checks.items() if not passed]
for name, passed in checks.items():
    print(f"  {'ok  ' if passed else 'FAIL'} {name}")
sys.exit(1 if failed else 0)
