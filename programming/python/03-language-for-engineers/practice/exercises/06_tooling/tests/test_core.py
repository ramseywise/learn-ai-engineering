import pytest

from textstats.core import main, reading_time, word_frequencies


def test_frequencies_ignore_case_and_punctuation():
    assert word_frequencies("The cat. the CAT, a dog!") == {"the": 2, "cat": 2, "a": 1, "dog": 1}


def test_frequencies_empty():
    assert word_frequencies("") == {}


@pytest.mark.parametrize(
    "words, wpm, expected",
    [(0, 200, 0), (1, 200, 1), (200, 200, 1), (201, 200, 2), (1000, 250, 4)],
)
def test_reading_time_rounds_up(words, wpm, expected):
    assert reading_time(" ".join(["w"] * words), wpm=wpm) == expected


def test_reading_time_rejects_bad_wpm():
    with pytest.raises(ValueError, match="wpm"):
        reading_time("hello", wpm=0)


def test_cli(tmp_path, capsys):
    f = tmp_path / "doc.txt"
    f.write_text("b a b", encoding="utf-8")
    assert main([str(f)]) == 0
    assert capsys.readouterr().out == "b 2\na 1\nreading time: 1 min\n"


def test_cli_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "nope.txt")]) == 1
    assert "not found" in capsys.readouterr().err
