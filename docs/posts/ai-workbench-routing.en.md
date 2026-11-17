---
title: "Claude oversees; Codex, local AI and Muse share the work"
nav_title: "Local AI, Codex and Muse"
date: 2026-11-17
tags: [local-llm, qwen, ollama, claude-code, codex, muse, mcp]
lang: en
description: "A continuation of local GPU reading: Claude Code oversees, Codex executes and reviews first, Qwen handles large documents, and Muse researches products. Verified paths are separated from new workflow plans."
---

# Claude oversees; Codex, local AI and Muse share the work

In the [previous article](local-llm-reading.md), I passed file paths to a local AI and received short summaries instead of putting an entire book into Claude's conversation. The next question was how to share other work without spending the savings on repeated handoffs.

My current division is: **Claude Code oversees the work and makes important judgments; Codex handles execution; local Qwen reads large inputs; Muse researches products.** Some paths are verified, while others remain operating plans.

![Claude Code oversees and reviews final decisions, with Codex executing, local Qwen reading large documents and Muse researching products](../assets/diagrams_en/muse-workbench.svg)

## The short version

- Claude Code retains overall oversight, important judgments and final review. User approvals for actions such as purchasing or publishing still belong to me.
- Codex allowance is used first for research, implementation, tests and first-pass review. On confirmed quota exhaustion, Claude Code takes over the existing work.
- Local Qwen is reserved for large PDFs and long documents—tables of contents, reading and summaries—and basic web research support.
- FLUX/H3 execution and initial visual review are assigned to Codex to avoid loading a review model into the same local VRAM. This new assignment has not yet been tested with a generation run.
- I plan to update this article with a Qwen 4.0 migration and comparison after release. No release date or performance is assumed here.

## Replacing a model differs from using a tool

The earlier article described both replacing the model behind the coding interface and leaving Claude in charge while delegating reading. This article follows the second pattern. MCP supplies a common way to call tools, but each client still needs its own registration, credentials and working execution environment.

