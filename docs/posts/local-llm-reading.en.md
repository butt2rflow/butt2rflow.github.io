---
title: "A 1,069-Page Book in 15 Minutes: Cutting Claude Usage by Over 90% With a Local AI on My GPU"
nav_title: "Handing the reading to a local AI"
date: 2026-10-25
tags: [local-llm, ollama, qwen, claude-code, rtx-3090, token-savings]
lang: en
description: "Running Qwen3.6 35B on a home graphics card (RTX 3090) next to Claude Code. The local AI summarized a 1,069-page book in 15 minutes and a 3-minute video in about 40 seconds, and on the book and 131 blog posts Claude usage fell by over 90% (against an estimate of Claude reading them). The same Claude Code screen can also run on the local model. Also: what didn't pay off, the wrong calls, and the trap of sharing one GPU."
---

# A 1,069-Page Book in 15 Minutes: Cutting Claude Usage by Over 90% With a Local AI on My GPU

Each Claude plan has a set amount you can use (a usage limit). Work with Claude Code for a while and you see where that usage goes: far more into **reading** than into editing code. Have it read dozens of documents, a book-length PDF or several web pages, and the limit fills up fast.

So I installed an AI model on the graphics card at home (an RTX 3090) and handed the reading to it. This is a record of one day of setting it up and measuring it.

![Claude finds, judges and edits; the local AI reads and sends back something short](../assets/diagrams_en/llm-split.svg)

---

## 30-second summary

- The local AI summarized a **1,069-page book in 15 minutes**, chapter by chapter, and a 3-minute video in about 40 seconds. The numbers were right, but some explanations came out reversed.
- On the book and on **131 blog posts** (4 min 38 s), **Claude usage fell by over 90%**. That is against an estimate of Claude reading them itself; for just a few posts the difference is small.
- The model is **Qwen3.6 35B**. It answers at about 164 tokens per second and can look at images (a token is the unit an AI counts text in; roughly three quarters of an English word). It's weaker than Claude, but enough for "read and summarize."
- **You can keep the same Claude Code screen and swap only the brain for the local model.** One line, `claude-local`, gives you file edits, terminal runs and even web search with no Claude usage.
- Day to day we split the roles. **Claude finds, judges and edits**; **the local AI reads and sends back something short**.
- The payoff starts once there are dozens of things to read. For 7 posts the difference was small.
- Anything that needs judgment, like reviews, and code edits stay with Claude. The local AI also makes wrong calls.

---

## What I installed

