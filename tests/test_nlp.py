import pytest
from nlp.processor import TextProcessor

processor = TextProcessor()


def test_stopword_removal():
    result = processor.process("the cat is sitting on a mat")
    assert "the" not in result
    assert "is" not in result
    assert "on" not in result
    assert "cat" in result
    assert "sit" in result or "sitting" in result


def test_phrase_map_how_are_you():
    result = processor.process("how are you")
    assert result == ["you", "how"]


def test_phrase_map_love():
    result = processor.process("i love you")
    assert result == ["love", "you"]


def test_asl_wh_reorder():
    result = processor.process("where bathroom")
    assert result[-1] == "where"


def test_empty_input():
    assert processor.process("") == []


def test_none_like_input():
    assert processor.process("   ") == []


def test_filler_words():
    result = processor.process("um uh like okay")
    assert result == []


def test_lemmatization():
    result = processor.process("running cats eating")
    assert "run" in result
    assert "cat" in result
    assert "eat" in result
