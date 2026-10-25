---
title: "Handing the Reading to a Local AI: an RTX 3090 and Claude Code"
nav_title: "Handing the reading to a local AI"
date: 2026-10-25
tags: [local-llm, ollama, qwen, claude-code, rtx-3090, token-savings]
lang: en
description: "A day of running Qwen3.6 on a home RTX 3090 next to Claude Code. The same Claude Code screen can run on the local model with no Claude usage. Reading-heavy jobs went to the local model, judging and editing stayed with Claude, and summarizing 131 blog posts used about 98% less Claude usage. Switching from the 27B to the 35B model made the same jobs 1.6-2.8x faster. Also: what didn't pay off, the wrong calls, and the trap of sharing one GPU."
---

# Handing the Reading to a Local AI: an RTX 3090 and Claude Code

Claude plans come with a usage limit. Work with Claude Code for a while and you can see where that usage goes: far more into **reading** than into editing code. Have it read dozens of documents, a long PDF or a handful of web pages, and the limit fills up fast.

So I installed an AI model on the graphics card at home (an RTX 3090) and handed it only the reading. This is a record of one day of setting it up and measuring it.

![Claude finds, judges and edits; the local AI reads and sends back something short](../assets/diagrams_en/llm-split.svg)

---

## 30-second summary

- With **Qwen3.6 35B** on the 3090, answers come at about 164 tokens per second, and it can look at images (a token is the unit an AI counts text in; roughly three quarters of an English word). It's weaker than Claude, but enough for "read and summarize."
- **You can keep the same Claude Code screen and swap only the brain for the local model.** One command (`claude-local`) gives you file edits, commands and even web search with no Claude usage.
- Day to day we split the roles. **Claude finds, judges and edits**; **the local AI reads and sends back something short**.
- Summarizing **131 blog posts**: 4 min 38 s locally, with **about 98% less Claude usage** (against an estimate of Claude reading them itself).
- I started with the 27B model. Switching to the 35B made the same jobs 1.6-2.8x faster.
- For **7 posts** the difference was small. The payoff starts once there are dozens of things to read.
- Anything that needs judgment, like reviews, and code edits stay with Claude. The local AI also makes wrong calls.

---

## What I installed

