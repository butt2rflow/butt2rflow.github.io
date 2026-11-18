---
title: "Don’t Spend Claude Tokens on Shopping: Send Muse and Use Its Free Allowance"
nav_title: "Shopping with Muse"
date: 2026-11-17
tags: [muse, mcp, claude-code, codex, cloudflare]
lang: en
description: "I wanted Muse to research products while I kept coding. Instead, I spent an evening fixing a tunnel and learning which box wanted the name of a secret."
---

# Don’t Spend Claude Tokens on Shopping: Send Muse and Use Its Free Allowance

Picking a single camera for my robot was eating into my Claude allowance. I compared fields of view, sellers, and shipping costs without fixing a line of code. Muse was good at shopping, and its free allowance gave me plenty of room. I figured I could send over my criteria and get back to coding.

## The short version

- I put the shopping tools on Muse's virtual machine and called them from Claude Code and Codex through Cloudflare Tunnel.
- A healthy tunnel still needs a route from the public hostname to the server. My service URL inside the VM also needed plain HTTP.
- Muse gives you a request ID first. Mine survived a disconnect, so I could pick up the result in a fresh session.

![Send criteria from Claude Code or Codex and pick up Muse’s research later](../assets/diagrams_en/muse-errand.png)

## The tunnel came up, and then I saw zero routes

I wanted a little service counter next to my coding window. **MCP** is an agreement that lets an AI app discover and call tools at that counter. Muse could reach its catalog from inside its virtual machine (VM), so that's where I put the Python MCP server. The program that handles queued requests and the tunnel connector ran there too. Claude Code and Codex stayed on my PC.

That evening, I tried a temporary Quick Tunnel and then ngrok. Neither connected. I switched to a named Cloudflare tunnel, but the VM's DNS, which looks up network addresses by name, didn't return the records the connector needed. Fixing that got me as far as the next problem. The VM couldn't connect directly to the outside. Late that night, I got the tunnel up by using `socat` to forward the connection through the VM's outbound proxy. That was specific to this VM.

The dashboard finally said **Healthy**. Next to it was **Routes 0**. The tunnel was up and had nowhere to send a request.

