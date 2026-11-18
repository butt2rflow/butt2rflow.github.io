---
title: "Build an MCP bridge from Claude Code to Codex and local Qwen"
nav_title: "Build a Codex and Qwen MCP bridge"
date: 2026-11-17
tags: [local-llm, qwen, ollama, claude-code, codex, muse, mcp]
lang: en
description: "Build a Python stdio bridge that runs Codex for Claude Code, saves jobs across reconnects, and optionally sends reading tasks to an already loaded Qwen model."
---

# Build an MCP bridge from Claude Code to Codex and local Qwen

## 1. Set up the handoff

Keep Claude Code as the coordinator. It sends a scoped task over MCP, gets a job ID, and looks up the result later. Codex handles investigation, edits, tests, and first-pass review. An optional local Qwen route handles long-document reading, outlines, and summaries. Claude Code keeps responsibility for important decisions and final review.

![Claude Code stays in charge and calls tools to delegate part of a task](../assets/diagrams_en/muse-model-or-tool.svg)

Use a Linux host with Python 3, Git, Claude Code, and a signed-in Codex CLI. Put the bridge script `coop.py` in a trusted directory such as `~/ai-cooperation`, outside projects it can edit, and use a disposable personal Git project for the examples. Delegate personal projects only. Keep work code and documents out of requests. This scope rule is applied by the caller.

**Check.** Run `python3 --version`, `git --version`, `claude --version`, and `codex --version` in the host shell. Confirm the disposable project is separate from the bridge directory.

