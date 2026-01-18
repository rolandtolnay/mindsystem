# Migration Guide: Research Features from v1.6.x

This guide migrates two research improvements from v1.6.x to your v1.5.17 fork:

1. **CONTEXT.md Integration** - Researchers respect discuss-phase decisions
2. **Research Synthesizer** - Atomic commits and unified summaries for project research

---

## Why These Features Matter

### CONTEXT.md Integration

In v1.5.17, `/gsd:discuss-phase` creates a CONTEXT.md file with user decisions, but the researcher agent doesn't formally consume it. The researcher might waste context exploring alternatives to decisions the user already locked.

**After migration:** The researcher reads CONTEXT.md and:
- Researches locked decisions deeply (not alternatives)
- Explores options only for "Claude's Discretion" items
- Ignores "Deferred Ideas" entirely

### Research Synthesizer

In v1.5.17, `/gsd:research-project` spawns 4 parallel `gsd-researcher` agents. Each writes and commits its own file independently. This can result in:
- Multiple separate commits instead of one atomic commit
- No unified summary connecting the research files
- No roadmap implications derived from combined findings

**After migration:** A synthesizer agent:
- Reads all 4 research outputs
- Creates SUMMARY.md with roadmap implications
- Commits everything atomically

---

## Prerequisites

- v1.5.17 fork installed
- `gsd-researcher.md` agent exists (the original monolithic researcher)

---

## Part 1: CONTEXT.md Integration

### What Changes

Add an `<upstream_input>` section to `gsd-researcher.md` that teaches it to read and respect CONTEXT.md from discuss-phase.

### Step 1.1: Locate Your Researcher Agent

```bash
cat ~/.claude/agents/gsd-researcher.md | head -20
```

You should see the v1.5.17 researcher with description mentioning "Spawned by /gsd:research-phase and /gsd:research-project orchestrators."

### Step 1.2: Add Upstream Input Section

Open `~/.claude/agents/gsd-researcher.md` and add this section **after the `</role>` tag** and **before the `<gsd_integration>` section**:

```markdown
<upstream_input>
**CONTEXT.md** (if exists) — User decisions from `/gsd:discuss-phase`

| Section | How You Use It |
|---------|----------------|
| `## Decisions` | Locked choices — research THESE deeply, don't explore alternatives |
| `## Claude's Discretion` | Your freedom areas — research options, make recommendations |
| `## Deferred Ideas` | Out of scope — ignore completely |

If CONTEXT.md exists, it constrains your research scope. Don't waste context exploring alternatives to locked decisions.
</upstream_input>
```

### Step 1.3: Update Execution Flow

Find the `<execution_flow>` section in `gsd-researcher.md`. Locate "Step 1: Receive Research Scope" and replace it with:

```markdown
## Step 1: Receive Research Scope and Load Context

Orchestrator provides:
- Research question or topic
- Research mode (ecosystem/feasibility/implementation/comparison)
- Project context (from PROJECT.md, CONTEXT.md)
- Output file path

**Load phase context (if phase research):**

```bash
# For phase research, check for CONTEXT.md from discuss-phase
PHASE_DIR=$(ls -d .planning/phases/${PHASE}-* 2>/dev/null | head -1)
if [ -n "$PHASE_DIR" ]; then
  cat "${PHASE_DIR}"/*-CONTEXT.md 2>/dev/null
fi
```

**If CONTEXT.md exists**, parse it before proceeding:

| Section | How It Constrains Research |
|---------|---------------------------|
| **Decisions** | Locked choices — research THESE deeply, don't explore alternatives |
| **Claude's Discretion** | Your freedom areas — research options and recommend |
| **Deferred Ideas** | Out of scope — ignore completely |

**Examples:**
- User decided "use library X" → research X deeply, don't explore alternatives
- User decided "simple UI, no animations" → don't research animation libraries
- Marked as Claude's discretion → research options and recommend

Parse and confirm understanding before proceeding.
```

### Step 1.4: Verify

```bash
grep -A 10 "upstream_input" ~/.claude/agents/gsd-researcher.md
```

You should see the new section with the Decisions/Discretion/Deferred table.

---

## Part 2: Research Synthesizer Agent

### What It Does

The synthesizer is a new agent spawned after parallel project researchers complete. It:
1. Reads STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md
2. Creates SUMMARY.md with executive summary and roadmap implications
3. Commits all research files atomically

### Step 2.1: Fetch the Synthesizer Agent

```bash
curl -sL https://raw.githubusercontent.com/glittercowboy/get-shit-done/main/agents/gsd-research-synthesizer.md \
  -o ~/.claude/agents/gsd-research-synthesizer.md
```

Verify:
```bash
head -15 ~/.claude/agents/gsd-research-synthesizer.md
```

You should see:
```
---
name: gsd-research-synthesizer
description: Synthesizes research outputs from parallel researcher agents into SUMMARY.md...
tools: Read, Write, Bash
---
```

### Step 2.2: Update research-project.md Command

The command needs to spawn the synthesizer after parallel researchers complete.

Open `~/.claude/commands/gsd/research-project.md` and find where it spawns 4 parallel agents. After the parallel Task calls, add a new step:

**Add after Step 5 (Spawn Research Agents):**

```markdown
## 6. Wait for Completion and Synthesize

