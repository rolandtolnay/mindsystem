# GSD Patterns for Multi-Command Pipelines

A distillation of the 20% of GSD patterns that deliver 80% of value for building multi-step processing pipelines with Claude Code.

---

## Core Philosophy

### The Problem: Context Rot

Claude's output quality degrades predictably as context fills:
- **0-30%**: Peak quality
- **30-50%**: Good quality
- **50-70%**: Degrading ("I'll be more concise" = cutting corners)
- **70%+**: Poor quality, errors, hallucinations

**The 50% Rule**: Tasks should complete within ~50% context usage. Stop BEFORE quality degrades.

### The Solution: Aggressive Atomicity

1. **Small execution units** — Each command does ONE thing well
2. **Fresh context per unit** — Subagents get full 200k tokens
3. **State persisted externally** — Not in Claude's context window
4. **Plans ARE prompts** — Executable, not documents to transform

---

## Pattern 1: External State Management

### Why It Matters

Claude's context is volatile. Between commands, between sessions, context is lost. External state files are your persistent memory.

### Implementation

Create a `.pipeline/` directory (or similar) with:

```
.pipeline/
├── STATE.md           # Living memory - where are we?
├── CONFIG.json        # Execution preferences
├── steps/             # Per-step artifacts
│   ├── 01-extract/
│   │   ├── PLAN.md    # What to do
│   │   └── SUMMARY.md # What happened
│   ├── 02-transform/
│   └── 03-load/
└── data/              # Pipeline data between steps
    ├── raw/           # Step 1 output
    ├── processed/     # Step 2 output
    └── final/         # Step 3 output
```

### STATE.md Template

```markdown
# Pipeline State

## Current Position
Step: [X] of [Y] ([step name])
Status: [Ready / In progress / Complete / Failed]
Last activity: [YYYY-MM-DD] — [What happened]

Progress: [████████░░] 80%

## Data Locations
- Raw data: .pipeline/data/raw/
- Processed: .pipeline/data/processed/
- Output: .pipeline/data/final/

## Accumulated Context

### Decisions
- [Step X]: [Decision and rationale]

### Blockers
- [Issue description and how to resolve]

## Last Run
Started: [ISO timestamp]
Completed: [ISO timestamp]
Duration: [time]
Records processed: [count]
```

### Key Insight

**Read STATE.md first in every command.** This single file provides instant context restoration.

---

## Pattern 2: Plans as Executable Prompts

### Why It Matters

A PLAN.md isn't documentation — it's the exact prompt that drives execution. Claude reads it and knows precisely what to do.

### PLAN.md Structure

```markdown
---
step: 01-extract
type: execute
depends_on: []
output: .pipeline/data/raw/
---

<objective>
Extract product data from [source] and save as structured JSON.

Purpose: Gather raw data for transformation pipeline
Output: JSON files in .pipeline/data/raw/
</objective>

<context>
@.pipeline/STATE.md
@.pipeline/CONFIG.json
</context>

<tasks>
<task type="auto">
  <name>Task 1: Authenticate and fetch data</name>
  <files>.pipeline/data/raw/products-{date}.json</files>
  <action>
    1. Load API credentials from CONFIG.json
    2. Fetch all products from /api/products endpoint
    3. Handle pagination (100 items/page)
    4. Save raw response to output file

    Do NOT transform data — that's step 2.
    Do NOT skip failed pages — log and continue.
  </action>
  <verify>
    - File exists: .pipeline/data/raw/products-{date}.json
    - JSON is valid: cat file | jq '.' > /dev/null
    - Has records: jq '.items | length' returns > 0
  </verify>
  <done>Raw JSON file exists with valid product data</done>
</task>
</tasks>

<verification>
- [ ] Output file exists and is valid JSON
- [ ] STATE.md updated with completion
- [ ] No unhandled errors in logs
</verification>

<success_criteria>
- Raw data extracted and saved
- STATE.md reflects completion
- Ready for step 2
</success_criteria>
```

### Task Anatomy

Every task needs four fields:

| Field | Purpose | Example |
|-------|---------|---------|
| `<files>` | Exact paths affected | `.pipeline/data/raw/out.json` |
| `<action>` | Specific steps, including what NOT to do | "Fetch data. Do NOT transform." |
| `<verify>` | Executable verification | `cat file \| jq '.' > /dev/null` |
| `<done>` | Measurable completion | "File exists with >0 records" |

### Anti-Patterns

