#!/usr/bin/env python3
"""Model-assisted rubric assessment of shuffled, anonymized response pairs."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import random
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = {"type": "object", "properties": {
    "assessments": {"type": "array", "items": {"type": "object", "properties": {
        "label": {"type": "string", "enum": ["X", "Y"]},
        "criteria": {"type": "array", "items": {"type": "object", "properties": {
            "index": {"type": "integer"}, "met": {"type": "boolean"},
            "evidence": {"type": "string"}}, "required": ["index", "met", "evidence"], "additionalProperties": False}},
        "note": {"type": "string"}}, "required": ["label", "criteria", "note"], "additionalProperties": False}},
    "preference": {"type": "string", "enum": ["X", "Y", "tie"]},
    "comparison_note": {"type": "string"}},
    "required": ["assessments", "preference", "comparison_note"], "additionalProperties": False}


def grade(pair, case, args):
    baseline, treatment, repetition = pair
    key = f"{case['id']}-r{repetition}"
    folder = args.output
    folder.mkdir(parents=True, exist_ok=True)
    source = {"baseline": baseline, "lr": treatment}
    source_hash = hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    target = folder / f"{key}.json"
    if target.exists():
        saved = json.loads(target.read_text())
        if saved.get("source_sha256") == source_hash:
            return key, "already assessed"
        raise ValueError(f"Changed source for {key}; preserve old judgment and choose another output directory")
    variants = ["baseline", "lr"]
    random.Random(key).shuffle(variants)
    mapping = dict(zip(["X", "Y"], variants))
    payload = {"scenario": case['id'], "questions": case['turns'], "criteria": case['criteria'], "responses": []}
    for label, variant in mapping.items():
        record = source[variant]
        payload["responses"].append({"label": label, "turns": [t['response'] for t in record['turns']],
                                      "runtime_status": record['status'],
                                      "artifact_checks": [c for c in record['artifact_checks'] if c['check'] != 'installed_skill_unchanged'],
                                      "final_fixture_contents": record['artifacts']})
    prompt = ("评估两份匿名回答是否满足同一个任务。仅依据给定问题、实际回答、文件产物和逐项标准。"
              "不要联网或调用工具。每项给 met 布尔值和可核对的具体依据；不要因字数、标题、术语或自称已操作而给分。"
              "实际产物检查优先于回答声称。隐含但正确的覆盖可以满足标准，不要求匹配措辞。"
              "如果有实质差异再选择偏好，否则 tie。长篇附加内容可能降低表达效率。"
              "不要推测条件对应哪种技能；只比较实际回答。\n\n" + json.dumps(payload, ensure_ascii=False))
    with tempfile.TemporaryDirectory(prefix="lr-judge-") as temporary:
        cwd = Path(temporary)
        schema_path = cwd / "schema.json"; schema_path.write_text(json.dumps(SCHEMA))
        answer = cwd / "assessment.json"
        command = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--disable", "plugins",
                   "--disable", "remote_plugin", "--disable", "apps", "--disable", "hooks",
                   "--disable", "multi_agent", "--sandbox", "read-only", "--skip-git-repo-check",
                   "-C", str(cwd), "-m", args.model, "-c", 'model_reasoning_effort="medium"',
                   "--output-schema", str(schema_path), "--json", "-o", str(answer), prompt]
        completed = subprocess.run(command, input="", capture_output=True, text=True, timeout=360)
        if completed.returncode != 0 or not answer.exists():
            raise RuntimeError(f"Judge failed for {key}: exit {completed.returncode}")
        judgment = json.loads(answer.read_text())
        assessed_labels = [a['label'] for a in judgment['assessments']]
        if sorted(assessed_labels) != ["X", "Y"]:
            raise ValueError(f"Judge did not assess both responses for {key}")
        for assessment in judgment['assessments']:
            if sorted(c['index'] for c in assessment['criteria']) != list(range(1, len(case['criteria'])+1)):
                raise ValueError(f"Judge did not cover every criterion for {key}")
        usage = {}
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
                if event.get('type') == 'turn.completed':
                    usage = event.get('usage', {})
            except ValueError:
                pass
    saved = {"scenario": case['id'], "repetition": repetition, "assessment_type": "model_assisted",
             "judge_model": args.model, "source_sha256": source_hash,
             "condition_mapping_revealed_after_assessment": mapping, "judgment": judgment, "usage": usage,
             "limitations": "Same model family as responses; not an independent human evaluation. Output style can partially reveal a condition despite anonymized labels."}
    target.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n")
    return key, "assessed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", type=Path, default=ROOT / "evals/results/release-v1.1.4")
    parser.add_argument("--output", type=Path, default=ROOT / "evals/assessments/release-v1.1.4")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    scenarios = {c['id']: c for c in json.loads((ROOT / "evals/scenarios.json").read_text())}
    pairs = []
    for path in sorted(args.input.glob("*-baseline-r*.json")):
        baseline = json.loads(path.read_text())
        treatment_path = path.with_name(path.name.replace("-baseline-", "-lr-"))
        if treatment_path.exists():
            treatment = json.loads(treatment_path.read_text())
            if baseline['status'] != 'completed' or treatment['status'] != 'completed':
                print(f"{baseline['scenario']}-r{baseline['repetition']}: not assessed; runtime incomplete", flush=True)
                continue
            pairs.append(((baseline, treatment, baseline['repetition']), scenarios[baseline['scenario']]))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(grade, pair, case, args) for pair, case in pairs]
        for future in as_completed(futures):
            key, status = future.result()
            print(f"{key}: {status}", flush=True)


if __name__ == "__main__":
    main()
