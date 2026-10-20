#!/usr/bin/env python3
"""Render actual evaluation excerpts as a local documentation page and screenshots."""
import argparse
import html
import json
import re
import hashlib
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTED = [("core-01", "Understand the mechanism", "从字段声明到校验、错误与边界", "concept"),
            ("core-07", "Follow the evidence", "依据分路指标建立可证伪假设", "diagnosis"),
            ("core-09", "Update the decision", "新约束出现后，修正受影响的判断", "continuity")]


def inline(text):
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)


def markdown_excerpt(text, limit=650):
    if len(text) > limit:
        boundary = text.rfind("\n\n", 0, limit)
        text = text[:boundary if boundary > limit // 2 else limit]
        if text.count("```") % 2:
            text = text[:text.rfind("```")]
    blocks = []
    code = []
    in_code = False
    table = []
    def flush_table():
        if table:
            rows = [row for row in table if not all(re.fullmatch(r":?-+:?", cell.replace(" ", "")) for cell in row)]
            blocks.append("<table>" + "".join("<tr>" + "".join("<td>"+inline(cell)+"</td>" for cell in row) + "</tr>" for row in rows) + "</table>")
            table.clear()
    for line in text.splitlines():
        if not in_code and line.strip().startswith("|"):
            table.append([cell.strip() for cell in line.strip().strip("|").split("|")])
            continue
        flush_table()
        if line.startswith("```"):
            if in_code:
                blocks.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code = []
            in_code = not in_code
        elif in_code:
            code.append(line)
        elif line.strip():
            line = re.sub(r"^#{1,6}\s+", "", line)
            blocks.append("<p>" + inline(line) + "</p>")
    if code:
        blocks.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
    flush_table()
    return "\n".join(blocks)


def render(input_dir):
    scenarios = {c['id']: c for c in json.loads((ROOT / "evals/scenarios.json").read_text())}
    cards = []
    for index, (case_id, title, subtitle, slug) in enumerate(SELECTED, 1):
        path = input_dir / f"{case_id}-lr-r1.json"
        record = json.loads(path.read_text())
        if record['status'] != 'completed':
            raise ValueError(f"Cannot display an incomplete run: {case_id}")
        question = scenarios[case_id]['turns'][-1]
        answer = record['turns'][-1]['response']
        link = "../" + path.relative_to(ROOT).as_posix()
        cards.append(f'''<article class="case" id="{slug}">
<div class="case-heading"><span class="number">0{index}</span><div><div class="eyebrow">{html.escape(case_id)} / ACTUAL OUTPUT</div><h2>{title}</h2><p class="subtitle">{subtitle}</p></div></div>
<div class="question"><span class="tag">PROMPT{f' · TURN {len(record["turns"])}' if len(record['turns']) > 1 else ''}</span><p>{html.escape(question)}</p></div>
<div class="answer"><span class="tag">RESPONSE EXCERPT · 节选</span>{markdown_excerpt(answer)}<span class="excerpt-end">… 查看完整回答和运行记录</span></div>
<a class="record" href="{link}">Full transcript ↗</a></article>''')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>lucid-reason · Actual evaluation examples</title><style>
*{box-sizing:border-box}body{margin:0;background:#edf1ec;color:#23352f;font-family:Inter,"Noto Sans CJK SC","Microsoft YaHei",Arial,sans-serif;font-size:16px;line-height:1.65}main{max-width:1120px;margin:0 auto;padding:36px}header{background:#14232b;border-radius:22px;padding:48px 52px;color:#f2f4eb;position:relative;overflow:hidden}header:after{content:"lr";position:absolute;right:45px;top:1px;font-size:180px;font-weight:600;letter-spacing:-12px;color:#dceba81c}.brand{font-size:14px;letter-spacing:2px;color:#dceba8;font-weight:700}h1{font-size:46px;line-height:1.18;letter-spacing:-1.5px;margin:22px 0 18px;font-weight:600}header p{max-width:650px;color:#bacbc4;margin:0}.meta{display:flex;gap:10px;margin-top:28px;flex-wrap:wrap}.meta span{border:1px solid #697c6c66;border-radius:30px;padding:5px 12px;font-size:12px;color:#dceba8}.disclosure{font-size:13px;margin:20px 5px 26px;color:#60746b}.case{background:#fff;border:1px solid #dce5dc;border-radius:18px;padding:32px 36px;margin-bottom:22px;box-shadow:0 5px 20px #1d302805}.case-heading{display:flex;align-items:center;gap:22px;margin-bottom:22px}.number{font-size:44px;font-weight:300;color:#8eab81;line-height:1}.eyebrow{font-size:10px;letter-spacing:1.6px;color:#71846e;text-transform:uppercase}h2{font-size:25px;letter-spacing:-.5px;margin:2px 0;font-weight:600}.subtitle{font-size:14px;margin:0;color:#718077}.question{background:#f0f3ec;border-left:3px solid #9fba8c;padding:14px 20px;margin:0 0 18px;border-radius:0 8px 8px 0}.tag{display:block;font-size:10px;letter-spacing:1.4px;font-weight:600;color:#667b63}.question p{font-size:14px;margin:7px 0 0}.answer{font-size:14px;color:#35473e}.answer .tag{margin-bottom:12px}.answer p{margin:8px 0}.answer code{background:#eff3eb;border-radius:4px;padding:1px 4px;font-size:12px}.answer pre{background:#17252c;color:#dceba8;border-radius:10px;padding:18px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.5}.answer pre code{background:none;color:inherit;padding:0}.excerpt-end{display:block;color:#89968b;font-size:12px;margin-top:16px}.record{display:inline-block;font-size:12px;color:#4b7352;text-decoration:none;border-bottom:1px solid #aec69c;margin-top:18px}footer{font-size:12px;color:#6e8073;padding:6px 4px 22px;display:flex;justify-content:space-between;gap:20px}a{color:inherit}@media(max-width:700px){main{padding:16px}header{padding:30px}h1{font-size:34px}.case{padding:24px}.case-heading{gap:14px}h2{font-size:22px}footer{display:block}}
</style></head><body><main><header><div class="brand">LUCID-REASON / LR</div><h1>Reason with context.<br>Make the evidence visible.</h1><p>系统性理解与可靠问题解决。下面展示真实测试中的回答节选，完整输入、输出和限制均可查阅。</p><div class="meta"><span>v1.1.4 · MIT</span><span>Codex CLI 0.160.0</span><span>gpt-6.1-sol · medium</span><span>OFFLINE EVALUATION</span></div></header><p class="disclosure">测试输出排版展示 / Rendered actual test outputs. These are documentation screenshots, not a chat product UI or proof of general superiority.</p>'''
    page += "\n".join(cards)
    page += '''<footer><span>Same source version. Actual responses. Traceable records.</span><a href="../evals/REPORT.md">Method, results & limitations ↗</a></footer></main></body></html>'''
    page = page.replace('</style>', '.answer table{border-collapse:collapse;width:100%;margin:16px 0}.answer td{padding:9px 12px;border:1px solid #dce5dc}.answer tr:first-child{font-weight:600;background:#f0f3ec}</style>')
    destination = ROOT / "docs/showcase.html"
    destination.write_text(page)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "evals/results/release-v1.1.4")
    parser.add_argument("--screenshots", action="store_true")
    parser.add_argument("--browser-executable", type=Path)
    args = parser.parse_args()
    page = render(args.input)
    print(page)
    if args.screenshots:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=str(args.browser_executable) if args.browser_executable else None)
            tab = browser.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1.5)
            tab.goto(page.as_uri(), wait_until="load")
            tab.evaluate("document.fonts.ready")
            for _, _, _, slug in SELECTED:
                tab.locator("#" + slug).screenshot(path=str(ROOT / f"docs/assets/{slug}.png"))
            for case_id, _, _, slug in SELECTED:
                record = json.loads((args.input / f"{case_id}-lr-r1.json").read_text())
                first_paragraph = record['turns'][-1]['response'].split("\n\n")[0]
                summary = '<span class="tag">RESPONSE EXCERPT · 节选</span>' + markdown_excerpt(first_paragraph, 1200)
                tab.locator("#" + slug + " .answer").evaluate("(node, content) => node.innerHTML = content", summary)
            tab.add_style_tag(content="header{padding:34px 40px}h1{font-size:38px;margin:15px 0}.case{padding:23px 30px;margin-bottom:16px}.case-heading{margin-bottom:15px}.question{padding:10px 16px;margin-bottom:13px}.record{margin-top:12px}")
            tab.screenshot(path=str(ROOT / "docs/assets/showcase.png"), full_page=True)
            metadata = {"renderer": "Playwright " + version('playwright'), "browser": browser.version,
                        "viewport": {"width": 1200, "height": 900}, "device_scale_factor": 1.5,
                        "requested_cjk_font": "Noto Sans CJK SC",
                        "description": "Local HTML renderings of actual CLI response excerpts; not screenshots of a chat product UI.",
                        "sources": {}, "screenshots": {}}
            for case_id, _, _, _ in SELECTED:
                source = args.input / f"{case_id}-lr-r1.json"
                metadata['sources'][source.relative_to(ROOT).as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
            for name in ['showcase', 'concept', 'diagnosis', 'continuity']:
                source = ROOT / f'docs/assets/{name}.png'
                metadata['screenshots'][source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
            (ROOT/'docs/assets/rendering.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
            browser.close()


if __name__ == "__main__":
    main()
