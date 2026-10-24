from unittest.mock import patch, MagicMock
import pytest
from backend.resource_processing.web_handler import validate_web_url, extract_web_content
from backend.text_processing.metadata import build_chunks_from_web


def test_validate_web_url():
    assert validate_web_url("https://example.com/ai") == "https://example.com/ai"
    assert validate_web_url("http://example.org") == "http://example.org"
    with pytest.raises(ValueError):
        validate_web_url("ftp://example.com")
    with pytest.raises(ValueError):
        validate_web_url("just-text")


@patch("backend.resource_processing.web_handler.requests.get")
def test_extract_web_content_html(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_resp.text = """
    <html>
      <head><title>Machine Learning Basics</title></head>
      <body>
        <nav><a href="/">Home</a></nav>
        <h1>Introduction to ML</h1>
        <p>Machine learning is a subset of artificial intelligence.</p>
        <h2>Supervised Learning</h2>
        <p>Uses labeled training data to predict outcomes.</p>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    mock_get.return_value = mock_resp

    res = extract_web_content("https://example.com/ml-basics", resource_id="web_ml_01")
    assert res["resource_id"] == "web_ml_01"
    assert res["source_type"] == "website"
    assert res["title"] == "Machine Learning Basics"
    assert "Supervised Learning" in res["headings"]
    assert "subset of artificial intelligence" in res["text"]
    assert "Copyright" not in res["text"]  # footer stripped


def test_build_chunks_from_web():
    mock_web = {
        "resource_id": "web_001",
        "source_type": "website",
        "source_name": "ML Guide",
        "url": "https://example.com/ml",
        "sections": [
            {
                "heading": "Overview",
                "content": "Machine learning enables computers to learn from experience without being explicitly programmed.",
            }
        ],
    }
    chunks = build_chunks_from_web(mock_web, chunk_size=10, chunk_overlap=2)
    assert len(chunks) > 0
    assert chunks[0]["metadata"]["source_type"] == "website"
    assert chunks[0]["metadata"]["heading"] == "Overview"
