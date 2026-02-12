---
description: Audit prompt-related file changes against the prompt quality guide
argument-hint: "[file paths...]"
allowed-tools: [Read, Grep, Glob, Bash]
---

<objective>
Audit changed prompt-related files against @references/prompt-quality-guide.md. Validates commands, workflows, agents, skills, templates, references — any file containing LLM instructions.
</objective>

<context>
**Uncommitted changes (staged + unstaged):**
!`git diff HEAD --name-only`

**Untracked files:**
!`git ls-files --others --exclude-standard`

**Target files (from arguments):** $ARGUMENTS
</context>

<process>

1. **Identify files to audit:**
   - If `$ARGUMENTS` contains file paths, use those exclusively
   - If `$ARGUMENTS` is empty, combine uncommitted + untracked files from context. If both are empty, run `git show --name-only --format="" HEAD` to get files from the last commit
   - Filter to prompt-related files — any `.md` or `.yaml` that contains LLM instructions (slash commands, workflows, agent definitions, skills, templates, references, CLAUDE.md files). When unclear, check for XML tags, YAML frontmatter, or behavioral instructions
   - If no prompt-related files found, report "No prompt-related changes detected" and stop

2. **For each file, read full content.** For uncommitted files, also run `git diff HEAD -- <file>` to isolate what changed. Focus audit on changed sections but flag pre-existing issues only if severe.

3. **Evaluate against the quality guide.** Apply The Reliability Test to each instruction. Check against the Common Waste and Common Value tables. Map findings to these categories:
   - `Budget waste` → Common Waste table (fluff, filler, verbose restatements, unlikely negations)
   - `Positioning` → Positional Attention Bias (critical constraints buried in middle, success criteria ordering)
   - `Context efficiency` → Context Is a Shared, Depletable Resource + Progressive Disclosure (eager vs lazy loading)
   - `Specificity` → Specificity Over Abstraction + Patterns and Anti-Patterns (vague instructions, missing contrastive examples)
   - `Structure` → project conventions (semantic XML tags, plan format, output format specs)

4. **Report per file:**

   ```
   ### path/to/file.md

   **N issues found**

   1. **[Category]** (line ~N): [specific issue]
      → [concrete fix: "change X to Y" or "remove this line"]

   2. ...
   ```

   Categories: `Budget waste` | `Positioning` | `Context efficiency` | `Specificity` | `Structure`

   Clean files: `**path/to/file.md** — Clean`

5. **Summary:**
   - Files audited: N
   - Findings by category (counts)
   - Top 3 highest-impact fixes

</process>

<success_criteria>
- [ ] Every finding cites a specific quality guide principle — no subjective opinions
- [ ] Suggestions are concrete ("change X to Y"), not vague ("could be improved")
- [ ] Valid patterns (peripheral reinforcement, corrective rationale, contrastive examples) not flagged as waste
</success_criteria>
