<p align="center"><img src="docs/assets/hero.svg" alt="lucid-reason — systematic understanding, engineering reasoning and reliable problem solving for ChatGPT" width="100%"></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-151d2b.svg" alt="MIT license"></a>
  <a href="https://github.com/aikuozone/lucid-reason/actions/workflows/ci.yml"><img src="https://github.com/aikuozone/lucid-reason/actions/workflows/ci.yml/badge.svg" alt="Offline checks"></a>
  <a href="https://github.com/aikuozone/lucid-reason/releases"><img src="https://img.shields.io/badge/version-1.1.4-467b5b.svg" alt="Version 1.1.4"></a>
</p>

<p align="center"><a href="README.zh-CN.md">简体中文</a> · <a href="examples/README.md">ChatGPT showcase</a> · <a href="docs/installation.md">Get started</a> · <a href="evals/REPORT.md">Evaluation evidence</a></p>

**Help ChatGPT explain a problem all the way through: the concepts, the mechanism, the connections, and the boundaries.**

**lucid-reason (`lr`)** is a skills-only plugin for systematic understanding, engineering reasoning, and reliable problem solving. It supports focused concepts and complete domains, mathematics and algorithms, research, system design, technical decisions, and troubleshooting.

For learning, it connects the knowledge in an order you can follow. For practical problems, it brings the explanation back to the actual goal, project constraints, evidence, and verification. In **ChatGPT Chat mode**, available native diagrams, mathematical notation, charts, and interactive components can help make those relationships visible.

The principle is **necessary completeness**: explain what the question needs, at the depth it needs. A small concept can take a few paragraphs; a whole domain needs a connected structure. You can ask naturally without arranging a workflow or deploying a separate service.

## A real ChatGPT conversation

The question was simply **`lr 系统讲解 transformer`** (“lr, explain Transformer systematically”). The shared conversation moves from a knowledge map through Q/K/V, attention matrices and causal masks to architecture, training, generation, and KV Cache.

**[Open the original ChatGPT conversation](https://chatgpt.com/share/6ad6bc80-00d0-83e8-a6c7-f83d75adaf68)** · [Full-page screenshot](docs/assets/chatgpt-transformer/full.png) · [More views and capture details](examples/README.md)

<a href="docs/assets/chatgpt-transformer/full.png"><img src="docs/assets/chatgpt-transformer/knowledge-map.png" alt="Real ChatGPT shared page: Transformer knowledge map and module relationships" width="100%"></a>

*A viewport from the actual public ChatGPT page. Open the complete capture to follow the question and answer from beginning to end, including native diagrams, mathematics, and a chart.*

## What lr brings to a question

| Capability | What it is for |
|---|---|
| Systematic understanding | Explain what something is, why it exists, how it works, what it depends on, and where it stops applying. |
| Causal explanation | Connect inputs, intermediate steps, outputs, and failures instead of listing terminology. |
| Visual learning | Use a useful knowledge map, diagram, matrix, chart, or supported interactive explanation when it adds understanding. |
| Engineering reasoning | Keep the actual business, data, resources, architecture, and acceptance criteria consistent. |
| Decision calibration | Judge the gap between the current system and the real goal, then weigh the value and cost of a change. |
| Evidence and review | Separate facts, derivations, estimates, simulations, and unknowns; check consequential claims and repair specific gaps. |
| Follow-up continuity | Build on available context and revise affected conclusions when the premises change. |

These are instructions for the model, with no fixed answer template. The skill has no rendering engine, server, credentials, or permanent memory. The host supplies the model, tools, interface, permissions, and accessible context.

## Use it in ChatGPT Chat mode

If lucid-reason is available in your account or workspace, open a Chat conversation, type **`@`**, and select lucid-reason or its skill from the picker. Then ask your question. `lr` is a convenient natural-language hint; explicit selection is the way to make your intended skill clear.

```text
lr 系统讲解 Transformer。

lr 解释 Softmax。如果界面支持，让我调节输入分数并观察概率如何变化。

lr 分析这个 RAG 项目：保留现有架构，先定位效果下降的证据与原因。
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

The [evaluation report](evals/REPORT.md) retains 68 completed local conversations across 22 scenarios, including paired baseline/lr runs and a repeated subset. These are Codex CLI observations with model-assisted rubric judgments. They do not test the ChatGPT frontend or establish a universal quality improvement. A missed rollback-trigger requirement remains documented in the report.

Read the [methodology and reproduction commands](docs/evaluation.md), [full CLI examples](examples/cli.md), and [native screenshot provenance](docs/presentation.md). The public ChatGPT example is a presentation case with an unspecified original model and skill version, separate from the controlled evaluation.

## Package and contribute

The runtime ZIP contains `plugin.json`, the compatibility manifest, `skills/`, `LICENSE`, and a distribution guide. The display name is **lucid-reason**; the existing identifiers `systematic-knowledge-architect` (plugin) and `systematic-knowledge-construction` (skill) are preserved. Instructions are authored in Chinese; the evaluation includes an English transfer case.

Bring a reproducible example of a wrong conclusion, missed constraint, or unhelpful explanation. Include the host, model, skill version, prompt, and response. See [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md), and [source provenance](docs/provenance.json).

**Understand completely. Explain causally. Decide carefully. Verify reliably.**

MIT licensed. Copyright © 2026 blunt.
