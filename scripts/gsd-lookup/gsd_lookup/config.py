"""Configuration and environment variables."""

import os
from pathlib import Path

# API Keys from environment
CONTEXT7_API_KEY = os.environ.get("CONTEXT7_API_KEY", "")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

# API URLs
CONTEXT7_BASE_URL = "https://context7.com/api/v2"
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "gsd-lookup"
CACHE_TTL_DOCS = 60 * 60 * 24  # 24 hours for docs
CACHE_TTL_DEEP = 60 * 60 * 6   # 6 hours for deep research

# Default token limits
DEFAULT_MAX_TOKENS = 2000

# Perplexity model
PERPLEXITY_DEEP_MODEL = "sonar-deep-research"
