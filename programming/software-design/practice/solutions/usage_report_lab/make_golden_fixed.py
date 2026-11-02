"""Record step 3's behaviour after reviewing how it differs from golden.json."""
import json

from harness import HERE, grid, observe

golden = {json.dumps(f, sort_keys=True): observe("step3_fix_pinned_bugs", **f) for f in grid()}
(HERE / "golden_fixed.json").write_text(json.dumps(golden, indent=1, sort_keys=True) + "\n")
print(f"recorded {len(golden)} cases")
