"""Check actual update-run provenance and scoped file artifacts, not prose quality."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals/results/release-v1.1.5"
SKILL = ROOT / "skills/systematic-knowledge-construction"


class UpdateEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.spec = ROOT / "evals/update-scenarios.json"
        self.cases = json.loads(self.spec.read_text())
        self.records = [json.loads(p.read_text()) for p in RESULTS.glob("*-lr-r1.json")]
        self.by_case = {r["scenario"]: r for r in self.records}
        self.environment = json.loads((RESULTS / "environment.json").read_text())

    def test_all_update_scenarios_have_real_completed_turns(self):
        self.assertEqual(len(self.records), len(self.by_case))
        self.assertEqual(set(self.by_case), {c["id"] for c in self.cases})
        for case in self.cases:
            with self.subTest(scenario=case["id"]):
                record = self.by_case[case["id"]]
                self.assertEqual(record["status"], "completed")
                self.assertEqual(record["variant"], "lr")
                self.assertTrue(record["skill_load_observed"])
                self.assertEqual(len(record["turns"]), len(case["turns"]))
                self.assertTrue(all(t["exit_code"] == 0 and t["response"].strip() for t in record["turns"]))
                self.assertTrue(all(c["passed"] for c in record["artifact_checks"]))

    def test_update_records_match_distribution_and_scenario_source(self):
        hashes = {p.relative_to(SKILL).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in SKILL.rglob("*") if p.is_file()}
        self.assertEqual(self.environment["source_version"], json.loads((ROOT / "plugin.json").read_text())["version"])
        self.assertEqual(self.environment["skill_files_sha256"], hashes)
        self.assertEqual(self.environment["scenario_specification_sha256"], hashlib.sha256(self.spec.read_bytes()).hexdigest())
        for record in self.records:
            self.assertEqual(record["installed_skill_files_sha256"], hashes)
            self.assertEqual(record["requested_model"], self.environment["requested_model"])
            self.assertEqual(record["reasoning_effort"], self.environment["reasoning_effort"])

    def test_actual_edit_preserves_first_turn_and_final_scope(self):
        for case in self.cases:
            if not case.get("fixtures"):
                continue
            record = self.by_case[case["id"]]
            checks = {c["check"]: c["passed"] for c in record["artifact_checks"]}
            self.assertTrue(checks["first_turn_preserves_files"])
            for name, expected in case["expected_json"].items():
                self.assertEqual(json.loads(record["artifacts"][name]), expected)
                self.assertTrue(checks[f"json_values:{name}"])


if __name__ == "__main__":
    unittest.main()
