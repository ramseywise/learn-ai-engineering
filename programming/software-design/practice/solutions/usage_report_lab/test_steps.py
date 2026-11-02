"""Every step runs the same tests. Only step 3 is allowed to change what they expect."""
import json
import pathlib

import pytest

from harness import CALLS, HERE, grid, load, observe

REFACTORS = ["step0_original", "step1_split_phases", "step2_types_and_table"]
FIXED = ["step3_fix_pinned_bugs", "step4_add_feature"]
ALL = REFACTORS + FIXED
ROW = {"id": "r1", "model": "atlas-small", "prompt_tokens": 1000, "completion_tokens": 0, "status": "ok", "latency_ms": 100}

GOLDEN = json.loads((HERE / "golden.json").read_text())
GOLDEN_FIXED = json.loads((HERE / "golden_fixed.json").read_text())
FLAGS = list(grid())


def key(flags):
    return json.dumps(flags, sort_keys=True)


def write_log(tmp_path: pathlib.Path, *rows) -> pathlib.Path:
    path = tmp_path / "calls.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


def without_cached_tokens(tmp_path):
    """Step 4 bills cached tokens. Remove them and it must equal step 3."""
    path = tmp_path / "plain.jsonl"
    lines = []
    for line in CALLS.read_text().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            lines.append(line)
            continue
        row.pop("cached_tokens", None)
        lines.append(json.dumps(row))
    path.write_text("\n".join(lines) + "\n")
    return path


@pytest.mark.parametrize("step", REFACTORS)
@pytest.mark.parametrize("flags", FLAGS, ids=key)
def test_refactors_match_original_golden(step, flags):
    assert observe(step, **flags) == GOLDEN[key(flags)]


@pytest.mark.parametrize("flags", FLAGS, ids=key)
def test_step3_matches_reviewed_golden(flags):
    assert observe("step3_fix_pinned_bugs", **flags) == GOLDEN_FIXED[key(flags)]


@pytest.mark.parametrize("flags", FLAGS, ids=key)
def test_step4_matches_step3_when_nothing_is_cached(flags, tmp_path):
    assert observe("step4_add_feature", path=without_cached_tokens(tmp_path), **flags) == GOLDEN_FIXED[key(flags)]


@pytest.mark.parametrize("step", REFACTORS)
def test_pinned_bugs_still_there_in_refactors(step, tmp_path, capsys):
    module = load(step)
    path = write_log(tmp_path, ROW)
    first = module.report(str(path))
    capsys.readouterr()
    module.report(str(path))
    assert "calls: 0" in capsys.readouterr().out
    assert module.report(str(write_log(tmp_path, {**ROW, "id": "r2"}))) == pytest.approx(2 * first)

    module = load(step)
    module.report(str(write_log(tmp_path, {**ROW, "status": "error"}, ROW)))
    assert "calls: 0" in capsys.readouterr().out


@pytest.mark.parametrize("step", FIXED)
def test_pinned_bugs_gone_after_step3(step, tmp_path, capsys):
    module = load(step)
    path = write_log(tmp_path, ROW)
    first = module.report(str(path))
    capsys.readouterr()
    assert module.report(str(path)) == first
    assert "calls: 1" in capsys.readouterr().out

    module.report(str(write_log(tmp_path, {**ROW, "status": "error"}, ROW)))
    assert "calls: 1" in capsys.readouterr().out


@pytest.mark.parametrize("step", ALL)
def test_kept_behaviours(step, tmp_path, capsys):
    path = write_log(tmp_path, {**ROW, "model": "mystery"})
    assert load(step).report(str(path)) == pytest.approx(0.001)
    capsys.readouterr()
    assert load(step).report(str(path), mode="nope") is None
    assert "bad mode" in capsys.readouterr().err
    path.write_text(path.read_text() + '{"id": "cut off\n')
    load(step).report(str(path))
    assert "calls: 1" in capsys.readouterr().out


# Tests that only became possible once the logic was out of report().
def test_cached_tokens_cost_a_tenth():
    step4 = load("step4_add_feature")
    call = step4.Call("atlas-medium", 1000, 0, 100, "acme", cached_tokens=1000)
    assert step4.call_cost(call) == pytest.approx(0.0003)


def test_tenant_breakdown(tmp_path, capsys):
    step4 = load("step4_add_feature")
    path = write_log(tmp_path, {**ROW, "tenant": "acme"}, {**ROW, "id": "r2", "tenant": "globex"})
    step4.report(str(path), by_tenant=True)
    out = capsys.readouterr().out
    assert out.splitlines()[0].startswith("tenant")
    assert "acme" in out and "globex" in out


def test_p95_on_empty_and_short_lists():
    step4 = load("step4_add_feature")
    assert step4.p95([]) == 0
    assert step4.p95([7]) == 7


def test_feature_on_original_agrees_with_step4_when_no_bug_applies(tmp_path):
    """Keeps the diff comparison in the README honest: both versions do the same job."""
    rows = [json.loads(line) for line in CALLS.read_text().splitlines() if line.endswith("}") and json.loads(line)["status"] == "ok"]
    unique = {row["id"]: row for row in rows}
    path = write_log(tmp_path, *unique.values())
    for flags in ({"by_tenant": False}, {"by_tenant": True}):
        assert observe("feature_on_original", path=path, **flags) == observe("step4_add_feature", path=path, **flags)
