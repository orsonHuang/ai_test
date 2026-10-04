"""Project-local MCP playtest helpers. Inputs use native viewport coordinates."""
import json
from mcp_bridge import GodotMCP, compact_images, EVIDENCE


class DemoProbe:
    def __init__(self):
        self.client = GodotMCP()
        self.call("session_activate", session_id="cat-idle")

    def call(self, tool, **args):
        response = self.client.call(tool, args)
        if response.get("isError"):
            raise RuntimeError(response)
        return response.get("structuredContent", response)

    def evaluate(self, code):
        return self.call("editor_manage", op="game_eval", params={"code": code}).get("result")

    def elements(self):
        return self.call("game_manage", op="get_ui_elements", params={"max_depth": 20})["elements"]

    def click(self, name):
        matches = [e for e in self.elements() if e["name"] == name and e.get("visible") and not e.get("disabled")]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one enabled {name}, got {len(matches)}")
        rect = matches[0]["global_rect"]
        point = {axis: rect["position"][axis] + rect["size"][axis] / 2 for axis in ["x", "y"]}
        transform = self.evaluate('return get_viewport().get_final_transform()')
        physical = {axis: transform['origin'][axis] + point['x'] * transform['x'][axis] + point['y'] * transform['y'][axis] for axis in ['x', 'y']}
        self.click_point(physical)
        return matches[0].get("text")

    def click_point(self, point):
        for pressed in [True, False]:
            self.call("game_manage", op="input_mouse", params={"event": "button", "position": point, "button": "left", "pressed": pressed})

    def shot(self, name):
        result = compact_images(self.client.call("editor_screenshot", {"source": "game", "max_resolution": 1600, "include_image": True}), name)
        (EVIDENCE / (name + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
        return result

    def state(self):
        return self.evaluate('var g = get_tree().current_scene\nreturn {"phase": g.run.data.phase, "current": g.run.data.current, "ap": g.run.budget(), "party": g.run.members(), "modal": g.n("Modal").visible, "inventory": g.run.data.inventory.size(), "error": g.run.error_message}')