| Item | Details |
|---|---|
| Graphics card | RTX 3090 (24 GB of memory) |
| Runtime | Ollama (a free program that downloads and runs models) |
| Model | Qwen3.6 35B (Alibaba's open model. 35B means 35 billion numbers inside; it uses only about 3 billion of them at a time, which makes it fast) |
| Model file | 22 GB (each number stored in 4 bits, a much shorter form) |
| GPU memory used | 23.2 GB (of 24 GB) |
| Reading window | 65,536 tokens (well over 100 book pages) |
| Speed | about 164 tokens/s (the 27B I started with: about 63) |

One memory setting made a big difference. Storing the space where the model keeps what it has already read (the KV cache) in shorter numbers halves its memory. I spent the saving on a reading window twice as large.

---

## Same screen, different brain: Claude Code on a local model

This was the most useful thing I got working. **You keep the Claude Code screen you already use and swap only the brain that answers for the model on your own graphics card.**

![One Claude Code screen used by Claude and by the local model](../assets/diagrams_en/llm-same-ui.svg)

- Open it with `claude` and Claude on Anthropic's servers answers, as usual.
- Open it with `claude-local` and you get the same screen and the same tools, but Qwen3.6 35B at home answers. Claude usage: zero.
- Editing files, running terminal commands and reading web pages all work. Web search, which didn't work at first, now goes through a search program running at home (see "Why search didn't work at first" below).

So running out of Claude usage doesn't stop the work. Before you hit the limit, have Claude write a few lines on where things stand, reopen with `claude-local`, hand it that note, and carry on in the same screen.

The measured numbers:

- Create one file, run it and report the result: 39 s with the 35B (1 min 42 s with the 27B I started with)
- 4 hard research questions that need dates and numbers from several pages: all 13 facts right, 68 s per question on average

There are limits. The local runtime can't remember instructions it has already read (prompt caching), so every turn it re-reads Claude Code's 20,000-token set of standing instructions from the start. Even short jobs take tens of seconds, and long jobs with dozens of steps are clearly weaker than Claude. Two setup traps are listed under "The trap" below.

---

## Splitting the roles: Claude finds, the local AI reads

Day to day, I use it like this: I work with Claude and hand over **only the reading-heavy jobs**.

1. Claude decides what to read. It picks file paths or web addresses and doesn't read the content.
2. The local AI opens the files and pages and reads them.
3. The local AI sends back a few lines of summary.
4. Claude reads those few lines and makes the call.

The expensive part is the source text. Because it never passes through Claude, Claude's usage drops by that much.

---

## Measured: 7 posts and 131 posts

I tested it twice on my own blog.

![Claude usage for summarizing 7 and 131 posts](../assets/diagrams_en/llm-savings.svg)

Seven series posts (52,000 characters) took 41 s locally (1 min 56 s with the 27B). With 7 posts the percentage drop looks large, but the actual saving is only 20,000-30,000 tokens, and since it was the first run, the tokens Claude spent writing the summary script are counted in. With the 27B it wasn't even faster than Claude reading the posts itself.

The 131 investment posts (650,000 characters) were different. They took 4 min 38 s locally (12 min 16 s with the 27B), and Claude's side ended at about 5,000 tokens for reading the result. Reading them itself, Claude would have spent hundreds of thousands of tokens and nearly filled the conversation.

In both cases the "if Claude read it itself" figure is an estimate from character counts, not a measured run of Claude doing the same job.

The summaries were usable. The accuracy figures in the series summary (95%, 97%) matched the posts. But a few stray Chinese words (three or four spots across 131 summaries) slipped into the Korean text, with both the 27B and the 35B. It's a habit of this model family, so I check key numbers and names against the source.

---

## What to hand over, and what not

![Splitting jobs between the local AI and Claude by how much there is to read and whether judgment is needed](../assets/diagrams_en/llm-fit.svg)

The rule is simple. **Lots to read, short result**: hand it to the local AI.

- Hand over: summarizing several documents, boiling down long logs, reading several web pages, finding what you need in a long PDF
- Keep: code edits and debugging (Claude has to read the code anyway), fact checks, post reviews, final edits, small jobs

I also looked at my blog reviews. Every post goes through six steps: copyright, fact check, removing AI-sounding phrasing, reading as a math-averse reader, final edit, and Korean proofreading. Four of them need judgment, so Claude does them. Only "reading as a reader" and "Korean proofreading" looked worth letting the local AI draft candidates for. I tested that on this very post; the result is below in "The test I ran on this post."

---

## PDFs, Hangul files and web pages too

I added a step that turns files into plain text the local AI can read.

| Format | How |
|---|---|
| PDF | Text is pulled out page by page. Pages with no text (scans) are read by the model as images |
| Word, Excel, PowerPoint | Paragraphs, tables and sheets become text, old formats (.doc, .xls, .ppt) included |
| Hangul (.hwp, .hwpx) | Text is pulled out with an open-source tool |
| Web pages | Give it the address and it fetches just the main text |

The biggest win is **long PDFs**. When Claude reads a PDF, it receives each page's text plus an image of the page. The text alone is 1,500-3,000 tokens per page, and the image costs extra, so a 36-page English technical manual runs over 50,000-110,000 tokens. The local AI summarized the title, the product and the main contents in 16 s.

Number-heavy files like spreadsheets I don't hand over. The model gets sums and trends wrong easily. Having Claude compute the numbers with code is more accurate and cheap anyway.

The old Word and PowerPoint formats need a conversion tool that is no longer maintained, and old software doesn't get its security holes fixed. Since this means opening files of unknown origin, the tool runs only inside an isolated container (Docker) with no internet access and no write permission.

---

## Why search didn't work at first

**Reading** web pages works locally. **Searching** didn't.

Claude Code's web search runs on Anthropic's servers, not on my computer. Once Claude Code points at a local model, requests no longer reach those servers, so search goes away with them. So I set up SearXNG, an open-source program that queries several search engines on your behalf, on the home PC. It uses about 125 MB of memory.

As a test I asked it to find the latest Ollama version. The local AI searched, opened the GitHub page and answered with the right version and its source in 52 s. Even on a day when my Claude usage runs out, it can now look things up on its own.

---

## The model can see, too

Qwen3.6 also reads images. I had it check photos I had made with an AI image model.

![Problems the local AI found in an AI-generated photo](../assets/diagrams_en/llm-vision.svg)

- The 35B checked 7 photos in 19 s, about 2.7 s each.
- In one pass it found a Canadian flag with a malformed maple leaf, a car standing on bare rock with no road, and uneven dock posts.
- The 27B I used first took about 7 s per photo and made a wrong call: it said trees should be mostly bare in late October, when in that region the leaves often still have color. Its scores wobbled too: the same photo got 3 out of 10 one time and 4 the next.

So I settled on how to use it. When I generate several images, **the local AI weeds out the clear failures first**, and Claude looks only at the few that remain. Choosing between two good images is not its job. Each image Claude views costs about 1,500 tokens.

---

## Switching models: from the 27B to the 35B

I started with Qwen3.6 27B. Then I learned that the 35B model of the same family was faster and could also see, and switched. The 35B has more numbers, but it uses only a part of them (about 3 billion) at a time, a design called MoE, so it is actually faster. Think of a team of experts where each job calls in only a few of them. I also tried BigBang-v1, a version tuned for search.

| | Qwen3.6 27B | BigBang-v1 | **Qwen3.6 35B** |
|---|---|---|---|
| Speed | 63 tokens/s | 144 tokens/s | **164 tokens/s** |
| Sees images | yes | no | **yes** |
| Search test (3 questions, 7 facts) | 6 of 7, 323 s | all 7, 168 s | **all 7, 128 s** |
| Checking 7 photos | about 47 s | - | **19 s** |
| Summarizing 7 posts | 1 min 56 s | - | **41 s** |

In the end the 35B alone took over summaries, search and image checks. BigBang-v1 searched well but couldn't see images. The copy I downloaded was an unofficial upload by an individual, and it failed as soon as I connected it to Claude Code: the chat-format settings bundled with the model didn't match the shape of the requests Claude Code sends. So I removed it.

The 35B has a downside too. It takes 23.2 GB of graphics memory, so if any other program holds even a little memory, it slows down.

After the switch I checked with numbers whether the local AI could take on more work. The research and full-Claude-Code results are above in "Same screen, different brain"; here is the rest.

| Use | Test | Result |
|---|---|---|
| Sorting lots of photos | Captions and tags for 61 photos | 97 s (1.6 s per photo). In 5 I checked myself, the scene descriptions were all right |
| Short summaries | Summarizing 3 posts | 13 s |

For finding photos ("river and snowy forest," "domed building"), the tagging was good enough. Details were weak, though. It made up text that wasn't in a photo, called a stone wall a bridge and counted people loosely. It recognized only 1 of 5 AI-generated photos as AI-generated.

---

## The trap: one graphics card

![Sharing the GPU's 24 GB between an image generator and the local AI](../assets/diagrams_en/llm-gpu.svg)

This was the biggest trap I fell into. I also make images on the same card (ComfyUI). I finished an image job without closing that program, and it kept holding 15.8 GB. When I then ran the local AI, three quarters of the model didn't fit on the card and spilled onto the CPU, which does this kind of math far more slowly. No error appeared. The 27B I used then simply slowed from 63 tokens/s to 7. Only when the speed looked wrong did I check who was using the graphics memory (`nvidia-smi`) and find the cause. The 35B I use now takes 23.2 GB, so there is even less room.

Since then I follow three rules.

1. When an image job is done, always close the image program.
2. Before using the local AI, check that the model sits 100% on the graphics card (`ollama ps`).
3. Before making images again, unload the local model (`ollama stop`).

For anyone trying this, two more technical traps.

- Running Claude Code on a local model can fail mid-session with "model not found." The small model it uses for background work (the haiku alias) also has to point at the local model.
- Claude Code assumes an unknown model reads 200,000 tokens at a time. If you don't tell it the real size (65,536), the local runtime rejects requests once the conversation gets long.

---

## The test I ran on this post

I used the draft of this post to test two review steps. First I had the local AI read the draft and saved its list of findings to a file. Without opening that list, I did the same two reviews with Claude. Then I compared them. After switching models, I ran the 35B on the same draft too.

| | Reading as a math-averse reader | Korean proofreading |
|---|---|---|
| Time (27B → 35B) | 26 s → 8 s | 34 s → 12 s |
| Of Claude's findings, also found | 4 of 9 → 6 | 1 of 7 key ones → 2 |
| Useful findings only the local AI had | 3 → 3 | 2 → 0 |
| Wrong findings | almost none | 3 → 3 (called correct phrasing wrong) |

As a reader it was useful. "Why does spilling onto the CPU slow things down," "what does 4-bit mean" and "how did you notice who held the memory" were things I had missed, and they're now in the post. The 35B also caught a wrong analogy I had found myself.

For Korean proofreading both models went the wrong way. Most suggestions turned plain everyday words into stiff, formal ones, which would have made the Korean read more like a translation. So Korean proofreading stays with Claude, and the local AI's list is used only for the reader step.

---

## Takeaways

- A local AI can't replace Claude, but as a **reader** it's enough.
- The payoff grows with how much there is to read. For a few documents just use Claude; from dozens on, it clearly pays.
- Treat the results as drafts. Check numbers and names against the source, and leave judgment and editing to Claude.
- If you share the graphics card with other work, first check who is holding its memory.
- One model, Qwen3.6 35B, could take on summaries, search and image checks. Details and judgment are still weak.

---

### Sources and notices

Settings (KV cache quantization, context length, keep-alive) follow the official Ollama FAQ; the environment variables for running Claude Code on a local model follow the Ollama and Claude Code docs and community guides; tokens per PDF page follow Anthropic's PDF support documentation. Speeds, times and memory figures are single measurements on my PC on October 25, 2026, and the "if Claude read it itself" figures are estimates from character counts. The photos checked are not real places; I generated them with FLUX.2 [klein]. Claude and Claude Code are trademarks of Anthropic PBC; Qwen of Alibaba Cloud; Ollama of Ollama, Inc.; NVIDIA, GeForce and RTX of NVIDIA Corporation; Docker of Docker, Inc.; Microsoft Word, Excel and PowerPoint of Microsoft Corporation; Hangul (HWP) of Hancom Inc.; GitHub of GitHub, Inc.; FLUX of Black Forest Labs; ComfyUI of Comfy Org. They are used for identification only.

### Glossary

- *Local AI*: an AI model that runs on your own computer instead of an online service
- *Token*: the unit an AI reads and writes text in. Roughly three quarters of an English word
- *Claude usage*: how many tokens Claude has read and written. Each plan has a limit
- *Ollama*: a free program that downloads AI models and runs them on your computer
- *4-bit version (quantization)*: a version with its numbers shortened to save memory, at a small cost in quality
- *KV cache*: the memory where a model keeps what it has already read
- *Prompt caching*: remembering instructions so they don't have to be re-read. The local runtime didn't have it
- *Container (Docker)*: a box that runs a program apart from the rest of the system
- *SearXNG*: an open-source program that asks several search engines for you and gathers the results
- *MoE (mixture of experts)*: a model split into many "experts," using only some of them for each job. Fast for its size
