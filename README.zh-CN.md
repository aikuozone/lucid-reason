<p align="center"><img src="docs/assets/hero.svg" alt="lucid-reason：系统性理解与可靠问题解决" width="100%"></p>

<p align="center"><a href="README.md">English</a> · <a href="docs/installation.md">安装说明</a> · <a href="examples/README.md">真实案例</a> · <a href="evals/REPORT.md">测试证据</a> · <a href="LICENSE">MIT</a></p>

**lucid-reason（简称 lr）是一项由指令和参考文档组成的技能，用于理解知识、做工程决策和基于证据排查问题。** 它围绕当前任务串起必要概念、机制、因果、现实约束和核验方法，按问题决定表达形式与长度。

适合“知道定义但不明白怎样运作”“方案必须保留现有项目约束”“缺少证据，不能直接宣布根因”等情况。它由宿主模型执行，实际效果需要结合模型、工具和问题判断。

## 开始使用

```bash
git clone https://github.com/aikuozone/lucid-reason.git
cd lucid-reason
python3 scripts/install_skill.py --target /你的项目绝对路径/.agents/skills
```

在目标项目中新开 Codex 会话，显式调用：

```text
$systematic-knowledge-construction 解释 BaseModel 如何参与 Agent 工具调用，覆盖参数校验、业务授权、执行和结果确认。
```

`lr`、`lucid-reason` 可以表达自然语言调用意图；是否自动选择由宿主决定。稳定的显式技能名称是 `$systematic-knowledge-construction`。完整安装目录、发行包使用和卸载方法见[安装说明](docs/installation.md)。

## 主要用途

| 场景 | 期望行为 |
|---|---|
| 概念与领域学习 | 解释存在原因、运行机制、必要先修、例子和边界。 |
| 工程设计与决策 | 保留项目基线，根据实际差距、约束和收益判断是否改动。 |
| 故障诊断 | 区分现象和假设，给出能推翻假设的证据与验证方法。 |
| 研究与说明 | 分清事实、推导、估算、教学模拟与未核实主张。 |
| 连续追问 | 承接可用上下文，新证据出现时修正受影响的判断。 |

这些是对模型的行为指导，不是正确率保证。模型、工具、权限和上下文由宿主提供；技能本身不附带服务器、密钥、永久记忆或外部连接。

## 查看实际效果

[三个案例](examples/README.md)选自真实本地运行，保留提问、回答和环境信息。图片是标注过的测试输出排版截图，可以追溯完整记录。

<a href="examples/README.md"><img src="docs/assets/showcase.png" alt="三个真实测试案例的回答节选，完整记录见案例文档" width="100%"></a>

## 测试和复现

维护脚本需要 Python 3.10+。安装和打包使用标准库；离线配置校验另外需要 PyYAML。

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_project.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

实际回答测试另外需要已安装并登录的 Codex CLI：

```bash
python3 scripts/run_evaluation.py --model gpt-6.1-sol --workers 3 --run-id my-evaluation
```

该命令使用本机账号及其额度，对 22 个场景分别运行基线组和 lr 组，包含真实多轮续接。账号凭据不应放入公开 CI。[方法与评分边界](docs/evaluation.md)、[实际测试报告](evals/REPORT.md)分别说明如何运行与观察到了什么。

原有 16 题来自技能验收规范；新增 6 题是本次发布作者编写的迁移测试，并非独立封闭基准。报告不承诺所有问题都变好，也不宣称已证明普遍减少幻觉。

报告保留了一个实际缺口：英文排障案例中，两组回答都未明确给出评分标准要求的回滚触发条件。安装和打包检查通过，不代表这项回答质量缺口已经解决。

## 分发和兼容

运行包包含根 Manifest、可选兼容 Manifest、完整技能及 MIT 许可；GitHub 源码包含文档、脚本、测试和公开运行记录。展示名为 lucid-reason，保留插件标识 `systematic-knowledge-architect` 和技能标识 `systematic-knowledge-construction`。

技能正文使用中文，当前测试包含一个英文迁移场景。各宿主路径的验证状态见[兼容表](docs/installation.md)。

欢迎提交可以复现的错误结论、遗漏约束或解释问题，附上模型、宿主、版本、输入与实际回答。详见[贡献指南](CONTRIBUTING.md)、[更新记录](CHANGELOG.md)与[来源记录](docs/provenance.json)。

MIT 许可，版权归 blunt 所有。宿主软件与模型适用各自条款。
