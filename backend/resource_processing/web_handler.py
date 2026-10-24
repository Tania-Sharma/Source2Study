import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


def validate_web_url(url: str) -> str:
    """
    Validate that the input string is a valid HTTP/HTTPS URL.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL must have http or https scheme: {url}")

    if not parsed.netloc:
        raise ValueError(f"URL must have a valid host: {url}")

    return url


def extract_web_content(
    url: str,
    resource_id: str | None = None,
    timeout: int = 15,
) -> dict:
    """
    Safely retrieve and extract relevant educational text from a website URL.

    Strips navigational boilerplate, ads, scripts, and styling while preserving
    headings, paragraphs, lists, and tables.

    Args:
        url (str): Website URL.
        resource_id (str, optional): Unique resource ID.
        timeout (int): Request timeout in seconds.

    Returns:
        dict: Standardized web resource dictionary containing:
            - resource_id: str | None
            - source_type: "website"
            - source_name: str (page title or domain)
            - url: str
            - title: str
            - headings: list[str]
            - text: str
            - sections: list[dict] with 'heading' and 'content'
    """
    valid_url = validate_web_url(url)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36 Source2StudyBot/1.0"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(valid_url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise ValueError(f"Website request timed out after {timeout} seconds: {valid_url}") from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Failed to fetch content from {valid_url}: {str(exc)}") from exc

    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        # Check if plain text
        if "text/plain" in content_type:
            raw_text = response.text.strip()
            return {
                "resource_id": resource_id,
                "source_type": "website",
                "source_name": urlparse(valid_url).netloc,
                "url": valid_url,
                "title": urlparse(valid_url).path.split("/")[-1] or urlparse(valid_url).netloc,
                "headings": [],
                "text": raw_text,
                "sections": [{"heading": "Main Content", "content": raw_text}],
            }
        raise ValueError(f"Unsupported content type '{content_type}' at {valid_url}. Expected HTML.")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unwanted non-content elements
    for tag in soup.find_all(
        ["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form", "iframe"]
    ):
        tag.decompose()

    # Extract Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    else:
        title = urlparse(valid_url).netloc

    # Look for main content container if available
    main_container = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|article|post|main", re.I)) or soup.body

    if not main_container:
        raise ValueError(f"Could not extract body content from website: {valid_url}")

    headings = []
    sections = []
    current_heading = "Introduction"
    current_paragraphs = []

    for elem in main_container.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "table"]):
        tag_name = elem.name.lower()
        if tag_name in ("h1", "h2", "h3", "h4"):
            text = elem.get_text(separator=" ", strip=True)
            if text:
                if current_paragraphs:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n\n".join(current_paragraphs),
                    })
                    current_paragraphs = []
                current_heading = text
                headings.append(text)
        elif tag_name == "p":
            text = elem.get_text(separator=" ", strip=True)
            if text:
                current_paragraphs.append(text)
        elif tag_name in ("ul", "ol"):
            items = [li.get_text(separator=" ", strip=True) for li in elem.find_all("li") if li.get_text(strip=True)]
            if items:
                current_paragraphs.append("\n".join(f"- {item}" for item in items))
        elif tag_name == "table":
            rows = []
            for tr in elem.find_all("tr"):
                cells = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(" | ".join(cells))
            if rows:
                current_paragraphs.append("\n".join(rows))

    if current_paragraphs:
        sections.append({
            "heading": current_heading,
            "content": "\n\n".join(current_paragraphs),
        })

    all_text = "\n\n".join(
        f"### {sec['heading']}\n{sec['content']}" if sec['heading'] != "Introduction" else sec['content']
        for sec in sections
    )

    if not all_text.strip():
        # Fallback to general text extraction
        all_text = main_container.get_text(separator="\n", strip=True)

    return {
        "resource_id": resource_id,
        "source_type": "website",
        "source_name": title or urlparse(valid_url).netloc,
        "url": valid_url,
        "title": title,
        "headings": headings,
        "text": all_text,
        "sections": sections,
    }
