import pytest

from backend.text_processing.text_cleaner import clean_text


def test_clean_text_normalizes_whitespace():
    raw = "Hello    world\t\tthis   is   spaced"
    result = clean_text(raw)

    assert result == "Hello world this is spaced"


def test_clean_text_collapses_excess_blank_lines():
    raw = "Paragraph one.\n\n\n\n\nParagraph two."
    result = clean_text(raw)

    assert result == "Paragraph one.\n\nParagraph two."


def test_clean_text_removes_trailing_line_spaces():
    raw = "Line one   \nLine two\t\nLine three"
    result = clean_text(raw)

    assert "Line one   \n" not in result
    assert "Line two\t\n" not in result
    assert result == "Line one\nLine two\nLine three"


def test_clean_text_removes_divider_artifacts():
    raw = "Chapter 1\n------------\nSome content here.\n............\nMore content."
    result = clean_text(raw, remove_artifacts=True)

    assert "------------" not in result
    assert "............" not in result
    assert "Chapter 1" in result
    assert "Some content here." in result
    assert "More content." in result


def test_clean_text_keeps_artifacts_when_disabled():
    raw = "Section A\n------------\nContent."
    result = clean_text(raw, remove_artifacts=False)

    assert "------------" in result


def test_clean_text_does_not_touch_code_or_math():
    raw = "y = x - 1\nresult = a---b  # not a divider line"
    result = clean_text(raw)

    assert "y = x - 1" in result
    assert "result = a---b" in result


def test_clean_text_empty_string_returns_empty():
    assert clean_text("") == ""
    assert clean_text("   \n\n   ") == ""


def test_clean_text_non_string_raises_value_error():
    with pytest.raises(ValueError):
        clean_text(None)

    with pytest.raises(ValueError):
        clean_text(12345)


def test_clean_text_preserves_headings_and_lists():
    raw = "Introduction\n\n1. First point\n2. Second point\n\nConclusion"
    result = clean_text(raw)

    assert "Introduction" in result
    assert "1. First point" in result
    assert "2. Second point" in result
    assert "Conclusion" in result