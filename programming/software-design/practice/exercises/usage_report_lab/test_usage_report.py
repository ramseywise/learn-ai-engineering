"""Characterization tests. They say what the code does, not what it should do."""
import importlib
import json
import pathlib

import pytest

from make_golden import HERE, grid, observe

GOLDEN = json.loads((HERE / "golden.json").read_text())


@pytest.mark.parametrize("flags", list(grid()), ids=lambda f: json.dumps(f, sort_keys=True))
def test_matches_golden_master(flags):
    assert observe("usage_report", HERE / "calls.jsonl", **flags) == GOLDEN[json.dumps(flags, sort_keys=True)]


def fresh():
    return importlib.reload(importlib.import_module("usage_report"))


def write_log(tmp_path: pathlib.Path, *rows) -> pathlib.Path:
    path = tmp_path / "calls.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


ROW = {"id": "r1", "model": "atlas-small", "prompt_tokens": 1000, "completion_tokens": 0, "status": "ok", "latency_ms": 100}


def test_PINNED_second_call_in_a_process_sees_nothing(tmp_path, capsys):
    """Suspected bug: `seen` is a module global, so the dedupe outlives the call."""
    module = fresh()
    path = write_log(tmp_path, ROW)
    module.report(str(path))
    capsys.readouterr()
    module.report(str(path))
    assert "calls: 0" in capsys.readouterr().out


def test_PINNED_totals_accumulate_between_calls(tmp_path):
    """Suspected bug: TOTAL is a module global too."""
    module = fresh()
    first = module.report(str(write_log(tmp_path, ROW)))
    second = module.report(str(write_log(tmp_path, {**ROW, "id": "r2"})))
    assert second == pytest.approx(2 * first)


def test_PINNED_failed_attempt_hides_its_successful_retry(tmp_path, capsys):
    """Suspected bug: the id is marked seen before status is checked."""
    module = fresh()
    module.report(str(write_log(tmp_path, {**ROW, "status": "error"}, ROW)))
    assert "calls: 0" in capsys.readouterr().out


def test_unknown_model_is_charged_a_default_price(tmp_path):
    """Maybe a bug, maybe policy. Ask the owner; the refactor keeps it either way."""
    module = fresh()
    assert module.report(str(write_log(tmp_path, {**ROW, "model": "mystery"}))) == pytest.approx(0.001)


def test_malformed_lines_are_skipped_silently(tmp_path, capsys):
    module = fresh()
    path = write_log(tmp_path, ROW)
    path.write_text(path.read_text() + '{"id": "cut off\n')
    module.report(str(path))
    assert "calls: 1" in capsys.readouterr().out


def test_bad_mode_prints_to_stderr_and_returns_none(tmp_path, capsys):
    module = fresh()
    assert module.report(str(write_log(tmp_path, ROW)), mode="nope") is None
    assert "bad mode" in capsys.readouterr().err
