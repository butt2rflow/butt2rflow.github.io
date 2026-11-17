---
title: "Shopping from the coding screen: Muse as an MCP server"
nav_title: "Ask Muse to shop"
date: 2026-11-17
tags: [muse, mcp, claude-code, codex, cloudflare, so-101]
lang: en
description: "Connecting remote Muse shopping tools to Claude Code and Codex, then separating queued work, approvals, credentials and stale sessions in a real debugging session."
---

# Shopping from the coding screen: Muse as an MCP server

I was looking for a camera for the wrist of a small SO-101 robot arm. Fixed focus, USB, a small board, and no fisheye lens. A mounting problem had turned into a comparison of shopping listings.

I wanted to stay in the coding screen and say:

> Ask Muse to find a fixed-focus SO-101 wrist camera. Exclude fisheye lenses, compare shipping to Canada and prices in CAD, and do not buy anything.

Muse is the AI assistant I use for product research. Claude Code and Codex are the AI tools I use for coding. I connected Muse's shopping tools through a separate MCP server. Claude Code submitted a camera search and received the final result. A freshly launched Codex retrieved an existing RAM search result. Getting there involved missing credentials, a broken connection and work that had finished before I could retrieve it.

![The coding client sends requirements to Muse through MCP and receives research; purchasing remains a separate human decision](../assets/diagrams_en/muse-delegate.svg)

## The short version

- Both clients made successful calls, with different verification scopes: a full camera search in Claude Code and retrieval of an existing RAM result in a fresh Codex.
- This is a custom server using shopping tools available in my Muse environment, not a public package that gives everyone the same catalog access.
- Direct search and queued research have different response patterns. An accepted job is not a completed search.
- Catalog permission and purchase approval are separate. No purchase was made.

## A common way to call another tool

In the [previous article](local-llm-reading.md), Claude delegated reading to a local AI. Here it delegates product research to Muse. MCP supplies a common format for tool calls. Claude Code or Codex turns my request into a call and receives the response; neither client needs to click through the other's interface.

My server exposed six tools:

| Job | Custom server tool |
|---|---|
| Find product candidates directly | `search_products` |
| Check a product's variants and availability | `product_details` |
| Read saved shopping preferences | `search_memory` |
| Queue research including seller checks | `ask_muse_to_shop` |
| Retrieve a queued job's status and result | `check_shopping_request` |
| Prepare a request for human purchase approval | `file_purchase_request` |

These are this server's tool names, not shopping commands built into MCP. Preparing a purchase request does not execute payment.

## Reaching the server inside a remote VM

Muse ran in a remote virtual machine. A server listening only inside that machine was not reachable from my PC, so I used Cloudflare Tunnel.

![Requests reach a public HTTPS endpoint, cross the tunnel and arrive at the local MCP server; the VM initiates the tunnel connection](../assets/diagrams_en/muse-tunnel.svg)

