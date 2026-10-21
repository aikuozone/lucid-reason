<p align="center"><img src="docs/assets/hero.svg" alt="lucid-reason — systematic understanding, engineering reasoning and reliable problem solving for ChatGPT" width="100%"></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-151d2b.svg" alt="MIT license"></a>
  <a href="https://github.com/aikuozone/lucid-reason/actions/workflows/ci.yml"><img src="https://github.com/aikuozone/lucid-reason/actions/workflows/ci.yml/badge.svg" alt="Offline checks"></a>
  <a href="https://github.com/aikuozone/lucid-reason/releases"><img src="https://img.shields.io/badge/version-1.1.5-467b5b.svg" alt="Version 1.1.5"></a>
</p>

<p align="center"><a href="README.zh-CN.md">简体中文</a> · <a href="examples/README.md">ChatGPT showcase</a> · <a href="docs/installation.md">Get started</a> · <a href="evals/UPDATE-1.1.5.md">Update verification</a></p>

**Help AI understand your idea in context, make its proposal understandable, and build a shared view through discussion.**

**lucid-reason (`lr`)** is a skills-only plugin for learning, planning, discussing solutions, engineering decisions, research, and troubleshooting. It guides AI to place your ideas within their goals, constraints, and relationships, then explain mechanisms, evidence, tradeoffs, and proposals in a form you can understand, judge, and revise.

For visual learning, **ChatGPT Chat mode** brings the explanation together with available native diagrams, mathematical notation, charts, and interactive components. For planning, lr also considers the whole: which parts an idea affects, why a proposal fits, and what a later change would alter.

The principle is **necessary completeness and a discussion you can build on**. A small concept can take a few paragraphs; a complex proposal needs a connected structure. Start with an idea, question, or objection in natural language, without arranging a workflow or deploying a separate service.

## A real ChatGPT conversation

The question was simply **`lr 系统讲解 transformer`** (“lr, explain Transformer systematically”). The shared conversation moves from a knowledge map through Q/K/V, attention matrices and causal masks to architecture, training, generation, and KV Cache.