![Replacing the model changes who answers; delegation lets the original coding AI keep control and receive a tool's result](../assets/diagrams_en/muse-model-or-tool.svg)

For a camera driver, Codex investigates, edits and tests. Claude Code handles important choices and final review. A long manual goes to the local reader for a table of contents and relevant sections; shopping goes to Muse. Running Qwen does not create permission to access Muse's catalog.

## Let the local tool read the source

Pasting a document into the coding conversation before delegating it already sends the document to that model. Passing an accessible file path lets the local program open it directly and return a short result.

![Passing the source through chat duplicates reading; passing a path lets the local tool read it and send only a summary and selected evidence](../assets/diagrams_en/muse-read-route.svg)

My local tool accepts fields including `task`, `file_paths`, `urls` and `model`, and calls Ollama, the local model runner. The current local MCP code and operating record identify Qwen 3.8 as its default. I did not run a fresh speed test for this article.

```text
Have local_llm read this manual using its file path.
Do not paste the full document into chat first.
Build a table of contents, then summarize USB support,
resolutions and warnings, with source locations for key figures.
```

The path must be accessible on the machine running that tool. The same-looking path on my PC and Muse's remote VM does not identify shared storage. Important figures still need checking against the source. The previous article's usage estimates do not establish a new savings percentage for Codex or Muse.

## Claude Code delegates execution to Codex

I built a separate cooperation MCP server. Claude Code sends a goal and working directory with `delegate_task`; the bridge starts a Codex job and records it. Claude Code retrieves a short result using `job_result`.

```text
Goal: check resolution handling in the camera settings.
Allowed changes: this personal project's configuration and relevant tests.
Completion: report the change, actual test results and unresolved issues.
```

The retained November 16 host verification record reports successful live Codex reading and reconnection, editing and tests, and a review finding a deliberately introduced defect. Those live checks are separate from 27 automated tests using fake responses. I did not rerun paid model calls while writing this article.

**Qwen inference through the new bridge remains unverified.** Its check skipped the call because another GPU workload was active. Successful reading with the older local tool does not establish successful inference through the new bridge.

Claude Code reads the short result first and opens additional evidence for important judgments. This does not replace the human approvals required for purchases or publication.

## Do not spend the savings on handoffs

If two models read the same full source and then reread each other's long answers, delegation can become expensive. My request contains the objective, directory, allowed changes, completion checks and source locations. The response contains the result, changed files, verification status, unresolved issues and detailed evidence paths.

The report target is eight lines and about 800 characters; the bridge's short result is limited to 1,200 characters. Detailed output remains in files. Truncation or an important decision is a reason to inspect more evidence, not to hide a failure or invent a passing test.

Ideally a program would poll progress and notify the model only on completion, failure or needed input. That new notification mechanism is not implemented here. Current manual checks are spaced out and use the existing job ID rather than submitting duplicate work.

Characters are not tokens. When actual input/output/cached-token usage is available, I will retain it; otherwise estimates stay labeled as estimates. API prices and subscription allowances are also different. The goal is less duplicate reading and calling without weakening necessary checks.

## Muse returns research to the original screen

Claude Code submitted a revised SO-101 camera search and received its final answer. A fresh Codex launched with a credential-forwarding wrapper retrieved a completed RAM job. The [Muse MCP article](muse-mcp-shopping.md) covers the server, tunnel and session problems.

```text
Use ask_muse_to_shop for research only, with intent=find.
Compare Canadian shipping and CAD totals. Do not buy.
Keep the job ID for check_shopping_request.
```

`pending` means waiting; `done` means complete. My worker checked the queue every five minutes, but the camera conversation took about ten minutes from submission to receipt of the completed result on November 17, Toronto time. Required catalog permission is handled in Muse chat and remains separate from purchase approval.

## Review outputs without evicting the generation model

I had tried using local Qwen 3.8 to inspect FLUX and MiniMax H3 outputs. They shared the GPU's memory, so loading the reviewer meant unloading another model. Switching back and forth was a practical problem.

The new plan assigns execution and first visual review to Codex, with Claude Code overseeing and reviewing final decisions. With an available image-input tool, Codex can inspect the output without loading Qwen into the local GPU. Images are sent to the model service; this is different from keeping inference local.

![The local GPU generates FLUX/H3 outputs; Codex reviews images and Claude Code oversees. Video also needs temporal checks](../assets/diagrams_en/muse-gpu-review.svg)

A few extracted frames can show distorted objects but miss flicker and motion discontinuities. The review must record frame timestamps and distinguish sampled-frame checks from continuous temporal inspection.

This assignment is **not a finding that Codex has universally better vision**. [OpenAI reports GPT-6.1 Sol advantages on GDP.pdf against Opus 5.5 with fallbacks](https://openai.com/index/introducing-gpt-6-1-sol/). [Anthropic reports chart-recognition results for Opus 5.5](https://www.anthropic.com/claude-opus-5-5), but that table does not supply the corresponding GPT score. These evaluations do not establish which detects FLUX/H3 defects better.

The clear operational benefit is avoiding another reviewer model in the same VRAM. Accuracy needs a separate comparison: identical images and video segments, human-labeled defects, and matched review conditions. If Codex quota is exhausted, Claude Code inherits the current job and outputs; a connection error is not grounds to classify quota as exhausted or submit generation again.

## What is verified

![Verified Codex and Muse calls are distinguished from unverified Qwen inference through the new bridge and a future Qwen comparison](../assets/diagrams_en/muse-checks.svg)

| Path | Evidence or limit |
|---|---|
| Claude Code → local AI | Prior reading with the existing tool; new-bridge Qwen inference unverified |
| Claude Code → Codex | Prior host checks for reading, reconnecting, editing, testing and review |
| Claude Code → Muse | Camera submission, polling and final result |
| Fresh Codex → Muse | Retrieval of a completed RAM result |
| FLUX/H3 execution and initial review → Codex | New operating rule; no generation/review run verified yet |
| Qwen 4.0 migration | Planned comparison after release |

## When the next Qwen is available

I want the caller to keep passing file paths while the local tool's model choice changes. Compatibility with the runner and tools still needs checking; a tag substitution is not a guaranteed migration.

I will compare similar documents for missed figures, omitted conditions, truncated inputs, response time and GPU memory. Local model migration and Muse shopping remain separate checks. This article records the current arrangement; the changed configuration and measured results will be added after the upgrade.

---

*Configuration and operating decisions recorded November 17, 2026. Qwen 4.0 is a planned upgrade target, not a release or performance announcement. Product names identify the tools and imply no affiliation. Diagrams are original.*

**Previous:** [Local GPU AI for reading](local-llm-reading.md) · **Related:** [Muse as an MCP server](muse-mcp-shopping.md)
