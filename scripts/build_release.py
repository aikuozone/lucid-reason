#!/usr/bin/env python3
"""Build a deterministic runtime plugin ZIP and its SHA-256 checksum."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def runtime_files(root):
    root = Path(root)
    paths = [root / "LICENSE", root / "plugin.json", root / ".codex-plugin/plugin.json"]
    paths += sorted(p for p in (root / "skills").rglob("*") if p.is_file())
    if any(p.is_symlink() for p in (root / "skills").rglob("*")):
        raise ValueError("Runtime files must not be symlinks")
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in paths}


def build(output_dir, root=ROOT):
    root = Path(root)
    version = json.loads((root / "plugin.json").read_text())["version"]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"lucid-reason-{version}.zip"
    files = runtime_files(root)
    files["DISTRIBUTION.md"] = (
        "# lucid-reason runtime plugin\n\n"
        f"Version: {version}. License: MIT.\n\n"
        "Extract the ZIP before installing it. The plugin manifest and skills/ directory "
        "must stay together. For a local Codex skill, copy "
        "skills/systematic-knowledge-construction into your project's .agents/skills/ "
        "directory, then invoke $systematic-knowledge-construction in a new session.\n\n"
        "Source, tested installation instructions, examples, and evaluation limitations: "
        "https://github.com/aikuozone/lucid-reason\n"
    ).encode()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content, compresslevel=9)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    (output_dir / "SHA256SUMS").write_text(f"{digest}  {destination.name}\n")
    return destination, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    path, digest = build(args.output_dir)
    print(f"{path}\nsha256: {digest}")


if __name__ == "__main__":
    main()
