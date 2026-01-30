# /// script
# dependencies = ["youtube-transcript-api", "requests", "beautifulsoup4"]
# ///
"""Fetch YouTube video transcript and save to a text file."""

import re
import sys
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    parsed = urlparse(url)

    # Handle youtu.be/VIDEO_ID
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    # Handle youtube.com/watch?v=VIDEO_ID
    if parsed.netloc in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            if "v" in query_params:
                return query_params["v"][0]
        # Handle youtube.com/v/VIDEO_ID or youtube.com/embed/VIDEO_ID
        if parsed.path.startswith(("/v/", "/embed/")):
            return parsed.path.split("/")[2]

    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_video_title(video_id: str) -> str:
    """Fetch video title from YouTube page."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    og_title = soup.find("meta", property="og:title")

    if og_title and og_title.get("content"):
        return og_title["content"]

    raise ValueError("Could not extract video title")


def sanitize_filename(title: str) -> str:
    """Sanitize title for use as filename."""
    # Remove or replace filesystem-unsafe characters
    unsafe_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(unsafe_chars, "", title)
    # Replace multiple spaces with single space
    sanitized = re.sub(r"\s+", " ", sanitized)
    # Strip leading/trailing whitespace and dots
    sanitized = sanitized.strip(". ")
    # Limit length (leaving room for .txt extension)
    if len(sanitized) > 200:
        sanitized = sanitized[:200].rsplit(" ", 1)[0]
    return sanitized


def fetch_transcript(video_id: str) -> str:
    """Fetch English transcript, preferring manual captions."""
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)

    transcript = None

    # Try manual transcript first
    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except Exception:
        pass

    # Fall back to auto-generated
    if transcript is None:
        try:
            transcript = transcript_list.find_generated_transcript(["en"])
        except Exception:
            pass

    if transcript is None:
        raise ValueError("No English transcript available")

    # Fetch and format as plain text
    formatter = TextFormatter()
    return formatter.format_transcript(transcript.fetch())


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run youtube_transcript.py <youtube_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        title = fetch_video_title(video_id)
    except Exception as e:
        print(f"Error fetching video title: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        transcript = fetch_transcript(video_id)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        sys.exit(1)

    filename = f"{sanitize_filename(title)}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Transcript saved to: {filename}")


if __name__ == "__main__":
    main()
