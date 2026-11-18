---
title: "How to connect Claude Code and Codex to Muse over MCP"
nav_title: "Set up Muse Shopping MCP"
date: 2026-11-17
tags: [muse, mcp, claude-code, codex, cloudflare]
lang: en
description: "Set up a Muse shopping MCP server on a VM, expose it through Cloudflare Tunnel, and connect Claude Code and Codex from your PC."
---

# How to connect Claude Code and Codex to Muse over MCP

I use Muse as a shopping assistant. This setup lets me send it a search from Claude Code or Codex and look up the result later. MCP is the protocol the coding tools use to discover and call Muse's tools.

## 1. Decide what runs on each machine

- **On the Muse VM**, run the custom MCP server, its shopping queue worker, and the Cloudflare tunnel connector. The bridge needs access to the shopping tools inside Muse. The server is specific to my Muse environment and has no public install package. To build your own bridge, you need equivalent access on the VM.
- **On your PC**, run Claude Code or Codex. Both use the same public HTTPS MCP URL and bearer token.

The request path is **Claude Code or Codex → HTTPS MCP → Cloudflare Tunnel → MCP server in the Muse VM → Muse shopping tools**. Throughout this guide, replace `muse.example.com` with your own hostname.

**Check.** You can run programs on the VM with access to the Muse shopping backend, and you can sign in to the client you plan to use on your PC.

## 2. Create and store the token

On the VM, generate a random token once in your server directory. The following Bash command creates `.token` with owner-only permissions and refuses to overwrite an existing file.

```bash
(umask 077; set -o noclobber; openssl rand -hex 32 > .token)
```

Have the server read that file at startup. Transfer the value to the PC using a trusted secret store or secure file transfer. For the examples below, save it as `~/.config/muse-shopping/token`, in a private directory with file permissions `0600`. Store only the raw value. Keep the token out of chat, shell arguments, logs, screenshots and Git.

**Check.** On both machines, check the token file with `ls -l`. The permissions should show `-rw-------`. You will test authentication when you start the server.

## 3. Set up the MCP server on the Muse VM

Use the Python MCP SDK to register these six tools in your bridge. The handlers call the Muse functions that are available inside the VM.

| Tool | What it does |
| --- | --- |
| `search_products` | Returns catalog matches during the call. Seller stock and shipping still need verification. |
| `product_details` | Looks up one catalog item and its variants by product ID. |
| `search_memory` | Reads saved shopping preferences. Keep this tool read-only. |
| `ask_muse_to_shop` | Queues a fuller search, including seller, stock and delivered-cost checks. Returns a request ID immediately. |
| `check_shopping_request` | Reads the status and result for a request ID. |
| `file_purchase_request` | Queues a request for a person to review in Muse chat. The bridge never places orders or pays. |

Listen on the VM loopback interface at port `8765`. Serve MCP with **Streamable HTTP** on `/mcp` and check `Authorization: Bearer <token>` on every request to that path. Return HTTP 401 for missing or invalid credentials. Add a separate, unauthenticated `GET /healthz` that reports only whether the server is up.

