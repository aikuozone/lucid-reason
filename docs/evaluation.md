# Evaluation method

The repository separates three kinds of evidence:

1. **Offline checks:** metadata, reference paths, packaging, deterministic archives, and conservative installation. These do not prove that a model follows the instructions.
2. **Actual conversations:** native Codex runs in isolated workspaces, preserving full task inputs and final responses. Fixture checks verify real local edits.
3. **Response assessment:** criterion-based, explicitly identified model-assisted judgments and a documented publisher spot review. A model judge is not an independent human study.

The [native ChatGPT showcase](../examples/README.md) is separate presentation evidence: a real user-provided public conversation captured in its original shared-page renderer. It demonstrates the displayed text, formulas, diagrams, and chart. It does not supply a controlled baseline, identify the original model/skill version, validate fresh plugin installation, or test parameter-control interactivity. Its [capture provenance](presentation.md) records exactly what was rendered. CLI evaluation results do not establish ChatGPT frontend behavior.

## Scenario inventory

[scenarios.json](../evals/scenarios.json) contains ten core scenarios and six decision-calibration scenarios derived from the existing v1.1.3 acceptance specification. It also contains six new transfer cases: untrusted retrieved instructions, unsupported private results, a short explanation, an English diagnosis, average concurrency versus peak capacity, and simulated versus real achievements.

The additional cases are publisher-authored, not a sealed independent benchmark. The original cases are visible in the skill references, so performance on them cannot establish generalization by itself.

## Focused verification for v1.1.5

[update-scenarios.json](../evals/update-scenarios.json) covers the seven new upstream acceptance directions and a three-turn planning discussion: evidence boundaries, deployment dependencies, a real scoped edit, audience-appropriate delivery, cross-domain reasoning, necessary redesign, a focused concept, and revision toward a coherent proposal. These scenarios were written with the updated instructions visible.

The update run uses only the lr condition, once per scenario. This is a focused regression check, not a new paired benchmark or a measure of improvement. Runtime completion, source reads, and fixture checks are recorded separately from the coding assistant's review of the actual responses against the criteria. There is no independent human or blinded judge in this review.

```bash
python3 scripts/run_evaluation.py --model gpt-6.1-sol \
  --scenarios evals/update-scenarios.json --variants lr \
  --workers 3 --run-id my-v1.1.5-regression
```

The [update verification record](../evals/UPDATE-1.1.5.md) links every actual response and describes the observations and limits. It does not establish ChatGPT frontend interaction or fresh catalog installation.

## Historical source and version boundaries

The original [v1.1.4 results](../evals/REPORT.md) remain tied to their exact [frozen skill source and manifest](../evals/sources/release-v1.1.4/source.json). Offline checks compare those historical records against that snapshot, rather than the current instructions. The recorded v1.1.4 environment and answers have not been rewritten to use the new version.

Use a fresh run ID after changing source. The runner now rejects an existing run before replacing its environment record, and an incompatible resume leaves the original metadata intact. A successful current package check cannot turn a historical response-quality observation into a claim about the current version.

## Controlled execution

The question and neutral offline instructions are the same in both conditions. The lr condition additionally begins with the explicit `$systematic-knowledge-construction` selector. That intervention is recorded in the full input.

Each condition and scenario uses a fresh temporary workspace and session. Only the lr condition receives an installed skill. User configuration is ignored; plugins, remote plugins, app connections, hooks, and nested agents are disabled for both. The recorded machine has no user-scope `.agents/skills` collection. Built-in Codex system behavior remains present in both conditions.

The model identifier and reasoning effort are fixed by command-line options. The CLI does not expose a seed or temperature for this workflow; their defaults and backend nondeterminism remain limitations. Sandbox permissions are read-only except for two scenarios that require actual scoped file edits. Both conditions receive identical fixtures and permissions.

Multi-turn scenarios use actual native session continuation. The runner checks that the planning-only first turn preserves files and that the authorized second turn changes only the expected fixture. It does not reconstruct prior model answers as a substitute for native continuity.

## Run

Use an installed and authenticated local Codex CLI. This uses the account's allowance and may incur usage depending on that account. Keep account authentication out of public CI.

```bash
python3 scripts/run_evaluation.py --model gpt-6.1-sol --workers 3 --run-id my-evaluation
```

The default run executes all 22 scenarios once in both conditions. For repeated runs, use `--repetitions 3`. To repeat a subset, name scenario IDs with `--cases` and choose a distinct run ID. Do not silently select the best repetition.

Use `--resume-incomplete` to continue an interrupted run with the same model, effort, and frozen source. Completed records are retained, and earlier incomplete attempts are archived. The runner stops queued model calls after observing an account usage limit. It refuses to overwrite an existing run without the explicit resume option.

```bash
python3 scripts/run_evaluation.py --model gpt-6.1-sol \
  --cases core-07 core-08 core-09 decision-03 decision-05 holdout-01 \
  --repetitions 2 --start-repetition 2 --run-id release-v1.1.4
```

The first release uses this predefined six-scenario subset for additional repetitions. Preserve earlier results, runtime errors, unsuccessful tool executions, and rubric failures. The short probe run used to debug the harness is kept separate from the release results and excluded from their counts.

## Records and grading

Each public scenario record includes full user inputs and final responses, condition, repetition, requested model, timing, token usage, command trace summaries, and observed file artifacts. Raw CLI logs stay in ignored `.evalraw/`; they may contain private local details or reasoning events and are not distribution material. Public records intentionally omit hidden reasoning and credentials.

An explicit skill read observed in a tool trace is recorded separately from answer quality. No-skill records must show no such read. A completed runtime does not automatically pass semantic criteria.

The optional `scripts/grade_evaluation.py` evaluates anonymized responses in shuffled condition order. Its rubric is the versioned scenario criteria, with evidence required for every judgment. The same model family is used, so these ratings remain model-assisted assessments rather than independent proof. Preserve the judge output and inspect material failures against the actual responses.

Artifact checks override a model judge's impression about whether a file was actually edited. Report errors, failures, passes, and items not assessed separately. Do not infer response quality from answer length, heading count, keyword matches, or a diagram's presence. Do not publish a percentage as a universal quality or hallucination improvement.

## Known limits

- One local CLI version and one model; no cross-host, cross-model, or statistically powered user study.
- The offline condition cannot measure live citation verification or real business actions.
- Successful explicit selection does not establish reliable implicit activation.
- A small repeated subset gives observations about variation, not a calibrated reliability guarantee.
- More explanation is not necessarily more useful. A baseline answer may already satisfy the task.

Current observations are in the [release evaluation report](../evals/REPORT.md). The official basis for CLI JSON events and continuation is [OpenAI's non-interactive mode documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
