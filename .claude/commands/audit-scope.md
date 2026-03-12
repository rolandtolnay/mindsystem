---
description: Show which files changed and their token impact to prioritize prompt quality audits
argument-hint: "[commit-hash or description of changes]"
allowed-tools: [Bash, Grep, Glob, Read, AskUserQuestion]
---

<objective>
Identify files modified by a set of changes and rank them by new token volume to prioritize prompt quality audits. Output a table with total lines, total tokens, lines added, tokens added, and percentage of new content per file.
</objective>

<context>
- User input: $ARGUMENTS
- Recent commits: !`git log --oneline -15`
- Current branch: !`git branch --show-current`
</context>

<process>

1. **Determine the commit range** from `$ARGUMENTS`:
   - **Commit hash provided** (e.g., `abc1234` or `abc1234..def5678`): use it directly. A single hash means `hash~1..hash` (that one commit). A range is used as-is.
   - **Verbal description provided** (e.g., "browser verification feature"): search `git log --oneline -15` for matching commits by keywords. If multiple related commits form a contiguous group, use the full range. If the match is ambiguous, proceed to step 2.
   - **Empty / no argument**: ask the user what changes they want to audit.

2. **Confirm if ambiguous.** If the verbal description matches commits that aren't obviously related, or matches nothing, present the recent commit list and ask the user to pick the range. Use `AskUserQuestion` with concrete options.

3. **List changed files** in the resolved range:
   ```
   git diff --name-only <range>
   ```
   Exclude binary files and files that no longer exist on disk.

4. **Compute metrics** for each file. Run a single shell loop:
   - **Total lines**: `wc -l`
   - **Total tokens**: `wc -c` divided by 4 (rounded)
   - **Lines added**: count lines starting with `+` (excluding `+++` headers) from `git diff <range> -- <file>`
   - **Tokens added**: byte count of those added lines divided by 4 (rounded)
   - **% new**: tokens added / total tokens × 100

5. **Output the table** sorted by % new descending:

   ```
   | File | Lines | Tokens | Lines added | Tokens added | % new |
   ```

   Format tokens with commas for readability. Right-align numeric columns.

6. **Add a brief recommendation** after the table: which files are highest priority for prompt audit (files with high % new AND high absolute token count matter most — a 100% new file with 50 tokens is less urgent than a 40% new file with 2,000 new tokens).

</process>

<success_criteria>
1. Commit range resolved correctly — single hash, range, or keyword match — with user confirmation when ambiguous
2. Token counts use bytes/4 approximation consistently for both total and added
3. Added lines counted accurately (no off-by-one from diff headers or `+` prefixed content lines)
4. Table sorted by % new descending with readable number formatting
5. Recommendation weighs both percentage and absolute token volume
</success_criteria>
