# Claude Code–Codex/Qwen MCP bridge

This core reference implementation lets Claude Code delegate a scoped job to
Codex or local Qwen over stdio MCP. A detached worker saves the result so the
caller can disconnect and later resume polling the same job ID.

## Setup

Use Linux with Python 3.9+, Git, Claude Code, and an authenticated Codex CLI on
PATH. The bridge uses the Python standard library. For optional local reading,
use NVIDIA's `nvidia-smi` and Ollama on `127.0.0.1:11434`. Set
`AI_COOP_QWEN_MODEL` in the server environment to override `qwen3.8:27b`.

Place the files in a private, writable directory outside the projects you
delegate. Replace the script path in this user-scope registration command.

```bash
claude mcp add --transport stdio --scope user ai-cooperation -- /usr/bin/python3 /path/to/coop.py serve
```

Open Claude Code's `/mcp` view to check the connection.

## Tools and task contract

- `cooperation_status` reports Qwen readiness and recent jobs.
- `delegate_task` accepts an absolute project `cwd`, task, and optional
  `target`, `write`, `files`, and `timeout` (30–7,200 seconds). Codex is the
  default. With explicit `target=codex`, optionally set `model` and `effort`.
  Model aliases `sol`, `astra`, and `terra` use the local Codex model cache.
- `job_result` takes the job ID. Poll every 30–60 seconds for long jobs.
  The summary is capped at 1,200 characters, or 12,000 with `detail=true`.
  The full result, logs, and Git snapshots live under `runs/<id>/`.

Give the worker a goal, allowed changes, evidence paths inside the project,
acceptance criteria, and checks to run. Request a short report with failures
first, changed paths or review findings, and PASS, FAIL, or NOT RUN for checks.
Review the actual changes and evidence before accepting a completed job.

## CLI

```bash
python3 coop.py status
python3 coop.py start --cwd /path/to/project --target codex --timeout 600 \
  --file README.md --file notes.txt --task 'Report missing setup steps.'
python3 coop.py result JOB_ID --detail
```

`start` and MCP's `delegate_task` share request validation.

- `--target {codex,qwen,auto}` defaults to `codex`.
- `--write` authorizes project edits and routes `auto` to Codex. The default
  is read-only. Qwen rejects write requests.
- `--timeout` accepts 30–7,200 seconds and defaults to 1,800.
- Repeat `--file` for each input file inside `--cwd`, up to 180,000 bytes total.
  Relative paths are resolved from `--cwd`.
- `--model` accepts a Codex model slug or a local cache alias (`sol`, `astra`,
  `terra`). `--effort` accepts a supported reasoning level such as `high`.
  Both flags are optional and require the `codex` target.
- `--continue-job` resumes a finished Codex job as described below.

## Follow up in the same Codex conversation

When `job_result` shows `resumable: true`, pass that job ID as
`continue_job` to `delegate_task` and provide the new request in `task`.
The CLI equivalent is:

```bash
python3 coop.py start --cwd /path/to/project --continue-job JOB_ID --task 'Summarize the remaining setup steps.'
```

The bridge runs `codex exec resume` with the recorded session ID (tested
with Codex CLI 0.169.0). Each follow-up has its own job ID and records the
prior job as `continued_from`. Use the same resolved directory as the earlier
job. Only finished Codex jobs with a recorded session can be continued.
Jobs recorded before session tracking need a fresh start. Set MCP `write=true`
or CLI `--write` again if the new request authorizes edits. If Codex doesn't confirm the same
session, inspect the job record before retrying.

Codex diagnostics go to `codex.log`, and its JSON events go to
`codex.events.jsonl`. The detailed result shows the captured session ID
or explains why none was recorded.

## Safety and limits

Use trusted callers and personal projects only. Review and investigation use
Codex's read-only sandbox. Explicitly authorized edits use workspace-write.
The runner uses no sandbox bypass flags. File-level edit limits are task
instructions. Bridge locks coordinate jobs in the same Git working tree
(or directory outside Git). Coordinate interactive edits separately. Keep
credentials out of requests and keep job records private. Inspect partial
changes and logs before retrying a failed or interrupted job.

Use Qwen for text analysis. The bridge only submits chat when the configured
model is already fully GPU-resident and the GPU probe finds no competing
compute process. It never issues automatic model load or unload commands.
Readiness checks and inference are separate, so external workloads or Ollama
model expiry can race them. Before starting a competing workload, run
`python3 coop.py qwen-disable` and wait for active Qwen jobs to finish.
`python3 coop.py qwen-enable` clears the block. With `target=auto`, the bridge
may choose Codex before launch if Qwen is unavailable. There is no automatic
quota switching. The author's host run skipped live Qwen inference because
the GPU was busy.

## Verification

Run `python3 -m unittest -v test_coop.py` in this directory. The tests use
fixtures without network access, GPU calls, or paid model calls. Optional
`python3 verify_host.py` uses the installed Codex CLI for live calls on
disposable projects and tries Qwen only when ready. It writes its report
under `verification/`.
