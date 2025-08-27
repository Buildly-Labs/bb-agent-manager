bb-agent-manager/
├─ pyproject.toml
├─ README.md
├─ bb_agent_manager/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ plugin.py            # <- register(app, settings) lives here
│  ├─ router.py            # FastAPI APIRouter for /agent
│  ├─ orchestrator.py      # agent loop + tool-calling glue
│  ├─ llm/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ gemini.py
│  │  ├─ ollama.py
│  │  └─ router.py
│  ├─ tools/
│  │  ├─ __init__.py
│  │  ├─ devdocs.py
│  │  ├─ labs_sync.py
│  │  ├─ git_ops.py
│  │  └─ test_ops.py
│  └─ mcp/
│     ├─ __init__.py
│     └─ server.py         # optional MCP server mounted under /mcp (HTTP transport)
└─ tests/
   └─ test_smoke.py


## Option A — entry-point auto-load (preferred)

Add your private index/credentials to BabbleBeaver’s environment (so pip can read your private repo).

Install in BabbleBeaver’s runtime image:

pip install bb-agent-manager @ git+ssh://git@github.com/your-org/bb-agent-manager.git


In BabbleBeaver startup (where the FastAPI app is created), add this generic loader:

# in babblebeaver/main.py (or wherever app is constructed)
import pkg_resources

for ep in pkg_resources.iter_entry_points(group="babblebeaver.modules"):
    try:
        register_fn = ep.load()
        register_fn(app, {})  # can pass merged settings dict if you keep a central config
    except Exception as e:
        print(f"[BB] Failed to load module {ep.name}: {e}")


No changes to the agent module are required—register mounts /agent and /agent/mcp.

## Option B — explicit import

If you don’t want dynamic entry-points:

# babblebeaver/main.py
from bb_agent_manager import register as register_bb_agent
register_bb_agent(app, {})

11) Env & Docker compose (example)

Add to BabbleBeaver’s .env (or secrets):

LABS_BASE_URL=https://labs.buildly.io/api
LABS_API_TOKEN=...
BB_AM_DEFAULT_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro
OLLAMA_BASE_URL=http://ollama:11434/v1
OLLAMA_MODEL=llama3.1:8b
BB_AM_MOUNT_PATH=/agent
GITHUB_TOKEN=ghp_...


Compose snippet (add Ollama if you want local models):

services:
  babblebeaver:
    build: .
    env_file: .env
    volumes:
      - ./:/app
    ports:
      - "8000:8000"
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
volumes:
  ollama: {}

12) How an IDE/Agent would call it

Chat (from any UI) POST to /agent/chat:

{
  "provider": "gemini",
  "messages": [
    {"role":"system","content":"You are the Buildly Agent. Use tools to update devdocs & Labs."},
    {"role":"user","content":"Refactor user service; update devdocs and create a Labs task."}
  ]
}


MCP-like tooling:

GET /agent/mcp/tools → discover available tools

POST /agent/mcp/invoke { "name": "update_devdocs", "arguments": {...} }

13) Where to wire Buildly-specific behavior

Replace the stubs in tools/ with:

git_ops.py using GitHub App (least-privilege) to branch/commit/PR,

devdocs.py writing to /devdocs/* and maintaining an index with timestamps,

labs_sync.py pointing at your real Labs endpoints for tasks, PR linkage, release notes, etc.

If BabbleBeaver already has a module registry or DI container, you can have register() receive shared services (e.g., repo access) via settings_dict.

14) Security notes (quick wins)

Enforce a repo allow-list and path allow-list inside tools (e.g., only devdocs/, src/, tests/).

Keep model provider choice behind env vars per deployment.

Use a GitHub App instead of a PAT where possible; restrict to needed repos.

That’s it. This slots into BabbleBeaver as a clean, private module with:

a single register(app, settings) entrypoint,

FastAPI routes for chat and tool invocation,

a provider router to flip between Gemini and Ollama, and

Buildly-opinionated tools for /devdocs + Labs sync you can harden over time.

