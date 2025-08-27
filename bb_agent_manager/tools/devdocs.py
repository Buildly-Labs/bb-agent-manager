from typing import List
import os, subprocess, tempfile, json

DEV_DOCS_TOOL = {
  "name": "update_devdocs",
  "description": "Create or update /devdocs entries and index with a summary and reuse notes.",
  "parameters": {
    "type": "object",
    "properties": {
      "files": {"type":"array","items":{"type":"string"}},
      "summary": {"type":"string"},
      "component_reuse_notes": {"type":"string"}
    },
    "required": ["files","summary"]
  }
}

async def update_devdocs(files: List[str], summary: str, component_reuse_notes: str = "") -> str:
    """
    Minimal placeholder: writes/updates devdocs index.md locally and commits.
    Replace this with your repo IO (gitpython or GH App).
    """
    entry = f"## Change\n\n**Files:** {', '.join(files)}\n\n**Summary:** {summary}\n\n**Reuse:** {component_reuse_notes}\n\n"
    os.makedirs("devdocs", exist_ok=True)
    index = "devdocs/index.md"
    with open(index, "a", encoding="utf-8") as f:
        f.write(entry)
    # naive local commit; in production, use a scoped token or GitHub App
    try:
        subprocess.run(["git","add",index], check=True)
        subprocess.run(["git","commit","-m","chore(devdocs): update index"], check=True)
        commit = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
    except Exception as e:
        commit = f"(not committed: {e})"
    return json.dumps({"status":"ok","commit":commit})
