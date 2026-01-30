# Perplexity Sonar Chat Completions API

Generates a model's response for the given chat conversation.

**Endpoint:** `POST https://api.perplexity.ai/chat/completions`

---

## Authentication

**Authorization** `string` `header` `required`

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

---

## Request Body

Content-Type: `application/json`

### Required Parameters

---

**model** `enum<string>` `required`

The name of the model that will complete your prompt. Choose from our available Sonar models: sonar (lightweight search), sonar-pro (advanced search), sonar-deep-research (exhaustive research), or sonar-reasoning-pro (premier reasoning).

Available options: `sonar`, `sonar-pro`, `sonar-deep-research`, `sonar-reasoning-pro`

Example: `"sonar-deep-research"`

---

**messages** `Message · object[]` `required`

A list of messages comprising the conversation so far.

Example:

```json
[
  {
    "role": "system",
    "content": "Be precise and concise."
  },
  {
    "role": "user",
    "content": "How many stars are there in our galaxy?"
  }
]
```

---

### Optional Parameters

---

**search_mode** `enum<string>` `default: web`

Controls search mode: 'academic' prioritizes scholarly sources, 'sec' prioritizes SEC filings, 'web' uses general web search. See [academic guide](https://docs.perplexity.ai/guides/academic-filter-guide) and [SEC guide](https://docs.perplexity.ai/guides/sec-guide).

Available options: `academic`, `sec`, `web`

---

**reasoning_effort** `enum<string>`

Perplexity-Specific: Controls how much computational effort the AI dedicates to each query for deep research models. 'low' provides faster, simpler answers with reduced token usage, 'medium' offers a balanced approach, and 'high' delivers deeper, more thorough responses with increased token usage. This parameter directly impacts the amount of reasoning tokens consumed.

**WARNING:** This parameter is ONLY applicable for sonar-deep-research. Defaults to 'medium' when used with sonar-deep-research.

Available options: `low`, `medium`, `high`

---

**max_tokens** `integer`

OpenAI Compatible: The maximum number of completion tokens returned by the API. Controls the length of the model's response. If the response would exceed this limit, it will be truncated. Higher values allow for longer responses but may increase processing time and costs.

---

**temperature** `number` `default: 0.2`

The amount of randomness in the response, valued between 0 and 2. Lower values (e.g., 0.1) make the output more focused, deterministic, and less creative. Higher values (e.g., 1.5) make the output more random and creative. Use lower values for factual/information retrieval tasks and higher values for creative applications.

Required range: `0 <= x < 2`

---

**top_p** `number` `default: 0.9`

OpenAI Compatible: The nucleus sampling threshold, valued between 0 and 1. Controls the diversity of generated text by considering only the tokens whose cumulative probability exceeds the top_p value. Lower values (e.g., 0.5) make the output more focused and deterministic, while higher values (e.g., 0.95) allow for more diverse outputs. Often used as an alternative to temperature.

---

**language_preference** `string`

Perplexity-Specific: Specifies the preferred language for the chat completion response (i.e., English, Korean, Spanish, etc.) of the response content. This parameter is supported only by the `sonar` and `sonar-pro` models. Using it with other models is on a best-effort basis and may not produce consistent results.

---

**search_domain_filter** `Search Domain Filter · array`

A list of domains to limit search results to. Currently limited to 20 domains for Allowlisting and Denylisting. For Denylisting, add a `-` at the beginning of the domain string. More information about this [here](https://docs.perplexity.ai/guides/search-domain-filters).

---

**return_images** `boolean` `default: false`

Perplexity-Specific: Determines whether search results should include images.

---

**return_related_questions** `boolean` `default: false`

Perplexity-Specific: Determines whether related questions should be returned.

---

**search_recency_filter** `string`

Perplexity-Specific: Filters search results based on time (e.g., 'week', 'day').

---

**search_after_date_filter** `string`

Perplexity-Specific: Filters search results to only include content published after this date. Format should be %m/%d/%Y (e.g. 3/1/2025)

---

**search_before_date_filter** `string`

Perplexity-Specific: Filters search results to only include content published before this date. Format should be %m/%d/%Y (e.g. 3/1/2025)

---

**last_updated_after_filter** `string`

Perplexity-Specific: Filters search results to only include content last updated after this date. Format should be %m/%d/%Y (e.g. 3/1/2025)

---

**last_updated_before_filter** `string`

Perplexity-Specific: Filters search results to only include content last updated before this date. Format should be %m/%d/%Y (e.g. 3/1/2025)

---

**top_k** `number` `default: 0`

OpenAI Compatible: The number of tokens to keep for top-k filtering. Limits the model to consider only the k most likely next tokens at each step. Lower values (e.g., 20) make the output more focused and deterministic, while higher values allow for more diverse outputs. A value of 0 disables this filter. Often used in conjunction with top_p to control output randomness.

---

**stream** `boolean` `default: false`

OpenAI Compatible: Determines whether to stream the response incrementally.

---

**presence_penalty** `number` `default: 0`

OpenAI Compatible: Positive values increase the likelihood of discussing new topics. Applies a penalty to tokens that have already appeared in the text, encouraging the model to talk about new concepts. Values typically range from 0 (no penalty) to 2.0 (strong penalty). Higher values reduce repetition but may lead to more off-topic text.

---

**frequency_penalty** `number` `default: 0`

OpenAI Compatible: Decreases likelihood of repetition based on prior frequency. Applies a penalty to tokens based on how frequently they've appeared in the text so far. Values typically range from 0 (no penalty) to 2.0 (strong penalty). Higher values (e.g., 1.5) reduce repetition of the same words and phrases. Useful for preventing the model from getting stuck in loops.

---

**response_format** `Response Format · object`

Enables structured JSON output formatting.

---

**disable_search** `boolean` `default: false`

Perplexity-Specific: When set to true, disables web search completely and the model will only use its training data to respond. This is useful when you want deterministic responses without external information. More information about this [here](https://docs.perplexity.ai/guides/search-control-guide#disabling-search-completely).

---

**enable_search_classifier** `boolean` `default: false`

Perplexity-Specific: Enables a classifier that decides if web search is needed based on your query. See more [here](https://docs.perplexity.ai/guides/search-control-guide#search-classifier).

---

**web_search_options** `Web Search Options · object`

Perplexity-Specific: Configuration for using web search in model responses.

Example:

```json
{ "search_context_size": "high" }
```

---

**media_response** `Media Response · object`

Perplexity-Specific: Configuration for controlling media content in responses, such as videos and images. Use the overrides property to enable specific media types.

Example:

```json
{
  "overrides": {
    "return_videos": true,
    "return_images": true
  }
}
```

---

## Response

`200` `application/json` OK

---

**id** `string` `required`

A unique identifier for the chat completion.

---

**model** `string` `required`

The model that generated the response.

---

**created** `integer` `required`

The Unix timestamp (in seconds) of when the chat completion was created.

---

**usage** `UsageInfo · object` `required`

Token usage information containing:

| Field | Type | Description |
|-------|------|-------------|
| `prompt_tokens` | integer | Tokens in the prompt |
| `completion_tokens` | integer | Tokens in the completion |
| `total_tokens` | integer | Total tokens used |
| `search_context_size` | string | Size of search context |
| `citation_tokens` | integer | Tokens used for citations |
| `num_search_queries` | integer | Number of search queries performed |
| `reasoning_tokens` | integer | Tokens used for reasoning |

---

**object** `string` `default: chat.completion` `required`

The type of object, which is always `chat.completion`.

---

**choices** `ChatCompletionsChoice · object[]` `required`

A list of chat completion choices. Can be more than one if `n` is greater than 1.

| Field | Type | Description |
|-------|------|-------------|
| `index` | integer | Index of the choice |
| `message.role` | string | Role of the message author |
| `message.content` | string | The generated content |
| `finish_reason` | string | Reason for completion (e.g., `stop`) |

---

**search_results** `ApiPublicSearchResult · object[] | null`

A list of search results related to the response.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Title of the search result |
| `url` | string | URL of the source |
| `date` | string | Publication date (format: `YYYY-MM-DD`, e.g. `2023-12-25`) |

---

**videos** `VideoResult · object[] | null`

A list of video results when media_response.overrides.return_videos is enabled. Contains video URLs and metadata.

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Video URL |
| `thumbnail_url` | string | Thumbnail image URL |
| `thumbnail_width` | integer | Thumbnail width in pixels |
| `thumbnail_height` | integer | Thumbnail height in pixels |
| `duration` | integer | Video duration in seconds |

---

## Examples

### Request

```bash
curl --request POST \
  --url https://api.perplexity.ai/chat/completions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "sonar-deep-research",
    "messages": [
      {
        "role": "system",
        "content": "Be precise and concise."
      },
      {
        "role": "user",
        "content": "How many stars are there in our galaxy?"
      }
    ]
  }'
```

### Response

```json
{
  "id": "<string>",
  "model": "<string>",
  "created": 123,
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 123,
    "total_tokens": 123,
    "search_context_size": "<string>",
    "citation_tokens": 123,
    "num_search_queries": 123,
    "reasoning_tokens": 123
  },
  "object": "chat.completion",
  "choices": [
    {
      "index": 123,
      "message": {
        "content": "<string>",
        "role": "system"
      },
      "finish_reason": "stop"
    }
  ],
  "search_results": [
    {
      "title": "<string>",
      "url": "<string>",
      "date": "2023-12-25"
    }
  ],
  "videos": [
    {
      "url": "<string>",
      "thumbnail_url": "<string>",
      "thumbnail_width": 123,
      "thumbnail_height": 123,
      "duration": 123
    }
  ]
}
```

---

## Related Endpoints

- [POST /search](https://docs.perplexity.ai/api-reference/search-post) — Search API
- [POST /chat/completions (async)](https://docs.perplexity.ai/api-reference/async-chat-completions-post) — Create Async Chat Completion
- [GET /chat/completions (async)](https://docs.perplexity.ai/api-reference/async-chat-completions-get) — List Async Chat Completions
- [GET /chat/completions/{request_id}](https://docs.perplexity.ai/api-reference/async-chat-completions-request_id-get) — Get Async Chat Completion Response
- [POST /auth/token](https://docs.perplexity.ai/api-reference/generate-auth-token-post) — Generate Auth Token
- [POST /auth/token/revoke](https://docs.perplexity.ai/api-reference/revoke-auth-token-post) — Revoke Auth Token
