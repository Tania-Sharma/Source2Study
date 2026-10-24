import re
from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


def extract_video_id(url: str) -> str:
    """
    Extract the YouTube video ID from various URL formats.
    Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            queries = parse_qs(parsed.query)
            if "v" in queries and queries["v"]:
                return queries["v"][0]
        elif parsed.path.startswith(("/embed/", "/v/", "/shorts/")):
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[1]:
                return parts[1]
    elif parsed.hostname in ("youtu.be", "www.youtu.be"):
        path = parsed.path.strip("/")
        if path:
            return path.split("/")[0]

    # Fallback to regex pattern for 11-character video IDs
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)", url)
    if match:
        return match.group(1)

    raise ValueError(f"Could not extract a valid YouTube video ID from URL: {url}")


def extract_youtube(
    url: str,
    resource_id: str | None = None,
    languages: list[str] | None = None,
) -> dict:
    """
    Fetch and process the transcript of a YouTube video.

    Args:
        url (str): YouTube video URL.
        resource_id (str, optional): Unique resource ID.
        languages (list[str], optional): Preferred transcript languages (defaults to ['en']).

    Returns:
        dict: Standardized YouTube resource dictionary containing:
            - resource_id: str | None
            - source_type: "youtube"
            - source_name: str (video title or video ID)
            - video_id: str
            - url: str
            - total_duration: float
            - segment_count: int
            - full_text: str
            - segments: list[dict] with 'text', 'start', 'duration'
    """
    video_id = extract_video_id(url)
    preferred_languages = languages or ["en"]

    try:
        # youtube-transcript-api supports list_transcripts or get_transcript
        # Using YouTubeTranscriptApi directly
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # Try to get preferred language or fallback to any available transcript
            try:
                transcript_obj = transcript_list.find_transcript(preferred_languages)
            except NoTranscriptFound:
                # Try finding any generated or manual transcript
                transcript_obj = next(iter(transcript_list))
            raw_segments = transcript_obj.fetch()
        except Exception:
            # Fallback to get_transcript directly
            raw_segments = YouTubeTranscriptApi.get_transcript(
                video_id, languages=preferred_languages
            )

    except (TranscriptsDisabled, NoTranscriptFound) as exc:
        raise ValueError(f"No transcript or captions available for video: {video_id}") from exc
    except VideoUnavailable as exc:
        raise ValueError(f"YouTube video unavailable or private: {video_id}") from exc
    except Exception as exc:
        raise ValueError(f"Failed to retrieve YouTube transcript: {str(exc)}") from exc

    segments = []
    text_parts = []
    total_duration = 0.0

    for seg in raw_segments:
        text = seg.get("text", "").strip()
        start = float(seg.get("start", 0.0))
        duration = float(seg.get("duration", 0.0))

        if text:
            segments.append({
                "text": text,
                "start": start,
                "duration": duration,
                "end": round(start + duration, 2),
            })
            text_parts.append(text)
            total_duration = max(total_duration, start + duration)

    full_text = " ".join(text_parts)

    return {
        "resource_id": resource_id,
        "source_type": "youtube",
        "source_name": f"YouTube_{video_id}",
        "video_id": video_id,
        "url": url,
        "total_duration": round(total_duration, 2),
        "segment_count": len(segments),
        "full_text": full_text,
        "segments": segments,
    }
