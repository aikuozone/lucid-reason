# Installation and compatibility

For the visual learning experience shown in this repository, use **ChatGPT Chat mode** with lucid-reason available in your account or workspace. The same instruction files can also be installed into a Codex project's `.agents/skills` directory for local use and reproducible text evaluation. The skill itself needs no API key or server.

## ChatGPT Chat mode

If your account or workspace has access to lucid-reason, open a Chat conversation, type `@`, and select the plugin or its skill. Ask a natural-language question such as `lr 系统讲解 Transformer`. Explicit selection clarifies the intended skill; `lr` alone is a natural-language hint whose automatic activation depends on the host.

The [real shared conversation](../examples/README.md) demonstrates ChatGPT's native display of the answer, mathematics, diagrams, and a chart. Rendering and interactive tools come from the host. A public shared page may display a different set of features from the original signed-in conversation.

This repository and its release ZIP provide open-source plugin/skill files. They do not automatically install a plugin into a ChatGPT account or create a public catalog listing. Where custom plugin creation or import is available, use that account or workspace's supported authoring workflow with the complete `plugin.json` and `skills/` package. Follow OpenAI's [skill authoring and invocation documentation](https://learn.chatgpt.com/docs/build-skills); import availability is controlled by the host.

## Codex: from source

Requirements: Git, Python 3.10+, and an installed Codex host. The installer uses only the Python standard library.

```bash
git clone https://github.com/aikuozone/lucid-reason.git
cd lucid-reason
python3 scripts/install_skill.py --target /absolute/path/to/your/project/.agents/skills
```

The result is:

```text
your-project/
└── .agents/skills/systematic-knowledge-construction/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── knowledge-architecture.md
        ├── project-engineering.md
        ├── evidence-and-review.md
        └── output-and-evaluation.md
```

Start a new Codex session inside the target project and invoke:

```text
$systematic-knowledge-construction Explain a concept's purpose, mechanism, practical example, and boundaries.
```

The installer copies all files and verifies the staged bytes. Repeating an identical installation is safe. If an existing installation has changed, the installer stops without overwriting it. Back up or move that specific skill directory before updating; do not delete the entire `.agents/skills` collection.

To remove the skill, remove only `your-project/.agents/skills/systematic-knowledge-construction` after preserving any local edits.

## From a release ZIP

Download `lucid-reason-1.1.5.zip` and `SHA256SUMS` from the GitHub release. On Linux, verify the downloaded file in the same directory:

```bash
sha256sum -c SHA256SUMS
```

Extract the ZIP. For local skill installation, copy the complete `skills/systematic-knowledge-construction` directory into the target project's `.agents/skills` directory. Retain `LICENSE` when redistributing the package. Host plugin importers can consume the root `plugin.json` and compatibility overlay according to their own installation workflow; no marketplace import success is claimed here.

## Verification scope

| Path | Status and evidence |
|---|---|
| Python source installer on Linux / Python 3.12 | Automated tests verify complete copy, repeat installation, preservation of edits, and refusal of symlink destinations. |
| Runtime ZIP extraction and installation | Automated test verifies all runtime bytes and installs the extracted skill. |
| Codex CLI 0.160.0 project skill loading | Actual evaluation uses a fresh `.agents/skills` directory and an explicit selector; tool traces record observed reads. See the runtime report. |
| Codex CLI native multi-turn continuation | Evaluated with actual session continuation, not reconstructed conversations. |
| Natural-language `lr` implicit activation | Not measured; selection is controlled explicitly for reproducibility. |
| ChatGPT public shared-page rendering | Real Transformer conversation captured with native formulas, diagrams, and a chart. Original model/skill version unspecified; no parameter-control interaction tested. See the presentation provenance. |
| ChatGPT / Codex desktop marketplace import | Not run. Included manifests and a shared conversation are not proof of a fresh marketplace installation. |
| Windows / macOS installation | Not run in the recorded environment. |

The plugin's display name is lucid-reason. Existing identifiers remain `systematic-knowledge-architect` (plugin) and `systematic-knowledge-construction` (skill), so existing references remain usable.

An existing plugin installation can expose the same skill identifier as a local copy. Keep one active copy in a normal session if duplicate selectors appear. The evaluation disables plugins and installs one local copy to control this condition.

References: [OpenAI skill locations and invocation](https://learn.chatgpt.com/docs/build-skills), [OpenAI plugin documentation](https://learn.chatgpt.com/docs/plugins). Consult the host's current documentation if its installation workflow changes.