The [core reference implementation](https://github.com/butt2rflow/butt2rflow.github.io/tree/main/code/claude-codex-bridge) includes the bridge and tests. The GPU recipe runner is outside the scope of this release.

## 2. Build the Python stdio server

Build `coop.py` with the Python standard library. Use `argparse` for the `serve` and internal worker subcommands, `json` and `pathlib` for records, and `subprocess` for worker launches. Read one JSON-RPC message per line from stdin, preserve the request ID in each reply, and flush newline-delimited JSON to stdout. Send diagnostics to stderr. Handle `initialize`, `ping`, `tools/list`, and `tools/call`. Publish input schemas and validate arguments before calling a handler. [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)

| Tool | What to implement |
|---|---|
| `cooperation_status()` | Return recent jobs and Qwen readiness. |
| `delegate_task(cwd, task, ...)` | Validate the request, acquire the project lock, save the job, and start a detached worker. Return its ID without waiting for the model. |
| `job_result(job_id, detail=false)` | Read persisted status and return a compact final summary when available. |

Resolve `cwd` and any input files, and reject files that resolve outside `cwd`, including through symlinks. Use a nonblocking exclusive `fcntl.flock` keyed by the Git working-tree root, or by the resolved directory outside Git. Keep the requested `cwd` for execution. Pass the lock descriptor to the worker and its Codex child so the lock survives a worker crash while that child is still running. Interactive editors and CLI sessions must coordinate separately.

Under `runs/<id>/`, write `request.json` and a queued `state.json` before spawning the worker with `start_new_session=True` and redirected standard streams. Replace state files atomically. Save the final message in `result.md`, and write the Git snapshots, logs, and handoff before publishing terminal state. Keep these records private and omit secrets from requests.

**Check.** From the bridge directory, send a handshake and discovery request. Expect two JSON replies, with the three tools in the second.

```bash
python3 coop.py serve <<'JSON'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
JSON
```

## 3. Register the bridge in Claude Code

Add a user-scope stdio server. The arguments after `--` start the server. Adjust the script location if you put it elsewhere. [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp)

```bash
claude mcp add --transport stdio --scope user ai-cooperation \
  -- /usr/bin/python3 "$HOME/ai-cooperation/coop.py" serve
```

**Check.** Start Claude Code in that project, open `/mcp`, and look for a connected `ai-cooperation` server. Ask Claude to call `cooperation_status`. A Qwen-unavailable reason can appear even when the bridge is connected.

## 4. Run Codex from the worker

Build an argument list and pass the task on stdin, using `-` as the prompt argument. Redirect Codex output to `codex.log` and capture the final message separately. Here is the equivalent of the core read-only invocation. The worker supplies the project and result paths.

```bash
codex -a never exec --cd "$project_dir" --sandbox read-only \
  --output-last-message "$result_path" -
```

Use `read-only` for investigation and reviews. Select `workspace-write` only for an authorized `write=true` task. The allowed files in the task constrain the model by instruction. The sandbox applies workspace-level permissions. Keep the sandbox enabled and use no bypass flags.

Start Codex in its own process group. The bridge defaults to 1,800 seconds and accepts 30–7,200 seconds. If the deadline expires, send SIGTERM to the group, wait up to 10 seconds for Codex, and send SIGKILL to the group if Codex still has not exited. Save `needs_review` and retain partial changes for inspection.

**Check.** Delegate a read-only README task in the disposable project and check its output and unchanged working tree. Then try an authorized one-file edit and run its acceptance check independently. With a fake Codex, test that a timeout records `needs_review` and that a second job in the same working tree is refused while the first holds the lock.

## 5. Add local Qwen if you need it

![A local tool reads the file from its path and returns a short summary](../assets/diagrams_en/muse-read-route.svg)

For the bridge’s `target=qwen` route, set `AI_COOP_QWEN_MODEL` in the server environment to override the default `qwen3.8:27b`. Use `urllib.request` to call the local Ollama API. Preflight with `nvidia-smi` and Ollama’s `/api/ps`. Refuse if a non-Ollama compute process holds the GPU, the configured model is absent, model metadata indicates CPU offload, or the probes fail. Require valid sizes with `size > 0` and `size_vram >= size`. Recheck just before sending a non-streaming `/api/chat` request with the task and selected text. Return the draft in `result.md`. Use extracted text for PDFs on this route.

The bridge issues no automatic model load, unload, or workload stop commands. The check and chat request are separate. Ollama can still load a model if it drops out between the two, and an external GPU job can start after the check. Use `qwen-disable` before starting a competing workload and wait for existing Qwen jobs to finish. `qwen-enable` only clears the block.

The default route is Codex. Explicit `qwen` refuses an unavailable GPU route. For eligible reading tasks, `auto` may pick Codex before launch if Qwen is unavailable. A failure after launch calls for inspection. The worker never switches models mid-job.

The existing `local_llm` tool is a separate MCP connection that also uses Ollama. For an existing installation, call `local_llm` with `task` and absolute `file_paths` for PDF or office extraction. It uses its own GPU checks. The new bridge’s guard and job records apply to calls through `delegate_task`. [Local GPU AI for reading](local-llm-reading.md)

**Check.** Confirm busy GPU, missing model, and CPU offload cases are rejected with fixtures. On the host, use `cooperation_status` to check readiness. If ready, submit a read-only task with `target=qwen` and a small project-relative text file in `files` and compare the summary against the source. Record SKIP if the preflight blocks it.

## 6. Send a concrete task and verify the result

Set `cwd` to the actual absolute project path. Give the goal, allowed changes, completion criteria, checks, and evidence paths the worker can access. For example, call `delegate_task` with `target=codex` and `write=true` in the disposable project.

- Goal — Fix the broken setup command.
- Allowed changes — README.md only. Preserve existing edits.
- Done — The command works from the project root.
- Checks — Run the command and `git diff --check`. Report the result and evidence paths.

Ask for up to eight short lines and 800 characters. Put failures first, then report the outcome, changed files or review findings, checks marked `PASS`, `FAIL`, or `NOT RUN`, and any open decision or evidence path. The bridge caps the default summary at 1,200 characters and sets `summary_truncated` when needed. Request `job_result(job_id, detail=true)` for up to 12,000 characters, or open the full `result.md` on disk.

**Check.** Save the ID and poll `job_result` every 30–60 seconds for long tasks. While the job runs, expect status without a running report. For Codex, `completed` means it exited successfully and produced a final message. Confirm the reported checks and inspect the required files or test evidence before accepting the work.

## 7. Recover from the job record

| What you see | What to do |
|---|---|
| `Read-only file system` during startup | Two early runs stopped before model execution because the outer environment mounted `~/.codex` read-only. Check `codex.log` and the Git snapshots. Use a host session where Codex can initialize while keeping the requested project sandbox. |
| Connection error or timeout | Check `/mcp` or the job log for the failing layer. Treat quota as exhausted only when Codex reports an explicit usage-limit error. After confirmed exhaustion, Claude can take over from the saved record. |
| Caller disconnected | The detached worker continues. Reconnect and look up the same ID. If you lost it, check recent jobs with `cooperation_status` before sending anything again. |
| `needs_review` | Open `state.json`, the logs, and `HANDOFF.md`. Compare the before/after snapshots with the actual Git diff. A failed or interrupted run can leave partial edits, and the snapshots also include preexisting work. Decide whether to finish from that state or retry. |

**Check.** Close the caller after a disposable job returns its ID. Reopen it and confirm the same ID reaches terminal state without a second submission. If MCP is unavailable, run `python3 coop.py result JOB_ID` from the bridge directory.

## 8. Check what your setup actually verifies

| Path | Recorded result |
|---|---|
| Claude Code registration and tool discovery | PASS. Claude Code showed Connected, and the host verifier found all three tools. |
| MCP → live Codex | PASS. Read and reconnect, edit with an independent acceptance test, and read-only review of a seeded defect. |
| Job handling and GPU denial | PASS in automated fixtures. The host also detected a busy GPU and skipped Qwen. |
| MCP → live Qwen through this bridge | SKIP in host verification because the GPU was busy. Inference remains unverified. |

**Check.** Run these commands from `code/claude-codex-bridge` in the blog repository. The first uses fixtures for model and GPU behavior. The second is optional. It makes live Codex calls on disposable inputs and saves a report under `verification/host-*/REPORT.md`. Record any unrun checks separately.

```bash
python3 -m unittest -v test_coop.py
python3 verify_host.py
```

For shopping delegation, see [How to connect Claude Code and Codex to Muse over MCP](muse-mcp-shopping.md).