| Item | Details |
|---|---|
| Graphics card | RTX 3090 (24 GB of memory) |
| Runtime | Ollama (a free program that downloads and runs models) |
| Model | Qwen3.6 35B (Alibaba's open model. 35B means 35 billion numbers inside; it uses only about 3 billion of them at a time, which makes it fast; explained under "Why the 35B") |
| Model file | 22 GB (each number stored in 4 bits, a much shorter form) |
| GPU memory used | 23.2 GB (of 24 GB) |
| Reading window | 65,536 tokens (well over 100 book pages) |
| Speed | about 164 tokens/s |

One memory setting made a big difference. Storing the space where the model keeps what it has already read (the KV cache) in shorter numbers halves its memory. I spent the saving on a reading window twice as large.

It isn't NVIDIA-only. The runtime (Ollama) also supports AMD graphics cards and Apple silicon Macs, and there are Mac builds of Qwen3.6. What matters is memory, not the brand.

The 35B (4-bit) with a 65,536-token reading window needs about 23 GB, so you need a 24 GB graphics card or a Mac with 32 GB or more. With less memory, use a smaller model (the 27B takes 20.6 GB, and smaller versions exist) or a shorter reading window. Speed depends on how fast the memory moves data (memory bandwidth), much as a wider road lets more cars through at once, so the same model can run faster or slower than the numbers here on other hardware. I only measured on NVIDIA, though.

---

## Same screen, different brain: Claude Code on a local model

This was the most useful part. **You keep the Claude Code screen you already use and swap only the brain that answers for the model on your own graphics card.**

![One Claude Code screen used by Claude and by the local model](../assets/diagrams_en/llm-same-ui.svg)

- Open it with `claude` and Claude on Anthropic's servers answers, as usual.
- Open it with `claude-local` and you get the same screen and the same tools, but Qwen3.6 35B at home answers. Claude usage: zero.
- Editing files, running terminal commands and reading web pages all work. Web search goes through a search program I run at home (see "Search had to be added" below).

So running out of Claude usage doesn't stop the work. Before the limit hits, have Claude write a few lines on where things stand, reopen with `claude-local`, hand it the note, and carry on in the same screen.

The two sessions can also message each other. Claude Code can send a message to another session open on the same computer, and a session running on the local model joins in the same way. Opening a local session and having it message the Claude session took 13 s, and the message arrived intact. The other way round, the Claude session sent "ping," and the local session, busy with a task, read it and answered "pong." So you can pass the progress note as a message, or have the Claude session hand a long job to the local session and get the result back as a message.

The local model needed instructions spelled out as "step 1, step 2…". Told vaguely to wait, it ignored that and finished within seconds. The local session also couldn't see sessions on other computers or connected remotely.

The numbers:

- Create one file, run it and report the result: 39 s
- Four hard research questions that needed dates and numbers from several pages: all 13 facts right, 68 s per question on average

There are limits. The local runtime has no way to remember instructions it has already read (prompt caching), so every exchange re-reads Claude Code's 20,000-token system prompt from scratch. Even short jobs take tens of seconds, and long jobs with dozens of steps are clearly weaker than on Claude. Two setup traps are under "The trap" below.

---

## Splitting the roles: Claude finds, the local AI reads

Day to day it works like this. I work in Claude and hand over **only the reading-heavy jobs**.

1. Claude decides what to read. It picks file paths or web addresses, without reading the contents.
2. The local AI opens and reads the files and pages itself.
3. The local AI sends back only a few lines of summary.
4. Claude judges from those few lines.

The expensive part is the source text. It never passes through Claude, so the usage drops by that much.

The link is built with MCP, a standard plug for adding tools to Claude. Register a small program and Claude sees it as one more tool, next to "edit a file" or "run a command." I built a "have the local AI read this" tool and plugged it in. The tool opens the files on my computer itself, so the source text never goes through Claude. Its description says "use this when there's a lot to read," and Claude hands work over without my asking.

| Way | Who answers | When |
|---|---|---|
| `claude-local` | The local model runs the whole session | When Claude usage runs out |
| MCP tool | Claude works; only the reading goes to the local model | Day to day |

---

## Measured: summarizing 7 and 131 blog posts

I tested it twice on my own blog.

![Claude usage when summarizing 7 and 131 posts](../assets/diagrams_en/llm-savings.svg)

Seven series posts (52,000 characters) took 41 s locally. The percentage saved looks large, but the actual saving was only about 20,000-30,000 tokens, and it includes the tokens spent writing the summary program for the first time.

The 131 investment posts (650,000 characters) were a different story. Locally they took 4 min 38 s, and the Claude side used only about 5,000 tokens to read the summaries. Had Claude read them itself, it would have taken hundreds of thousands of tokens and nearly filled the conversation.

In both cases the "if Claude read it itself" figures are estimates from character counts, not measurements of Claude doing the same job.

The summaries were usable. The accuracy figures in the series summary (95%, 97%) matched the source. But a few Chinese words slipped into the 131-post summary, an occasional habit of this model family. So I check key numbers and names against the source.

---

## PDFs, Hangul files, web pages and phone photos

I added a step that turns files into plain text the local AI can read.

| Format | How it's converted |
|---|---|
| PDF | Text is pulled from each page. Pages with no text (scans) are read by the model as images |
| Word, Excel, PowerPoint | Paragraphs, tables and sheets become text. Old formats (.doc, .xls, .ppt) work too |
| Hangul (.hwp, .hwpx) | Text is pulled with an open-source tool |
| Web pages | Give it an address and it fetches only the main text |

The biggest win is **long PDFs**. When Claude reads a PDF, it gets each page's text plus an image of the page. Text alone is 1,500-3,000 tokens per page, and the images cost extra. A 36-page English technical manual comes to over 50,000-110,000 tokens. The local AI summarized its title, target product and main contents in 16 s.

I don't hand over number-heavy files like Excel sheets. This model gets totals and trends wrong easily. Claude computing the numbers with code is more accurate and uses little to begin with.

The old Word and PowerPoint formats need a converter that is no longer maintained, and old programs don't get security holes fixed. Because these are files of unknown origin, it runs only inside an isolated container (Docker) with no internet and no write access.

**Phone photos and screenshots** work the same way. I often photograph news articles on my phone and send them to Claude. But attaching a photo straight to a message puts it into Claude the moment it's sent, so the usage is already spent. So photos go to an inbox folder in my cloud sync, and I just say "read the inbox." The local AI reads the photos on my home PC, and Claude gets only the summary. With 6 article screenshots, Claude's side went from about 12,000 tokens (an estimate from image size) to about 1,000, and the reading took 13 s. Titles, text and numbers were transcribed correctly. For just a few photos, attaching them directly is easier, since Claude can look and judge for itself.

---

## The model can see, too

Qwen3.6 can look at images. Claude sees images well too and judges more accurately, but every image costs usage: about 1,500 tokens each. So I gave the local AI the first pass over a batch.

First I had it look for flaws in photos I had generated with AI.

![Problems the local AI caught in AI-generated photos](../assets/diagrams_en/llm-vision.svg)

- It checked 7 photos in 19 s, about 2.7 s each.
- In one pass it found a Canadian flag with a malformed maple leaf, a car standing on bare rock with no road, and uneven dock posts.
- The scores wobbled. The 27B, run for comparison, gave the same photo 3 out of 10 one time and 4 the next, and made a wrong call: it said trees should be mostly bare in late October, when in that region the leaves often still have color.

So I settled on how to use it. When I generate several images, **the local AI weeds out the clear failures first**, and Claude looks only at the few that remain. Choosing between two good images is not its job.

I also tried sorting photos in bulk. Captioning and tagging 61 photos took 97 s (1.6 s each), and in the 5 I checked, every scene description was right. That's enough for finding things later, like "river and snow-covered forest" or "domed building." Details were weak, though: it made up text in photos, called a stone wall a bridge, and counted people loosely. It also spotted only 1 of 5 AI-generated photos as AI-made.

---

## A whole book and a video

I also tried things bigger than a few dozen posts.

**A 1,069-page book.** I had it summarize an options-investing textbook chapter by chapter. The PDF is a scanned paper book with a text layer added. It had no bookmarks, so first the local AI read the contents pages and found where each of the 42 chapters starts (42 s). Then it read and summarized each chapter and wrote one file: a contents table, an overview of the book, and per-chapter summaries. It took **15 minutes**, and the local AI read about 630,000 tokens. Claude spent about 30,000 tokens writing the program and checking the result. Reading the book itself would have taken over 630,000, so that is over 90% less (an estimate).

I checked two chapters against the book. Every number was right. But one chapter had **two explanations reversed**. The book says "sell time value and buy intrinsic value," and the summary said the opposite. Five Chinese words slipped in too. It is great for skimming the book's structure and finding the chapter you need, but risky to act on the summary alone. The book is under copyright, so the summary is for my own study only.

**A 3-minute video.** I tried a 3-minute video NASA released, about finding mine pollution from space. A speech-to-text model (Whisper) transcribed the audio, and Qwen3.6 looked at 24 frames taken wherever the scene changed. Together they produced a one-line summary, a timeline table and the facts that appear only on screen. All of it took **about 40 seconds**. It read the on-screen text exactly: the "~50,000 mines" caption, the instrument's acronym spelled out, and the numbers on a data screen all matched the video. Having Claude look at the 24 frames and the transcript would have cost about 10,000-30,000 tokens depending on frame size (an estimate); the result file, full transcript included, was about 4,000. It made small slips, like calling a blank white frame "a person speaking."

---

## Search had to be added

**Reading** web pages works locally. **Searching** didn't, at first.

Claude Code's search runs on Anthropic's servers, not on my computer. Switch to a local model and requests no longer go there, so search disappears with them. So I ran an open-source program at home that queries several search engines for you (SearXNG), and plugged it into the local session as an MCP tool, the same way as above. It uses only about 125 MB of memory.

As a test I asked, "find the latest Ollama version." The local AI searched, opened the GitHub page and answered with the right version and its source in 52 s. Even on a day with no Claude usage left, it can look things up on its own.

---

## What to hand over, and what not

![Splitting jobs between the local AI and Claude by amount of reading and need for judgment](../assets/diagrams_en/llm-fit.svg)

The rule is simple. If a job means **reading a lot and returning something short**, it goes to the local AI.

- Hand over: summarizing many documents, condensing long logs, reading several web pages, finding what you need in a long PDF or a book, summarizing a video, a first pass over photos
- Keep on Claude: code edits and debugging (Claude has to read the code anyway), fact checks, post reviews, final edits, calculations, small jobs

I also considered post reviews. I check every post in six steps (copyright, fact check, removing AI-sounding prose, reading as a math-averse reader, final edit, Korean proofreading). Four of them need judgment, so Claude does them. Only two, reading as a reader and Korean proofreading, seemed worth letting the local AI draft "candidates" for first. I tested that on this post; the results are under "The test I ran on this post."

---

## Why the 35B: against the 27B and BigBang-v1

I gave the same jobs to the Qwen3.6 27B from the same family and to BigBang-v1, a model tuned for search. The 35B has more numbers yet runs faster, thanks to a design called MoE (mixture of experts). Picture a company with 100 experts, where a front desk passes each question to only the two or three who fit it best. The 27B uses all 27 billion of its numbers for every token it writes; the 35B uses about 3 billion of its 35 billion. The catch is that all the experts have to wait in memory, so it needs more memory.

| | Qwen3.6 27B | BigBang-v1 | **Qwen3.6 35B** |
|---|---|---|---|
| Speed | 63 tokens/s | 144 tokens/s | **164 tokens/s** |
| Sees images | yes | no | **yes** |
| Search test (3 questions, 7 facts) | 6 of 7, 323 s | all 7, 168 s | **all 7, 128 s** |
| Checking 7 photos | about 47 s | - | **19 s** |
| Summarizing 7 posts | 1 min 56 s | - | **41 s** |
| Summarizing 131 posts | 12 min 16 s | - | **4 min 38 s** |
| `claude-local` task (create and run a file) | 1 min 42 s | - | **39 s** |

The same jobs ran 1.6-2.8x faster on the 35B, so summarizing, search and image checks all go to that one model. BigBang-v1 searched well but can't see images. The copy I got was an unofficial upload by an individual, and it threw errors as soon as I connected Claude Code: the chat-format settings bundled with the model didn't match the shape of the requests Claude Code sends.

The 35B has a downside too. It takes 23.2 GB of GPU memory, so it slows down as soon as another program holds a little memory. That is the next trap.

---

## The trap: one graphics card

![Image generation and the local AI sharing 24 GB of GPU memory](../assets/diagrams_en/llm-gpu.svg)

This is the problem I spent longest on. I also make images on the same graphics card (ComfyUI). I finished an image job without closing that program, and it kept holding 15.8 GB. When I then ran the 27B, three quarters of the model didn't fit on the graphics card and spilled onto the CPU, which does this kind of math far slower than a graphics card. There was no error. It just slowed from 63 to 7 tokens per second. The odd speed made me check who was using GPU memory (`nvidia-smi`), and only then did I find the cause. The 35B takes 23.2 GB, so it has even less room.

So I set rules:

1. Always close the image program when an image job is done.
2. Before using the local AI, check that the model is 100% on the graphics card (`ollama ps`).
3. Before making images again, unload the local model (`ollama stop`).

For anyone trying this, two technical traps:

- Running Claude Code on a local model can throw "model not found" mid-session. The small model name used for background tasks (haiku) has to point at the local model too.
- For an unknown model, Claude Code assumes it reads 200,000 tokens at once. Unless you tell it the real size (65,536), the local runtime rejects requests once the conversation gets long.

---

## The test I ran on this post

I tested two review steps on this post's draft. First the local AI read the draft and its list of findings was saved to a file. Without opening that list, I ran the same two review steps with Claude separately. Then I compared them. I ran it with both the 27B and the 35B.

| | Reading as a math-averse reader | Korean proofreading |
|---|---|---|
| Time (27B / 35B) | 26 s / 8 s | 34 s / 12 s |
| Of Claude's findings, also found | 4 of 9 / 6 | 1 of 7 key items / 2 |
| Useful findings only the local AI had | 3 / 3 | 2 / 0 |
| Wrong findings | almost none | 3 / 3 (called correct phrasing wrong) |

As a reader it was useful. "Why does spilling onto the CPU make it slow," "what does 4-bit mean" and "how did you notice who was holding the memory" were things I had missed, and they went into this post. The 35B even caught a wrong analogy I had caught ("a few pages of a book").

For Korean proofreading both models did the opposite of what I want. Most suggestions turned plain words like "돌려줘요" (sends back) and "받아 와요" (fetches) into stiff ones like "제공해요" (provides), "추출해요" (extracts) and "반환해요" (returns). Following them would make the prose read more like a translation. So Korean proofreading stays with Claude, and only the reader step uses the local AI's list as a reference.

---

## Takeaways

- A local AI can't replace Claude, but as a **reading worker** it is enough.
- The payoff grows with the amount of reading. For a few documents just use Claude; from dozens on, and for a whole book even more, it clearly pays.
- Treat results as drafts. Check numbers and names against the source, and leave judging and editing to Claude. An explanation can come out reversed.
- If you share the graphics card with other work, first check who is holding the memory.
- One model, Qwen3.6 35B, handled summarizing, search, image checks and video summaries. Details and judgment are still its weak spot.

---

### Sources and notices

Settings (KV cache quantization, context length, keep-alive) follow the official Ollama FAQ; the environment variables for running Claude Code on a local model follow the Ollama and Claude Code docs and community guides; tokens per PDF page follow Anthropic's PDF support documentation. The book summarized is Lawrence G. McMillan's *Options as a Strategic Investment*, 5th edition, and the video is NASA's "How NASA Uses Light to Detect Waste From Mines" (public domain). AMD and Mac support is based on Ollama's release files and model library (not tested here). Speeds, times and memory figures are single measurements on my PC on October 25, 2026, and the "if Claude read it itself" figures are estimates from character counts. The photos checked are not real places; I generated them with FLUX.2 [klein]. Claude and Claude Code are trademarks of Anthropic PBC; Qwen of Alibaba Cloud; Ollama of Ollama, Inc.; NVIDIA, GeForce and RTX of NVIDIA Corporation; Docker of Docker, Inc.; Microsoft Word, Excel and PowerPoint of Microsoft Corporation; Hangul (HWP) of Hancom Inc.; GitHub of GitHub, Inc.; FLUX of Black Forest Labs; ComfyUI of Comfy Org; Whisper of OpenAI. They are used for identification only.

### Glossary

- *Local AI*: an AI model that runs on your own computer instead of an online service
- *Session*: one running Claude Code window and the conversation in it
- *Token*: the unit an AI reads and writes text in. Roughly three quarters of an English word
- *Claude usage*: how many tokens Claude has read and written. Each plan has a limit
- *Ollama*: a free program that downloads AI models and runs them on your computer
- *4-bit version (quantization)*: a version with its numbers shortened to save memory, at a small cost in quality
- *KV cache*: the memory where a model keeps what it has already read
- *Prompt caching*: remembering instructions so they don't have to be re-read. The local runtime didn't have it
- *Container (Docker)*: a box that runs a program apart from the rest of the system
- *SearXNG*: an open-source program that asks several search engines for you and gathers the results
- *MCP*: a standard way to connect outside tools to an AI like Claude. A registered program shows up in the AI's tool list
- *MoE (mixture of experts)*: a model split into many "experts," using only some of them for each job. Fast for its size
- *Whisper*: an open speech-to-text model
