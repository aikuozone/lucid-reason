#!/usr/bin/env python3
"""Check packaging invariants; this does not evaluate response quality."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = "systematic-knowledge-construction"
REFERENCE_NAMES = {"knowledge-architecture.md", "project-engineering.md",
                   "evidence-and-review.md", "output-and-evaluation.md"}


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and ((tag == "img" and key == "src") or (tag == "a" and key == "href")):
                self.links.append(value)


def check(root=ROOT):
    root = Path(root).resolve()
    errors = []
    required = ["LICENSE", "README.md", "README.zh-CN.md", "CHANGELOG.md",
                "CONTRIBUTING.md", "docs/installation.md", "docs/evaluation.md",
                "plugin.json", ".codex-plugin/plugin.json", "evals/scenarios.json"]
    for name in required:
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    try:
        portable = json.loads((root / "plugin.json").read_text())
        overlay = json.loads((root / ".codex-plugin/plugin.json").read_text())
        for key in ("name", "version", "description", "author", "keywords"):
            if portable.get(key) != overlay.get(key):
                errors.append(f"Manifest mismatch: {key}")
        if portable["name"] != "systematic-knowledge-architect":
            errors.append("Stable plugin identity changed")
        if not re.fullmatch(r"\d+\.\d+\.\d+", portable["version"]):
            errors.append("Invalid semantic version")
        if portable["extensions"]["com.openai"]["interface"] != overlay["interface"]:
            errors.append("Manifest interface metadata differs")
        if overlay.get("skills") != "./skills":
            errors.append("Compatibility skill discovery path changed")
        if portable.get("author", {}).get("email"):
            errors.append("Public manifest contains a personal contact email")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        errors.append(f"Cannot validate manifests: {exc}")
    skill_dir = root / "skills" / SKILL
    try:
        raw = (skill_dir / "SKILL.md").read_text()
        if not raw.startswith("---\n"):
            raise ValueError("Missing YAML frontmatter")
        fields = yaml.safe_load(raw.split("---", 2)[1])
        if fields.get("name") != SKILL or not isinstance(fields.get("description"), str):
            errors.append("Invalid skill identity or description")
        config = yaml.safe_load((skill_dir / "agents/openai.yaml").read_text())
        if config["policy"]["allow_implicit_invocation"] is not True:
            errors.append("Implicit invocation policy unexpectedly changed")
        if "$" + SKILL not in config["interface"]["default_prompt"]:
            errors.append("Default prompt must name the explicit skill selector")
        if not 25 <= len(config["interface"]["short_description"]) <= 64:
            errors.append("Short description must contain 25–64 characters")
        actual = {p.name for p in (skill_dir / "references").glob("*.md")}
        if actual != REFERENCE_NAMES:
            errors.append("Packaged references differ from the upstream reference set")
    except (ValueError, OSError, KeyError, TypeError, yaml.YAMLError) as exc:
        errors.append(f"Cannot validate skill metadata: {exc}")
    try:
        license_text = (root / "LICENSE").read_text()
        if not (license_text.startswith("MIT License\n") and
                'THE SOFTWARE IS PROVIDED "AS IS"' in license_text):
            errors.append("MIT license is missing or incomplete")
        scenarios = json.loads((root / "evals/scenarios.json").read_text())
        ids = [case["id"] for case in scenarios]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate evaluation scenario IDs")
        if sum(c["group"] == "core" for c in scenarios) != 10:
            errors.append("Expected ten core regression scenarios")
        if sum(c["group"] == "decision" for c in scenarios) != 6:
            errors.append("Expected six decision calibration scenarios")
        if sum(c["group"] == "holdout" for c in scenarios) != 6:
            errors.append("Expected six additional transfer scenarios")
        for case in scenarios:
            if not case.get("turns") or not case.get("criteria"):
                errors.append(f"Scenario lacks turns or criteria: {case['id']}")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        errors.append(f"Cannot validate evaluation cases: {exc}")
    ignored = {".git", "dist", ".evalraw", ".venv", ".agents", "__pycache__"}
    for path in list(root.rglob("*.md")) + list(root.rglob("*.html")):
        if ignored.intersection(path.relative_to(root).parts):
            continue
        raw = path.read_text()
        parser = LocalLinks()
        parser.feed(raw)
        links = re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", raw) + parser.links
        for link in links:
            link = link.strip("<>")
            split = urlsplit(link)
            if split.scheme or link.startswith("#") or not split.path:
                continue
            target = (path.parent / unquote(split.path)).resolve()
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"Broken or nonportable link: {path.relative_to(root)} -> {link}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: packaging, metadata, scenario inventory, and local Markdown links")


if __name__ == "__main__":
    main()
