# README Guide

Principles and patterns for writing effective README files. Synthesized from research on developer-facing open-source projects (Oh My Zsh, HTTPie, Glow, shadcn/ui, Homebrew, nvm) and developer documentation best practices.

---

## Core Principles

1. **The README is a storefront, not a manual.** It answers three questions in 30 seconds: What is this? Why should I care? How do I start? Everything else links out.

2. **Show, don't claim.** Developers distrust vague promises. Instead of "saves you hours," show a workflow that obviously saves time. Let the reader draw their own conclusions.

3. **Write like a knowledgeable colleague.** Not a marketer, not a professor. Conversational, direct, technically precise, and respectful of the reader's time.

4. **Progressive disclosure.** Front-load the most important information. Push complexity into later sections, collapsible blocks, or linked docs.

5. **Benefits are implicit in examples.** Rather than stating "improves your productivity," show the tool doing something useful in three lines. The value should be self-evident.

6. **Scanability is non-negotiable.** Engineers scan, they don't read. Short paragraphs (2-3 sentences max), headers as signposts, tables for comparisons, code blocks for anything executable.

7. **The top 20% is the pitch.** Everything above the installation section should work as a standalone pitch. Everything below is reference material for people already convinced.

---

## Recommended Structure

```
# Project Name
> One-line tagline: names the category and key differentiator

## What This Is
2-3 sentences. What it does, who it's for, what problem it solves.

## What's Included (for collections) / Features (for single tools)
Scannable table or categorized list.
Group by use case, not alphabetically.
Format: Name | What it does | When to use it

## Quick Start / Install
Fastest path to a working result. Copy-paste ready.

## Usage Examples (if not covered above)
2-3 concrete examples showing different interaction patterns (not exhaustive coverage).

## Configuration / Setup (if needed)
Only what's required. Link to full docs for advanced config.

## Updating
How to get new versions. Cover each install mode separately if they differ.

## Uninstalling
How to remove. State what it does and does not touch (e.g. "removes only toolkit files").

## Contributing (if applicable)
Brief guidance or link to CONTRIBUTING.md.

## License
One line with link.
```

### Structural Decisions

**Tables vs lists vs prose:**
- Tables for comparing items (features, commands, options with multiple attributes)
- Bullet lists for enumerating items with one attribute each
- Prose only for narrative context (the "What This Is" section)

**Collapsible sections** (`<details>`) for:
- Platform-specific installation variants
- Advanced configuration
- Edge case behaviors (conflict resolution, force overwrite flags)
- Anything useful to 20% of readers but noise for the other 80%

**Inline vs standalone:** If a caveat or limitation is 1-2 sentences, merge it into the relevant section (e.g. scope caveats into "What This Is"). Don't create a standalone section for a single sentence.

**Badges:** 3-5 max. Build status, version, license. More than that signals insecurity, not quality.

---

## Tone Guidelines

### Target Voice

Senior engineer explaining their tool to a peer. Confident without being boastful, specific without being exhaustive.

### Do

| Principle | Example |
|-----------|---------|
| State facts, let value be obvious | "Generates type-safe API clients from OpenAPI specs in under 5 seconds." |
| Use second person, active voice | "Run the command to install the skill into your project." |
| Be specific, not superlative | "Reduces boilerplate by eliminating manual model mapping." |
| Acknowledge tradeoffs honestly | "Optimized for speed over flexibility — if you need custom X, see alternatives." |
| Show personality through brevity | "No config files. No build step. Just works." |

### Don't

| Anti-pattern | Example | Why it fails |
|--------------|---------|--------------|
| Hype language | "Revolutionary AI-powered developer experience!" | Triggers immediate skepticism |
| Vague benefits | "Improve your workflow and boost productivity" | Says nothing concrete |
| Condescending simplifiers | "Simply run the command" / "It's easy" | Implies the reader is foolish if they struggle |
| Overly formal | "The aforementioned utility enables acquisition of..." | Creates distance, wastes time |
| Excessive punctuation | "Check out these amazing features!!!" | Reads as desperate |

### Word Choice

**Avoid:** "supercharge," "streamline," "empower," "leverage," "seamlessly," "next-generation," "enterprise-grade," "cutting-edge"

**Prefer:** "automate," "generate," "skip," "replace," "handle," "check," "run"

**Framing:** Describe what each tool *does* (verb-oriented), not what it *is* (noun-oriented). Frame around developer agency: "Use this to..." not "This will make you..."

### The Google Calibration Test

- Too informal: "Dude! This API is totally awesome!"
- Just right: "This API lets you collect data about what your users like."
- Too formal: "The API documented by this page may enable the acquisition of information pertaining to user preferences."

---

## Installation Section

### Formatting Rules

