# Contributing

Useful contributions start with a task the skill handled poorly: an incorrect mechanism, a missed prerequisite, an unjustified decision, a broken project constraint, or a claim without evidence.

Include the host and model, plugin version, complete reproducible prompt, relevant context, actual response, and the observed problem. Remove credentials and private data. Do not post hidden model reasoning or account authentication files.

For instruction changes, prefer a focused correction supported by a real failure. Preserve the existing task scope and invocation identifiers. Avoid universal workflow rules added only to accommodate one example. Update the relevant evaluation case or add a transfer case that can detect the failure without requiring exact wording.

Run before submitting:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_project.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

Static success does not prove behavioral quality. Report runtime and multi-turn testing separately, including failures and tests not run. Model-assisted grading must be identified as such; reproducible source evidence takes precedence over a score.

Keep public `plugin.json` and `.codex-plugin/plugin.json` metadata consistent in shared fields. Their schemas and host-specific layout differ; byte equality is not required.

Contributions are provided under this repository's MIT license. Do not add third-party material unless its license permits redistribution and required notices are included.
