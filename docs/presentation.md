# Native ChatGPT presentation provenance

The main README and [showcase](../examples/README.md) use browser screenshots of the author's public [Transformer conversation](https://chatgpt.com/share/6ad6bc80-00d0-83e8-a6c7-f83d75adaf68). The author supplied this link for public presentation. The introduction was reorganized using the author's accompanying project description.

The page title is **系统讲解 Transformer**. Its prompt is `lr 系统讲解 transformer`, followed by one assistant response. The original model and installed skill version are not exposed by the public page; this example is not assigned to the controlled v1.1.4 evaluation. The screenshots show the public shared-page renderer, which can differ from the original signed-in conversation.

## What was captured

| Asset | Native content |
|---|---|
| [opening.png](assets/chatgpt-transformer/opening.png) | The actual user question and beginning of the response. |
| [knowledge-map.png](assets/chatgpt-transformer/knowledge-map.png) | Transformer knowledge map and module responsibilities. |
| [attention.png](assets/chatgpt-transformer/attention.png) | Rendered mathematics and an attention-weight matrix. |
| [architecture.png](assets/chatgpt-transformer/architecture.png) | Encoder–Decoder architecture and explanation. |
| [complexity.png](assets/chatgpt-transformer/complexity.png) | Native chart relating sequence length to attention-position pairs. |
| [full.png](assets/chatgpt-transformer/full.png) | The question and complete response in a single 1440 × 29467 image. |

Preview screenshots use a 1440 × 1100 viewport at device scale factor 1. ChatGPT uses a nested conversation scroller, so a normal `full_page=True` screenshot at that viewport captures only the first screen. For the complete capture, the script enlarges the browser viewport height to include that scroller's entire content. It verifies that the final response fits and that all message text is unchanged before and after resizing. No CSS is injected, messages or graphics replaced, or screenshots stitched together.

The capture waited for the real conversation, fonts, and native rendering. A login-only shell was discarded during inspection. Static diagrams, mathematics, and the chart are visible in the final images. Parameter changes and other interactive behavior were not tested. No follow-up conversation was added to the original.

The [capture record](assets/chatgpt-transformer/capture.json) includes the source URL, UTC timestamp, actual browser and Playwright versions, viewports, message count, rendered element inventory, text checksum, and SHA-256 checksums of every screenshot. Page chrome and relative timestamps reflect the native renderer at capture time. Anonymous account-service errors did not prevent the shared conversation from rendering.

## Reproduce

Screenshot tooling is optional and separate from the plugin and normal offline checks:

```bash
python3 -m venv /tmp/lr-capture-venv
/tmp/lr-capture-venv/bin/pip install playwright==1.48.0
/tmp/lr-capture-venv/bin/playwright install chromium
/tmp/lr-capture-venv/bin/python scripts/capture_chatgpt.py \
  --url https://chatgpt.com/share/6ad6bc80-00d0-83e8-a6c7-f83d75adaf68
```

Provide a browser's required system libraries and Chinese fonts in your environment. `--browser-executable /path/to/chromium` selects an existing browser. This capture used Chromium 130.0.6723.31 and Noto Sans CJK SC. The recorded environment's missing libraries and fonts were extracted into temporary tooling directories; they are not plugin dependencies.

The script is a preset for this Transformer example. It stops on a failed page load, a missing conversation, missing expected sections, changed message content, or a clipped final response. It uses the anonymous public page and does not access account cookies or log in. A future ChatGPT layout or removed share link may require updating the capture preset; rerenders are not expected to have identical pixels.

The screenshots document third-party ChatGPT interface elements; the project's MIT license does not grant rights to third-party branding or software. [hero.svg](assets/hero.svg) is an original project title image. The previous CLI cards and their source records remain separately documented in [CLI presentation provenance](cli-presentation.md).
