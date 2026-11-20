---
title: "Saving Claude Tokens by Having Local AI Read a 1,069-Page Book"
nav_title: "Reading a 1,069-page book with local AI"
date: 2026-10-25
tags: [local-llm, ollama, qwen, claude-code, rtx-3090, token-savings]
lang: en
description: "I ran Qwen3.8 27B on an RTX 3090 to summarize 42 book chapters and 131 posts, estimated what Claude would save by reading the summaries, and checked numbers and explanations against the book."
---

# Saving Claude Tokens by Having Local AI Read a 1,069-Page Book

When a 1,000-page PDF user manual lands in front of you, you know what's coming. Today the tokens are going to burn.

<video controls playsinline muted autoplay loop preload="metadata" poster="/assets/llm/local-llm-tokens-poster.jpg" src="/assets/llm/local-llm-tokens.mp4" style="width:100%"></video>

There are two ways out. The first is to sweet-talk the new hire into lending you some tokens; they may have barely touched this week's limit. The second is in this post. It's easier on the conscience.

Sometimes Claude has to read hundreds of thousands of characters to give me a few lines back. I let Qwen3.8 27B on my RTX 3090 read the sources and give Claude the summary and the passages worth checking.

![Estimated Claude reading tokens saved per task: 131 blog posts, a 1,069-page book, 6 article screenshots, a 3-minute NASA video](../assets/diagrams_en/llm-cut.svg)

---

## 30-second summary

- A **1,069-page book with 42 chapters** took about 33 minutes. Reading the entire summary file would cut Claude’s estimated input by **over 90%**.
- The **131 investment posts** took 11 min 10 s. Sending Claude just the overview saves **over 99%** of the estimated reading tokens.
- Estimated savings came to about 20% for six screenshots and over 80% for a NASA video. A long answer can eat up much of the saving.
- These estimates compare the input for reading the source with the input for reading the local result. Building the tools and checking the source cost extra.
- Numbers and on-screen text were mostly accurate, but the book summary and the rules pulled from indicator posts had a few places where a meaning or a number changed. So **Claude double-checks the local AI's summaries against the source**.
- **You can keep the same Claude Code screen and swap only the brain for the local model.** One line, `claude-local`, gives you file edits, terminal runs and even web search with no Claude usage.
- Code edits and anything that needs judgment stay with Claude.

---

## What I installed

