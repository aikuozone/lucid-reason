# Presentation provenance

The README preview and three case images are screenshots of a local documentation page generated from real evaluation records. They do not reproduce a proprietary chat interface or stand in for the original transcripts.

Selected examples were named before final grading: BaseModel mechanisms (`core-01`), evidence-driven RAG diagnosis (`core-07`), and a changed authorization constraint in native follow-up (`core-09`). The preview shows the first paragraph of each actual final response; detailed images contain longer excerpts ending at paragraph boundaries. Full prompts and responses are linked from the [examples](../examples/README.md).

Generate the HTML with standard-library Python:

```bash
python3 scripts/render_showcase.py
```

Open `docs/showcase.html` locally. To regenerate screenshots, supply an installed Playwright and compatible Chromium:

```bash
python3 scripts/render_showcase.py --screenshots
```

`--browser-executable` can select an existing browser. The release was rendered with Playwright 1.48.0, Chromium 130, a 1200×900 viewport, device scale factor 1.5, and Noto Sans CJK SC. The release environment's missing browser libraries and fonts were extracted only into temporary tooling directories; they are not part of the plugin or repository.

[rendering.json](assets/rendering.json) records the actual browser version and source/image checksums. [hero.svg](assets/hero.svg) is an original vector title image. No generated image is presented as evidence of a successful model run.
