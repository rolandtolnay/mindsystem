# Beyond MCP
> It's time to push beyond MCP Servers... Right?
>
> Let's breakdown real engineering trade offs between MCP, CLI, File System Scripts, and Skills based approaches for building reusable toolsets for your AI Agents.
>
> Watch the full video breakdown here: [Beyond MCP](https://youtu.be/OIKTsVjTVJE)

## Purpose of this Repo

- MCP Servers are the standard way to build reusable toolsets for your AI Agents. But they are not the only way.
- MCP Servers come with a massive cost - **instant context loss**.
- When you have a single, or a few MCP Servers, this is not a big deal. But as you scale to many agents, many tools, and many contexts - this cost quickly becomes a bottleneck.
- So what are the alternatives that big players are using to build powerful, reusable, context preserving toolsets for their AI Agents?

_Here we explore 4 concrete approaches in this repo, all implementing access to Kalshi prediction market data._


## The 4 Approaches

![The 4 Approaches Revealed](images/NodeGraphLR-revealed.gif)

### `apps/1_mcp_server/` - MCP Server

![MCP Server Architecture](images/NodeGraphLR-mcp-server.gif)

### `apps/2_cli/` - CLI

![CLI Architecture](images/NodeGraphLR-cli.gif)

### `apps/3_file_system_scripts/` - File System Scripts

![File System Scripts Architecture](images/NodeGraphLR-scripts.gif)

### `apps/4_skill/` - Skill

![Agent Skill Architecture](images/NodeGraphLR-skills.gif)

## Quick Start

### 1. MCP Server
```bash
cp .mcp.testing .mcp.json

claude --mcp-config .mcp.json

prompt: "kalshi: get exchange status"
```

### 2. CLI
```bash
# or by agent
claude

prompt: "/prime_kalshi_cli_tools"

prompt: "kalshi: Get exchange status"

prompt: "kalshi: List events"

prompt: "kalshi: List events in JSON"

prompt: "kalshi: List events in JSON, limit 100"

# or by hand
cd apps/2_cli
uv sync
uv run kalshi status
uv run kalshi events
uv run kalshi events --json
uv run kalshi events --json --limit 100
```

### 3. File System Scripts
```bash
# by agent
claude

prompt: "/prime_file_system_scripts"

prompt: "kalshi: Get exchange status"

prompt: "kalshi: List events"

...

# or by hand
cd apps/3_file_system_scripts/scripts

uv run status.py

uv run *.py
```

### 4. Skill
```bash
cd apps/4_skill/

claude

prompt: "kalshi markets: Get exchange status"

prompt: "kalshi markets: search for events about 'best ai'" # Note this will trigger the cache build on first run which will take several minutes

...
```


## The 4 Approaches In Detail

- `apps/1_mcp_server/` - MCP Server
- `apps/2_cli/` - CLI
- `apps/3_file_system_scripts/` - File System Scripts
- `apps/4_skill/` - Skill

### 1. MCP Server (`apps/1_mcp_server/`)

**Classic Model Context Protocol implementation**

- ✅ **Standardized integration** - Works with any MCP-compatible client
- ✅ **Tool discovery** - Auto-exposes 15 tools to LLMs
- ✅ **Clean abstractions** - MCP protocol handles complexity
- ❌ **Instant context loss** - Every tool call loses conversational context
- ❌ **Wrapper overhead** - Delegates to CLI via subprocess

**Architecture:**
```
Claude/LLM → MCP Protocol → MCP Server → subprocess → CLI → Kalshi API
```

**Key files:**
- `server.py` - FastMCP server with 15 tool definitions
- Wraps CLI commands in MCP tool interface
- Each tool call is stateless

**When to use:** Building tools for multiple LLM clients, need standardized protocol, context loss is acceptable.

---

### 2. CLI (`apps/2_cli/`)

**Direct HTTP API access via command-line interface**

- ✅ **Single source of truth** - Direct API calls, no wrappers
- ✅ **Dual output modes** - Human-readable or pure JSON
- ✅ **Smart caching** - Pandas-based search with 6-hour TTL
- ✅ **Minimal overhead** - Direct httpx calls, no SDK
- ✅ **Improved Context** - Agent reads ~half as much context as the MCP Server

**Architecture:**
```
Claude → subprocess → CLI (13 commands) → Direct HTTP → Kalshi API
```

**Key files:**
- `kalshi_cli/cli.py` - All 13 commands (552 lines)
- `kalshi_cli/modules/client.py` - HTTP client & search cache
- `kalshi_cli/modules/formatting.py` - Output formatters

**When to use:** Need direct API control, want both CLI and programmatic access, caching important, okay with subprocess overhead.

---

### 3. File System Scripts (`apps/3_file_system_scripts/`)

**Progressive disclosure via standalone scripts**

- ✅ **Progressive disclosure** - Only load scripts you need (~200-300 lines each)
- ✅ **Complete isolation** - Each script is fully self-contained
- ✅ **Zero dependencies** - HTTP client embedded in each script
- ✅ **Context efficient** - Agent only reads relevant scripts
- ⚠️ **Code duplication** - HTTP client repeated in each script
- ⚠️ **No shared state** - Cache and utilities duplicated

**Architecture:**
```
Claude → Read tool → Individual script → Embedded HTTP client → Kalshi API
```

**Available scripts (10):**
- `status.py` - Exchange operational status
- `markets.py` - Browse markets with filters
- `market.py` - Detailed market information
- `orderbook.py` - Bid/ask depth
- `trades.py` - Recent trading activity
- `search.py` - Keyword search (with caching)
- `events.py` - List event collections
- `event.py` - Event details
- `series_list.py` - Browse all ~6900 series
- `series.py` - Series information

**When to use:** Context preservation critical, want progressive disclosure, okay with code duplication, need standalone portability.

---

### 4. Skill (`apps/4_skill/.claude/skills/kalshi-markets/`)

**Claude Code Agent Skills with embedded scripts**

- ✅ **Model-invoked** - Claude autonomously decides when to use
- ✅ **Progressive disclosure** - Same scripts as approach #3
- ✅ **Team sharing** - Commit to git for team access
- ✅ **Discovery** - Description triggers automatic activation
- ✅ **Context preservation** - Agent reads only what's needed
- ⚠️ **Claude Code specific** - Only works in Claude Code
- ⚠️ **Learning curve** - Requires understanding Skill system

**Architecture:**
```
Claude (detects trigger) → Loads SKILL.md → Runs scripts → Kalshi API
```

**Structure:**
```
.claude/skills/kalshi-markets/
├── SKILL.md (concise description & instructions)
└── scripts/ (copies of all 10 file system scripts)
```

**When to use:** Using Claude Code, want automatic skill discovery, team collaboration via git, need context preservation with progressive disclosure.

---

## My Approach ([IndyDevDan](https://www.youtube.com/@indydevdan))

### External Tools

1. 80% Just use **MCP servers**. Don't overthink it.
2. 15% **CLI** - If you need modify, extend, or control tools and context.
3. 5% **Scripts or Skills** - For serious context preservation, portability or ecosystem reuse

### New Tools

1. 80% Just use **CLI** + Prime Prompt (works for you, your team and your agents).
2. 10% Wrap in **MCP Server** when I need multiple agents at scale - and don't want to add 'another' thing for my agents to focus on.
3. 10% **Scripts or Skills** - For serious context preservation, portability or ecosystem reuse.

## Key Technical Details

**API Access:**
- Base URL: `https://api.elections.kalshi.com/trade-api/v2`
- No authentication required (read-only public data)
- ~6900 market series available

**Search Caching:**

The Kalshi API doesn't provide a native search endpoint, which creates a challenge for finding markets by keyword. Our solution: intelligent local caching.

- **The Problem:** No API search endpoint means we'd need to paginate through thousands of markets on every search
- **The Solution:** Build a complete local cache once, then search instantly using pandas
- **First run:** 2-5 minutes to fetch all ~6900 markets and build cache
- **Subsequent searches:** Instant (searches cached pandas DataFrame)
- **Cache location:** `.kalshi_cache/` at project root (shared across CLI and scripts)
- **TTL:** 6 hours (auto-refresh when stale)
- **Search scope:** Searches titles, subtitles, tickers, series names, and descriptions

**Why the delay matters:**
- First search in a session will take 2-5 minutes while the cache builds
- Users will see progress messages during cache building
- After initial build, searches are instant for 6 hours
- This trade-off enables comprehensive keyword search across ALL markets instead of just the first 100-500 results from paginated API calls

**Path Resolution:**
- All scripts use absolute path resolution via `Path(__file__).resolve()`
- Works correctly when invoked from any directory
- Cache always resolves to project root

## Trade-off Comparison

|                                | MCP                                                                              | CLI                            | Scripts                        | Skills                            |
| ------------------------------ | -------------------------------------------------------------------------------- | ------------------------------ | ------------------------------ | --------------------------------- |
| **Agent Invoked**              | Yes                                                                              | No                             | No                             | Yes                               |
| **Context Window Consumption** | High                                                                             | Medium (Depends)               | Low (w/incr)                   | Low (w/incr)                      |
| **Customizable**               | No (unless you own)                                                              | Yes                            | Yes                            | Yes                               |
| **Portability**                | Low                                                                              | Medium                         | High                           | High                              |
| **Composability**              | Yes (MCP Prompts)                                                                | Yes but requires local prompts | Yes but requires local prompts | Yes but requires local prompts    |
| **Simplicity**                 | High                                                                             | Medium                         | Medium                         | Medium                            |
| **Engineering Investment**     | Low if external, Medium if custom                                                | Medium                         | Medium                         | Low if external, Medium if custom |
| **Feature Set**                | Tools, Resources, Prompts, Elicitation, Completion, Sampling, Logging, Auth. etc | Whatever you build             | Whatever you build             | Whatever you build                |

### Key Insights

**Context Window Consumption:**
- **MCP & CLI** consume full context on every tool call
- **Scripts & Skills** use progressive disclosure - only load what's needed

**Agent Invoked:**
- **MCP & Skills** are automatically triggered by Claude based on context
- **CLI & Scripts** require explicit agent decision to use

**Customizable:**
- **MCP** is locked unless you own/fork the server
- **CLI, Scripts, Skills** are fully under your control

**Portability:**
- **Scripts & Skills** are most portable (just Python files)
- **CLI** requires installation but works anywhere
- **MCP** needs MCP-compatible client setup

## When to Use Each Approach

### Choose MCP Server if:
- Building for multiple LLM clients (not just Claude)
- Need standardized tool protocol
- Context loss per call is acceptable
- Want automatic tool discovery across clients
- Using external MCP servers you don't control

### Choose CLI if:
- Need both human CLI and programmatic access
- Want single source of truth for API logic
- Direct HTTP control is important
- Willing to accept subprocess overhead
- Building general-purpose tooling

### Choose File System Scripts if:
- Context preservation is critical
- Want maximum portability (just Python + httpx)
- Need progressive disclosure (minimize token usage)
- Okay with code duplication for isolation
- Building one-off integrations

### Choose Skill if:
- Using Claude Code (and the ecosystem) specifically
- Want autonomous skill discovery
- Team collaboration via git is important
- Need context preservation + progressive disclosure
- Building reusable team capabilities

## Project Structure

```
beyond-mcp/
├── apps/
│   ├── 1_mcp_server/          # MCP Server implementation
│   │   ├── server.py           # 15 MCP tools wrapping CLI
│   │   └── README.md
│   ├── 2_cli/                  # CLI implementation
│   │   ├── kalshi_cli/
│   │   │   ├── cli.py          # 13 commands (552 lines)
│   │   │   └── modules/        # HTTP client, cache, formatters
│   │   └── README.md
│   ├── 3_file_system_scripts/  # Progressive disclosure scripts
│   │   ├── scripts/            # 10 standalone scripts
│   │   │   ├── status.py
│   │   │   ├── markets.py
│   │   │   ├── market.py
│   │   │   ├── orderbook.py
│   │   │   ├── trades.py
│   │   │   ├── search.py
│   │   │   ├── events.py
│   │   │   ├── event.py
│   │   │   ├── series_list.py
│   │   │   └── series.py
│   │   └── README.md
│   └── 4_skill/                # Claude Code Skill
│       └── .claude/skills/kalshi-markets/
│           ├── SKILL.md        # Skill description & instructions
│           └── scripts/        # Same 10 scripts as #3
└── .kalshi_cache/              # Shared cache directory (CLI & scripts)
```


## Resources

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
- [Kalshi API Documentation](https://docs.kalshi.com/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)


## Master **Agentic Coding**
> Prepare for the future of software engineering

Learn tactical agentic coding patterns with [Tactical Agentic Coding](https://agenticengineer.com/tactical-agentic-coding?y=byndmcp).

Follow the [IndyDevDan YouTube channel](https://www.youtube.com/@indydevdan) to improve your agentic coding advantage.