I added a **Published application** route with a public hostname, then got the protocol wrong. My PC talks HTTPS to Cloudflare, but the server inside the VM speaks plain HTTP. I set the **Service URL** to `http://localhost:8765` and left Path empty so both `/mcp` and `/healthz` could get through. [Cloudflare's published application docs](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/routing-to-tunnel/)

![A healthy tunnel with zero routes has nowhere to send requests until a route points to the VM’s HTTP server](../assets/diagrams_en/muse-routes.png)

## I put the password on the name tag

I tripped over the Codex settings too. An environment variable lets you pass a named value to a program when it starts. I put the actual secret in a box that wanted its name. It was like writing the password on a locker’s name tag.

![The config holds the environment variable name and the launched process receives the token value](../assets/diagrams_en/muse-name-tag.png)

## I clicked Allow and got Deny

The first catalog search brought up a permission card in **Muse chat**. I clicked **Allow**, got an error, and found **Deny** in the record. Search worked after I restarted the MCP server in a fresh context where the earlier denial no longer applied. That card grants access to read the catalog. A person reviews any purchase request separately.

![Catalog permission allows reading, while a person reviews purchase requests separately](../assets/diagrams_en/muse-permission.png)

When I sent research to the queue, I got `pending` and a request ID. Later that night, a lookup hit a 502. Muse reported that the server restarted and its old MCP sessions expired. Whether that restart was the 502's culprit, I still don't know.

In the new session, I looked up the **same request ID** and got `done` and the result. I'd opened and closed plenty of windows that night. At least I didn't have to ask Muse to shop twice.

![The request ID from pending retrieves the done result in a fresh session](../assets/diagrams_en/muse-ticket.png)

## If you’d like to try it

### 1. Try a lookup inside the VM

My server can search the catalog, look up product details, and read saved shopping preferences. For longer research, `ask_muse_to_shop` adds a job to the queue. Give `check_shopping_request` the request ID to read its status and result. The server can also queue a purchase request for a person to review in Muse chat. It places no orders and makes no payments.

Here's the little server I used to show the lookup. To use it with Muse itself, you'd need access to Muse's tools from the VM. In the server directory, run `(umask 077; set -o noclobber; openssl rand -hex 32 > .token)` to create a private token file and save `{"status":"pending"}` in `queue/demo.json`. Use `demo` as the request ID. Save the example as `server.py` and run `python3 server.py`. It listens on `127.0.0.1:8765` inside the VM. The `/mcp` endpoint exchanges MCP messages over HTTP (**Streamable HTTP**) and requires `Bearer <token>` in the authorization header. The `/healthz` endpoint just tells me whether the server answers. [Python MCP SDK docs](https://py.sdk.modelcontextprotocol.io/run/asgi/)

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

I ran this exact example on my PC (Python MCP SDK 2.3.0). `/healthz` answered 200, `/mcp` without a token slammed the door with a 401, and with the token the queue file opened right up. On the real server another program checks the queue every five minutes and saves results to disk. Research can take longer than one round.

### 2. Connect the tunnel and register the clients

Point the Cloudflare Published application route at `http://localhost:8765` inside the VM and try `/healthz` on the public hostname first.

On my PC, I kept the same token in a private file with `0600` permissions. Replace `/path/to/private/token` with the path to that file and replace `muse.example.com` in the server code and client settings with your public hostname. The Claude Code setting refers to the environment variable by name. The single quotes keep the shell from expanding `${MUSE_SHOPPING_TOKEN}` so Claude Code can read it when it connects. [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)

```bash
export MUSE_SHOPPING_TOKEN="$(cat /path/to/private/token)"
claude mcp add --transport http --scope user muse-shopping https://muse.example.com/mcp \
  --header 'Authorization: Bearer ${MUSE_SHOPPING_TOKEN}'
claude
```

In Codex’s `config.toml`, put the name (`MUSE_SHOPPING_TOKEN`) in `bearer_token_env_var`. Codex looks up the token in its environment using that name. [Codex MCP docs](https://developers.openai.com/codex/mcp)

```toml
[mcp_servers.muse-shopping]
url = "https://muse.example.com/mcp"
bearer_token_env_var = "MUSE_SHOPPING_TOKEN"
```

Even with the name fixed, a Codex process launched somewhere else won't inherit the token from my terminal. I used a launcher that reads the file and hands the token to a fresh Codex process. This is the short version of the `--no-daemon` launch I used with CLI 0.169.0.

```bash
MUSE_SHOPPING_TOKEN="$(cat /path/to/private/token)" codex --no-daemon
```

When `/mcp` showed `unknown (0 tools)`, the tool list was unavailable in that session. I checked the public health endpoint and the authenticated tool list separately. In the end both Claude Code and Codex connected with this setup. When I forgot the environment variable and opened Claude Code, a 401 came straight back. Codex, started fresh with the token handed over, brought back a finished result. Why the old session showed `unknown`, I never found out.

### 3. Look up the same request ID

On the real Muse server, save the ID from `ask_muse_to_shop` and give it to `check_shopping_request`. If you see `pending`, check the same ID a little later.

For a 502, I'd compare `/healthz` inside the VM with the public endpoint. If the local check fails, I'd check the server first. If only the local check works, I'd look at the tunnel and its service URL. An expired MCP session after a restart needs a fresh connection.

### Where to look when it gets stuck

| Symptom | What to check |
| --- | --- |
| Healthy, Routes 0 | Add a route from the public hostname to the service URL inside the VM. |
| 401 or zero tools | Check the authorization header and the launched process’s token environment. |
| 502 | Compare `/healthz` inside the VM and at the public hostname. |
| Search fails after approval | Check the permission card and its record in Muse chat. |

**Related** [Let local AI do the reading](local-llm-reading.md) · [Max 5x Was Too Expensive. I Only Needed Twice as Much: The Night I Put Codex to Work in Claude Code](ai-workbench-routing.md)
