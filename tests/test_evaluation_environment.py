"""Protect recorded evaluation provenance during reruns and source upgrades."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("lr_evaluation", ROOT / "scripts/run_evaluation.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "environment.json"
        self.metadata = {"source_version": "1.1.4", "skill_files_sha256": {"SKILL.md": "old"},
                         "requested_model": "recorded-model", "reasoning_effort": "medium",
                         "scenario_specification_sha256": "cases"}

    def test_new_environment_is_recorded(self):
        RUNNER.save_environment(self.path, self.metadata)
        self.assertEqual(json.loads(self.path.read_text()), self.metadata)

    def test_existing_run_is_not_overwritten_without_resume(self):
        original = json.dumps(self.metadata, indent=4) + "\n"
        self.path.write_text(original)
        with self.assertRaises(ValueError):
            RUNNER.save_environment(self.path, {**self.metadata, "source_version": "1.1.5"})
        self.assertEqual(self.path.read_text(), original)

    def test_incompatible_resume_preserves_original_bytes(self):
        original = json.dumps(self.metadata, indent=4) + "\n"
        self.path.write_text(original)
        changes = {"source_version": "1.1.5", "skill_files_sha256": {"SKILL.md": "new"},
                   "requested_model": "other-model", "reasoning_effort": "high",
                   "scenario_specification_sha256": "other-cases"}
        for key, value in changes.items():
            with self.subTest(changed=key):
                with self.assertRaises(ValueError):
                    RUNNER.save_environment(self.path, {**self.metadata, key: value}, resume=True)
                self.assertEqual(self.path.read_text(), original)

    def test_compatible_resume_keeps_original_record(self):
        previous = {**self.metadata, "original_note": "keep this observation"}
        original = json.dumps(previous, indent=4) + "\n"
        self.path.write_text(original)
        RUNNER.save_environment(self.path, {**self.metadata, "new_note": "not an original observation"}, resume=True)
        self.assertEqual(self.path.read_text(), original)


if __name__ == "__main__":
    unittest.main()