**[Open the original ChatGPT conversation](https://chatgpt.com/share/6ad6bc80-00d0-83e8-a6c7-f83d75adaf68)** · [Full-page screenshot](docs/assets/chatgpt-transformer/full.png) · [More views and capture details](examples/README.md)

<a href="docs/assets/chatgpt-transformer/full.png"><img src="docs/assets/chatgpt-transformer/knowledge-map.png" alt="Real ChatGPT shared page: Transformer knowledge map and module relationships" width="100%"></a>

*A viewport from the actual public ChatGPT page. Open the complete capture to follow the question and answer from beginning to end, including native diagrams, mathematics, and a chart.*

## Why use lr?

1. **Connect the explanation and the visuals.** A complex topic often becomes difficult at the relationships and intermediate steps: how modules connect, how a calculation changes, or what a chart demonstrates. lr organizes the explanation around those dependencies and uses useful diagrams, mathematics, charts, and available interactive tools in ChatGPT Chat mode. It explains how the visual relates to the text, then connects the overall structure to mechanisms, examples, and boundaries.

2. **Understand what an idea means for the whole system.** “Add a component” or “use a different approach” is often a proposed implementation. lr first identifies the intended result, current capabilities, and real constraints, then follows upstream dependencies, related parts, and end-to-end consequences. A proposed unified Agent framework, for example, might really be a way to reduce repeated data entry and page switching. The relevant question is how the complete workflow improves and whether the framework earns its added cost.

3. **Create a complete first proposal that makes discussion possible.** An initial plan connects the goal, main flow, responsibilities, tradeoffs, failure handling, and acceptance criteria. Even when it does not yet fit all your expectations, a coherent proposal lets you identify what is missing, what feels wrong, and what matters more. That shared starting point can reveal new ideas and better solutions.

4. **Keep the whole coherent as you revise it.** When you change a priority, reject a step, or ask to adjust one part, lr carries forward valid goals and confirmed decisions, checks the affected dependencies, and revises the relevant parts. Understanding the whole and changing the whole have different scopes. Unaffected choices stay stable; fundamental conflicts call for an explanation of the broader change needed. Each exchange helps establish a current proposal you can both understand.

5. **Explain the basis for decisions so you can take part.** lr makes the reasons, conditions, benefits, costs, and verification methods understandable, while separating facts, derivations, estimates, and unknowns. You can challenge an assumption, compare a tradeoff, or change direction. Shared understanding requires making disagreements and their reasons clear; a suggestion that violates the goal or constraints should prompt an explanation and a workable alternative.

These instructions guide the model's understanding, analysis, and communication; actual results depend on the model and task. The host supplies tools, rendering, permissions, and accessible context. The skill adds no server, credentials, rendering engine, or permanent memory.

## Discuss a plan and improve it together

Start with an unfinished idea. You do not need to write the entire requirements document or architecture first. For example:

| Stage | What you might say | What the discussion should establish |
|---|---|---|
| Form a complete proposal | “I have ticketing and search tools. I want less page switching and am considering a unified Agent. Understand the goal and propose a complete starting point.” | Connections between the actual goal, current system, full workflow, necessary changes, tradeoffs, and acceptance. |
| Explain what does not fit | “Repeated field entry is the main problem. Keep both tools and the existing permissions; revise the relevant flow.” | A corrected priority, its dependency impacts, and the conclusions that still hold. |
| Consolidate the shared view | “State the current proposal, reasons, unresolved assumptions, and next checks, then make the implementation plan.” | A shared proposal that is easy to understand, verify, and develop further. |

The initial proposal exposes disagreements; follow-up questions deepen understanding; revisions produce a better fit. See a [real three-turn planning discussion](examples/planning.md). Natural follow-ups also work for learning, technical decisions, and diagnosis.

## Use it in ChatGPT Chat mode

If lucid-reason is available in your account or workspace, open a Chat conversation, type **`@`**, and select lucid-reason or its skill from the picker. Then ask your question. `lr` is a convenient natural-language hint; explicit selection is the way to make your intended skill clear.

```text
lr Explain Transformer systematically.

lr Explain Softmax. If the interface supports it, let me adjust the scores and observe the probabilities.

lr Analyze what this idea would mean for the whole system, then give me a complete proposal we can discuss.

lr Keep the previous goals and constraints. Revise the part we discussed and explain the related impacts.
```

Follow up naturally: “Why is this step necessary?”, “Show the tensor shapes here”, or “Explain only the authorization step using the previous architecture.”

Visual and interactive features depend on the client and the tools available in that conversation. See OpenAI's [skills documentation](https://learn.chatgpt.com/docs/build-skills) and [visualizations documentation](https://learn.chatgpt.com/docs/visualizations). This GitHub release provides the source and runtime package; it does not itself add lr to the public ChatGPT plugin catalog. See [installation and availability](docs/installation.md).

## Use the skill in Codex

The same instructions can be installed as a project skill. This route is also used for reproducible text-behavior evaluation.

```bash
git clone https://github.com/aikuozone/lucid-reason.git
cd lucid-reason
python3 scripts/install_skill.py --target /absolute/path/to/your/project/.agents/skills
```

Start a new Codex session in that project and select it explicitly:

```text
$systematic-knowledge-construction Explain how BaseModel participates in an Agent tool call, from validation and authorization to execution and result confirmation.
```

See [tested paths, release ZIP installation, and removal](docs/installation.md). The native ChatGPT visual experience is demonstrated separately above.

## Test and reproduce

Python 3.10+ is required for maintenance scripts. Installation and runtime packaging use the standard library; offline metadata checks additionally use PyYAML.

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_project.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

The [v1.1.5 update verification](evals/UPDATE-1.1.5.md) records focused regressions for this update. The [historical v1.1.4 report](evals/REPORT.md) retains 68 completed local conversations across 22 scenarios, including paired runs, a repeated subset, and observed failures. Its source is now frozen separately; those results do not establish that the current version passed the same evaluation.

Read the [methodology and reproduction commands](docs/evaluation.md), [historical CLI examples](examples/cli.md), and [native screenshot provenance](docs/presentation.md). Observations and assessments do not establish universal improvement. The public ChatGPT example demonstrates native presentation with an unspecified original model and skill version.

## Package and contribute

The runtime ZIP contains `plugin.json`, the compatibility manifest, `skills/`, `LICENSE`, and a distribution guide. The display name is **lucid-reason**; the existing identifiers `systematic-knowledge-architect` (plugin) and `systematic-knowledge-construction` (skill) are preserved. Instructions are authored in Chinese; the evaluation includes an English transfer case.

Bring a reproducible example of a wrong conclusion, missed constraint, or unhelpful explanation. Include the host, model, skill version, prompt, and response. See [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md), and [source provenance](docs/provenance.json).

**Understand completely. Explain causally. Decide carefully. Verify reliably.**

MIT licensed. Copyright © 2026 blunt.