The VM establishes an outbound tunnel to Cloudflare. A public hostname routes requests through it to a local service. This is the connection pattern described in [Cloudflare's documentation](https://developers.cloudflare.com/tunnel/).

I had to check two things: the tunnel connection and the public hostname's route to the internal server. A Healthy label alone did not establish that a request could reach the shopping tools.

This VM also required an outbound proxy. Its initial setup record includes temporary-tunnel failures, DNS problems and failed edge connections. The eventual setup used HTTP/2 plus a forwarding process and a separate DNS responder. Those were accommodations for this VM, not a standard checklist for a normal PC.

To reproduce the architecture, first build a server around tools you are authorized to use and verify it locally. Then add remote access, authentication and a client registration. This article does not publish the whole server implementation; copying the client settings alone will not recreate the service.

## A variable name is not a credential

The longest Codex problem was credential delivery. A token is the secret value presented to the server. An environment variable gives a process a name under which it can read that value.

![The configuration contains an environment variable name; the running Codex process must be able to read the secret value under that name](../assets/diagrams_en/muse-token.svg)

My configuration had this shape, with an example hostname:

```toml
[mcp_servers.muse-shopping]
url = "https://muse.example.com/mcp"
bearer_token_env_var = "MUSE_SHOPPING_TOKEN"
```

The field takes a variable name, not the token itself, as explained in the [Codex MCP documentation](https://developers.openai.com/codex/mcp/). My logs repeatedly said that this variable was unavailable. It also happened in an in-process run, so the shared background process alone could not explain it.

A Python launcher eventually read the already stored credential and passed it into a new Codex process's environment. It did not print the token or put it in command-line arguments. My ordinary right-click Codex launcher lacked that extra step, so it could not guarantee the same environment.

Claude Code used a remote HTTP registration. Its connection and authentication options are documented in the [Claude Code MCP guide](https://code.claude.com/docs/en/mcp). In this session it completed the camera search. These observations concern specific launch environments and sessions, not a general ranking of every version of either product.

## Search now or queue work

I mostly used the queue after direct searches encountered approval waits and failures. A queue is a list of work to process in the background.

![Direct search returns products or an error in one call; queued work returns pending and an ID, then a later lookup returns done and the result](../assets/diagrams_en/muse-queue.svg)

| Path | First response | Next action |
|---|---|---|
| `search_products` | Candidates or an error | Check details |
| `ask_muse_to_shop` | Job ID and `pending` | Look up that same ID later |

My worker checked the queue every five minutes. That did not guarantee completion within five minutes. In the saved camera conversation, the request was submitted at 00:20, still pending at 00:24 and 00:29, and returned a completed result at 00:30. These are November 17 conversation timestamps in Toronto local time.

```text
Use ask_muse_to_shop with intent=find.
Compare Canadian shipping and totals in CAD. Do not buy.
Give me the request ID.
```

Later:

```text
Do not submit a new search.
Use check_shopping_request to retrieve the previous request ID.
```

Losing the connection did not prove the job was gone. My RAM search later returned `done` and its products under the original ID. Resubmitting before checking could duplicate the research.

## What the approval card allows

Catalog access and purchasing are different permissions.

![Allowing catalog access permits research; a purchase request still goes to a person for review and approval](../assets/diagrams_en/muse-approval.svg)

Muse explained that a required catalog approval would appear in its chat. Keeping that chat open on a phone would make the card visible; according to its guidance, the request could expire after about 60 seconds without a response. There was an actual case in which Allow could not be selected and Deny was chosen instead.

I did not verify a phone push notification while the app was closed. Nor does one card-free queue run guarantee that all later requests need no permission. This is guidance for this Muse setup, not a universal MCP rule.

## Reading the camera result

I revised the search to a diagonal field of view of roughly 60–90°, excluding fisheye lenses, while keeping fixed focus, USB UVC, Linux support and a small wrist-mountable board. Diagonal and horizontal fields of view are different measurements. UVC is a standard USB camera interface. Fixed focus also does not guarantee sharpness at the robot's working distance.

Muse's first candidate was Arducam B0196. I treated the answer as a research result with unresolved questions, not an order-ready recommendation:

| Muse reported | Still to check |
|---|---|
| B0196, fixed focus, UVC, 75° diagonal / 60° horizontal | Exact model and lens combination |
| A 31×31 mm board | The same answer flagged a conflicting 38×38 mm specification |
| US$29.99, approximately CA$42 | Shipping and import costs were missing from the delivered total |

The useful result was a shortlist plus questions to resolve before printing a mount. I did not independently recheck the retailer specifications and prices for this article, so these historical figures are not current buying advice.

## The tunnel recovered; the session might not have

Codex showed `unknown (0 tools)`—an unknown status with no available tools—and one retrieval returned HTTP 502, a failure to obtain a valid response along the gateway path.

![Check tunnel connectivity, credentials and MCP sessions separately; success at one layer does not establish success at all layers](../assets/diagrams_en/muse-recovery.svg)

I asked Muse to inspect its logs around 00:00–00:20 on November 17, Toronto time. It reported an expired or unknown session rejection at 00:03:15; several processes stopping together around 00:08; a watchdog restart around 00:10–00:11; and two restored edge connections. Old-session rejections continued afterward, alongside new sessions. The client responsible for each rejection was not identified.

Muse attributed the common interruption to VM replacement. I did not independently inspect the raw logs or VM lifecycle records. A common VM interruption fits the report, but replacement is not established by uptime and simultaneous stops alone. Session errors also predated that interruption.

An MCP session ID groups requests into a conversation. It is different from a shopping job ID. The [Streamable HTTP specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#session-management) requires a client to reinitialize when a session-using server returns 404 for a terminated session.

A fresh Codex, started with the credential launcher, retrieved the old RAM job at 00:29. Claude Code received the camera result at 00:30. That verified working calls from both clients. Because credential forwarding and the fresh session changed together in Codex, I could not isolate which change restored it or explain the earlier unknown display conclusively.

Other users have reported related issues: [Codex #30125](https://github.com/openai/codex/issues/30125) concerns token-variable visibility and [#4955](https://github.com/openai/codex/issues/4955) requests individual MCP reconnection. They are useful comparisons, not proof of the cause here.

## What I will do next time

I will specify the camera's focus method, size, field-of-view convention and destination at the start, retain the job ID, and check known facts before acting on a polished recommendation. For this camera, confirming dimensions comes before placing an order.

---

*Personal setup and usage record from November 16–17, 2026, using Claude Code 2.1.296 and Codex CLI 0.169.0. Names identify the products and do not imply an official integration or affiliation. Diagrams are original. Product examples are historical Muse responses, not guarantees of current availability or price.*

**Related:** [Local AI for reading](local-llm-reading.md) · [Claude oversees; the tools share the work](ai-workbench-routing.md)