**Vague actions:**
- "Fetch the data" ❌
- "Handle edge cases" ❌
- "Make it robust" ❌

**Good actions:**
- "Fetch from /api/products, paginate at 100/page, save to X" ✓
- "If status != 200, log error and continue to next page" ✓
- "Retry failed requests 3x with exponential backoff" ✓

---

## Pattern 3: Subagent Orchestration

### Why It Matters

Main context orchestrates. Subagents execute. This keeps orchestrator lean (~10% context) while execution gets fresh context.

### Orchestrator Pattern

```
Orchestrator (main context):
├── Read STATE.md
├── Identify next step
├── Spawn subagent with PLAN.md
├── Wait for completion
├── Read SUMMARY.md
├── Update STATE.md
└── Route to next step or completion
```

### Subagent Prompt Template

```
<objective>
Execute step {step_number}: {step_name}
</objective>

<execution_context>
@.pipeline/workflows/execute-step.md
</execution_context>

<context>
Plan: @.pipeline/steps/{step}/PLAN.md
State: @.pipeline/STATE.md
Config: @.pipeline/CONFIG.json
</context>

<success_criteria>
- [ ] All tasks executed
- [ ] Verification checks pass
- [ ] SUMMARY.md created
- [ ] STATE.md updated
</success_criteria>
```

### Benefits

- **Fresh context**: Each subagent starts at 0%
- **Parallel execution**: Independent steps run simultaneously
- **Fault isolation**: One failure doesn't corrupt orchestrator
- **Clear handoff**: SUMMARY.md captures what happened

---

## Pattern 4: Wave-Based Parallelization

### Why It Matters

Some steps depend on others. Some don't. Run independent steps in parallel, dependent steps in sequence.

### Wave Assignment

During planning, assign each step a wave number:

```yaml
# Step frontmatter
---
step: 01-fetch-products
wave: 1
depends_on: []
---

---
step: 02-fetch-inventory
wave: 1                    # Same wave = parallel
depends_on: []
---

---
step: 03-merge-data
wave: 2                    # After wave 1
depends_on: [01-fetch-products, 02-fetch-inventory]
---
```

### Execution

```
Wave 1: [01-fetch-products, 02-fetch-inventory] → run in parallel
Wave 2: [03-merge-data] → run after wave 1 completes
Wave 3: [04-transform] → run after wave 2 completes
```

### Implementation

Orchestrator spawns multiple Task tool calls in a single message for parallel execution:

```
Task(prompt="Execute step 01...", subagent_type="pipeline-executor")
Task(prompt="Execute step 02...", subagent_type="pipeline-executor")
# Both run simultaneously
```

---

## Pattern 5: Checkpoints and Error Recovery

### Checkpoint Types

| Type | When to Use | Example |
|------|-------------|---------|
| `auto` | Claude can do autonomously | API calls, transforms, file ops |
| `checkpoint:human-verify` | Human must verify result | Visual review, quality check |
| `checkpoint:human-action` | Only human can do | 2FA, email verification |
| `checkpoint:decision` | Human must choose | "Use API v1 or v2?" |

### Error Handling Rules

**Auto-fix rules** (no permission needed):

1. **Bugs** — Fix broken code immediately
2. **Missing critical** — Add error handling, validation
3. **Blockers** — Install deps, fix config

**Ask rules** (need human input):

4. **Architectural changes** — Different API, new service, schema changes

### Checkpoint Return Format

When subagent hits a checkpoint, return structured state:

```markdown
## CHECKPOINT REACHED

**Type:** human-action
**Step:** 01-extract
**Progress:** 2/3 tasks complete

### Completed Tasks

| Task | Name | Output |
|------|------|--------|
| 1 | Fetch products | 1,234 records |
| 2 | Fetch categories | 56 records |

### Current Task

**Task 3:** Upload to storage
**Blocked by:** S3 authentication required

### What You Need To Do

1. Run: `aws configure`
2. Enter credentials when prompted

### Awaiting

Type "done" when authenticated.
```

### Resumption

After checkpoint resolved, spawn fresh continuation agent:

```
<completed_tasks>
| Task | Name | Output |
| 1 | Fetch products | .pipeline/data/raw/products.json |
| 2 | Fetch categories | .pipeline/data/raw/categories.json |
</completed_tasks>

<resume_from>
Task 3: Upload to storage
User response: "done" (authenticated)
</resume_from>

Continue execution from task 3.
```

---

## Pattern 6: SUMMARY.md as Execution Record

### Why It Matters

