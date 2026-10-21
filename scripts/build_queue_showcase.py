#!/usr/bin/env python3
"""Export the recorded queue lesson without rewriting model output.

Run the recorded scenario first. This is documentation tooling, not plugin code.
"""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'examples/queue-lab'
RECORD = CASE / 'source/run/queue-lab-lr-r1.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export():
    record = json.loads(RECORD.read_text())
    env = json.loads((RECORD.parent / 'environment.json').read_text())
    spec = json.loads((CASE / 'source/scenario.json').read_text())[0]
    if (digest(CASE / 'source/scenario.json') != env['scenario_specification_sha256']
            or record['installed_skill_files_sha256'] != env['skill_files_sha256']):
        raise ValueError('Scenario or installed skill hashes do not match the recorded environment')
    if (record['status'] != 'completed' or len(record['turns']) != 3
            or not record['skill_load_observed']
            or not all(item['passed'] for item in record['artifact_checks'])):
        raise ValueError('A completed three-turn run with the skill observed is required')
    lesson = record['artifacts']['explanation.html']
    if not lesson or 'window.queueLab' not in lesson:
        raise ValueError('Missing generated interactive lesson')
    (ROOT / 'docs/demos/queue-lab/index.html').write_text(lesson)
    text = ['# 排队案例：完整真实运行记录', '',
            '虚构教学案例；问题由项目维护方编写，回答来自一次连续的原生 Codex 运行。', '',
            f"- 插件：lucid-reason {env['source_version']}",
            f"- 宿主：{env['cli_version']}；模型：{env['requested_model']}；推理设置：{env['reasoning_effort']}",
            '- 第一轮显式选择技能，后两轮在同一原生会话中继续；没有对照组。',
            '- 这是合成情景；运行真实，门店与经营结果并非实测。',
            '- 以下保留输入与最终回答全文；未公开隐藏推理或原始私有日志。', '',
            '[交互页面](https://aikuozone.github.io/lucid-reason/demos/queue-lab/) · '
            '[运行 JSON](source/run/queue-lab-lr-r1.json) · [运行环境](source/run/environment.json)', '']
    text += ['仅将回答中的临时工作区文件链接改为仓库中对应页面；其他回答内容保留。运行 JSON 保留原始路径。', '']
    for i, turn in enumerate(record['turns'], 1):
        if turn['exit_code'] != 0 or not turn['input'].endswith(spec['turns'][i-1]):
            raise ValueError(f'Incomplete or inconsistent turn {i}')
        text += [f'## 第 {i} 轮', '', '### 完整输入', '', turn['input'].rstrip(), '',
                 '### 完整回答', '', portable_response(turn['response']).rstrip(), '']
    (CASE / 'conversation.md').write_text('\n'.join(text))
    provenance = {
        'kind': 'publisher-authored synthetic scenario, actual native model run',
        'host': env['cli_version'], 'model': env['requested_model'],
        'reasoning_effort': env['reasoning_effort'], 'plugin_version': env['source_version'],
        'started_at': record['started_at'], 'completed_at': record['completed_at'],
        'native_session_turns': len(record['turns']), 'skill_read_observed': True,
        'path_base': 'repository root',
        'scenario': 'examples/queue-lab/source/scenario.json',
        'record': 'examples/queue-lab/source/run/queue-lab-lr-r1.json',
        'generated_artifact': 'docs/demos/queue-lab/index.html',
        'artifact_editorial_changes': 'none; copied verbatim from the recorded artifact',
        'readable_transcript_changes': 'Temporary absolute explanation.html links point to the corresponding repository artifact; the raw JSON is unchanged',
        'files_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [
            RECORD, RECORD.parent / 'environment.json', CASE / 'source/scenario.json',
            ROOT / 'docs/demos/queue-lab/index.html', CASE / 'conversation.md']},
        'boundaries': ['Not a native ChatGPT UI capture',
                       'No independently measured store outcomes or skill-versus-baseline comparison',
                       'Landing-page summaries are editorial; quotes must match recorded responses']}
    (CASE / 'source/provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
    render_landing(record)
    print('Exported the original lesson, full conversation, case page and provenance')


def portable_response(text, target='../../docs/demos/queue-lab/index.html'):
    import re
    return re.sub(r'/tmp/lr-eval-[^/\s)]+/queue-lab-lr-r1/explanation\.html', target, text)


def render_landing(record):
    stories = json.loads((CASE / 'source/story.json').read_text())
    sections = []
    for i, story in enumerate(stories, 1):
        if story['quote'] not in record['turns'][i-1]['response']:
            raise ValueError(f'Quote for turn {i} differs from the original response')
        esc = {key: html.escape(value) for key, value in story.items()}
        sections.append(f"""<article class="story"><div class="stage"><b>0{i}</b>{esc['stage']}</div>
<div><h3>{esc['title']}</h3><p class="prompt"><strong>本轮提问摘要：</strong>{esc['prompt_summary']}</p>
<blockquote><p>{esc['quote']}</p><div class="quote-label">第 {i} 轮原回答节选</div></blockquote>
<p>{esc['summary']}</p><p class="why">{esc['value']}</p></div></article>""")
    transcript = []
    for i, turn in enumerate(record['turns'], 1):
        transcript.append(f"""<details id="turn-{i}"><summary>展开第 {i} 轮完整输入与回答</summary>
<p class="label">完整输入（含实际运行前缀）</p><pre class="verbatim full-prompt">{html.escape(turn['input'])}</pre>
<p class="label">完整最终回答（Markdown 文本；临时文件链接已替换）</p><pre class="verbatim">{html.escape(portable_response(turn['response'], 'demos/queue-lab/'))}</pre></details>""")
    template = (ROOT / 'scripts/templates/queue-showcase.html.in').read_text()
    output = template.replace('$STORIES', '\n'.join(sections)).replace('$TRANSCRIPT', '\n'.join(transcript))
    (ROOT / 'docs/index.html').write_text(output)


if __name__ == '__main__':
    export()
