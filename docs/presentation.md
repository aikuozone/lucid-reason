# Showcase sources and reproduction

The README now uses a new, publisher-authored **coffee-shop queue** scenario. No screenshots, transcript text, or graphics from the earlier example were used to produce this case.

**[Open the showcase](https://aikuozone.github.io/lucid-reason/)** · [Case guide](../examples/queue-lab/README.md) · [Complete conversation](../examples/queue-lab/conversation.md)

## What is real, and what is simulated

The three-turn conversation was actually executed through Codex CLI **0.160.0**, **gpt-6.1-sol / medium**, with the public **lr 1.1.5** skill. The first turn explicitly selected the skill; later turns resumed the same native session. The runner observed a skill-file read and verified that installed skill files were unchanged. Plugins, apps, hooks and multi-agent features were disabled for this isolated run.

The coffee shop, customer arrivals, and preparation times are synthetic teaching conditions. The questions were written by the publisher to illustrate visual explanation and iterative planning; they are not independent customer feedback. There is no baseline comparison or measured business outcome.

The first turn actually wrote [the interactive lesson](demos/queue-lab/index.html). It is copied byte for byte from the artifact in the [raw result](../examples/queue-lab/source/run/queue-lab-lr-r1.json). The later turns did not edit it. This standalone HTML artifact is **not a native ChatGPT component or interface capture**.

The [case landing page](index.html) is an editorial guide. Its three excerpts must match the corresponding recorded responses exactly; the builder rejects changed quotes. The complete readable conversation retains input and final-response content, with temporary file links redirected to the same artifact in the repository. Raw JSON retains the original paths. Private logs and hidden reasoning are not published.

## Captures and checks

All screenshots and the recording come from an actual Chromium browser rendering the generated lesson and case page. The script operates page controls, scrolls, changes viewports and takes native screenshots; it does not inject replacement content, diagrams, or styles into the generated lesson. The README image is a browser crop of the controls, metrics and chart. Full-page desktop and mobile screenshots are also retained.

The continuous browser recording changes the presets and sliders, then opens the guide to read the three discussion stages. It is an interaction and reading walkthrough, not a replay of the model's generation process. Browser metadata, media hashes and checks are in [capture.json](assets/queue-lab/capture.json).

| Check | Scope |
|---|---|
| Independent closed-form calculation | All **3,721** integer parameter combinations, covering **301,401** customer records and all three summary metrics; one additional fractional case. |
| Input boundaries | Eight invalid inputs rejected. |
| Curve meaning | SVG area equals total customer waiting time for four parameter pairs, including zero waiting and completion after the observation window. |
| User interaction | Both presets reset both parameters; sliders change visible metrics; Home, End and arrow keys work. |
| Mobile | 390 × 844 viewport, working presets, no horizontal page overflow. |
| Case guide | Three stages and three expandable full turns on desktop and mobile. |

The checks verify this generated artifact. They do not establish a general skill-quality improvement or verify the native ChatGPT experience.

## Rebuild the committed case

The exporter uses only the Python standard library and the committed result:

```bash
python3 scripts/build_queue_showcase.py
```

Optional capture tooling requires Playwright, Chromium, browser system libraries and Chinese fonts. These are documentation tools, not plugin runtime dependencies:

```bash
python3 -m venv /tmp/lr-showcase-tools
/tmp/lr-showcase-tools/bin/pip install playwright==1.48.0
/tmp/lr-showcase-tools/bin/playwright install chromium
/tmp/lr-showcase-tools/bin/python scripts/capture_queue_showcase.py --video
```

Use `--browser-executable /path/to/chromium` to select an existing browser. This capture used Chromium **130.0.6723.31**. Missing system libraries and fonts in the recording environment were provided in temporary tooling directories. Pixel-identical rerenders are not expected across environments.

## Run the scenario again

With native Codex authentication, run a new conversation into a fresh output directory:

```bash
python3 scripts/run_evaluation.py --model gpt-6.1-sol --effort medium \
  --scenarios examples/queue-lab/source/scenario.json --variants lr --workers 1 \
  --run-id queue-reproduction --output /tmp/lr-queue-reproduction --timeout 720
```

This makes real model calls. Outputs and the resulting artifact may differ. Do not replace the committed source record with a later run while keeping its screenshots or claims. The [environment](../examples/queue-lab/source/run/environment.json) and [provenance](../examples/queue-lab/source/provenance.json) retain skill hashes, scenario hashes, timestamps and artifact hashes.

The previous [native shared-page provenance](archived-chatgpt-presentation.md) and [CLI card provenance](cli-presentation.md) remain historical records; they are not the source of this new showcase.
