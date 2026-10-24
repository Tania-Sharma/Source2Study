from unittest.mock import patch, MagicMock
import pytest
from backend.resource_processing.youtube_handler import extract_video_id, extract_youtube
from backend.text_processing.metadata import build_chunks_from_youtube


def test_extract_video_id_formats():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_video_id_invalid():
    with pytest.raises(ValueError):
        extract_video_id("not-a-url")
    with pytest.raises(ValueError):
        extract_video_id("")


@patch("backend.resource_processing.youtube_handler.YouTubeTranscriptApi")
def test_extract_youtube_success(mock_api):
    mock_api.list_transcripts.side_effect = Exception("No list")
    mock_api.get_transcript.return_value = [
        {"text": "Welcome to machine learning.", "start": 0.0, "duration": 4.5},
        {"text": "In this video we cover neural networks.", "start": 5.0, "duration": 6.0},
    ]

    res = extract_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ", resource_id="res_yt_01")

    assert res["resource_id"] == "res_yt_01"
    assert res["source_type"] == "youtube"
    assert res["video_id"] == "dQw4w9WgXcQ"
    assert res["segment_count"] == 2
    assert "machine learning" in res["full_text"]


def test_build_chunks_from_youtube():
    mock_result = {
        "resource_id": "yt_123",
        "source_type": "youtube",
        "source_name": "YouTube_123",
        "url": "https://youtu.be/123",
        "segments": [
            {"text": "Part one of lesson.", "start": 0.0, "duration": 10.0},
            {"text": "Part two explains gradient descent.", "start": 10.0, "duration": 15.0},
        ],
    }
    chunks = build_chunks_from_youtube(mock_result, chunk_size=5, chunk_overlap=1)
    assert len(chunks) > 0
    assert chunks[0]["metadata"]["source_type"] == "youtube"
    assert "timestamp" in chunks[0]["metadata"]
    assert chunks[0]["metadata"]["content_type"] == "transcript"
