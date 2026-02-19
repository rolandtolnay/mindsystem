# Claude Sonnet 4.6

**Source:** [Anthropic News](https://www.anthropic.com/news/claude-sonnet-4-6) | **Published:** Feb 17, 2026

Reference for LLM agents: capabilities, benchmarks, and product details of Claude Sonnet 4.6.

---

## Overview

Claude Sonnet 4.6 is Anthropic's most capable Sonnet model. Full upgrade across coding, computer use, long-context reasoning, agent planning, knowledge work, and design. Features a 1M token context window in beta.

**Availability:** Default model on [claude.ai](https://claude.ai) and [Claude Cowork](https://claude.com/product/cowork) for Free and Pro plans. Same pricing as Sonnet 4.5 (from $3/$15 per million tokens).

**Key differentiator:** Performance that previously required Opus-class models is now available with Sonnet 4.6. Major improvement in computer use skills. Developers with early access preferred it over Sonnet 4.5 by a wide margin, and often over Opus 4.5 (Nov 2025).

**Safety:** Extensive evaluations show Sonnet 4.6 as safe as or safer than recent Claude models. Character described as "broadly warm, honest, prosocial, and at times funny" with "very strong safety behaviors."

---

## Computer Use

Organizations often have software that can't be easily automated: specialized systems built before modern APIs. Sonnet 4.6 can use a computer the way a person does—clicking, typing—without bespoke connectors.

Anthropic introduced general-purpose computer use in October 2024. [OSWorld](https://os-world.github.io/), the standard benchmark, tests hundreds of tasks across real software (Chrome, LibreOffice, VS Code) on a simulated computer. No special APIs; the model sees and interacts with the computer like a human.

Sonnet models have made steady OSWorld gains over sixteen months. Early Sonnet 4.6 users report human-level capability in tasks like navigating complex spreadsheets and multi-step web forms across browser tabs. The model still lags behind the most skilled humans, but progress is substantial.

*Benchmark note: Scores prior to Sonnet 4.5 use original OSWorld; from 4.5 onward use OSWorld-Verified (July 2025 upgrade).*

**Prompt injection resistance:** Computer use poses risks (e.g., hidden instructions on websites). Sonnet 4.6 shows major improvement over 4.5 in resistance to prompt injections, performing similarly to Opus 4.6. See [API docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks) for mitigation guidance.

---

## Evaluation and Benchmarks

Sonnet 4.6 approaches Opus-level intelligence at a more practical price. Full capabilities and safety behavior in the [system card](https://anthropic.com/claude-sonnet-4-6-system-card).

### Claude Code (Coding)

- Users preferred Sonnet 4.6 over 4.5 ~70% of the time
- More effective at reading context before modifying code
- Consolidates shared logic instead of duplicating it
- Less frustrating over long sessions

Compared to Opus 4.5 (Nov 2025 frontier model):
- Users preferred Sonnet 4.6 59% of the time
- Less prone to overengineering and "laziness"
- Better instruction following
- Fewer false success claims, fewer hallucinations
- More consistent follow-through on multi-step tasks

### Long-Context Reasoning

1M token context holds entire codebases, lengthy contracts, or dozens of research papers. Sonnet 4.6 reasons effectively across that context—better at long-horizon planning.

**Vending-Bench Arena:** Tests running a simulated business over time with competition between AI models. Sonnet 4.6 developed a distinct strategy: heavy capacity investment for the first ten simulated months, then sharp pivot to profitability in the final stretch. Finished well ahead of competitors.

### Customer Feedback

- **Frontend code and financial analysis** stood out
- **Visual outputs** notably more polished—better layouts, animations, design sensibility
- Fewer iteration rounds to reach production-quality results

### Testimonials (Summary)

| Company | Quote |
|---------|-------|
| Databricks | Matches Opus 4.6 on OfficeQA (enterprise document comprehension). Meaningful upgrade for document workloads. |
| Replit | Exceptional performance-to-cost. Outperforms on orchestration evals, handles complex agentic workloads. |
| Cursor | Notable improvement across the board, including long-horizon tasks and difficult problems. |
| GitHub | Excels at complex code fixes when searching large codebases. Strong resolution rates, consistency at scale. |
| Cognition | Closed gap with Opus on bug detection; run more reviewers in parallel without cost increase. |
| Windsurf | First Sonnet with frontier-level reasoning in cost-effective form. Viable Opus alternative. |
| Hebbia | Significant jump in answer match rate; better recall on customer workflows. |
| Box | 15 percentage points better than 4.5 on heavy reasoning Q&A across enterprise documents. |
| Pace | 94% on insurance benchmark—highest-performing model for computer use. |
| Bolt | Frontier-level results on complex app builds and bug-fixing. |
| Rakuten | Best iOS code tested—better spec compliance, architecture, modern tooling adoption. |
| Zapier | Strong on branched, multi-step tasks: contract routing, conditional templates, CRM coordination. |
| Convey | Most accurate complex computer use among models tested. |
| Triple Whale | Strong frontend/design output; far less hand-holding. |
| Harvey | Exceptionally responsive to direction; precise figures and useful ideas on trial strategy. |

---

## Product Updates

**Claude Developer Platform:** Sonnet 4.6 supports [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking) and extended thinking, plus [context compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) in beta (auto-summarizes older context as conversations approach limits).

**API tools:** Web [search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [fetch](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) now filter and process results, keeping only relevant content—improving quality and token efficiency. Generally available: [code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), [memory](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), [programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling), [tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool), [tool use examples](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use#providing-tool-use-examples).

**Thinking:** Strong performance at any effort level, including with extended thinking off. Recommend exploring the spectrum when migrating from 4.5.

**When to use Opus 4.6 instead:** Deepest reasoning tasks—codebase refactoring, coordinating multiple agents, problems where precision is paramount.

**Claude in Excel:** MCP connectors supported; Claude works with S&P Global, LSEG, Daloopa, PitchBook, Moody's, FactSet. Pro, Max, Team, Enterprise plans.

---

## How to Use

Available on [Claude plans](https://claude.com/pricing), [Claude Cowork](https://claude.com/product/cowork), [Claude Code](https://claude.com/product/claude-code), API, and major cloud platforms. Free tier now defaults to Sonnet 4.6 with file creation, connectors, skills, and compaction.

**API model ID:** `claude-sonnet-4-6`

---

## Benchmark Methodology (Footnotes)

- GPT-5.2 and Gemini 3 Pro: compared against best reported version via API
- **OSWorld:** Tests a specific set of computer tasks in controlled environment; real-world use is messier and carries higher stakes
- **Terminal-Bench 2.0:** Reports reproduced scores and published scores from other labs; Sonnet 4.6 with thinking off
- **SWE-bench Verified:** Averaged over 10 trials; with prompt modification, 80.2% achieved
- **Humanity's Last Exam:** Claude models with web search, fetch, code execution, programmatic tool calling, context compaction at 50k up to 3M tokens, max reasoning effort, adaptive thinking
- **BrowseComp:** Web search, fetch, programmatic tool calling, compaction at 50k up to 10M tokens, max effort, no thinking
- **ARC-AGI-2:** Max and high effort, 120k thinking budget; max effort shown; high effort: 60.4%
- **MMMU-Pro:** Implementation updates: removed "Let's think step-by-step" prefix; now graded with separate model (Claude Sonnet 4) instead of token probabilities
