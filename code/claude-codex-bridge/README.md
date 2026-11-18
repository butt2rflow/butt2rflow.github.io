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

```bash
python3 coop.py status
python3 coop.py start --cwd /path/to/project --task 'Read README.md and report missing setup steps.'
python3 coop.py result JOB_ID --detail
```

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