After all 4 agents return:

```bash
# Verify all research files exist
ls .planning/research/STACK.md .planning/research/FEATURES.md \
   .planning/research/ARCHITECTURE.md .planning/research/PITFALLS.md
```

**If any missing:** Report which agent failed, offer to retry.

**If all present:** Spawn synthesizer:

```
Task(
  prompt="
Synthesize research outputs into SUMMARY.md.

Read all 4 files in .planning/research/:
- STACK.md
- FEATURES.md
- ARCHITECTURE.md
- PITFALLS.md

Create SUMMARY.md with:
- Executive summary (2-3 paragraphs)
- Key findings from each file
- Roadmap implications (suggested phase structure)
- Confidence assessment
- Gaps to address

Then commit ALL research files together:
git add .planning/research/
git commit -m 'docs: complete project research'
",
  subagent_type="gsd-research-synthesizer",
  description="Synthesize research"
)
```

## 7. Present Results

Display SUMMARY.md highlights:
- Executive summary
- Suggested phase structure
- Research flags (which phases need deeper research)

Offer next steps: Create roadmap, View full research, Done.
```

### Step 2.3: Prevent Individual Commits (Important)

In v1.5.17, each parallel researcher commits its own output. With the synthesizer, we want atomic commits.

**Option A: Modify researcher prompts in research-project.md**

Find where you spawn the 4 parallel researchers and add this to each prompt:

```markdown
<commit_behavior>
DO NOT commit your output file. Write the file only.
The synthesizer agent will commit all research files together after all researchers complete.
</commit_behavior>
```

**Option B: Let researchers commit (simpler)**

Keep the existing behavior. The synthesizer will still create SUMMARY.md and you'll have 5 commits instead of 1. Less clean but functional.

**Recommendation:** Option A is cleaner but Option B works if you want minimal changes.

### Step 2.4: Verify Installation

```bash
# Check synthesizer exists
ls -la ~/.claude/agents/gsd-research-synthesizer.md

# Check it has correct tools
grep "^tools:" ~/.claude/agents/gsd-research-synthesizer.md
# Should show: tools: Read, Write, Bash
```

---

## Part 3: Optional - Create SUMMARY.md Template

The synthesizer references a template. Create it if you want consistent formatting:

```bash
mkdir -p ~/.claude/get-shit-done/templates/research-project
```

```bash
cat > ~/.claude/get-shit-done/templates/research-project/SUMMARY.md << 'EOF'
# Research Summary: [Project Name]

**Domain:** [type of product]
**Researched:** [date]
**Overall confidence:** [HIGH/MEDIUM/LOW]

## Executive Summary

[3-4 paragraphs synthesizing all findings]

## Key Findings

**Stack:** [one-liner from STACK.md]
**Architecture:** [one-liner from ARCHITECTURE.md]
**Critical pitfall:** [most important from PITFALLS.md]

## Implications for Roadmap

Based on research, suggested phase structure:

1. **[Phase name]** - [rationale]
   - Addresses: [features from FEATURES.md]
   - Avoids: [pitfall from PITFALLS.md]

2. **[Phase name]** - [rationale]
   ...

**Phase ordering rationale:**
- [Why this order based on dependencies]

**Research flags for phases:**
- Phase [X]: Likely needs deeper research (reason)
- Phase [Y]: Standard patterns, unlikely to need research

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | [level] | [reason] |
| Features | [level] | [reason] |
| Architecture | [level] | [reason] |
| Pitfalls | [level] | [reason] |

## Gaps to Address

- [Areas where research was inconclusive]
- [Topics needing phase-specific research later]
EOF
```

---

## Verification Checklist

After migration, verify:

- [ ] `gsd-researcher.md` has `<upstream_input>` section
- [ ] `gsd-researcher.md` execution flow loads CONTEXT.md
- [ ] `gsd-research-synthesizer.md` exists in agents/
- [ ] `research-project.md` spawns synthesizer after parallel agents
- [ ] (Optional) SUMMARY.md template exists

---

## Testing

### Test CONTEXT.md Integration

1. Run `/gsd:discuss-phase` on a phase to create CONTEXT.md with some locked decisions
2. Run `/gsd:research-phase` on the same phase
3. Verify the researcher respects locked decisions (doesn't explore alternatives)

### Test Research Synthesizer

1. Run `/gsd:research-project`
2. Verify SUMMARY.md is created with roadmap implications
3. Check git log for atomic commit of all research files

---

## Rollback

To remove these features:

```bash
# Remove synthesizer
rm ~/.claude/agents/gsd-research-synthesizer.md

# Restore original gsd-researcher.md from v1.5.17
npx get-shit-done-cc@1.5.17
# Choose to reinstall agents when prompted
```

---

## Summary

| Feature | What Changed | Benefit |
|---------|--------------|---------|
| CONTEXT.md Integration | Researcher reads discuss-phase decisions | No wasted research on locked choices |
| Research Synthesizer | New agent after parallel research | Atomic commits, unified SUMMARY.md with roadmap implications |

These are surgical additions that enhance research without changing the core v1.5.17 interactive planning workflow you prefer.
