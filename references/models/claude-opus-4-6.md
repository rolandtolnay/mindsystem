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

### Full Benchmark Comparison

| Benchmark | Opus 4.6 | Opus 4.5 | Sonnet 4.5 | Gemini 3 Pro | GPT-5.2 |
|-----------|---------|---------|-----------|-------------|---------|
| **Agentic terminal coding** (Terminal-Bench 2.0) | **65.4%** | 59.8% | 51.0% | 56.2% (54.2% self-reported) | 64.7% (64.0% self-reported, Codex CLI) |
| **Agentic coding** (SWE-bench Verified) | 80.8% | **80.9%** | 77.2% | 76.2% | 80.0% |
| **Agentic computer use** (OSWorld-Verified) | **72.7%** | 66.3% | 61.4% | — | — |
| **Agentic tool use** (τ2-bench Retail) | **91.9%** | 88.9% | 86.2% | 85.3% | 82.0% |
| **Agentic tool use** (τ2-bench Telecom) | **99.3%** | 98.2% | 98.0% | 98.0% | 98.7% |
| **Scaled tool use** (MCP Atlas) | 59.5% | **62.3%** | 43.8% | 54.1% | 60.6% |
| **Agentic search** (BrowseComp) | **84.0%** | 67.8% | 43.9% | 59.2% (Deep Research) | 77.9% (Pro) |
| **Multidisciplinary reasoning** (HLE, no tools) | **40.0%** | 30.8% | 17.7% | 37.5% | 36.6% (Pro) |
| **Multidisciplinary reasoning** (HLE, with tools) | **53.1%** | 43.4% | 33.6% | 45.8% | 50.0% (Pro) |
| **Agentic financial analysis** (Finance Agent) | **60.7%** | 55.9% | 54.2% | 44.1% | 56.6% (5.1) |
| **Office tasks** (GDPval-AA Elo) | **1606** | 1416 | 1277 | 1195 | 1462 |
| **Novel problem-solving** (ARC-AGI-2) | **68.8%** | 37.6% | 13.6% | 45.1% (Deep Thinking) | 54.2% (Pro) |
| **Graduate-level reasoning** (GPQA Diamond) | 91.3% | 87.0% | 83.4% | 91.9% | **93.2%** (Pro) |
| **Visual reasoning** (MMMU-Pro, no tools) | 73.9% | 70.6% | 63.4% | **81.0%** | 79.5% |
| **Visual reasoning** (MMMU-Pro, with tools) | 77.3% | 73.9% | 68.9% | — | **80.4%** |
| **Multilingual Q&A** (MMMLU) | 91.1% | 90.8% | 89.5% | **91.8%** | 89.6% |

### Long-Context and Retrieval

Much better at retrieving relevant information from large document sets. Holds and tracks information over hundreds of thousands of tokens with less drift. Picks up buried details Opus 4.5 would miss.

**Long-context retrieval (MRCR v2, 8-needle):**

| Model | 256k | 1M |
|-------|------|-----|
| Opus 4.6 | 93.0% | 76.0% |
| Sonnet 4.5 | 10.8% | 18.5% |

Qualitative shift in usable context while maintaining peak performance.

**Long-context reasoning (Graphwalks, 1M tokens):**

| Model | Parents | BFS |
|-------|---------|-----|
| Opus 4.6 | 72.0% | 38.7% |
| Sonnet 4.5 | 50.2% | 25.6% |

### Software Engineering and Domains

**Software failure diagnosis (OpenRCA):**

| Model | Score |
|-------|-------|
| Opus 4.6 | 34.9% |
| Opus 4.5 | 26.9% |
| Sonnet 4.5 | 12.9% |

**Multilingual coding (SWE-bench Multilingual):**

| Model | Score |
|-------|-------|
| Opus 4.6 | 77.8% |
| Opus 4.5 | 76.2% |

**Long-term coherence (Vending-Bench 2, final balance):**

| Model | Balance |
|-------|---------|
| Opus 4.6 | $8,017.59 |
| Gemini 3 Pro | $5,478.16 |
| Opus 4.5 | $4,967.06 |
| Sonnet 4.5 | $3,838.74 |
| GPT-5.2 | $3,591.33 |

**Cybersecurity vulnerability reproduction (CyberGym):**

| Model | Score |
|-------|-------|
| Opus 4.6 | 66.6% |
| Opus 4.5 | 51.0% |
| Sonnet 4.5 | 29.8% |

**Computational biology (BioPipelineBench):**

| Model | Score |
|-------|-------|
| Opus 4.6 | 53.1% |
| Opus 4.5 | 28.5% |
| Sonnet 4.5 | 19.3% |

---

## Safety

Intelligence gains do not come at safety cost. Automated behavioral audit: low rates of deception, sycophancy, encouragement of delusions, cooperation with misuse. As well-aligned as Opus 4.5 (most-aligned frontier to date). Lowest over-refusal rate of any recent Claude model.

**Overall misaligned behavior (1–10, lower is better):**

| Model | Score |
|-------|-------|
| Opus 4.6 | ~1.8 |
| Opus 4.5 | ~1.9 |
| Haiku 4.5 | ~2.2 |
| Sonnet 4.5 | ~2.7 |
| Opus 4.1 | ~4.3 |

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
