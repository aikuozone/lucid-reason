#!/usr/bin/env python3
"""Capture an authorized public ChatGPT example with its native page renderer.

Optional documentation tooling: pip install playwright && playwright install chromium.
This script does not sign in, generate responses, or recreate the ChatGPT interface.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Public shared conversation you may publish")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/assets/chatgpt-transformer")
    parser.add_argument("--browser-executable", type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"https://chatgpt\.com/share/[a-f0-9-]+", args.url):
        parser.error("Use an https://chatgpt.com/share/ conversation URL")
    try:
        from importlib.metadata import version
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install optional Playwright tooling; see docs/presentation.md") from exc

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    viewport = {"width": 1440, "height": 1100}
    previews = [
        ("knowledge-map.png", "2. Transformer 的整体知识地图"),
        ("attention.png", "第一步：计算 Q 和 K 的匹配程度"),
        ("architecture.png", "1. 原始 Encoder–Decoder 架构"),
        ("complexity.png", "1. Attention 为什么存在长上下文成本问题？"),
    ]
    with sync_playwright() as p:
        launch = {"headless": True}
        if args.browser_executable:
            launch["executable_path"] = str(args.browser_executable)
        browser = p.chromium.launch(**launch)
        page = browser.new_page(viewport=viewport, device_scale_factor=1, color_scheme="light")
        response = page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        if response is None or response.status != 200:
            raise RuntimeError("The public page did not return HTTP 200")
        assistant = page.locator('[data-message-author-role="assistant"]')
        assistant.last.wait_for(timeout=90000)
        page.wait_for_function("""() => {
          const messages = [...document.querySelectorAll('[data-message-author-role="assistant"]')];
          return messages.reduce((n, e) => n + e.innerText.length, 0) > 10000;
        }""", timeout=60000)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(8000)
        # Force lazy content to enter view before recording the whole conversation.
        assistant.last.scroll_into_view_if_needed()
        page.wait_for_timeout(3000)
        before = page.locator('[data-message-author-role]').all_text_contents()
        prompt = page.locator('[data-message-author-role="user"]').first.inner_text()
        if "transformer" not in prompt.lower():
            raise RuntimeError("This capture preset expects the Transformer example")
        scroller = page.evaluate_handle("""() => {
          let e = document.querySelector('[data-message-author-role="assistant"]');
          while(e) {
            if(e.scrollHeight > e.clientHeight + 100 && /auto|scroll/.test(getComputedStyle(e).overflowY)) return e;
            e = e.parentElement;
          }
          throw Error('Conversation scroll container not found');
        }""")
        scroller.evaluate("e => e.scrollTop = 0")
        page.wait_for_timeout(500)
        page.screenshot(path=str(output / "opening.png"))
        offsets = {}
        for filename, heading in previews:
            node = page.get_by_role("heading", name=heading, exact=True)
            node.wait_for()
            node.evaluate("""e => {
              let s = e.parentElement;
              while(s && !(s.scrollHeight > s.clientHeight + 100 && /auto|scroll/.test(getComputedStyle(s).overflowY))) s=s.parentElement;
              if(!s) throw Error('Scroll container not found');
              s.scrollTop += e.getBoundingClientRect().top - s.getBoundingClientRect().top - 85;
            }""")
            page.wait_for_timeout(1000)
            offsets[filename] = round(scroller.evaluate("e => e.scrollTop"), 2)
            page.screenshot(path=str(output / filename))

        inventory = assistant.evaluate_all("""nodes => ({
          messages:nodes.length,
          characters:nodes.reduce((n,e)=>n+e.innerText.length,0),
          tables:nodes.reduce((n,e)=>n+e.querySelectorAll('table').length,0),
          svgElements:nodes.reduce((n,e)=>n+e.querySelectorAll('svg').length,0),
          rangeInputs:nodes.reduce((n,e)=>n+e.querySelectorAll('input[type=range]').length,0),
          chartOptionButtons:nodes.reduce((n,e)=>n+e.querySelectorAll('button[aria-label="Chart options"]').length,0)
        })""")
        # Native layout, no injected CSS: enlarge only the viewport so the nested
        # conversation scroller can be captured from first message to final answer.
        scroller.evaluate("e => e.scrollTop = 0")
        full_height = scroller.evaluate("e => e.scrollHeight") + 100
        for _ in range(3):
            if full_height > 60000:
                raise RuntimeError("Conversation exceeds this preset's safe screenshot height")
            page.set_viewport_size({"width": viewport["width"], "height": full_height})
            page.wait_for_timeout(1500)
            missing = scroller.evaluate("e => e.scrollHeight - e.clientHeight")
            if missing <= 1:
                break
            full_height += missing + 20
        else:
            raise RuntimeError("Could not expose the full conversation in the viewport")
        scroller.evaluate("e => e.scrollTop = 0")
        after = page.locator('[data-message-author-role]').all_text_contents()
        if before != after:
            raise RuntimeError("Conversation text changed while capturing; inspect before publication")
        last = assistant.last.bounding_box()
        if last is None or last["y"] + last["height"] > full_height:
            raise RuntimeError("The final answer is clipped")
        page.screenshot(path=str(output / "full.png"), full_page=True, timeout=60000)
        metadata = {
            "source_url": args.url,
            "page_title": page.title(),
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_kind": "User-provided public ChatGPT shared conversation",
            "original_model": "Not exposed by the public page",
            "original_skill_version": "Not exposed by the public page",
            "prompt": prompt,
            "message_count": len(before),
            "message_text_sha256": digest(json.dumps(before, ensure_ascii=False).encode()),
            "playwright_version": version("playwright"),
            "browser_version": browser.version,
            "preview_viewport": viewport,
            "full_viewport": {"width": viewport["width"], "height": full_height},
            "device_scale_factor": 1,
            "preview_scroll_offsets": offsets,
            "rendered_inventory": inventory,
            "capture_method": "Native browser screenshots. Full capture enlarges viewport height only; no CSS, message, diagram, or UI replacement; no stitching.",
            "interaction_validation": "Static rendering only; no parameter changes or interactive behavior asserted.",
            "images": {f.name: {"bytes": f.stat().st_size, "sha256": digest(f.read_bytes())}
                       for f in sorted(output.glob("*.png"))},
        }
        (output / "capture.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        browser.close()
    print(json.dumps({"output": str(output), "message_count": len(before), "full_height": full_height,
                      "images": list(metadata["images"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
