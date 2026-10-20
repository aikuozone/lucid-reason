#!/usr/bin/env python3
"""Summarize observed results, with execution and judgment kept separate."""
from collections import Counter
import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]


def generate():
    folder = ROOT / 'evals/results/release-v1.1.4'
    records = {p.stem: json.loads(p.read_text()) for p in folder.glob('*-r*.json')}
    cases = json.loads((ROOT / 'evals/scenarios.json').read_text())
    assessment_folder = ROOT / 'evals/assessments/release-v1.1.4'
    assessments = {p.stem: json.loads(p.read_text()) for p in assessment_folder.glob('*.json')}
    grades = {}
    preferences = {1: Counter(), 2: Counter(), 3: Counter()}
    unmet = []
    for key, record in assessments.items():
        mapping = record['condition_mapping_revealed_after_assessment']
        for assessment in record['judgment']['assessments']:
            variant = mapping[assessment['label']]
            missing = [c for c in assessment['criteria'] if not c['met']]
            grades[(record['scenario'], variant, record['repetition'])] = 'pass' if not missing else 'fail'
            for criterion in missing:
                unmet.append((record['scenario'], variant, record['repetition'], criterion))
        choice = record['judgment']['preference']
        preferences[record['repetition']][mapping.get(choice, choice)] += 1
    statuses = Counter(r['status'] for r in records.values())
    count = len(records)
    checks = [check for r in records.values() for check in r['artifact_checks']]
    model = json.loads((folder/'environment.json').read_text())
    lines = ['# Release evaluation: v1.1.4', '',
        'Recorded on 2026-10-20. This report describes one model and one local CLI host. It is not a cross-model benchmark or an independent human study.', '',
        f'Observed execution: **{statuses.get("completed",0)} of {count} recorded conversations completed**. '
        f'The set contains 22 scenarios in two conditions, plus two extra repetitions for six preselected scenarios. '
        f'There are **{sum(c["passed"] for c in checks)} passing and {sum(not c["passed"] for c in checks)} failing artifact/integrity observations**. '
        'A completed conversation means the scenario finished; it does not mean every intermediate tool invocation succeeded.', '',
        f'Environment: `{model["cli_version"]}`, requested model `{model["requested_model"]}`, reasoning effort `{model["reasoning_effort"]}`. '
        'The lr condition explicitly selects the installed skill. The baseline has no installed skill; plugins and app connections are disabled in both conditions.', '',
        '[Method and limitations](../docs/evaluation.md) · [Scenario inputs and criteria](scenarios.json) · '
        '[Environment and frozen source](results/release-v1.1.4/environment.json) · [Examples](../examples/README.md)', '',
        '## Offline distribution checks', '']
    offline_path = ROOT/'evals/offline-checks.json'
    if offline_path.exists():
        offline = json.loads(offline_path.read_text())
        for item in offline['checks']:
            lines.append(f'- `{item["command"]}`: **{item["result"]}**.')
        lines += ['', '[Observed command results](offline-checks.json). Checks cover installation, edit preservation, archive completeness, byte reproducibility, reference paths, and the provenance of published runtime records.', '']
    else:
        lines += ['Not yet recorded. No passing offline-test claim is made until the command results are present.', '']
    lines += ['## Primary paired scenarios', '',
              'The following pass/fail labels are **model-assisted rubric judgments**. Each row links actual inputs and final responses. They are separate from execution status and file checks.', '',
              '| Scenario | Baseline | lr | Assessment |', '|---|---|---|---|']
    for case in cases:
        key = case['id']
        cells = []
        for variant in ['baseline', 'lr']:
            record = records.get(f'{key}-{variant}-r1')
            status = grades.get((key, variant, 1), 'not_assessed')
            if not record or record['status'] != 'completed':
                status = record['status'] if record else 'not_run'
            cells.append(f'[{status}](results/release-v1.1.4/{key}-{variant}-r1.json)')
        judge_link = f'[criteria](assessments/release-v1.1.4/{key}-r1.json)' if f'{key}-r1' in assessments else 'not_assessed'
        lines.append(f'| {key} · {case["title"]} | {cells[0]} | {cells[1]} | {judge_link} |')
    primary = {variant: Counter(grades.get((c['id'], variant, 1), 'not_assessed') for c in cases) for variant in ['baseline','lr']}
    lines += ['', 'Primary rubric totals: ' + '; '.join(f'**{variant}**: '+', '.join(f'{n} {label}' for label,n in values.items()) for variant,values in primary.items()) + '.', '',
              'Primary pair preferences from the same-model judge: ' + ', '.join(f'{key}={value}' for key,value in sorted(preferences[1].items())) + '. '
              'These are small-suite observations, not estimates of a universal success rate or a hallucination reduction.', '',
              '## Repeated boundary scenarios', '',
              '| Scenario | Recorded conditions / repetitions | Rubric observations |', '|---|---|---|']
    repeated = ['core-07','core-08','core-09','decision-03','decision-05','holdout-01']
    for key in repeated:
        found = [r for r in records.values() if r['scenario']==key]
        observed = Counter(grades.get((key,r['variant'],r['repetition']), 'not_assessed') for r in found)
        lines.append(f'| {key} | {len(found)} conversations, expected 6 across both conditions × 3 repetitions | '+', '.join(f'{n} {k}' for k,n in observed.items())+' |')
    lines += ['', 'All repetitions are retained. Repetition adds observations about variation, but this small subset does not establish a reliability guarantee.', '',
              '## Unmet rubric items', '']
    if not unmet:
        lines += ['No unmet criteria were recorded in the available assessments. Unassessed items remain unassessed.', '']
    for case, variant, repetition, criterion in unmet:
        lines.append(f'- `{case}` / `{variant}` / repetition {repetition}, criterion {criterion["index"]}: {criterion["evidence"]} '
                     f'[Assessment](assessments/release-v1.1.4/{case}-r{repetition}.json).')
    lines += ['', 'The publisher’s release agent spot-reviewed selected claims and the two primary baseline omissions. This is a disclosed model-based review, not a human expert panel. '
              'See [spot-review evidence](release-agent-review.json).', '',
              '## Observed resource use', '',
              '| Condition | Conversations | CLI input tokens | CLI output tokens | Median scenario duration |', '|---|---:|---:|---:|---:|']
    for variant in ['baseline','lr']:
        selected = [r for r in records.values() if r['variant']==variant and r['status']=='completed']
        inputs = sum(t.get('usage',{}).get('input_tokens',0) for r in selected for t in r['turns'])
        outputs = sum(t.get('usage',{}).get('output_tokens',0) for r in selected for t in r['turns'])
        durations = [sum(t['elapsed_seconds'] for t in r['turns']) for r in selected]
        lines.append(f'| {variant} | {len(selected)} | {inputs:,} | {outputs:,} | {median(durations):.1f}s |' if durations else f'| {variant} | 0 | 0 | 0 | not_run |')
    lines += ['', 'Token counts include cached input and are not billed dollar estimates. Durations include local CLI startup, model work, and tool execution under concurrent testing; they are not production latency measurements.', '',
              '## Preparation and interrupted attempts', '',
              '- Initial discovery and native-continuation probes are retained in [probe-discovery](results/probe-discovery/environment.json), outside release counts.',
              '- One initial export had an extra trailing newline. Its successful response was retained as an [export-normalization probe](results/probe-export-normalization/NOTE.md); the affected case was rerun against exact upstream instruction bytes.',
              '- Before recovery, the release result set contained 16 completed conversations and 28 account-limit interruptions. [Earlier incomplete attempts](results/release-v1.1.4/previous-attempts/) are preserved. A fresh recovery check succeeded; only incomplete items were rerun, without changing their model, effort, criteria, or instructions. One original scenario JSON was replaced during recovery; its original service-error events are retained with that limitation stated explicitly.',
              '- An independent fresh agent forward task initially hit the same limit, then completed after recovery. Its [input](forward-test/input.md), [actual answer](forward-test/answer.md), and [execution limits](forward-test/metadata.json) are outside the paired counts.', '',
              '## Interpretation and untested paths', '',
              'The baseline model already meets most criteria in this suite. The observed differences concern specific verification and acceptance details; they do not demonstrate that lr improves every task. The skill also adds context and can produce longer responses. Keep the raw records and judge limitations in view when deciding whether to use it.', '',
              'A specific observed gap remains: both English diagnosis responses lacked explicit rollback trigger conditions required by the rubric. The answers still provide useful hypothesis and measurement plans, but this item is retained as unmet rather than silently passed. No semantic instruction change was made solely to fit this one case.', '',
              'Live web verification, real business systems, implicit activation, desktop marketplace import, and Windows/macOS host installation were not tested. The six transfer cases are publisher-authored; the original 16 cases are visible in the skill’s own specification. No independent sealed benchmark, long-term memory, or universal safety guarantee is claimed.', '']
    (ROOT/'evals/REPORT.md').write_text('\n'.join(lines))
    print(f'Report generated: {count} runtime records, {len(assessments)} paired assessments')


if __name__=='__main__':
    generate()