This **minimal example** is separate from the original Muse server. It uses `MCPServer` from the Python MCP SDK 2.x and registers one lookup tool. Save it as `server.py` and run `python3 server.py` from the server directory so it can read `.token` and look up the request ID in `queue/<ID>.json`. [Official Python SDK docs](https://py.sdk.modelcontextprotocol.io/run/asgi/)

Claude ran the example unchanged with Python MCP SDK 2.3.0 (the pip package `mcp`). `GET /healthz` returned 200, and a request to `/mcp` without a token returned 401. With authentication, `initialize` succeeded and calling `check_shopping_request` through `tools/call` returned the queue file contents.

```python
import json
import re
from pathlib import Path
from secrets import compare_digest

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

token = Path(".token").read_bytes().strip()
if not token:
    raise SystemExit("The .token file is empty.")
mcp = MCPServer("Muse shopping example")

@mcp.tool()
def check_shopping_request(request_id: str) -> dict:
    """Read the status and result for a shopping request."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", request_id):
        raise ValueError("Invalid request ID")
    return json.loads((Path("queue") / f"{request_id}.json").read_text(encoding="utf-8"))

@mcp.custom_route("/healthz", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})

async def require_token(request, call_next):
    header = request.headers.get("authorization", "").encode("latin-1")
    if request.url.path.rstrip("/") == "/mcp" and not compare_digest(header, b"Bearer " + token):
        return JSONResponse({"error": "Unauthorized"}, 401, headers={"WWW-Authenticate": "Bearer"})
    return await call_next(request)

security = TransportSecuritySettings(allowed_hosts=["127.0.0.1:*", "localhost:*", "muse.example.com"])
app = mcp.streamable_http_app(transport_security=security)
app.add_middleware(BaseHTTPMiddleware, dispatch=require_token)
uvicorn.run(app, host="127.0.0.1", port=8765)
```

For queued work, save each request under its ID in persistent storage. Run a worker on a schedule to process pending requests and save results under the same IDs. My worker runs every five minutes. A search can take longer than one worker interval, and its ID survives a normal MCP server restart.

**Check.** On the VM, `curl -fsS http://localhost:8765/healthz` succeeds. A request to `/mcp` without the token gets 401. With an authenticated MCP test client, run `initialize`, send `notifications/initialized`, then run `tools/list` in the same session. Expect six tools for the full server and one for the example above.

## 4. Publish the endpoint through Cloudflare Tunnel

1. Use a domain managed in your Cloudflare account. In the Cloudflare One dashboard, create a named tunnel and run its `cloudflared` connector on the Muse VM using the connector credential. Keep that credential private and separate from the MCP bearer token.
2. In the tunnel's **Routes** tab, add a **Published application** route (the public hostname). Set the hostname to your chosen subdomain and the service URL to `http://localhost:8765`. Leave the route path blank so both `/mcp` and `/healthz` reach the server. The VM service uses plain HTTP locally. Your PC uses HTTPS at Cloudflare.
3. Confirm that the tunnel shows the route. **Healthy with Routes 0** means the connector is online but has no hostname route. Adding a DNS record alone leaves that route missing. [Cloudflare's published application guide](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/routing-to-tunnel/)

![The PC connects over HTTPS to Cloudflare. The VM opens the tunnel and forwards requests to the local MCP server.](../assets/diagrams_en/muse-tunnel.svg)

Only if your VM restricts outbound traffic as mine did, check DNS discovery and edge connectivity separately. In my VM, a local DNS stub in the connector's mount namespace handled discovery, and HTTP/2 used a local `socat` forwarder through the VM's outbound proxy. The proxy credential was scoped to the launch session, so the forwarder and connector started together. The watchdog restarted the pair only when there were no live tunnel connections.

**Check.** From the PC, `curl -fsS https://muse.example.com/healthz` succeeds. Repeat the authenticated `initialize` and `tools/list` check against `https://muse.example.com/mcp`. A healthy endpoint and a six-tool list check different parts of the setup.

## 5. Register Muse in Claude Code on the PC

In Bash, load the token into the launch environment and register the server at user scope. Keep the single quotes around the header so the shell passes the variable reference to Claude Code. Claude Code resolves it when connecting. [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp)

```bash
export MUSE_SHOPPING_TOKEN="$(cat "$HOME/.config/muse-shopping/token")"
claude mcp add --transport http --scope user muse-shopping https://muse.example.com/mcp \
  --header 'Authorization: Bearer ${MUSE_SHOPPING_TOKEN}'
claude
```

This adds the following entry under `mcpServers.muse-shopping` in `~/.claude.json`. The effective header on the connection is `Authorization: Bearer <token>`.

```json
{
  "type": "http",
  "url": "https://muse.example.com/mcp",
  "headers": {
    "Authorization": "Bearer ${MUSE_SHOPPING_TOKEN}"
  }
}
```

**Check.** In the new Claude Code session, open `/mcp` and check that `muse-shopping` is connected and its tools are listed. For future launches, load the same environment variable before starting Claude Code.

## 6. Register Muse in Codex on the PC

Add this to `~/.codex/config.toml`, or edit the existing Muse entry. On this setup, `approval_mode = "approve"` pre-approves these three tool calls in Codex. Muse's catalog permissions and human purchase approval are separate. [Codex MCP configuration](https://developers.openai.com/codex/mcp)

```toml
[mcp_servers.muse-shopping]
url = "https://muse.example.com/mcp"
bearer_token_env_var = "MUSE_SHOPPING_TOKEN"

[mcp_servers.muse-shopping.tools.search_products]
approval_mode = "approve"

[mcp_servers.muse-shopping.tools.ask_muse_to_shop]
approval_mode = "approve"

[mcp_servers.muse-shopping.tools.check_shopping_request]
approval_mode = "approve"
```

`bearer_token_env_var` is the **name** Codex looks up. The actual Codex process needs the raw token in its environment. Codex builds the authorization header. An export in one terminal only reaches programs launched from that environment. If a GUI launcher or existing background process misses the value, start a fresh CLI instance with the token supplied explicitly.

![Codex reads the variable name from its config and the secret value from its process environment.](../assets/diagrams_en/muse-token.svg)

Save this Linux example as `start-codex-muse.py` and run `python3 start-codex-muse.py` from your project directory. It reads the private file and passes the secret through the process environment. `--no-daemon` starts the CLI directly in Codex CLI 0.169.0, the version I used.

```python
import os
from pathlib import Path
import sys

token = (Path.home() / ".config/muse-shopping/token").read_text().strip()
if not token:
    sys.exit("The Muse token file is empty.")

env = os.environ.copy()
env["MUSE_SHOPPING_TOKEN"] = token
os.execvpe("codex", ["codex", "--no-daemon", *sys.argv[1:]], env)
```

**Check.** Open `/mcp` in the fresh Codex session and look for `muse-shopping: connected (6 tools)`. `unknown (0 tools)` means that session has no usable tool list. Check the environment and transport before drawing conclusions about any queued search.

## 7. Queue your first research request

> Use Muse to compare desk lamp options under CA$50 including delivery to Canada. Report only; do not buy.

Use `ask_muse_to_shop` with `intent: "find"`. Put the decision criteria in the request, ask for unverified details to be labeled, and keep the returned `request_id`. `pending` means the queue accepted the work. When you want the result, call `check_shopping_request` with that ID. While it is pending, keep using the same ID and avoid submitting another search. If the requirements change, say “Replace request `<ID>`” in the new request so Muse can mark the old one as superseded.

Muse may show a catalog access card in **Muse chat**. Open Muse chat before the first search. If you see a card, review it promptly. Muse gave me about a minute to respond. It grants access to search the catalog. Any purchase request needs separate human approval in Muse chat, and the bridge never buys anything.

![A catalog access card permits research. Any purchase request goes to a person for separate review.](../assets/diagrams_en/muse-approval.svg)

**Check.** First confirm you receive a request ID. Later, confirm the same ID returns `done` and the research result.

## 8. Troubleshoot from the VM to the client

| Symptom | What to do |
| --- | --- |
| `unknown (0 tools)` | Check the public `/healthz`, then try authenticated MCP initialization and tool listing. If those succeed, open a fresh client session and check `/mcp`. |
| Missing `MUSE_SHOPPING_TOKEN` or 401 | Check the variable name in config, the token file, and the process that actually starts the client. Confirm the client uses the same token as the server. Keep the value out of diagnostic output. |
| Claude Code shows `Failed to connect ... HTTP 401` | Claude Code started without `MUSE_SHOPPING_TOKEN` in its environment. Load the variable as shown in step 5, then restart Claude Code. |
| HTTP 502 | Compare the VM's local `/healthz` with the public one. If local health fails, check the MCP process. If local works, check the tunnel connection and its origin URL. Once it recovers, retry the lookup with the same ID. |
| MCP session expires after a restart | Reconnect or open a fresh client session to initialize MCP again. Reuse the shopping request ID from persistent storage. |
| Catalog approval times out or Allow errors | Open Muse chat before retrying and review the card promptly if it appears. In my setup, a failed Allow was recorded as Deny. Restarting the MCP server in a fresh context fixed it. |
| Tunnel is Healthy, Routes 0 | Add the Published application route to `http://localhost:8765` and retry public `/healthz`. |

**Check.** After a fix, confirm public health and the six-tool list. If you already queued a search, verify recovery by checking its existing ID.

I checked both clients against the real Muse server with this setup on November 17, 2026. Claude Code connected with the `${MUSE_SHOPPING_TOKEN}` header and got HTTP 401 when started without the variable, and Codex returned a finished result from a tool call after starting through the token launcher.

---

**Related** [Local AI for reading](local-llm-reading.md) · [Build an MCP bridge from Claude Code to Codex and local Qwen](ai-workbench-routing.md)
