"""Context7 API client for library documentation."""

import httpx

from gsd_lookup.config import CONTEXT7_API_KEY, CONTEXT7_BASE_URL
from gsd_lookup.errors import ErrorCode, GsdLookupError


class Context7Client:
    """Client for Context7 documentation API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or CONTEXT7_API_KEY
        self.base_url = CONTEXT7_BASE_URL

    def _check_api_key(self) -> None:
        """Verify API key is configured."""
        if not self.api_key:
            raise GsdLookupError(
                ErrorCode.MISSING_API_KEY,
                "CONTEXT7_API_KEY environment variable not set",
                suggestions=[
                    "Set CONTEXT7_API_KEY in your environment",
                    "Get an API key at https://context7.com/dashboard",
                ],
            )

    def resolve_library(self, library_name: str, query: str) -> dict:
        """Resolve library name to Context7 library ID.

        Args:
            library_name: Library name to search for
            query: User's original query (used for relevance ranking)

        Returns:
            Dict with library_id and library info

        Raises:
            GsdLookupError: If library not found or API error
        """
        self._check_api_key()

        url = f"{self.base_url}/libs/search"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"query": library_name, "limit": 5}

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise GsdLookupError(
                    ErrorCode.MISSING_API_KEY,
                    "Invalid CONTEXT7_API_KEY",
                    suggestions=["Check your API key at https://context7.com/dashboard"],
                )
            elif e.response.status_code == 429:
                raise GsdLookupError(
                    ErrorCode.RATE_LIMITED,
                    "Context7 API rate limit exceeded",
                    suggestions=["Wait a moment and try again", "Use --no-cache sparingly"],
                )
            raise GsdLookupError(
                ErrorCode.API_ERROR,
                f"Context7 API error: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            raise GsdLookupError(
                ErrorCode.NETWORK_ERROR,
                f"Network error connecting to Context7: {str(e)}",
            )

        # Find best matching library
        libraries = data.get("results", [])
        if not libraries:
            raise GsdLookupError(
                ErrorCode.LIBRARY_NOT_FOUND,
                f"Could not find library '{library_name}' in Context7",
                suggestions=self._get_library_suggestions(library_name),
            )

        # Return first (best) match
        best_match = libraries[0]
        return {
            "library_id": best_match.get("id", ""),
            "name": best_match.get("name", library_name),
            "description": best_match.get("description", ""),
            "url": best_match.get("url", ""),
        }

    def query_docs(self, library_id: str, query: str) -> dict:
        """Query documentation for a library.

        Args:
            library_id: Context7 library ID (e.g., "/vercel/next.js")
            query: Documentation query

        Returns:
            Dict with documentation results

        Raises:
            GsdLookupError: If API error
        """
        self._check_api_key()

        url = f"{self.base_url}/context"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"libraryId": library_id, "query": query}

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()

                # Context7 can return JSON or plain text depending on the endpoint
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                else:
                    # Plain text/markdown response - wrap in a structure
                    data = {"content": response.text, "format": "markdown"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise GsdLookupError(
                    ErrorCode.LIBRARY_NOT_FOUND,
                    f"Library '{library_id}' not found in Context7",
                )
            elif e.response.status_code == 429:
                raise GsdLookupError(
                    ErrorCode.RATE_LIMITED,
                    "Context7 API rate limit exceeded",
                )
            raise GsdLookupError(
                ErrorCode.API_ERROR,
                f"Context7 API error: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            raise GsdLookupError(
                ErrorCode.NETWORK_ERROR,
                f"Network error connecting to Context7: {str(e)}",
            )

        return data

    def format_results(self, raw_response: dict) -> list[dict]:
        """Transform Context7 response to unified format.

        Args:
            raw_response: Raw API response

        Returns:
            List of formatted result dicts
        """
        results = []

        # Process code snippets
        for snippet in raw_response.get("codeSnippets", []):
            results.append({
                "title": snippet.get("title", "Code Example"),
                "content": snippet.get("code", ""),
                "source_url": snippet.get("url", ""),
                "type": "code",
            })

        # Process info snippets
        for snippet in raw_response.get("infoSnippets", []):
            results.append({
                "title": snippet.get("title", "Documentation"),
                "content": snippet.get("content", ""),
                "source_url": snippet.get("url", ""),
                "type": "info",
            })

        # If no structured snippets, try to extract from content field
        if not results and "content" in raw_response:
            results.append({
                "title": "Documentation",
                "content": raw_response["content"],
                "source_url": raw_response.get("url", ""),
                "type": "info",
            })

        return results

    def _get_library_suggestions(self, query: str) -> list[str]:
        """Get suggestions for similar library names."""
        # Common library name variations
        suggestions = []
        query_lower = query.lower()

        # Common mappings
        mappings = {
            "react": ["react", "react-dom", "react-router"],
            "next": ["nextjs", "next.js", "vercel/next.js"],
            "nextjs": ["nextjs", "next.js", "vercel/next.js"],
            "vue": ["vue", "vuejs", "vue-router"],
            "angular": ["angular", "@angular/core"],
            "express": ["express", "expressjs"],
            "fastapi": ["fastapi", "tiangolo/fastapi"],
            "django": ["django", "djangoproject"],
            "flask": ["flask", "pallets/flask"],
            "three": ["three.js", "threejs", "mrdoob/three.js"],
            "r3f": ["react-three-fiber", "@react-three/fiber"],
        }

        for key, values in mappings.items():
            if key in query_lower:
                suggestions.extend(values)
                break

        if not suggestions:
            suggestions = [
                "Try the exact package name from npm/pypi",
                "Check for common aliases (e.g., 'nextjs' for Next.js)",
            ]

        return suggestions[:3]
