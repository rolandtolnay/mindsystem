# Pro Search Quickstart

Get started with Pro Search for Sonar Pro - enhanced search with automated tools, multi-step reasoning, and real-time thought streaming.

---

## Overview

Pro Search enhances [Sonar Pro](https://docs.perplexity.ai/getting-started/models/models/sonar-pro) with automated tool usage, enabling multi-step reasoning through intelligent tool orchestration including web search and URL content fetching.

**Pro Search only works when streaming is enabled.** Non-streaming requests will fall back to standard Sonar Pro behavior.

### Standard Sonar Pro

- Single web search execution
- Fast response synthesis
- Fixed search strategy
- Static result processing

### Pro Search for Sonar Pro

- Multi-step reasoning with automated tools
- Dynamic tool execution
- Real-time thought streaming
- Adaptive research strategies

---

## Basic Usage

Enabling Pro Search requires setting `stream` to `true` and specifying `"search_type": "pro"` in your API request. The default search type is `"fast"` for regular Sonar Pro.

Here is an example of how to enable Pro Search with streaming:

**Python SDK**

```python
from perplexity import Perplexity

client = Perplexity(api_key="YOUR_API_KEY")

messages = [
    {
        "role": "user",
        "content": "Analyze the latest developments in quantum computing and their potential impact on cryptography. Include recent research findings and expert opinions."
    }
]

response = client.chat.completions.create(
    model="sonar-pro",
    messages=messages,
    stream=True,
    web_search_options={
        "search_type": "pro"
    }
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Response**

```json
{
  "id": "2f16f4a0-e1d7-48c7-832f-8757b96ec221",
  "model": "sonar-pro",
  "created": 1759957470,
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 98,
    "total_tokens": 113,
    "search_context_size": "low",
    "cost": {
      "input_tokens_cost": 0.0,
      "output_tokens_cost": 0.001,
      "request_cost": 0.014,
      "total_cost": 0.015
    }
  },
  "search_results": [
    {
      "title": "Quantum Computing Breakthrough 2024",
      "url": "https://example.com/quantum-breakthrough",
      "date": "2024-03-15",
      "snippet": "Researchers at MIT have developed a new quantum error correction method...",
      "source": "web"
    }
  ],
  "reasoning_steps": [
    {
      "thought": "I need to search for recent quantum computing developments first.",
      "type": "web_search",
      "web_search": {
        "search_keywords": [
          "quantum computing developments 2024 cryptography impact",
          "post-quantum cryptography"
        ],
        "search_results": [
          {
            "title": "Quantum Computing Breakthrough 2024",
            "url": "https://example.com/quantum-breakthrough",
            "date": "2024-03-15",
            "last_updated": "2024-03-20",
            "snippet": "Researchers at MIT have developed a new quantum error correction method...",
            "source": "web"
          }
        ]
      }
    },
    {
      "thought": "Let me fetch detailed content from this research paper.",
      "type": "fetch_url_content",
      "fetch_url_content": {
        "contents": [
          {
            "title": "Quantum Error Correction Paper",
            "url": "https://arxiv.org/abs/2024.quantum",
            "date": null,
            "last_updated": null,
            "snippet": "Abstract: This paper presents a novel approach to quantum error correction...",
            "source": "web"
          }
        ]
      }
    }
  ],
  "object": "chat.completion.chunk",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "## Latest Quantum Computing Developments\n\nBased on my research and analysis..."
      }
    }
  ]
}
```

---

## Enabling Automatic Classification

Sonar Pro can be configured to automatically classify queries into Pro Search or Fast Search based on complexity. This is the recommended approach for most applications.

Set `search_type: "auto"` to let the system intelligently route queries based on complexity.

**Python SDK**

```python
from perplexity import Perplexity

client = Perplexity(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="sonar-pro",
    messages=[
        {
            "role": "user",
            "content": "Compare the energy efficiency of Tesla Model 3, Chevrolet Bolt, and Nissan Leaf"
        }
    ],
    stream=True,
    web_search_options={
        "search_type": "auto"  # Automatic classification
    }
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### How Classification Works

The classifier analyzes your query and automatically routes it to:

**Pro Search** for complex queries requiring:
- Multi-step reasoning or analysis
- Comparative analysis across multiple sources
- Deep research workflows

**Fast Search** for straightforward queries like:
- Simple fact lookups
- Direct information retrieval
- Basic question answering

### Billing with Auto Classification

**You are billed based on which search type your query triggers:**

- If classified as **Pro Search**: $14–$22 per 1,000 requests (based on context size)
- If classified as **Fast Search**: $6–$14 per 1,000 requests (based on context size - same as standard Sonar Pro)

To see the full pricing details, see the [Pricing](#pricing) section.

Automatic classification is recommended for most applications as it balances cost optimization with query performance. You get Pro Search capabilities when needed without overpaying for simple queries.

---

## Manually Specifying the Search Type

If needed, you can manually specify the search type. This is useful for specific use cases where you know the query requires Pro Search capabilities.

| Value | Description |
|-------|-------------|
| `"search_type": "pro"` | Manually specify Pro Search for complex queries when you know multi-step tool usage is needed |
| `"search_type": "fast"` | Manually specify Fast Search for simple queries to optimize speed and cost (this is also the default when `search_type` is omitted) |

---

## Built-in Tool Capabilities

Pro Search provides access to two powerful built-in tools that the model can use automatically:

### web_search

Conduct targeted web searches with custom queries, filters, and search strategies based on the evolving research context.

[Learn more →](https://docs.perplexity.ai/guides/pro-search-tools#web-search)

### fetch_url_content

Retrieve and analyze content from specific URLs to gather detailed information beyond search result snippets.

[Learn more →](https://docs.perplexity.ai/guides/pro-search-tools#fetch-url-content)

---

The model automatically decides which tools to use and when, creating dynamic research workflows tailored to each specific query. These are built-in tools that the system calls for you—you cannot register custom tools.

Learn more in the [Built-in Tool Capabilities](https://docs.perplexity.ai/guides/pro-search-agentic-tools) guide.

---

## Additional Capabilities

Pro Search also provides access to advanced Sonar Pro features that enhance your development experience:

- **[Stream Mode Guide](https://docs.perplexity.ai/guides/pro-search-stream-mode-guide)**: Control streaming response formats with concise or full mode for optimized bandwidth usage and enhanced reasoning visibility.

---

## Pricing

Pro Search pricing consists of token usage plus request fees that vary by search type and context size.

### Token Usage (Same for All Search Types)

| Type | Price |
|------|-------|
| Input Tokens | $3 per 1M |
| Output Tokens | $15 per 1M |

### Request Fees (per 1,000 requests)

#### Pro Search (Complex Queries)

| Context Size | Price |
|--------------|-------|
| High Context | $22 |
| Medium Context | $18 |
| Low Context | $14 |

#### Fast Search (Simple Queries)

| Context Size | Price |
|--------------|-------|
| High Context | $14 |
| Medium Context | $10 |
| Low Context | $6 |

When using `search_type: "auto"`, you're billed at the Pro Search rate if your query is classified as complex, or the Fast Search rate if classified as simple. See the full pricing details [here](https://docs.perplexity.ai/getting-started/pricing).

---

## Next Steps

- [Chat Completions Guide](https://docs.perplexity.ai/guides/chat-completions-guide) — Comprehensive guide to the chat completions API
- [API Reference](https://docs.perplexity.ai/api-reference/chat-completions-post) — Complete API documentation and parameter reference
