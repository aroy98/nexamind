from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.errors import ProviderError

MAX_NOTE_LENGTH = 50_000
FETCH_TIMEOUT_SECONDS = 10


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _extract_note(content: str) -> tuple[str, None, str]:
    text = content.strip()
    if not text:
        raise ValueError("content must not be empty")
    if len(text) > MAX_NOTE_LENGTH:
        raise ValueError(f"content exceeds {MAX_NOTE_LENGTH} character limit")
    title = text[:60] + ("..." if len(text) > 60 else "")
    return text, None, title


def _extract_url(content: str) -> tuple[str, str, str]:
    url = content.strip()
    if not _is_valid_url(url):
        raise ValueError("content must be a valid absolute http(s) URL")

    try:
        response = requests.get(url, timeout=FETCH_TIMEOUT_SECONDS, headers={"User-Agent": "ai-knowledge-inbox/1.0"})
    except requests.RequestException as exc:
        raise ProviderError("failed to fetch URL", detail=str(exc)) from exc

    if not response.ok:
        raise ProviderError("URL fetch returned a non-success status", detail=f"status={response.status_code}")

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type.lower():
        raise ProviderError("URL did not return HTML content", detail=f"content-type={content_type}")

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    if not text:
        raise ProviderError("URL returned no extractable text")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag and title_tag.get_text(strip=True) else url

    return text, url, title


def validate_and_extract(source_type: str, content: str) -> tuple[str, str | None, str]:
    """Returns (raw_content, source_url, title). Raises ValueError (422) or ProviderError (502).
    source_type is validated as Literal["note", "url"] by IngestRequest before this runs."""
    if source_type == "note":
        return _extract_note(content)
    return _extract_url(content)