SUMMARY.md captures what actually happened, enabling:
- Debugging (what went wrong?)
- Resumption (where did we stop?)
- Auditability (what was processed?)

### Template

```markdown
---
step: 01-extract
completed: 2025-01-20
duration: 12min
---

# Step 01: Extract Summary

**Extracted 1,234 products from API in 12 minutes**

## Performance
- **Duration:** 12 min
- **Records:** 1,234 products
- **Pages:** 13 API calls
- **Rate:** 103 records/min

## Output Files
- `.pipeline/data/raw/products-2025-01-20.json` — 2.3 MB

## Deviations
### Auto-fixed Issues

**1. [Rule 3 - Blocking] Rate limit hit**
- **Issue:** 429 response on page 8
- **Fix:** Added 2-second delay between requests
- **Impact:** Increased duration by ~30s

## Issues
- None

## Next Step Readiness
- Data extracted, ready for step 02 (transform)
- No blockers
```

---

## Pattern 7: Data Persistence Between Steps

### File-Based Data Flow

```
Step 1 (Extract):
  Output: .pipeline/data/raw/products.json

Step 2 (Transform):
  Input:  .pipeline/data/raw/products.json
  Output: .pipeline/data/processed/products-clean.json

Step 3 (Load):
  Input:  .pipeline/data/processed/products-clean.json
  Output: Database / API / Final destination
```

### Plan References

In PLAN.md, reference data explicitly:

```markdown
<context>
Input data: @.pipeline/data/raw/products.json
Schema: @.pipeline/schemas/product.schema.json
</context>

<task type="auto">
  <name>Transform product data</name>
  <files>.pipeline/data/processed/products-clean.json</files>
  <action>
    Read: .pipeline/data/raw/products.json
    Transform:
    - Normalize prices to USD
    - Strip HTML from descriptions
    - Validate against schema
    Write: .pipeline/data/processed/products-clean.json
  </action>
</task>
```

### Validation

Each step should validate its input:

```markdown
<task type="auto">
  <name>Validate input data</name>
  <action>
    1. Check input file exists
    2. Validate JSON structure
    3. Check required fields present
    4. Log validation errors, continue with valid records
  </action>
  <verify>
    - Input file exists
    - JSON is valid
    - At least 1 valid record
  </verify>
</task>
```

---

## Pattern 8: Command Interface Design

### Command Structure

```yaml
---
name: pipeline:extract
description: Extract data from source
argument-hint: "[source-url]"
allowed-tools: [Read, Write, Bash, Glob, Grep, WebFetch]
---

<objective>
Extract data from [source] and save to .pipeline/data/raw/
</objective>

<process>
<step name="load_state">
Read .pipeline/STATE.md for current position.
</step>

<step name="validate_input">
Check source URL is valid and accessible.
</step>

<step name="execute">
Spawn extraction subagent with PLAN.md.
</step>

<step name="update_state">
Update STATE.md with completion.
</step>

<step name="offer_next">
Suggest next command: /pipeline:transform
</step>
</process>
```

### Command Chaining

Commands should naturally lead to the next:

```
/pipeline:extract [url]
  → "Extraction complete. Run `/pipeline:transform` to continue."

/pipeline:transform
  → "Transformation complete. Run `/pipeline:load` to continue."

/pipeline:load
  → "Pipeline complete! 1,234 records processed."
```

### Progress Command

Essential for resumption:

```
/pipeline:progress
  → Shows: Current step, what's done, what's next
  → Routes to: appropriate next command
```

---

## Pattern 9: Configuration Management

### CONFIG.json Structure

```json
{
  "pipeline": {
    "name": "product-sync",
    "version": "1.0"
  },
  "sources": {
    "api": {
      "base_url": "https://api.example.com",
      "rate_limit": 100,
      "timeout": 30
    }
  },
  "destinations": {
    "database": {
      "connection_string": "${DATABASE_URL}"
    }
  },
  "execution": {
    "mode": "interactive",
    "parallel_steps": true,
    "retry_count": 3
  }
}
```

### Environment Variables

Reference env vars with `${VAR_NAME}` syntax:
- Never commit secrets
- Document required vars in README
- Validate presence before execution

---

## Pattern 10: The /progress Pattern

### Why It Matters

Users come back after breaks. They need instant context restoration.

### Implementation

