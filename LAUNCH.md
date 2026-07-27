# Launch playbook — how this gets stars

**Reality check:** nobody ships 10,000 stars overnight without distribution. Great repos still need a front page, a demo people can share, and a crisp story. This file is the playbook.

## Product (done in-repo)

- [x] One-sentence pitch
- [x] Zero-dep badge + honest LangGraph comparison
- [x] Copy-paste quickstart under 30 seconds
- [x] Live Mermaid demo (GitHub Pages)
- [x] Multiple example patterns (retry, tools, multi-agent)
- [x] CI green on 3.9–3.13
- [x] MIT license
- [x] Terminal demo GIF in README
- [x] PyPI package `simple-graph-agents` + publish workflow

## Enable GitHub polish (5 minutes)

1. **GitHub Pages**  
   Settings → Pages → Source: **GitHub Actions**  
   After the next push to `main`, open:  
   `https://cobusgreyling.github.io/graph-engineering/`

2. **Social preview**  
   Settings → General → Social preview → upload `ge1.jpg` (or a 1280×640 crop).

3. **Topics** (already set — keep sharp)  
   `agents` `graph` `langgraph` `mermaid` `python` `workflow` `zero-dependency` `multi-agent` `orchestration`

4. **About blurb**  
   `Zero-dependency Python graph runtime for agent loops · Mermaid + ASCII · LangGraph energy, bicycle size`

5. **Pin the repo** on your profile for 2–4 weeks post-launch.

## Day-0 content (ship with the launch)

| Asset | Why |
|-------|-----|
| README hero + mermaid | First 5 seconds of trust |
| 15–30s terminal GIF | `python examples/research_write_verify.py` + trail |
| Short blog / LinkedIn / X thread | Your distribution graph is the moat |
| One diagram of *your* production graph | Proof it's not a toy |

**Suggested thread skeleton (X / LinkedIn):**

1. Hook: “I got tired of installing half of PyPI to draw a state machine.”
2. Show Mermaid from `render_mermaid()`.
3. Show the 15-line fluent API.
4. Honest “not a LangGraph replacement” line (builds trust → stars).
5. Link repo + live demo.
6. Ask: “What agent loop would you delete a framework for?”

## Channels that actually move stars

| Channel | Tip |
|---------|-----|
| **Hacker News** | Title like: *Show HN: Zero-dep agent graphs in ~400 lines of Python* — post Tue–Thu morning US |
| **Reddit** | r/MachineLearning (Research), r/LocalLLaMA, r/Python — lead with code, not hype |
| **X / LinkedIn** | Post Mermaid image; tag people who teach agents, not random influencers |
| **Dev.to / Medium / personal blog** | “Why agent control flow should be boring” + embed demo |
| **Discord / Slack communities** | LangChain, LlamaIndex, AI Engineer — share as teaching tool |
| **YouTube short** | Screen record: define graph → run → Mermaid in 60s |

## What *not* to do

- Don't buy stars or use star-exchange groups (GitHub detects; kills trust).
- Don't claim “LangGraph killer” — the README comparison is stronger because it's honest.
- Don't spam the same link in 20 subreddits in one hour.
- Don't gatekeep simple questions — early issues and “good first issue” labels compound.

## Metrics that matter more than vanity stars

1. **Clone → run example without opening an issue** (docs quality)
2. **Issues that say “used this in class / demo”** (product-market fit)
3. **Forks that add one example** (ecosystem seed)
4. **Mentions next to LangGraph as the *tiny* alternative** (positioning)

## 7-day cadence

| Day | Action |
|-----|--------|
| 0 | Tag `v0.2.0`, enable Pages, post thread + HN |
| 1 | Reply to every comment within a few hours |
| 2 | Publish a 3-minute demo video |
| 3 | Add one community-requested example (if any) |
| 5 | Write “Graph Engineering vs if/else vs LangGraph” short post |
| 7 | Summarize learnings; ship 0.2.1 polish if needed |

## North star

A star is a bookmark with applause. Earn it by making someone's **next agent loop** fit in their head before lunch.

When someone says *“I finally understand control flow”* — that's the 10k path, even if the counter takes longer than a night.
