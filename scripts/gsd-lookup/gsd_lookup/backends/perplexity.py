"""Perplexity API client for deep research."""

import re

import httpx

from gsd_lookup.config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, PERPLEXITY_DEEP_MODEL
from gsd_lookup.errors import ErrorCode, GsdLookupError


class PerplexityClient:
    """Client for Perplexity deep research API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.base_url = PERPLEXITY_BASE_URL

    def _check_api_key(self) -> None:
        """Verify API key is configured."""
        if not self.api_key:
            raise GsdLookupError(
                ErrorCode.MISSING_API_KEY,
                "PERPLEXITY_API_KEY environment variable not set",
                suggestions=[
                    "Set PERPLEXITY_API_KEY in your environment",
                    "Get an API key at https://docs.perplexity.ai/",
                ],
            )

    def query(self, query: str) -> dict:
        """Perform deep research query.

        Args:
            query: Research query

        Returns:
            Dict with research response

        Raises:
            GsdLookupError: If API error
        """
        self._check_api_key()

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": PERPLEXITY_DEEP_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a technical research assistant. Think step-by-step to analyze the query, "
                        "search for authoritative sources, and synthesize actionable findings.\n\n"
                        "RESEARCH APPROACH:\n"
                        "1. Identify the core technical question\n"
                        "2. Search for current best practices from official docs and trusted sources\n"
                        "3. Verify claims across multiple sources when possible\n"
                        "4. Synthesize into practical guidance\n\n"
                        "OUTPUT FORMAT:\n"
                        "- Lead with the recommended approach or answer\n"
                        "- Support with 8-12 key findings as bullet points\n"
                        "- Each finding cites its source inline [Source]\n"
                        "- Include code examples when relevant\n"
                        "- Flag any caveats or edge cases\n"
                        "- End with clear next steps if applicable\n"
                    ),
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
        }

        try:
            with httpx.Client(timeout=90.0) as client:  # Reasoning model is faster
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise GsdLookupError(
                    ErrorCode.MISSING_API_KEY,
                    "Invalid PERPLEXITY_API_KEY",
                    suggestions=["Check your API key at https://docs.perplexity.ai/"],
                )
            elif e.response.status_code == 429:
                raise GsdLookupError(
                    ErrorCode.RATE_LIMITED,
                    "Perplexity API rate limit exceeded",
                    suggestions=["Wait a moment and try again"],
                )
            raise GsdLookupError(
                ErrorCode.API_ERROR,
                f"Perplexity API error: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            raise GsdLookupError(
                ErrorCode.NETWORK_ERROR,
                f"Network error connecting to Perplexity: {str(e)}",
            )

        return data

    def _strip_think_tags(self, content: str) -> str:
        """Remove <think>...</think> blocks from response."""
        # Remove think tags and their content (including multiline)
        return re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    def format_results(self, raw_response: dict) -> tuple[list[dict], list[str]]:
        """Transform Perplexity response to unified format.

        Args:
            raw_response: Raw API response

        Returns:
            Tuple of (results list, citations list)
        """
        results = []
        citations = []

        # Extract content from response
        choices = raw_response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")

            # Strip think tags
            content = self._strip_think_tags(content)

            if content:
                results.append({
                    "title": "Research Findings",
                    "content": content,
                    "source_url": "",
                    "type": "research",
                })

        # Extract citations if available
        citations = raw_response.get("citations", [])

        return results, citations
