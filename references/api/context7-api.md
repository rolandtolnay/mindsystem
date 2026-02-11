### Schema: CodeExample

Source: https://context7.com/docs/openapi.json

A single code example

```markdown
## Schema: CodeExample

A single code example

**Type:** object

- **language** (string) (required): Programming language
- **code** (string) (required): The actual code content

```

--------------------------------

### API Overview: Context7 Public API

Source: https://context7.com/docs/openapi.json

The Context7 Public API provides programmatic access to library documentation and search functionality. Get up-to-date documentation and code examples for any library.

```yaml
# Context7 Public API
# Version: 2.0.0

The Context7 Public API provides programmatic access to library documentation and search functionality. Get up-to-date documentation and code examples for any library.

# Base URL: https://context7.com/api
```

--------------------------------

### GET /v2/libs/search

Source: https://context7.com/docs/openapi.json

Search for libraries by name with intelligent LLM-powered ranking based on your query context.

```markdown
### Parameters

- **libraryName** (string, query, required): Library name to search for (e.g., 'react', 'nextjs', 'express')
- **query** (string, query, required): User's original question or task - used for intelligent relevance ranking

### Responses

#### 200 - Search results ranked by relevance

**SearchResponse**
- **results** (array (Library)) (required): Array of matching libraries ranked by relevance
  Array items:
    - **id** (string): Library ID in format `/owner/repo` (example: "/vercel/next.js")
    - **title** (string): Display name of the library (example: "Next.js")
    - **description** (string): Short description (example: "The React Framework")
    - **branch** (string): Git branch being tracked (example: "canary")
    - **lastUpdateDate** (string (date-time)): ISO 8601 timestamp of last update (example: "2025-01-15T10:30:00.000Z")
    - **state** (string (finalized|initial|processing|error|delete)): Processing state of the library (example: "finalized") ("finalized"|"initial"|"processing"|"error"|"delete")
    - **totalTokens** (integer): Total tokens in documentation (example: 607822)
    - **totalSnippets** (integer): Number of code snippets (example: 3629)
    - **stars** (integer): GitHub stars count (example: 131745)
    - **trustScore** (integer): Source reputation score (0-10) (example: 10)
    - **benchmarkScore** (number): Quality indicator score (0-100) (example: 95.5)
    - **versions** (array (string)): Available version tags (example: ["v15.1.8","v14.3.0"])

#### 400 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 401 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 429 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 500 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 503 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

### Example Usage

```bash
curl -X GET "https://context7.com/api/v2/libs/search?libraryName=string&query=string"
```

```

--------------------------------

### GET /v2/context

Source: https://context7.com/docs/openapi.json

Retrieve intelligent, LLM-reranked documentation context for natural language queries. Returns the most relevant code snippets and documentation for your specific question.

```markdown
### Parameters

- **libraryId** (string, query, required): Context7-compatible library ID in format `/owner/repo` or `/owner/repo/version`
- **query** (string, query, required): User's original question or task - used for intelligent relevance ranking
- **type** (string (json|txt), query, optional): Response format type

### Responses

#### 200 - Documentation context

**ContextResponse**
- **codeSnippets** (array (CodeSnippet)) (required): Relevant code snippets
  Array items:
    - **codeTitle** (string) (required): Title of the code snippet
    - **codeDescription** (string) (required): Description of what the code does
    - **codeLanguage** (string) (required): Primary programming language
    - **codeTokens** (integer) (required): Token count for the snippet
    - **codeId** (string) (required): URL to source location
    - **pageTitle** (string) (required): Title of the documentation page
    - **codeList** (array (CodeExample)) (required): Code examples in different languages
      Array items:
        - **language** (string) (required): Programming language
        - **code** (string) (required): The actual code content
- **infoSnippets** (array (InfoSnippet)) (required): Relevant documentation snippets
  Array items:
    - **pageId** (string): URL to source page
    - **breadcrumb** (string): Navigation breadcrumb path
    - **content** (string) (required): The documentation content
    - **contentTokens** (integer) (required): Token count for the content
- **rules** (object): Optional library-specific rules


#### 202 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 301 - response

**RedirectErrorResponse**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code
- **redirectUrl** (string): New location of the library

#### 400 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 401 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 403 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 404 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 422 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 429 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

#### 500 - response

**Error**
- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

### Example Usage

```bash
curl -X GET "https://context7.com/api/v2/context?libraryId=string&query=string&type=txt"
```

```

--------------------------------

### Security: bearerAuth

Source: https://context7.com/docs/openapi.json

