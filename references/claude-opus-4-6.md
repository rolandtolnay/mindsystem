# Claude Opus 4.6

**Source:** [Anthropic News](https://www.anthropic.com/news/claude-opus-4-6) | **Published:** Feb 5, 2026

Reference for LLM agents: capabilities, benchmarks, and product details of Claude Opus 4.6.

---

## Overview

Claude Opus 4.6 is Anthropic's smartest model. Upgrades over 4.5 include: better coding skills, more careful planning, longer-sustained agentic tasks, more reliable operation in larger codebases, and stronger code review and self-debugging. First Opus-class model with 1M token context window (beta).

**Availability:** [claude.ai](https://claude.ai), API, and major cloud platforms. Same pricing as 4.5: $5/$25 per million tokens.

**Use cases:** Financial analysis, research, documents/spreadsheets/presentations. Within [Cowork](https://claude.com/blog/cowork-research-preview) (multitasking autonomous mode), applies all skills together.

**Benchmark highlights:**
- Highest score on [Terminal-Bench 2.0](https://www.tbench.ai/news/announcement-2-0) (agentic coding)
- Leads all frontier models on [Humanity's Last Exam](https://agi.safe.ai/) (multidisciplinary reasoning)
- [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa): ~144 Elo above GPT-5.2, ~190 above Opus 4.5 (economically valuable knowledge work: finance, legal, etc.)
- Best on [BrowseComp](https://openai.com/index/browsecomp/) (hard-to-find information online)

**Safety:** As good as or better than any frontier model; low misaligned behavior. See [system card](https://www.anthropic.com/claude-opus-4-6-system-card).

---

## First Impressions

Anthropic engineers use Claude Code daily. With Opus 4.6: more focus on the hardest parts without being told, faster through straightforward parts, better judgment on ambiguous problems, stays productive over long sessions. Often thinks more deeply and revisits reasoning before answering. This improves harder problems but can add cost/latency on simpler ones—consider dialing effort from high (default) to medium with the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort).

### Testimonials (Summary)

| Company | Quote |
|---------|-------|
| Notion | Strongest Anthropic model. Breaks complex requests into concrete steps, executes, produces polished work. Feels like a capable collaborator. |
| GitHub | Complex multi-step coding, especially agentic workflows with planning and tool calling. Unlocks long-horizon tasks at the frontier. |
| Replit | Huge leap for agentic planning. Breaks tasks into independent subtasks, runs tools/subagents in parallel, identifies blockers precisely. |
| Asana | Best model tested. Exceptional reasoning and planning for AI Teammates. State-of-the-art at navigating large codebases and identifying changes. |
| Cognition | Reasons through complex problems at a new level. Considers edge cases others miss. Strong in Devin Review—increased bug catching rates. |
| Windsurf | Noticeably better than 4.5 on debugging and unfamiliar codebases. Thinks longer; pays off when deeper reasoning is needed. |
| Thomson Reuters | Meaningful leap in long-context performance. Handles larger bodies of information with consistency for complex research workflows. |
| NBIM | Best results 38 of 40 times in blind ranking vs Claude 4.5 on 40 cybersecurity investigations (9 subagents, 100+ tool calls). |
| Cursor | New frontier on long-running tasks. Highly effective at code review. |
| Harvey | Highest BigLaw Bench score: 90.2%. 40% perfect scores, 84% above 0.8. Remarkably capable for legal reasoning. |
| Rakuten | Autonomously closed 13 issues, assigned 12 to right team members in one day. Managed ~50-person org across 6 repos. Product and org decisions; knew when to escalate. |
| Lovable | Uplift in design quality. Works with design systems; more autonomous. |
| Box | 10% lift: 68% vs 58% baseline on high-reasoning multi-source analysis (legal, financial, technical). Near-perfect technical domains. |
| Figma | Generates complex interactive apps in Figma Make. Translates detailed designs into code on first try. |
| Shopify | Best Anthropic model tested. Understands intent with minimal prompting. Explores and creates details proactively. |
| Bolt.new | Meaningful improvement for design systems and large codebases. One-shotted a fully functional physics engine. |
| Ramp | Biggest leap in months. Comfortable giving sequence of tasks across stack; smart use of subagents. |
| SentinelOne | Handled multi-million-line migration like a senior engineer. Planned up front, adapted strategy, finished in half the time. |
| Vercel | Frontier-level reasoning, especially edge cases. Helps elevate prototypes to production. |
| Shortcut.ai | Performance jump feels almost unbelievable. Challenging spreadsheet-agent tasks became easy. |

---

## Evaluation and Benchmarks

Industry-leading across agentic coding, computer use, tool use, search, and [finance](https://claude.com/blog/opus-4-6-finance). Full comparison table in [system card](https://www.anthropic.com/claude-opus-4-6-system-card).

### Long-Context and Retrieval

Much better at retrieving relevant information from large document sets. Holds and tracks information over hundreds of thousands of tokens with less drift. Picks up buried details Opus 4.5 would miss.

**Context rot:** Opus 4.6 performs markedly better. On 8-needle 1M variant of [MRCR v2](https://huggingface.co/datasets/openai/mrcr): 76% vs Sonnet 4.5's 18.5%. Qualitative shift in usable context while maintaining peak performance.

### Software Engineering and Domains

- **Root cause analysis:** Excels at diagnosing complex software failures
- **Multilingual coding:** Resolves issues across programming languages
- **Long-term coherence:** Maintains focus; earns $3,050.53 more than 4.5 on Vending-Bench 2
- **Cybersecurity:** Finds real vulnerabilities better than any other model
- **Life sciences:** Almost 2× better than 4.5 on computational biology, structural biology, organic chemistry, phylogenetics

---

## Safety

Intelligence gains do not come at safety cost. Automated behavioral audit: low rates of deception, sycophancy, encouragement of delusions, cooperation with misuse. As well-aligned as Opus 4.5 (most-aligned frontier to date). Lowest over-refusal rate of any recent Claude model.

Most comprehensive safety evaluations of any model: new user wellbeing tests, complex refusal tests, surreptitious harmful-action evaluations, interpretability methods.

**Cybersecurity safeguards:** Six new probes for harmful response detection. Accelerating defensive use—finding and patching vulnerabilities in open-source (see [cybersecurity blog](https://red.anthropic.com/2026/zero-days/)).

---

## Product and API Updates

**Claude Developer Platform**

- **[Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking):** Model decides when deeper reasoning helps (vs binary extended-thinking toggle)
- **[Effort](https://platform.claude.com/docs/en/build-with-claude/effort):** Four levels—low, medium, high (default), max
- **[Context compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) (beta):** Auto-summarizes older context when approaching threshold
- **1M token context (beta):** First Opus with 1M; premium pricing above 200k ($10/$37.50 per million). Developer Platform only.
- **128k output tokens:** Larger outputs without multiple requests
- **[US-only inference](https://platform.claude.com/docs/en/build-with-claude/data-residency):** 1.1× token pricing

**Claude Code:** [Agent teams](https://code.claude.com/docs/en/agent-teams) (research preview)—multiple agents working in parallel, coordinate autonomously. Take over any subagent with Shift+Up/Down or tmux.

**Claude in Excel:** Improved performance on long-running and harder tasks. Plans before acting, infers structure from unstructured data, handles multi-step changes in one pass.

**Claude in PowerPoint:** Research preview (Max, Team, Enterprise). Process data in Excel, build visuals in PowerPoint. Reads layouts, fonts, slide masters. Available from template or full deck from description.

---

## How to Use

Available on [claude.ai](https://claude.ai), [API](https://platform.claude.com/docs/en/about-claude/models/overview), and major cloud platforms.

**API model ID:** `claude-opus-4-6`

---

## Benchmark Methodology (Footnotes)

- **1M context:** Beta on Claude Developer Platform only
- **GDPval-AA:** Run by Artificial Analysis; [methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking#gdpval-aa). ~144 Elo ≈ Opus 4.6 beats GPT-5.2 ~70% of the time
- **GPT-5.2 / Gemini 3 Pro:** Best reported version in charts
- **Terminal-Bench 2.0:** Terminus-2 harness; 1× guaranteed / 3× ceiling; 5–15 samples per task
- **Humanity's Last Exam:** Web search, fetch, code execution, programmatic tool calling, compaction at 50k up to 3M tokens, max effort, adaptive thinking
- **SWE-bench Verified:** Averaged over 25 trials; with prompt modification: 81.42%
- **MCP Atlas:** Max effort; high effort: 62.7% (industry-leading)
- **BrowseComp:** Web search, fetch, programmatic tool calling, compaction at 50k up to 10M tokens, max effort, no thinking. Multi-agent harness: 86.8%
- **ARC-AGI 2:** Max effort, 120k thinking budget
- **CyberGym:** No thinking, default effort, temperature, top_p; "think" tool for multi-turn
- **OpenRCA:** 1 point if all root-cause elements match ground truth; 0 if any mismatch. Official harness and grading; submitted for verification
