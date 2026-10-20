# Installation and compatibility

The tested route installs the entire skill folder into a project's `.agents/skills` directory. The model and any tools are supplied by Codex; the skill needs no API key or server of its own.

## From source

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

Download `lucid-reason-1.1.4.zip` and `SHA256SUMS` from the GitHub release. On Linux, verify the downloaded file in the same directory:

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
| ChatGPT / Codex desktop marketplace import | Not run. Included manifests are packaging compatibility, not proof of UI installation. |
| Windows / macOS installation | Not run in the recorded environment. |

The plugin's display name is lucid-reason. Existing identifiers remain `systematic-knowledge-architect` (plugin) and `systematic-knowledge-construction` (skill), so existing references remain usable.

An existing plugin installation can expose the same skill identifier as a local copy. Keep one active copy in a normal session if duplicate selectors appear. The evaluation disables plugins and installs one local copy to control this condition.

References: [OpenAI skill locations and invocation](https://learn.chatgpt.com/docs/build-skills), [OpenAI plugin documentation](https://learn.chatgpt.com/docs/plugins). Consult the host's current documentation if its installation workflow changes.
