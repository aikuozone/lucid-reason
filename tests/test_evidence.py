"""Ensure published runtime claims remain tied to real, versioned observations."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals/results/release-v1.1.4"
SKILL = ROOT / "skills/systematic-knowledge-construction"


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / "evals/scenarios.json").read_text())
        self.records = [json.loads(p.read_text()) for p in RESULTS.glob("*-r*.json")]
        self.by_key = {(r['scenario'], r['variant'], r['repetition']): r for r in self.records}

    def test_every_scenario_has_two_completed_primary_conditions(self):
        for case in self.cases:
            for variant in ['baseline', 'lr']:
                with self.subTest(scenario=case['id'], variant=variant):
                    record = self.by_key[(case['id'], variant, 1)]
                    self.assertEqual(record['status'], 'completed')
                    self.assertEqual(len(record['turns']), len(case['turns']))
                    self.assertTrue(all(t['response'].strip() and t['exit_code'] == 0 for t in record['turns']))

    def test_observed_skill_reads_and_frozen_source(self):
        hashes = {p.relative_to(SKILL).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in SKILL.rglob('*') if p.is_file()}
        for record in self.records:
            with self.subTest(scenario=record['scenario'], variant=record['variant'], repetition=record['repetition']):
                self.assertEqual(record['status'], 'completed')
                self.assertEqual(record['skill_load_observed'], record['variant'] == 'lr')
                self.assertEqual(record['installed_skill_files_sha256'], hashes if record['variant'] == 'lr' else {})

    def test_authorized_fixture_changes_match_actual_artifacts(self):
        for case in self.cases:
            if not case.get('fixtures'):
                continue
            for variant in ['baseline', 'lr']:
                record = self.by_key[(case['id'], variant, 1)]
                self.assertTrue(all(c['passed'] for c in record['artifact_checks']))
                for name, expected in case.get('expected', {}).items():
                    self.assertEqual(record['artifacts'][name], expected)
                for name, expected in case.get('expected_json', {}).items():
                    self.assertEqual(json.loads(record['artifacts'][name]), expected)

    def test_environment_matches_records_and_source_version(self):
        environment = json.loads((RESULTS / 'environment.json').read_text())
        self.assertEqual(environment['source_version'], json.loads((ROOT/'plugin.json').read_text())['version'])
        for record in self.records:
            self.assertEqual(record['requested_model'], environment['requested_model'])
            self.assertEqual(record['reasoning_effort'], environment['reasoning_effort'])


if __name__ == '__main__':
    unittest.main()
