"""Project-local client for the already running Godot AI HTTP MCP server."""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PROJECT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT.parent / "docs" / "verification" / "godot-demo-v1"


class GodotMCP:
    def __init__(self) -> None:
        self.url = "http://127.0.0.1:8000/mcp"
        self.headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        self.counter = 0
        self.info = self.rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "RogueIdle-demo-builder", "version": "1.0"}})
        self.rpc("notifications/initialized", {}, notification=True)

    def rpc(self, method: str, params: dict, notification: bool = False) -> dict:
        self.counter += 1
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            payload["id"] = self.counter
        request = urllib.request.Request(self.url, json.dumps(payload).encode("utf-8"), self.headers)
        with urllib.request.urlopen(request, timeout=55) as response:
            session_id = response.headers.get("Mcp-Session-Id")
            if session_id:
                self.headers["Mcp-Session-Id"] = session_id
            raw = response.read().decode("utf-8")
        if not raw:
            return {}
        if raw.startswith("event:") or raw.startswith("data:"):
            result = next(json.loads(line[6:]) for line in raw.splitlines() if line.startswith("data: "))
        else:
            result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(result["error"])
        return result.get("result", {})

    def call(self, name: str, arguments: dict) -> dict:
        return self.rpc("tools/call", {"name": name, "arguments": arguments})


def compact_images(value, prefix: str):
    if isinstance(value, dict):
        if value.get("type") == "image" and "data" in value:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            suffix = ".png" if "png" in value.get("mimeType", "") else ".jpg"
            path = EVIDENCE / (prefix + suffix)
            path.write_bytes(base64.b64decode(value["data"]))
            return {"type": "saved_image", "path": str(path), "mimeType": value.get("mimeType")}
        return {key: compact_images(item, prefix + "_" + key) for key, item in value.items()}
    if isinstance(value, list):
        return [compact_images(item, prefix + "_" + str(i)) for i, item in enumerate(value)]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", action="store_true")
    parser.add_argument("--requests", type=Path)
    parser.add_argument("--name", default="probe")
    parser.add_argument("--brief", action="store_true")
    args = parser.parse_args()
    client = GodotMCP()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if args.catalog:
        catalog = client.rpc("tools/list", {})
        (EVIDENCE / "mcp_catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"server": client.info.get("serverInfo"), "tools": [{"name": t["name"],
              "description": t.get("description", "")[:160]} for t in catalog.get("tools", [])]}, ensure_ascii=False, indent=2))
    if args.requests:
        requests = json.loads(args.requests.read_text(encoding="utf-8-sig"))
        results = []
        for index, request in enumerate(requests):
            result = compact_images(client.call(request["name"], request.get("arguments", {})), f"{args.name}_{index}")
            entry = {"tool": request["name"], "result": result}
            results.append(entry)
            printable = entry
            if args.brief and "structuredContent" in result:
                printable = {"tool": request["name"], "result": result["structuredContent"]}
            print(json.dumps(printable, ensure_ascii=False, indent=2), flush=True)
            (EVIDENCE / (args.name + ".json")).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            if result.get("isError"):
                raise SystemExit("MCP returned an error; subsequent operations skipped")
            data = result.get("structuredContent", {})
            if any("Parse Error:" in str(d.get("text", "")) for d in data.get("diagnostics", [])):
                raise SystemExit("GDScript parse diagnostics; subsequent operations skipped")
            if request["name"] == "test_run" and data.get("failed", 0):
                raise SystemExit("Godot tests failed; inspect the saved verification record")


if __name__ == "__main__":
    main()
