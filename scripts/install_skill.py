#!/usr/bin/env python3
"""Install the complete instruction-only skill without overwriting local edits."""
import argparse
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "systematic-knowledge-construction"


def file_map(folder):
    if any(p.is_symlink() for p in folder.rglob("*")):
        raise ValueError("Symlinks are not accepted in an installed skill")
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in folder.rglob("*") if p.is_file()}


def install(target, source=None):
    source = Path(source or ROOT / "skills" / SKILL_NAME)
    target = Path(target).expanduser()
    if target.is_symlink():
        raise ValueError("The target directory must not be a symlink")
    files = file_map(source)
    if "SKILL.md" not in files:
        raise ValueError("Source is missing SKILL.md")
    target.mkdir(parents=True, exist_ok=True)
    destination = target / SKILL_NAME
    if destination.is_symlink():
        raise ValueError("The destination must not be a symlink")
    if destination.exists():
        if destination.is_dir() and file_map(destination) == files:
            return destination, "already installed"
        raise FileExistsError(f"Refusing to overwrite {destination}; back it up first")
    with tempfile.TemporaryDirectory(prefix=".lr-install-", dir=target) as staging:
        staged = Path(staging) / SKILL_NAME
        shutil.copytree(source, staged)
        if file_map(staged) != files:
            raise ValueError("Staged files differ from the source")
        staged.rename(destination)
    return destination, "installed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True,
                        help="Skill collection directory, e.g. /project/.agents/skills")
    args = parser.parse_args()
    try:
        destination, status = install(args.target)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Installation failed: {exc}\n")
    print(f"{status}: {destination}")


if __name__ == "__main__":
    main()