- **No `$` prefix** in code blocks — prevents clean copy-paste.
- **One logical action per code block** so each block is independently copy-pasteable.
- **State prerequisites before the install command**, not after. Only list prerequisites that aren't obvious or that the user might not have. Don't specify version numbers unless enforced in code.
- Use `bash` syntax highlighting on fenced code blocks.

### Multiple Installation Paths

Present from most common to most specialized. Use clear headers and explain when to use each:

```markdown
### Quick Install (recommended)

One-liner description of what this does.

\```bash
curl -fsSL https://example.com/install.sh | bash
\```

### Via Homebrew

\```bash
brew install toolname
\```

### Manual Installation

<details>
<summary>Click to expand</summary>

Step-by-step for edge cases...

</details>
```

### Scoped Installation (User vs Project)

When the tool supports different scopes, explain the tradeoff upfront:

```markdown
**User scope** — available across all your projects, only on your machine.

\```bash
install-command --user
\```

**Project scope** — shared with your team via version control.

\```bash
install-command --project
\```
```

### Symlinks vs Copies

- **Symlinks** for personal/user scope: auto-update when the source changes
- **Copies** for shared/project scope: won't break for other team members, but need manual re-copy to update

Note the tradeoff explicitly so users understand why each approach is used.

---

## Presenting Collections

When the README covers multiple tools, commands, or features, discoverability is the main challenge. The reader needs to scan the collection and find the 1-2 things relevant to their current need.

### Use Three-Column Tables

```markdown
| Tool | What it does | When to use it |
|------|-------------|----------------|
| `tool-a` | Verb-first description of action | Concrete trigger scenario |
| `tool-b` | Verb-first description of action | Concrete trigger scenario |
```

The "When to use it" column is what makes a collection useful. Without it, the reader has to read each tool's full documentation to know if it's relevant.

### Group by Use Case

Don't alphabetize — group by workflow or problem domain. A developer looking for "something to help with code review" will scan category headers, not an alphabetical list.

### Workflow Sections — Use Sparingly

If the collection section already has "when to use" triggers for each item, a workflow section often restates it. Only add one when it reveals non-obvious connections between tools that aren't apparent from the individual descriptions:

```markdown
## How These Fit Together

**Writing code:** Use X after implementing, then Y before merging.
**Reviewing code:** Run Z to catch issues A does not cover.
```

If you find yourself just listing the tools in sequential order, the workflow section is redundant — cut it.

---

## Common Pitfalls

1. **Wall of text at the top.** If the first three paragraphs are prose, most readers are gone. Lead with a one-liner, then a code block or table.

2. **Feature lists without context.** "Supports X, Y, Z" means nothing without showing when and why to use each. Pair features with use cases.

3. **Assuming the reader already cares.** Answer "why should I use this?" before "how do I use this?"

4. **Burying the quick start.** If the reader scrolls past a table of contents, feature matrix, philosophy section, and architecture diagram before finding how to install, the README has failed.

5. **Using "simply" or "just."** These words imply the step is trivial. If it were, the reader wouldn't need documentation. Drop them entirely.

6. **Stale content.** Outdated installation commands or broken links erode trust faster than anything. Keep installation instructions tested.

7. **Marketing language.** Developers have finely tuned BS detectors. State what the tool does concretely.

8. **Not saying when NOT to use it.** Honest scoping builds trust. "If you need X, check out Y" makes people trust your recommendations for when your tool *is* appropriate.

9. **Documenting the self-evident.** Don't tell users `--help` exists or that they can read the source code. Every line should earn its place.

10. **Usage examples that repeat patterns.** Three examples showing different interaction styles (natural language prompt, targeted command, slash command) are better than four where the last one demonstrates the same pattern as the third. Each example should reveal something new.

11. **No subtraction pass.** After writing, re-read and ask "does removing this lose information?" for every section. Workflow sections, closing summaries, and scope sections often restate what's already covered. If a section's content already lives elsewhere in the README, cut the section.

---

## Reference READMEs

### [Oh My Zsh](https://github.com/ohmyzsh/ohmyzsh)
Masters progressive disclosure and personality. Opens with a self-aware joke, provides multiple installation paths, manages a massive plugin/theme collection in a scannable way. The tone is fun without being unprofessional.

**Steal:** How it balances humor with utility. How it handles a large collection with categorized lists.

### [HTTPie CLI](https://github.com/httpie/cli)
Clean visual hierarchy, concise self-description ("human-friendly"), progressive code examples from simple to complex, strategic linking to full docs.

**Steal:** Features as a bulleted list of verb phrases. Examples progressing from basic to advanced.

### [Glow](https://github.com/charmbracelet/glow)
Animated GIF demo at the top immediately shows value. Crisp one-line description. Handles 13+ installation methods without overwhelming by grouping them logically.

**Steal:** Visual-first approach. Installation methods organized by platform. The broader Charm org is worth studying for how to present a collection of related tools with consistent tone.