| Item | Details |
|---|---|
| Graphics card | RTX 3090 (24 GB of memory) |
| Operating system | Ubuntu 24.04 (every test and tool in this post ran on Ubuntu; I haven't tried them on Windows) |
| Runtime | Ollama (a free program that downloads and runs models) |
| Model | qwen3.8:27b (dense, 27.3 billion parameters, image input) |
| Model files | 16.81 GB of Q4_K_M weights plus a 0.93 GB vision projector |
| GPU memory | 17.84 GB allocated to the model, all on GPU. Whole-board usage was 20,904 MiB |
| Reading window | Configured for 65,536 tokens |
| Output speed | 83.5 tokens/s while writing a prime-checking function |

I used an 8-bit KV cache to leave room for long chapters. The speed and memory figures are single observations on my PC with that setting.

---

## Same screen, different brain: Claude Code on a local model

This was the most useful part. **You keep the Claude Code screen you already use and swap only the brain that answers for a model running on your local PC.**

![One Claude Code screen used by Claude and by the local model](../assets/diagrams_en/llm-same-ui.svg)

- Open it with `claude` and Claude on Anthropic's servers answers, as usual.
- With `claude-local`, I use the same tools and Qwen3.8 27B answers on my PC.
- Editing files, running terminal commands and reading web pages all work. Web search goes through a search program I run on the local PC (see "Search had to be added" below).

So running out of Claude usage doesn't stop the work. Before the limit hits, have Claude write a few lines on where things stand, reopen with `claude-local`, hand it the note, and carry on in the same screen.

The numbers:

- Creating and running a file that correctly reported the eight primes below 20 took 115 seconds.
- In a separate search test it got all 13 facts on four hard questions, averaging 190 seconds per question. Including the easier set, it got 19 of 20.

---

## Splitting the roles: Claude finds, the local AI reads

Day to day it works like this. I work in Claude and hand over **only the reading-heavy jobs**.

![Claude finds, judges and edits; the local AI reads and sends back something short](../assets/diagrams_en/llm-split.svg)

1. Claude decides what to read. It picks file paths or web addresses, without reading the contents.
2. The local AI opens and reads the files and pages itself.
3. The local AI sends back only a few lines of summary.
4. Claude judges from those few lines and checks the important parts against the source once more.

The expensive part is the source text. It never passes through Claude, so the usage drops by that much.

The link is built with MCP, a standard plug for adding tools to Claude. Register a small program and Claude sees it as one more tool, next to "edit a file" or "run a command." I built a "have the local AI read this" tool and plugged it in. The tool opens the files on my computer itself, so the source text never goes through Claude. Its description says "use this when there's a lot to read," and Claude hands work over without my asking.

| Way | Who answers | When |
|---|---|---|
| `claude-local` | The local model runs the whole session | When Claude usage runs out |
| MCP tool | Claude works; only the reading goes to the local model | Day to day |

---

## Measured: 131 posts, a 1,069-page book, images, a video

### 131 blog posts

![Estimated reading tokens for the sources and overviews of 7 and 131 posts](../assets/diagrams_en/llm-savings.svg)

Reading 131 investment posts (about 650,000 characters) and writing an overview took 11 min 10 s. I estimate 350,000–420,000 tokens for Claude to read the sources and about 2,300 for the 3,902-character overview. That saves over 99% of the reading input.

Seven posts in a series (about 52,000 characters) took 93 seconds and the overview came to about 870 estimated tokens. For three or four posts I expect to reopen anyway, I just have Claude read them.

The individual summaries preserved the 95% sound-classification score and distinguished 94% on raw signals from 97% on vibration images for unseen subjects. It compared the mixed-subject score of 98% with 97%, although the matching raw-signal baseline was 94%. The final overview omitted those figures. In the larger batch, stray non-Korean wording appeared in one individual summary and in the overview.

The model extracted 166 rules from 12 indicator posts. At least three changed the meaning despite having a quotation alongside. One turned loss given default from one minus the recovery rate into its reciprocal. I check the formula before using a rule like that in a calculation.

### A 1,069-page book

This textbook is a scan with a text layer. In 36 seconds the model found all 42 real chapter starts but counted five extra entries as chapters. I supplied the verified boundaries. The chapter summaries and overview took **32 min 49 s**, with about 626,000 local input tokens.

I estimate over 630,000 tokens for Claude to read the source, or about 46,000 for the entire file including the contents and chapter summaries. That saves over 90%, and some passages still need checking. Eight of nine selected facts matched across two chapters. Chapter 8 preserved the trade directions and example payoffs. Chapter 1 skipped the broker’s role in selecting the customer and said the clearinghouse randomly picks the writer directly.

### Images: screenshots, photo checks, photo sorting

I tested the same model on images. The timings here are all for Qwen3.8 27B.

**Phone screenshots.** I put article screenshots in a synced folder and ask Claude to read the inbox. It receives the local transcription. Six images took 171 seconds. Qwen distinguished the article’s three models but left a long discussion about reading order in the answer. Against roughly 12,000 tokens for the images, the digest came to about 9,600, a saving of about 20%.

**Checking AI-generated photos.** I had it look for flaws in photos I had generated with AI.

![Three defects in the same image flagged by 3.6 and missed by 3.8](../assets/diagrams_en/llm-vision.svg)

Checking seven photos took 36 seconds. The 3.8 model gave full marks to the same image where the 35B had spotted a malformed flag, a car parked on bare rock and uneven dock posts. Even when I use it to narrow the list, I look at the finalists myself.

**Sorting photos.** Tagging 61 images took 184 seconds, about three seconds each. All five sampled captions got the broad scene right, such as a forested river or a domed building. One added a sculpture in front of the building. The model missed the AI origin of all five.

### A 3-minute NASA video

[NASA’s three-minute video](https://www.youtube.com/watch?v=Ac36aovF8ZQ) follows an effort to detect mine pollution from space. Whisper transcribed the audio and Qwen3.8 27B read 24 frames to build a timeline. Including transcription, it took about 74 seconds.

It read the caption about 50,000 mines and recognized the blank transition frame. I estimate 10,000–30,000 tokens for Claude to read the frames and transcript, versus about 1,800 for the summary and frame notes alone. That saves over 80%.

---

## PDFs, Hangul files and web pages too

I added a step that turns files into plain text the local AI can read.

| Format | How it's converted |
|---|---|
| PDF | Text is pulled from each page. Pages with no text (scans) are read by the model as images |
| Word, Excel, PowerPoint | Paragraphs, tables and sheets become text. Old formats (.doc, .xls, .ppt) work too |
| Hangul (.hwp, .hwpx) | Text is pulled with an open-source tool |
| Web pages | Give it an address and it fetches only the main text |

A 36-page FANUC technical manual took about 21 seconds. The model read six image-only pages visually. It found the EtherCAT setup, wiring and diagnostics, but rendered the R-30iB controller name as R-30+B. That one character matters when choosing a part.

I don't hand over number-heavy files like Excel sheets. This model gets totals and trends wrong easily. Claude computing the numbers with code is more accurate and uses little to begin with.

The old Word and PowerPoint formats need a converter that is no longer maintained, and old programs don't get security holes fixed. Because these are files of unknown origin, it runs only inside an isolated container (Docker) with no internet and no write access.

---

## Search runs locally too

**Reading** web pages worked locally from the start. **Searching** didn't.

Claude Code's search runs on Anthropic's servers, not on my computer. Switch to a local model and requests no longer go there, so search disappears with them. So I ran an open-source program on my local PC that queries several search engines for you (SearXNG), and plugged it in as an MCP tool, the same way as above. It uses only about 125 MB of memory.

In normal Claude sessions, web research goes to the local side as well. Here Claude doesn't pick addresses; it only passes the question.

1. The local PC searches with SearXNG.
2. The local PC opens the top five or six pages itself.
3. The local AI writes an answer from those pages only. Each sentence carries a source number and a verbatim quote, and it notes where sources disagree.
4. Claude reads the short answer and its source list.

Had Claude searched itself, reading the results and three or four pages would have cost well over 10,000 tokens (an estimate).

I tried three questions whose answers I could check against the source.

| Question | Local AI's answer | Checked against the source |
|---|---|---|
| Stable Ollama release at the time? | 0.40.16 | Matched the release record, but cited only secondary sources. |
| Default Python on Ubuntu 26.04? | 3.14 | Right version, but the official table row it quoted was for 25.10. |
| FLUX.2 klein licenses? | Non-commercial for 9B, Apache 2.0 for 4B | Matched both official model cards, which the answer did not link. |

It read six pages for each question and got all three main conclusions right. A source number only takes me so far. When a version or compatibility matters, I open the official page and check that the quoted line applies to my version.

---

## What to hand over, and what not

![Splitting jobs between the local AI and Claude by amount of reading and need for judgment](../assets/diagrams_en/llm-fit.svg)

The rule is simple. If a job means **reading a lot and returning something short**, it goes to the local AI.

- Hand over: summarizing many documents, condensing long logs, web research (search and page reading), finding what you need in a long PDF or a book, summarizing a video, a first pass over photos
- After handing over: don't use the result as is; Claude checks numbers, names and key explanations against the source once more
- Keep on Claude: code edits and debugging (Claude has to read the code anyway), fact checks, post reviews, final edits, calculations, small jobs

---

## Why I keep the 35B for quick reads

I keep just **qwen3.8:27b and qwen3.6:35b**. The 35B activates only some of its parameters for each token and is much faster on quick jobs. A separate decode benchmark gave 218 versus 57 tokens/s. The whole book took about 15 versus 33 minutes. The 83.5 in the setup table is for the prime-function prompt.

| For fidelity · 3.8 27B | For speed · 3.6 35B |
|---|---|
| Book and document summaries, drawing reads, web research, default `claude-local` sessions | Inbox and OCR, image ranking and tagging, video, quick skims |

In a separate comparison on three chapters, each summarized twice, 3.8 made zero wrong claims across six summaries and 3.6 made three. The 35B also gives a second opinion on drawings so I can check disputed dimensions, so I removed qwen3-vl, which I had kept for that. Claude does the code changes, and plain `claude-local` (3.8) is enough for coding I hand to the local side, so I removed qwen3-coder too.

---

## The trap: one graphics card

![Historical GPU contention between image generation and Qwen3.6 27B](../assets/diagrams_en/llm-gpu.svg)

The same GPU runs ComfyUI for images and video, and Isaac Sim for robotics. With the older Qwen3.6 27B, leaving ComfyUI holding 15.8 GB dropped output from 63 to 7 tokens/s. For the 3.8 measurements I finished other GPU jobs first and checked that the entire model fit on the card.

So I set rules:

1. Always close the image program when an image job is done.
2. Before using the local AI, check that the model is 100% on the graphics card (`ollama ps`).
3. Before making images again, unload the local model (`ollama stop`).

Remembering that every time is hard, so the check is now built in. `claude-local` and the summary tools look at who is using the graphics card before they start. If another job such as ComfyUI or Isaac Sim holds memory, they don't load the model; they report "who is using how many GB" and stop. They don't shut that job down either. Then I just use Claude, or try again after that job finishes.

For anyone trying this, two technical traps:

- Running Claude Code on a local model can throw "model not found" mid-session. The small model name used for background tasks (haiku) has to point at the local model too.
- I give Claude Code the same 65,536-token limit I set in Ollama so long conversations stay within the model’s configured window.

---

## Takeaways

- A local AI can't replace Claude, but as a **reading worker** it is enough.
- For books and large batches of posts, the length of what Claude actually reads is a good guide to savings. A long screenshot transcription can leave little to save.
- Treat results as drafts. An explanation can come out reversed, so Claude double-checks numbers, names and key explanations against the source, and does the judging and editing.
- If you share the graphics card with other work, first check who is holding the memory. Letting a program check for you is easier.

---

### Sources and notices

I estimated the book and blog outputs locally, counting a quarter token per ASCII character and one per other character. For the screenshots and video I scaled earlier estimates by the new digest size. These are input-size estimates. The local run produced no Claude bill to compare.

Settings (KV cache quantization, context length, keep-alive) follow the official Ollama FAQ; the environment variables for running Claude Code on a local model follow the Ollama and Claude Code docs and community guides; tokens per PDF page follow Anthropic's PDF support documentation. The video is NASA's ["How NASA Uses Light to Detect Waste From Mines"](https://www.youtube.com/watch?v=Ac36aovF8ZQ) (public domain). The photos checked are not real places; I generated them with FLUX.2 [klein]. The clip at the top is AI-made: first frame with FLUX 3 Image Klein, motion with MiniMax H3. Claude and Claude Code are trademarks of Anthropic PBC; Qwen of Alibaba Cloud; Ollama of Ollama, Inc.; NVIDIA, GeForce, RTX and Isaac Sim of NVIDIA Corporation; Docker of Docker, Inc.; Microsoft Word, Excel and PowerPoint of Microsoft Corporation; Hangul (HWP) of Hancom Inc.; GitHub of GitHub, Inc.; Ubuntu of Canonical Ltd.; Python of the Python Software Foundation; Hugging Face of Hugging Face, Inc.; Wikipedia of the Wikimedia Foundation; FLUX of Black Forest Labs; MiniMax of MiniMax; ComfyUI of Comfy Org; Whisper of OpenAI. They are used for identification only.

### Glossary

- *Local AI*: an AI model that runs on your own computer instead of an online service
- *Session*: one running Claude Code window and the conversation in it
- *Token*: the unit an AI reads and writes text in. Roughly three quarters of an English word
- *Claude usage*: how many tokens Claude has read and written. Each plan has a limit
- *Ollama*: a free program that downloads AI models and runs them on your computer
- *4-bit version (quantization)*: a version with its numbers shortened to save memory, at a small cost in quality
- *KV cache*: the memory where a model keeps what it has already read
- *Container (Docker)*: a box that runs a program apart from the rest of the system
- *SearXNG*: an open-source program that asks several search engines for you and gathers the results
- *MCP*: a standard way to connect outside tools to an AI like Claude. A registered program shows up in the AI's tool list
- *MoE (mixture of experts)*: a model split into many "experts," using only some of them for each job. Fast for its size
- *Whisper*: an open speech-to-text model

**Follow-up:** [Claude Directs, Codex Does the Work: A Bridge to Save Claude Usage](ai-workbench-routing.md) · [Don’t Spend Claude Tokens on Shopping: Send Muse and Use Its Free Allowance](muse-mcp-shopping.md)
