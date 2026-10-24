import pytest

from backend.text_processing.chunker import chunk_text


def test_chunk_text_basic_splitting():
    # 10 words, chunk_size=5, overlap=2 -> step=3
    text = "w0 w1 w2 w3 w4 w5 w6 w7 w8 w9"
    result = chunk_text(text, chunk_size=5, chunk_overlap=2)

    assert result[0]["text"] == "w0 w1 w2 w3 w4"
    assert result[1]["text"] == "w3 w4 w5 w6 w7"
    assert result[2]["text"] == "w6 w7 w8 w9"


def test_chunk_text_indices_are_sequential():
    text = " ".join(f"word{i}" for i in range(50))
    result = chunk_text(text, chunk_size=10, chunk_overlap=2)

    for expected_index, chunk in enumerate(result):
        assert chunk["chunk_index"] == expected_index


def test_chunk_text_overlap_repeats_boundary_words():
    text = " ".join(f"word{i}" for i in range(20))
    result = chunk_text(text, chunk_size=10, chunk_overlap=3)

    first_chunk_words = result[0]["text"].split()
    second_chunk_words = result[1]["text"].split()

    # Last 3 words of chunk 0 should equal first 3 words of chunk 1
    assert first_chunk_words[-3:] == second_chunk_words[:3]


def test_chunk_text_no_word_is_split_in_half():
    text = "supercalifragilisticexpialidocious " * 30
    result = chunk_text(text.strip(), chunk_size=10, chunk_overlap=2)

    for chunk in result:
        for word in chunk["text"].split():
            # Every word should be the whole word, never a fragment
            assert word == "supercalifragilisticexpialidocious"


def test_chunk_text_shorter_than_chunk_size_returns_single_chunk():
    text = "just a few words here"
    result = chunk_text(text, chunk_size=200, chunk_overlap=30)

    assert len(result) == 1
    assert result[0]["text"] == "just a few words here"
    assert result[0]["word_count"] == 5


def test_chunk_text_word_count_matches_actual_words():
    text = " ".join(f"word{i}" for i in range(45))
    result = chunk_text(text, chunk_size=10, chunk_overlap=2)

    for chunk in result:
        assert chunk["word_count"] == len(chunk["text"].split())


def test_chunk_text_empty_string_returns_empty_list():
    assert chunk_text("") == []
    assert chunk_text("   \n\n   ") == []


def test_chunk_text_non_string_raises_value_error():
    with pytest.raises(ValueError):
        chunk_text(None)

    with pytest.raises(ValueError):
        chunk_text(12345)


def test_chunk_text_invalid_chunk_size_raises_value_error():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=0)

    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=-5)

    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size="200")


def test_chunk_text_invalid_overlap_raises_value_error():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, chunk_overlap=-1)


def test_chunk_text_overlap_greater_or_equal_to_size_raises_error():
    # This specifically guards against the infinite-loop scenario
    with pytest.raises(ValueError):
        chunk_text("some text " * 500, chunk_size=100, chunk_overlap=100)

    with pytest.raises(ValueError):
        chunk_text("some text " * 500, chunk_size=100, chunk_overlap=150)


def test_chunk_text_last_chunk_can_be_smaller():
    # 11 words, chunk_size=5, overlap=2 -> step=3
    # Chunks start at 0,3,6,9 -> last chunk has only 2 words (w9,w10)
    text = " ".join(f"w{i}" for i in range(11))
    result = chunk_text(text, chunk_size=5, chunk_overlap=2)

    last_chunk = result[-1]
    assert last_chunk["word_count"] <= 5
    assert last_chunk["word_count"] > 0

def test_chunk_text_no_redundant_subset_chunk_at_end():
    text = " ".join(f"w{i}" for i in range(11))

    result = chunk_text(
        text,
        chunk_size=5,
        chunk_overlap=2
    )

    assert len(result) == 3
    assert result[-1]["text"] == "w6 w7 w8 w9 w10"