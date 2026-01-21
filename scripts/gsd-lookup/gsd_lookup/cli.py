"""Main CLI entry point for gsd-lookup."""

import sys
from typing import Optional

import typer

from gsd_lookup import __version__
from gsd_lookup.backends.context7 import Context7Client
from gsd_lookup.backends.perplexity import PerplexityClient
from gsd_lookup.cache import get_cached, set_cached
from gsd_lookup.config import DEFAULT_MAX_TOKENS
from gsd_lookup.errors import GsdLookupError
from gsd_lookup.output import format_error, format_success, output_json
from gsd_lookup.tokens import truncate_results

app = typer.Typer(
    name="gsd-lookup",
    help="GSD research CLI - Context7 docs and Perplexity deep research",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"gsd-lookup {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """GSD research CLI - Context7 docs and Perplexity deep research."""
    pass


@app.command()
def docs(
    library: str = typer.Argument(..., help="Library name (e.g., 'nextjs', 'react')"),
    query: str = typer.Argument(..., help="Documentation query"),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        "-t",
        help="Maximum tokens in response",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Skip cache lookup",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-p",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Query library documentation via Context7.

    Use for authoritative, version-aware API documentation.

    Examples:
        gsd-lookup docs nextjs "app router setup"
        gsd-lookup docs react "hooks useEffect cleanup"
        gsd-lookup docs "react-three-fiber" "physics integration"
    """
    command = "docs"

    # Check cache first
    if not no_cache:
        cached = get_cached(command, library, query, max_tokens=max_tokens)
        if cached is not None:
            cached["metadata"]["cache_hit"] = True
            typer.echo(output_json(cached, pretty=json_pretty))
            return

    try:
        client = Context7Client()

        # Resolve library name to ID
        library_info = client.resolve_library(library, query)
        library_id = library_info["library_id"]

        # Query documentation
        raw_response = client.query_docs(library_id, query)

        # Format results
        results = client.format_results(raw_response)
        total_available = len(results)

        # Truncate to token budget
        truncated_results, tokens_used = truncate_results(results, max_tokens)

        # Build response
        metadata = {
            "library_id": library_id,
            "total_available": total_available,
            "returned": len(truncated_results),
            "tokens_used": tokens_used,
            "max_tokens": max_tokens,
            "cache_hit": False,
            "confidence": "HIGH",
            "backend": "context7",
        }

        response = format_success(
            command=command,
            query=query,
            results=truncated_results,
            metadata=metadata,
            library=library,
        )

        # Cache result
        if not no_cache:
            set_cached(command, library, query, max_tokens=max_tokens, value=response)

        typer.echo(output_json(response, pretty=json_pretty))

    except GsdLookupError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


@app.command()
def deep(
    query: str = typer.Argument(..., help="Research query"),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        "-t",
        help="Maximum tokens in response",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Skip cache lookup",
    ),
    json_pretty: bool = typer.Option(
        False,
        "--json-pretty",
        "-p",
        help="Pretty-print JSON output",
    ),
) -> None:
    """Perform deep research via Perplexity.

    Use for comprehensive multi-source research and synthesis.
    Cost: ~$0.005 per query + tokens. Use sparingly for high-value questions.

    Examples:
        gsd-lookup deep "authentication patterns for SaaS applications"
        gsd-lookup deep "WebGPU browser support and performance 2026"
        gsd-lookup deep "best practices for real-time collaboration"
    """
    command = "deep"

    # Check cache first
    if not no_cache:
        cached = get_cached(command, query, max_tokens=max_tokens)
        if cached is not None:
            cached["metadata"]["cache_hit"] = True
            typer.echo(output_json(cached, pretty=json_pretty))
            return

    try:
        client = PerplexityClient()

        # Perform research query
        raw_response = client.query(query)

        # Format results
        results, citations = client.format_results(raw_response)
        total_available = len(results)

        # Truncate to token budget
        truncated_results, tokens_used = truncate_results(results, max_tokens)

        # Build response
        metadata = {
            "total_available": total_available,
            "returned": len(truncated_results),
            "tokens_used": tokens_used,
            "max_tokens": max_tokens,
            "cache_hit": False,
            "confidence": "MEDIUM-HIGH",
            "backend": "perplexity-deep-research",
        }

        if citations:
            metadata["citations"] = citations

        response = format_success(
            command=command,
            query=query,
            results=truncated_results,
            metadata=metadata,
        )

        # Cache result
        if not no_cache:
            set_cached(command, query, max_tokens=max_tokens, value=response)

        typer.echo(output_json(response, pretty=json_pretty))

    except GsdLookupError as e:
        error_response = format_error(command, e)
        typer.echo(output_json(error_response, pretty=json_pretty))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
