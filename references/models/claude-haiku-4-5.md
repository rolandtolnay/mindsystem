# Claude Haiku 4.5

**Source:** [Anthropic News](https://www.anthropic.com/news/claude-haiku-4-5) | **Published:** Oct 15, 2025

Reference for LLM agents: capabilities, benchmarks, and product details of Claude Haiku 4.5.

---

## Overview

Claude Haiku 4.5 is Anthropic's latest small model. Delivers similar coding performance to Claude Sonnet 4 (state-of-the-art five months prior) at one-third the cost and more than twice the speed.

**Key differentiator:** What was recently at the frontier is now cheaper and faster. Surpasses Sonnet 4 at certain tasks (e.g., computer use). Enables new orchestration patterns: Sonnet 4.5 can break complex problems into multi-step plans, then orchestrate multiple Haiku 4.5s for parallel subtasks.

**Availability:** Claude Code, apps, [Claude for Chrome](https://claude.ai/chrome), API, Amazon Bedrock, Google Cloud Vertex AI. Drop-in replacement for Haiku 3.5 and Sonnet 4 at most economical price point.

**Pricing:** $1/$5 per million input and output tokens.

**API model ID:** `claude-haiku-4-5`

**Use cases:** Real-time, low-latency tasks—chat assistants, customer service agents, pair programming. Multiple-agent projects and rapid prototyping in Claude Code.

---

## Evaluation and Benchmarks

One of Anthropic's most powerful models to date. See [system card](https://www.anthropic.com/claude-haiku-4-5-system-card) for full comparison table and methodology.

### Full Benchmark Comparison

| Benchmark | Haiku 4.5 | Sonnet 4.5 | Sonnet 4 | GPT-5 | Gemini 2.5 Pro |
|-----------|----------|-----------|---------|-------|----------------|
| **Agentic coding** (SWE-bench Verified) | 73.3% | 77.2% | 72.7% | 72.8% (high) / 74.5% (Codex) | 67.2% |
| **Agentic terminal coding** (Terminal-Bench) | 41.0% | 50.0% | 36.4% | 43.8% | 25.3% |
| **Agentic computer use** (OSWorld) | 50.7% | 61.4% | 42.2% | — | — |
| **Agentic tool use** (τ2-bench Retail) | 83.2% | 86.2% | 83.8% | 81.1% | — |
| **Agentic tool use** (τ2-bench Airline) | 63.6% | 70.0% | 63.0% | 62.6% | — |
| **Agentic tool use** (τ2-bench Telecom) | 83.0% | 98.0% | 49.6% | 96.7% | — |
| **High school math competition** (AIME 2025, python) | 96.3% | 100% | 70.5% | 99.6% | 88.0% |
| **High school math competition** (AIME 2025, no tools) | 80.7% | 87.0% | — | 94.6% | — |
| **Graduate-level reasoning** (GPQA Diamond) | 73.0% | 83.4% | 76.1% | 85.7% | **86.4%** |
| **Multilingual Q&A** (MMMLU) | 83.0% | 89.1% | 86.5% | **89.4%** | — |
| **Visual reasoning** (MMMU validation) | 73.2% | 77.8% | 74.4% | **84.2%** | 82.0% |

### Testimonials (Summary)

| Company | Quote |
|---------|-------|
| Augment | Near-frontier coding quality with blazing speed and cost efficiency. 90% of Sonnet 4.5's performance in agentic coding eval. |
| Warp | Leap forward for agentic coding—sub-agent orchestration and computer use. Responsiveness makes AI-assisted development feel instantaneous. |
| Windsurf | Blurs speed/cost/quality tradeoff. Fast frontier model that keeps costs efficient. |
| Shopify | Intelligence without sacrificing speed. Enables deep reasoning and real-time responsiveness. |
| Wrike | Remarkably capable—this performance would have been state-of-the-art six months ago. 4–5× faster than Sonnet 4.5 at a fraction of the cost. |
| — | Speed is the new frontier for agents in feedback loops. Intelligence and rapid output. Handles complex workflows, self-corrects in real-time. |
| Gamma | Outperformed premium models on instruction-following for slide text: 65% vs 44% accuracy—game-changer for unit economics. |
| GitHub | Efficient code generation with comparable quality to Sonnet 4 at faster speed. Excellent for Copilot users who value speed and responsiveness. |

---

## Safety Evaluations

Low rates of concerning behaviors. Substantially more aligned than Claude Haiku 3.5. Statistically significantly lower misaligned behavior rate than Sonnet 4.5 and Opus 4.1—by this metric, Anthropic's safest model yet.

Limited CBRN (chemical, biological, radiological, nuclear) production risks. Released under AI Safety Level 2 (ASL-2)—less restrictive than ASL-3 for Sonnet 4.5 and Opus 4.1. Full reasoning in [system card](https://www.anthropic.com/claude-haiku-4-5-system-card).

---

## How to Use

Available on Claude Code, apps, API, Amazon Bedrock, and Google Cloud Vertex AI. Efficiency means more within usage limits while maintaining premium performance.

**Further resources:** [System card](https://www.anthropic.com/claude-haiku-4-5-system-card), [model page](https://www.anthropic.com/claude/haiku), [documentation](https://docs.claude.com/en/docs/about-claude/models/overview).

---

## Benchmark Methodology (Footnotes)

- **SWE-bench Verified:** Simple scaffold, bash + file editing. 73.3% averaged over 50 trials, no test-time compute, 128K thinking budget, default sampling. Prompt addition: "You should use tools as much as possible, ideally more than 100 times. You should also implement your own tests first before attempting the problem."
- **Terminal-Bench:** Terminus 2, XML parser, 11 runs (6 without thinking: 40.21%; 5 with 32K thinking: 41.75%), n-attempts=1
- **τ2-bench:** 10 runs, extended thinking (128K), default sampling, tool use, prompt addenda for Airline/Telecom failure modes
- **AIME:** Average of 10 runs, pass@1 over 16 trials, default sampling, 128K thinking
- **OSWorld:** Official OSWorld-Verified, 100 max steps, 4 runs, 128K total + 2K per-step thinking
- **MMMLU:** 10 runs, 14 non-English languages, 128K thinking
- **Other benchmarks:** 10 runs, default sampling, 128K thinking
- **OpenAI/Gemini:** Scores from official posts and leaderboards (see system card)