Get your API key at [context7.com/dashboard](https://context7.com/dashboard). Treat your API key like a password and store it securely.

```markdown
## Security: bearerAuth

**Description:** Get your API key at [context7.com/dashboard](https://context7.com/dashboard). Treat your API key like a password and store it securely.

**Type:** http

**Scheme:** bearer


```

--------------------------------

### Schema: InfoSnippet

Source: https://context7.com/docs/openapi.json

A documentation snippet

```markdown
## Schema: InfoSnippet

A documentation snippet

**Type:** object

- **pageId** (string): URL to source page
- **breadcrumb** (string): Navigation breadcrumb path
- **content** (string) (required): The documentation content
- **contentTokens** (integer) (required): Token count for the content

```

--------------------------------

### Schema: ContextResponse

Source: https://context7.com/docs/openapi.json

Documentation context response

```markdown
## Schema: ContextResponse

Documentation context response

**Type:** object

- **codeSnippets** (array (CodeSnippet)) (required): Relevant code snippets
  Array items:
    - **codeTitle** (string) (required): Title of the code snippet
    - **codeDescription** (string) (required): Description of what the code does
    - **codeLanguage** (string) (required): Primary programming language
    - **codeTokens** (integer) (required): Token count for the snippet
    - **codeId** (string) (required): URL to source location
    - **pageTitle** (string) (required): Title of the documentation page
    - **codeList** (array (CodeExample)) (required): Code examples in different languages
      Array items:
        - **language** (string) (required): Programming language
        - **code** (string) (required): The actual code content
- **infoSnippets** (array (InfoSnippet)) (required): Relevant documentation snippets
  Array items:
    - **pageId** (string): URL to source page
    - **breadcrumb** (string): Navigation breadcrumb path
    - **content** (string) (required): The documentation content
    - **contentTokens** (integer) (required): Token count for the content
- **rules** (object): Optional library-specific rules

```

--------------------------------

### Schema: CodeSnippet

Source: https://context7.com/docs/openapi.json

A code snippet from library documentation

```markdown
## Schema: CodeSnippet

A code snippet from library documentation

**Type:** object

- **codeTitle** (string) (required): Title of the code snippet
- **codeDescription** (string) (required): Description of what the code does
- **codeLanguage** (string) (required): Primary programming language
- **codeTokens** (integer) (required): Token count for the snippet
- **codeId** (string) (required): URL to source location
- **pageTitle** (string) (required): Title of the documentation page
- **codeList** (array (CodeExample)) (required): Code examples in different languages
  Array items:
    - **language** (string) (required): Programming language
    - **code** (string) (required): The actual code content

```

--------------------------------

### Schema: Library

Source: https://context7.com/docs/openapi.json

Library metadata

```markdown
## Schema: Library

Library metadata

**Type:** object

- **id** (string): Library ID in format `/owner/repo` (example: "/vercel/next.js")
- **title** (string): Display name of the library (example: "Next.js")
- **description** (string): Short description (example: "The React Framework")
- **branch** (string): Git branch being tracked (example: "canary")
- **lastUpdateDate** (string (date-time)): ISO 8601 timestamp of last update (example: "2025-01-15T10:30:00.000Z")
- **state** (string (finalized|initial|processing|error|delete)): Processing state of the library (example: "finalized") ("finalized"|"initial"|"processing"|"error"|"delete")
- **totalTokens** (integer): Total tokens in documentation (example: 607822)
- **totalSnippets** (integer): Number of code snippets (example: 3629)
- **stars** (integer): GitHub stars count (example: 131745)
- **trustScore** (integer): Source reputation score (0-10) (example: 10)
- **benchmarkScore** (number): Quality indicator score (0-100) (example: 95.5)
- **versions** (array (string)): Available version tags (example: ["v15.1.8","v14.3.0"])

```

--------------------------------

### Schema: Error

Source: https://context7.com/docs/openapi.json

Standard error response

```markdown
## Schema: Error

Standard error response

**Type:** object

- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code

```

--------------------------------

### Schema: SearchResponse

Source: https://context7.com/docs/openapi.json

Search results response

```markdown
## Schema: SearchResponse

Search results response

**Type:** object

- **results** (array (Library)) (required): Array of matching libraries ranked by relevance
  Array items:
    - **id** (string): Library ID in format `/owner/repo` (example: "/vercel/next.js")
    - **title** (string): Display name of the library (example: "Next.js")
    - **description** (string): Short description (example: "The React Framework")
    - **branch** (string): Git branch being tracked (example: "canary")
    - **lastUpdateDate** (string (date-time)): ISO 8601 timestamp of last update (example: "2025-01-15T10:30:00.000Z")
    - **state** (string (finalized|initial|processing|error|delete)): Processing state of the library (example: "finalized") ("finalized"|"initial"|"processing"|"error"|"delete")
    - **totalTokens** (integer): Total tokens in documentation (example: 607822)
    - **totalSnippets** (integer): Number of code snippets (example: 3629)
    - **stars** (integer): GitHub stars count (example: 131745)
    - **trustScore** (integer): Source reputation score (0-10) (example: 10)
    - **benchmarkScore** (number): Quality indicator score (0-100) (example: 95.5)
    - **versions** (array (string)): Available version tags (example: ["v15.1.8","v14.3.0"])

```

--------------------------------

### Schema: RedirectErrorResponse

Source: https://context7.com/docs/openapi.json

Schema definition for RedirectErrorResponse

```markdown
## Schema: RedirectErrorResponse

Schema definition for RedirectErrorResponse

**Type:** object

- **error** (string) (required): Error code identifier
- **message** (string): Human-readable error message
- **status** (integer): HTTP status code
- **redirectUrl** (string): New location of the library

```

=== COMPLETE CONTENT === This response contains all available snippets from this library. No additional content exists. Do not make further requests.