<p align="center"><img src="docs/assets/hero.svg" alt="lucid-reason：面向 ChatGPT 的系统性理解、工程推理与可靠问题解决" width="100%"></p>

<p align="center"><a href="README.md">English</a> · <a href="examples/README.md">ChatGPT 真实展示</a> · <a href="docs/installation.md">使用与安装</a> · <a href="evals/REPORT.md">测试证据</a> · <a href="LICENSE">MIT</a></p>

**让 ChatGPT 不只是给出答案，而是真正把问题讲清楚。**

**lucid-reason（简称 `lr`）** 是一个基于 Skills 的系统性知识理解与可靠问题解决插件，面向局部概念、完整知识体系、数学与算法、跨学科研究、企业项目、系统设计、技术决策和故障诊断。

学习知识时，它按理解所需的依赖关系组织讲解，连接概念、机制、原因与边界；解决实际问题时，它把推演带回真实目标、项目约束、证据与验证。在 **ChatGPT Chat 模式**中，还可以结合当前可用的原生图示、数学表达、图表和交互组件，让复杂结构与变量关系更容易观察和理解。

核心理念是**必要范围内的完整理解**。局部概念可以用几个自然段讲清，完整领域需要建立主干并深入关键机制。用户可以直接用自然语言提问，无需手动编排流程或部署额外服务。

## 真实 ChatGPT 对话：系统讲解 Transformer

这条对话的提问只有一句：**`lr 系统讲解 transformer`**。回答从整体知识地图展开，逐步连接 Q/K/V、注意力矩阵、因果 Mask、模型架构、训练与生成，再落到 KV Cache 等工程问题。

**[打开原始 ChatGPT 共享对话](https://chatgpt.com/share/6ad6bc80-00d0-83e8-a6c7-f83d75adaf68)** · [查看完整页面长图](docs/assets/chatgpt-transformer/full.png) · [更多视图与截图说明](examples/README.md)

<a href="docs/assets/chatgpt-transformer/full.png"><img src="docs/assets/chatgpt-transformer/knowledge-map.png" alt="真实 ChatGPT 共享页面：Transformer 知识地图及模块关系" width="100%"></a>

*上图为真实共享页的局部视图；完整长图保留从提问到回答结尾的内容，包括对话中的原生图示、数学表达与图表。*

## 它如何帮助理解与解决问题

| 能力 | 具体作用 |
|---|---|
| 系统性知识理解 | 讲清对象是什么、为什么需要、如何运作、依赖什么，以及何时不适用。 |
| 因果与机制解释 | 连接输入、中间步骤、输出和失败条件，让每一步都有原因与去向。 |
| 可视化辅助学习 | 根据解释需要，选择知识地图、结构图、矩阵、图表或宿主支持的交互演示。 |
| 工程实践与系统设计 | 保持业务、数据、资源、架构和验收条件一致，将原理落实到实际过程。 |
| 专业决策校准 | 识别现状与真实目标的差距，判断改动是否具有合理的收益与代价。 |
| 证据核验与定向修复 | 分清事实、推导、估算、模拟和未知，核验关键结论，补全影响理解或执行的缺口。 |
| 连续追问 | 承接当前可用上下文，新前提出现时修正受影响的判断。 |

这些能力指导模型如何组织和检查答案，不要求固定章节或字数。技能由指令与参考文件组成；模型、工具、界面、权限和可用上下文由宿主提供，图表渲染和永久记忆也不由技能单独实现。

## 在 ChatGPT Chat 模式中使用

如果你的账号或工作区已经可以使用 lucid-reason，在 Chat 对话输入框输入 **`@`**，从选择器中选中 lucid-reason 或其技能，再自然描述问题。`lr` 是便于表达使用意图的简称；显式选择可以明确指定要使用的技能。

```text
lr 系统讲解 Transformer。

lr 解释 Softmax。如果界面支持，让我调节输入分数并观察概率如何变化。

lr 分析这个 RAG 项目：保留现有架构，先定位效果下降的证据与原因。
```

也可以继续追问：“为什么需要这一步？”“展示这里的张量形状变化。”“沿用前面的架构，只深入解释权限校验。”

图表和交互能力取决于当次客户端与可用工具。相关宿主说明见 OpenAI 的[技能文档](https://learn.chatgpt.com/docs/build-skills)与[可视化文档](https://learn.chatgpt.com/docs/visualizations)。本仓库提供源码和运行包，GitHub 开源发布本身不会将插件加入 ChatGPT 公共目录。接入条件见[使用与安装说明](docs/installation.md)。

## 在 Codex 中使用相同技能

也可以把完整技能安装到项目中。这条路径同时用于可复现的文本行为评估。

```bash
git clone https://github.com/aikuozone/lucid-reason.git
cd lucid-reason
python3 scripts/install_skill.py --target /你的项目绝对路径/.agents/skills
```

在目标项目中新开 Codex 会话，显式调用：

```text
$systematic-knowledge-construction 解释 BaseModel 如何参与 Agent 工具调用，覆盖参数校验、业务授权、执行和结果确认。
```

已测路径、发行包安装和移除方法见[安装说明](docs/installation.md)。ChatGPT 原生视觉效果由上面的真实共享案例展示。

## 测试与复现

维护脚本需要 Python 3.10+。安装和打包使用标准库；离线配置校验另外需要 PyYAML。

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_project.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

[测试报告](evals/REPORT.md)保留了 22 个场景下的 68 次已完成本地会话，包含基线/lr 成对运行及部分场景重复运行。这些是 Codex CLI 的实际记录与模型辅助评分，不能替代 ChatGPT 前端验证，也不能证明所有问题都获得提升。报告保留了未明确给出回滚触发条件的实际缺口。

[评估方法与复现命令](docs/evaluation.md)、[完整 CLI 案例](examples/cli.md)、[原生截图来源与复现方式](docs/presentation.md)分别记录不同证据。ChatGPT 共享案例用于展示实际呈现，原始模型与技能版本未在公开页面中标明，与受控评估分开说明。

## 分发与贡献

运行包包含 Manifest、完整技能、MIT 许可和分发说明。展示名为 **lucid-reason**，保留插件标识 `systematic-knowledge-architect` 和技能标识 `systematic-knowledge-construction`。技能正文使用中文，测试包含一个英文迁移场景。

欢迎提交可以复现的错误结论、遗漏约束或解释问题，附上宿主、模型、版本、输入与实际回答。详见[贡献指南](CONTRIBUTING.md)、[更新记录](CHANGELOG.md)与[来源记录](docs/provenance.json)。

**Understand completely. Explain causally. Decide carefully. Verify reliably.**

MIT 许可，Copyright © 2026 blunt。
