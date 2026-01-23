# ms-lookup

CLI tool for Mindsystem research providing access to Context7 library documentation and Perplexity deep research.

## Installation

The tool is installed automatically with Mindsystem. To use it standalone:

```bash
cd scripts/ms-lookup
uv sync
uv run python -m ms_lookup --help
```

Or with pip:

```bash
pip install -e .
ms-lookup --help
```

## Environment Variables

```bash
# Required for docs command
export CONTEXT7_API_KEY="your-context7-api-key"

# Required for deep command
export PERPLEXITY_API_KEY="your-perplexity-api-key"
```

Get API keys:
- Context7: https://context7.com/dashboard
- Perplexity: https://docs.perplexity.ai/

## Commands

### docs - Library Documentation

Query library documentation via Context7. Provides authoritative, version-aware API documentation.

```bash
ms-lookup docs <library> "<query>"

# Examples
ms-lookup docs nextjs "app router setup"
ms-lookup docs react "hooks useEffect cleanup"
ms-lookup docs "react-three-fiber" "physics integration"
```

### deep - Deep Research

Perform comprehensive multi-source research via Perplexity.

**Note:** This costs ~$0.005 per query + tokens. Use sparingly for high-value research questions.

```bash
ms-lookup deep "<query>"

# Examples
ms-lookup deep "authentication patterns for SaaS applications"
ms-lookup deep "WebGPU browser support and performance 2026"
```

## Options

| Option | Description |
|--------|-------------|
| `--max-tokens, -t` | Maximum tokens in response (default: 2000) |
| `--no-cache` | Skip cache lookup |
| `--json-pretty, -p` | Pretty-print JSON output |
| `--version, -v` | Show version |

## Output Format

All commands return JSON:

```json
{
  "success": true,
  "command": "docs",
  "query": "app router setup",
  "library": "nextjs",
  "results": [
    {
      "title": "App Router Getting Started",
      "content": "The App Router uses...",
      "source_url": "https://nextjs.org/docs/...",
      "tokens": 450,
      "type": "info"
    }
  ],
  "metadata": {
    "library_id": "/vercel/next.js",
    "total_available": 15,
    "returned": 3,
    "tokens_used": 830,
    "max_tokens": 2000,
    "cache_hit": false,
    "confidence": "HIGH",
    "backend": "context7"
  }
}
```

## Caching

Results are cached in `~/.cache/ms-lookup/`:
- docs: 24 hours TTL
- deep: 6 hours TTL

Use `--no-cache` to bypass cache.
