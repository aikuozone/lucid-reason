#!/usr/bin/env python3
"""Run native Codex skill / no-skill conversations in separate workspaces.

Uses existing local Codex authentication. Never put account auth in public CI.
Runtime errors are recorded as errors, never converted into passing tests.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("lr_installer", ROOT / "scripts/install_skill.py")
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)
COMMON = ("当前是离线测试；不要联网或调用外部连接。可读取工作区中已安装的技能。"
          "只为当前任务操作工作区中提供的项目文件，不修改评测环境或技能。"
          "缺少信息时说明假设，不虚构来源、数据或工具执行结果。\n\n")


def events_from(text):
    events = []
    for line in text.splitlines():
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                events.append(item)
        except ValueError:
            pass
    return events


def save_environment(path, metadata, resume=False):
    """Preserve the original environment, especially across source updates."""
    if path.exists():
        previous = json.loads(path.read_text())
        if not resume:
            raise ValueError("Run environment already exists; choose a new run ID or --resume-incomplete")
        keys = ["source_version", "skill_files_sha256", "requested_model", "reasoning_effort"]
        if "scenario_specification_sha256" in previous:
            keys.append("scenario_specification_sha256")
        if any(previous.get(key) != metadata.get(key) for key in keys):
            raise ValueError("Cannot resume with changed source, scenarios, model, or reasoning effort")
        return
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")


def execute(case, variant, repetition, args, work_root):
    key = f"{case['id']}-{variant}-r{repetition}"
    cwd = work_root / key
    cwd.mkdir(parents=True)
    for name, content in case.get("fixtures", {}).items():
        path = cwd / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if variant == "lr":
        INSTALLER.install(cwd / ".agents/skills")
    original_skill = INSTALLER.file_map(cwd / ".agents/skills" / INSTALLER.SKILL_NAME) if variant == "lr" else {}
    installed_hashes = {name: hashlib.sha256(content).hexdigest() for name, content in original_skill.items()}
    if variant == "lr" and installed_hashes != args.source_hashes:
        raise RuntimeError("Source changed while starting an evaluation; freeze source and use a fresh run")
    result = {"scenario": case['id'], "title": case['title'], "group": case['group'],
              "variant": variant, "repetition": repetition, "test_type": "multiturn" if len(case['turns']) > 1 else "runtime",
              "requested_model": args.model, "reasoning_effort": args.effort,
              "started_at": datetime.now(timezone.utc).isoformat(), "status": "running", "turns": [],
              "artifact_checks": [], "skill_load_observed": False}
    result["installed_skill_files_sha256"] = installed_hashes
    if args.stop_event.is_set():
        result.update(status="not_run", blocked_reason="usage_limit", artifacts={},
                      completed_at=datetime.now(timezone.utc).isoformat())
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / f"{key}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        return key, result
    session = None
    for index, question in enumerate(case['turns']):
        prompt = COMMON
        if variant == "lr" and index == 0:
            prompt += "使用 $systematic-knowledge-construction 完成下面的任务。\n\n"
        prompt += question
        command = [args.codex, "exec", "--ignore-user-config", "--disable", "plugins",
                   "--disable", "remote_plugin", "--disable", "apps", "--disable", "hooks",
                   "--disable", "multi_agent", "-m", args.model,
                   "-c", f'model_reasoning_effort="{args.effort}"',
                   "--sandbox", case.get("sandbox", "read-only"),
                   "--skip-git-repo-check", "-C", str(cwd)]
        answer_path = cwd / f"answer-{index+1}.md"
        if index == 0:
            if len(case['turns']) == 1:
                command += ["--ephemeral"]
        else:
            command += ["resume", session]
        command += ["--json", "-o", str(answer_path), prompt]
        started = time.monotonic()
        try:
            completed = subprocess.run(command, input="", text=True, capture_output=True,
                                       timeout=args.timeout, cwd=cwd)
            raw = completed.stdout
            error = completed.stderr
            code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            raw = exc.stdout or ""
            if isinstance(raw, bytes):
                raw = raw.decode(errors="replace")
            error = "Timed out"
            code = -1
        elapsed = round(time.monotonic() - started, 3)
        private = ROOT / ".evalraw" / args.run_id
        private.mkdir(parents=True, exist_ok=True)
        (private / f"{key}-turn{index+1}.jsonl").write_text(raw)
        (private / f"{key}-turn{index+1}.stderr").write_text(error)
        events = events_from(raw)
        service_errors = [e.get("message", "") for e in events if e.get("type") == "error"]
        if service_errors:
            error = "\n".join(service_errors)
        traces = []
        usage = {}
        for event in events:
            if event.get("type") == "thread.started":
                session = event.get("thread_id", session)
            if event.get("type") == "turn.completed":
                usage = event.get("usage", {})
            item = event.get("item", {})
            if item.get("type") == "command_execution" and event.get("type") == "item.completed":
                cmd = item.get("command", "")
                if "SKILL.md" in cmd and "systematic-knowledge-construction" in cmd:
                    result["skill_load_observed"] = True
                traces.append({"command": cmd.replace(str(cwd), "<workspace>"),
                               "exit_code": item.get("exit_code"),
                               "output_sha256": hashlib.sha256(item.get("aggregated_output", "").encode()).hexdigest()})
        answer = answer_path.read_text() if answer_path.exists() else ""
        turn = {"input": prompt, "response": answer, "exit_code": code,
                "elapsed_seconds": elapsed, "usage": usage, "tool_trace": traces}
        if code != 0 or not answer.strip():
            turn["error"] = error[-1500:].replace(str(cwd), "<workspace>")
            result["turns"].append(turn)
            result["status"] = "error"
            if "usage limit" in error.lower():
                result.update(status="blocked", blocked_reason="usage_limit")
                args.stop_event.set()
            break
        result["turns"].append(turn)
        if index == 0 and case.get("first_turn_unchanged"):
            passed = all((cwd / name).read_text() == content for name, content in case['fixtures'].items())
            result["artifact_checks"].append({"check": "first_turn_preserves_files", "passed": passed})
        if index + 1 < len(case['turns']) and not session:
            result["status"] = "error"
            result["error"] = "No native session ID returned for continuation"
            break
    else:
        result["status"] = "completed"
    for name, expected in (case.get("expected", {}) if result["status"] == "completed" else {}).items():
        path = cwd / name
        result["artifact_checks"].append({"check": f"exact_file:{name}", "passed": path.exists() and path.read_text() == expected})
    for name, expected in (case.get("expected_json", {}) if result["status"] == "completed" else {}).items():
        try:
            passed = json.loads((cwd / name).read_text()) == expected
        except (OSError, ValueError):
            passed = False
        result["artifact_checks"].append({"check": f"json_values:{name}", "passed": passed})
    if variant == "lr":
        result["artifact_checks"].append({"check": "installed_skill_unchanged",
            "passed": INSTALLER.file_map(cwd / ".agents/skills" / INSTALLER.SKILL_NAME) == original_skill})
    result["artifacts"] = {name: (cwd / name).read_text() if (cwd / name).is_file() else None
                           for name in case.get("fixtures", {})}
    result["completed_at"] = datetime.now(timezone.utc).isoformat()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / f"{key}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return key, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "max"])
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--scenarios", type=Path, default=ROOT / "evals/scenarios.json",
                        help="Scenario specification; use update-scenarios.json for the 1.1.5 regressions")
    parser.add_argument("--variants", nargs="+", default=["baseline", "lr"], choices=["baseline", "lr"])
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--start-repetition", type=int, default=1)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=360)
    parser.add_argument("--run-id", default="local-evaluation")
    parser.add_argument("--resume-incomplete", action="store_true",
                        help="Keep completed records and archive earlier incomplete attempts")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    args.output = args.output or ROOT / "evals/results" / args.run_id
    args.stop_event = threading.Event()
    scenario_bytes = args.scenarios.read_bytes()
    cases = json.loads(scenario_bytes)
    if args.cases:
        selected = set(args.cases)
        if selected - {c['id'] for c in cases}:
            parser.error("Unknown scenario ID")
        cases = [c for c in cases if c['id'] in selected]
    version = subprocess.run([args.codex, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    args.output.mkdir(parents=True, exist_ok=True)
    args.source_hashes = {name: hashlib.sha256(content).hexdigest()
                          for name, content in INSTALLER.file_map(ROOT / "skills" / INSTALLER.SKILL_NAME).items()}
    metadata = {"cli_version": version, "requested_model": args.model, "reasoning_effort": args.effort,
                "plugins_and_apps_disabled": True, "isolated_workspaces": True, "source_version": json.loads((ROOT / "plugin.json").read_text())["version"],
                "skill_sha256": hashlib.sha256((ROOT / "skills" / INSTALLER.SKILL_NAME / "SKILL.md").read_bytes()).hexdigest(),
                "sampling_seed": "not exposed", "temperature": "CLI default, not exposed", "run_id": args.run_id,
                "limitations": ["Uses one model and one local CLI host, not a cross-host benchmark", "Natural-language implicit activation and plugin marketplace UI are not tested", "No live web or external connectors are available", "Additional transfer scenarios were authored by the publisher; they are not a sealed independent benchmark"]}
    metadata["skill_files_sha256"] = args.source_hashes
    metadata["scenario_specification"] = args.scenarios.name
    metadata["scenario_specification_sha256"] = hashlib.sha256(scenario_bytes).hexdigest()
    try:
        save_environment(args.output / "environment.json", metadata, args.resume_incomplete)
    except ValueError as exc:
        parser.error(str(exc))
    work_root = Path(tempfile.mkdtemp(prefix="lr-eval-"))
    print(f"Run {args.run_id}; {version}; model={args.model}; workspaces={work_root}", flush=True)
    failures = 0
    jobs = []
    for repetition in range(args.start_repetition, args.start_repetition + args.repetitions):
        for case in cases:
            for variant in args.variants:
                path = args.output / f"{case['id']}-{variant}-r{repetition}.json"
                if path.exists():
                    if not args.resume_incomplete:
                        parser.error(f"Record already exists: {path}; choose a new run ID or --resume-incomplete")
                    previous = json.loads(path.read_text())
                    if previous['requested_model'] != args.model or previous['reasoning_effort'] != args.effort:
                        parser.error("Cannot resume with a different model or reasoning effort")
                    if previous['status'] == 'completed':
                        if variant == 'lr' and previous.get('installed_skill_files_sha256') != args.source_hashes:
                            parser.error("Completed treatment record uses a different source snapshot")
                        print(f"{path.stem}: keeping completed record", flush=True)
                        continue
                    archive = args.output / "previous-attempts"
                    archive.mkdir(exist_ok=True)
                    number = 1
                    while (archive / f"{path.stem}-attempt{number}.json").exists():
                        number += 1
                    shutil.copy2(path, archive / f"{path.stem}-attempt{number}.json")
                jobs.append((case, variant, repetition))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(execute, case, variant, repetition, args, work_root)
                   for case, variant, repetition in jobs]
        for future in as_completed(futures):
            key, result = future.result()
            artifact_ok = all(item["passed"] for item in result["artifact_checks"])
            if result["status"] != "completed" or not artifact_ok:
                failures += 1
            print(f"{key}: {result['status']}; artifacts={'pass' if artifact_ok else 'FAIL'}; skill_read={result['skill_load_observed']}", flush=True)
    print(f"Execution finished; {failures} runtime/artifact failures. Response quality is not graded by this runner.", flush=True)
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
