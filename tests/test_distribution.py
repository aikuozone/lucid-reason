import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


installer = module("install_skill")
builder = module("build_release")
validator = module("validate_project")


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def copy_project(self):
        destination = self.directory / "project"
        shutil.copytree(ROOT, destination,
                        ignore=shutil.ignore_patterns(".git", "dist", ".evalraw", "__pycache__", ".venv"))
        return destination

    def test_project_invariants(self):
        self.assertEqual(validator.check(ROOT), [])

    def test_manifest_drift_is_rejected(self):
        copy = self.copy_project()
        path = copy / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text()); data["version"] = "0.0.0"
        path.write_text(json.dumps(data))
        self.assertTrue(any("Manifest mismatch: version" in e for e in validator.check(copy)))

    def test_missing_reference_is_rejected(self):
        copy = self.copy_project()
        (copy / "skills" / installer.SKILL_NAME / "references/evidence-and-review.md").unlink()
        errors = validator.check(copy)
        self.assertTrue(any("Broken or nonportable link" in e for e in errors))

    def test_invalid_frontmatter_is_rejected(self):
        copy = self.copy_project()
        path = copy / "skills" / installer.SKILL_NAME / "SKILL.md"
        path.write_text("not YAML frontmatter\n")
        self.assertTrue(any("frontmatter" in e for e in validator.check(copy)))

    def test_broken_html_image_is_rejected(self):
        copy = self.copy_project()
        (copy / "README.md").write_text('<img src="docs/assets/missing.png">')
        self.assertTrue(any("missing.png" in e for e in validator.check(copy)))

    def test_installer_copies_all_reference_bytes(self):
        destination, status = installer.install(self.directory / ".agents/skills")
        source = ROOT / "skills" / installer.SKILL_NAME
        self.assertEqual(installer.file_map(source), installer.file_map(destination))
        self.assertEqual(status, "installed")

    def test_identical_install_is_idempotent(self):
        target = self.directory / "skills"
        installer.install(target)
        _, status = installer.install(target)
        self.assertEqual(status, "already installed")
        self.assertFalse(list(target.glob(".lr-install-*")))

    def test_local_edits_are_preserved(self):
        target = self.directory / "skills"
        destination, _ = installer.install(target)
        path = destination / "SKILL.md"
        path.write_text("my local modification")
        with self.assertRaises(FileExistsError):
            installer.install(target)
        self.assertEqual(path.read_text(), "my local modification")

    def test_symlink_destination_is_rejected(self):
        target = self.directory / "skills"; target.mkdir()
        elsewhere = self.directory / "elsewhere"; elsewhere.mkdir()
        (target / installer.SKILL_NAME).symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaises(ValueError):
            installer.install(target)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlink_source_is_rejected(self):
        source = self.directory / "source"; source.mkdir()
        (source / "SKILL.md").write_text("example")
        (source / "leak").symlink_to(ROOT / "LICENSE")
        with self.assertRaises(ValueError):
            installer.install(self.directory / "skills", source)

    def test_archive_contains_exact_runtime_files_and_hidden_manifest(self):
        archive, _ = builder.build(self.directory)
        with zipfile.ZipFile(archive) as z:
            expected = builder.runtime_files(ROOT)
            self.assertEqual(set(z.namelist()), set(expected) | {"DISTRIBUTION.md"})
            for name, content in expected.items():
                self.assertEqual(z.read(name), content)
            self.assertIn(".codex-plugin/plugin.json", z.namelist())
            self.assertFalse(any(n.startswith("/") or ".." in Path(n).parts for n in z.namelist()))

    def test_archive_is_reproducible(self):
        first, first_digest = builder.build(self.directory / "first")
        second, second_digest = builder.build(self.directory / "second")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(first_digest, second_digest)
        self.assertEqual(hashlib.sha256(first.read_bytes()).hexdigest(), first_digest)

    def test_extracted_archive_can_be_installed(self):
        archive, _ = builder.build(self.directory / "dist")
        extracted = self.directory / "unpacked"
        with zipfile.ZipFile(archive) as z:
            z.extractall(extracted)
        destination, _ = installer.install(self.directory / "fresh/.agents/skills",
                                            extracted / "skills" / installer.SKILL_NAME)
        self.assertEqual(installer.file_map(destination),
                         installer.file_map(ROOT / "skills" / installer.SKILL_NAME))


if __name__ == "__main__":
    unittest.main()