```
/pipeline:progress

# Product Sync Pipeline

**Progress:** [████████░░] 2/3 steps complete

## Recent Activity
- Step 1 (Extract): 1,234 products fetched
- Step 2 (Transform): 1,198 valid records

## Current Position
Step: 3 of 3 (Load)
Status: Ready to execute

## What's Next
Load processed data to database.

---

## ▶ Next Up

`/pipeline:load`
```

### Routing Logic

```
IF unexecuted step exists:
  → Suggest /pipeline:execute-step [N]
ELIF current step failed:
  → Suggest /pipeline:retry [N]
ELIF all steps complete:
  → Show completion summary
ELSE:
  → Suggest /pipeline:plan-step [next]
```

---

## Quick Reference: File Structure

```
.pipeline/
├── STATE.md              # Where are we?
├── CONFIG.json           # How do we run?
├── steps/
│   ├── 01-extract/
│   │   ├── PLAN.md       # What to do
│   │   └── SUMMARY.md    # What happened
│   ├── 02-transform/
│   │   ├── PLAN.md
│   │   └── SUMMARY.md
│   └── 03-load/
│       └── PLAN.md
├── data/
│   ├── raw/              # Step 1 output
│   ├── processed/        # Step 2 output
│   └── final/            # Step 3 output
└── logs/
    └── 2025-01-20.log
```

---

## Quick Reference: Task Template

```xml
<task type="auto">
  <name>Task N: [Action-oriented name]</name>
  <files>[exact paths]</files>
  <action>
    1. [Specific step]
    2. [Specific step]

    Do NOT: [anti-pattern to avoid]
    If [error condition]: [how to handle]
  </action>
  <verify>
    - [executable check 1]
    - [executable check 2]
  </verify>
  <done>[measurable completion criteria]</done>
</task>
```

---

## Quick Reference: Subagent Prompt

```
<objective>
Execute step {N}: {name}
</objective>

<context>
Plan: @.pipeline/steps/{N}/PLAN.md
State: @.pipeline/STATE.md
Prior output: @.pipeline/data/{prior-step}/
</context>

<success_criteria>
- [ ] All tasks complete
- [ ] Output files created
- [ ] SUMMARY.md written
- [ ] STATE.md updated
</success_criteria>
```

---

## Applying to Web Scraping

### Recommended Step Structure

```
.pipeline/
├── steps/
│   ├── 01-discover/      # Find URLs to scrape
│   ├── 02-fetch/         # Download pages (Firecrawl/etc)
│   ├── 03-extract/       # Parse HTML → structured data
│   ├── 04-validate/      # Check data quality
│   └── 05-store/         # Save to database/API
```

### Firecrawl Integration

```xml
<task type="auto">
  <name>Task 1: Fetch pages with Firecrawl</name>
  <files>.pipeline/data/raw/pages-{date}.json</files>
  <action>
    Use Firecrawl API to fetch URLs from .pipeline/data/urls.txt

    Configuration:
    - Format: markdown (for clean text)
    - Include metadata: title, description
    - Handle rate limits: 10 requests/minute

    On error: Log URL and continue
  </action>
  <verify>
    - Output file exists
    - JSON valid: jq '.' < file
    - At least 80% success rate
  </verify>
  <done>Pages fetched with metadata preserved</done>
</task>
```

### Data Persistence Strategy

For scraping, persist:
1. **URLs to scrape** → `.pipeline/data/urls.txt`
2. **Raw HTML/markdown** → `.pipeline/data/raw/`
3. **Extracted data** → `.pipeline/data/extracted/`
4. **Validated data** → `.pipeline/data/validated/`
5. **Load results** → `.pipeline/data/loaded/`

### Error Recovery

Scraping is error-prone. Build recovery into plans:

```xml
<task type="auto">
  <name>Task 2: Resume from last position</name>
  <action>
    1. Read .pipeline/STATE.md for last processed URL index
    2. Skip already-fetched URLs
    3. Continue from position N
    4. Update STATE.md with new position after each batch
  </action>
</task>
```

---

## Key Takeaways

1. **Context is precious** — Keep orchestrator lean, delegate to subagents
2. **State lives in files** — STATE.md is your persistent memory
3. **Plans are prompts** — Make them executable, not vague
4. **Tasks need all four fields** — files, action, verify, done
5. **Parallel what's independent** — Wave-based execution
6. **Checkpoint for humans** — Only when truly needed
7. **SUMMARY captures truth** — What actually happened
8. **Progress enables resumption** — Always know where you are
9. **Data flows through files** — Clear input/output per step
10. **Commands chain naturally** — Each suggests the next
