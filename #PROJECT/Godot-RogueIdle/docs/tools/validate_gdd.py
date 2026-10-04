"""Static GDD integrity checks. Not a combat simulator or balance test."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "GDD" / "data"
ARCHIVE = ROOT / "docs" / "archive" / "2026-10-04-before-gdd-v1"
errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as stream:
        result = list(csv.DictReader(stream))
    check(bool(result), f"Empty table: {name}")
    check(all(None not in row and all(v is not None for v in row.values()) for row in result),
          f"Malformed CSV fields: {name}")
    return result


def indexed(items: list[dict[str, str]], key: str, name: str) -> dict[str, dict[str, str]]:
    check(len({r[key] for r in items}) == len(items), f"Duplicate {key}: {name}")
    return {r[key]: r for r in items}


def ids(value: str) -> list[str]:
    return value.split("|") if value else []


def main() -> dict:
    documents = sorted((ROOT / "GDD").rglob("*.md"))
    documents += sorted((ROOT / "project-plan").glob("*.md"))
    documents += sorted((ROOT / "docs" / "design").glob("gdd-v1-*.md"))
    documents += [ROOT / "README.md", ARCHIVE / "ARCHIVE_NOTES.md"]
    link_count = 0
    for document in documents:
        content = document.read_text(encoding="utf-8-sig")
        check("\ufffd" not in content, f"Encoding replacement character: {document}")
        check(content.count("```") % 2 == 0, f"Unclosed fenced block: {document}")
        for target in re.findall(r"\]\(([^\n)]+)\)", content):
            target = target.strip().strip("<>")
            if re.match(r"^[a-zA-Z][\w+.-]*:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (document.parent / target).resolve()
            check(resolved.is_relative_to(ROOT), f"Link outside project: {document}: {target}")
            check(resolved.exists(), f"Broken link: {document.relative_to(ROOT)} -> {target}")
            link_count += 1

    with (ARCHIVE / "manifest.csv").open(encoding="utf-8-sig", newline="") as stream:
        manifest = list(csv.DictReader(stream))
    check(len(manifest) == 37, "Expected 37 original archive files")
    for item in manifest:
        path = (ARCHIVE / item["path"]).resolve()
        check(path.is_relative_to(ARCHIVE), f"Archive path escaped: {item['path']}")
        if not path.exists():
            check(False, f"Archive file missing: {item['path']}")
            continue
        raw = path.read_bytes()
        check(len(raw) == int(item["bytes"]), f"Archive byte count: {item['path']}")
        check(hashlib.sha256(raw).hexdigest().lower() == item["sha256"].lower(),
              f"Archive SHA256 mismatch: {item['path']}")

    rules = indexed(rows("rules.csv"), "id", "rules")
    values = {key: float(value["value"]) for key, value in rules.items()}
    check(all(math.isfinite(v) for v in values.values()), "Non-finite rule value")
    regions = indexed(rows("regions.csv"), "id", "regions")
    units = indexed(rows("units.csv"), "id", "units")
    activities = indexed(rows("activities.csv"), "id", "activities")
    gear = indexed(rows("equipment.csv"), "slot", "equipment")
    affixes = indexed(rows("affixes.csv"), "id", "affixes")
    skills = indexed(rows("skills.csv"), "id", "skills")
    events = indexed(rows("events.csv"), "id", "events")
    sets = rows("sets.csv")
    family_ids = {row["set_id"] for row in sets}
    check(len(regions) == 9, "Expected nine region blocks")
    check(len(units) == 12, "Expected twelve unit definitions")
    check(len(family_ids) == 3, "Expected three set families")
    check(set(gear) == {"weapon", "armor", "charm"}, "Three equipment slots required")
    check(len({(r['set_id'], r['piece_count']) for r in sets}) == len(sets), "Duplicate set threshold")
    for family in family_ids:
        check({int(r["piece_count"]) for r in sets if r["set_id"] == family} == {2, 3},
              f"Set thresholds invalid: {family}")
        check(family in units, f"Missing boss unit for family: {family}")
    for row in sets:
        check(float(row["value"]) > 0, f"Nonpositive set effect: {row['set_id']}")
        check(int(row["trigger_limit_per_round"]) >= 0 and float(row["heal_cap_per_round"]) >= 0,
              f"Invalid set caps: {row['set_id']}")

    for key, region in regions.items():
        adjacent, next_ids = ids(region["adjacent_ids"]), ids(region["next_ids"])
        check(len(set(adjacent)) == len(adjacent) and key not in adjacent, f"Invalid adjacency: {key}")
        stage = int(region["stage"])
        for neighbour in adjacent:
            check(neighbour in regions, f"Unknown neighbour {key}: {neighbour}")
            if neighbour in regions:
                check(key in ids(regions[neighbour]["adjacent_ids"]), f"Asymmetric edge {key}/{neighbour}")
        for target in next_ids:
            check(target in adjacent, f"Forward edge is not adjacent: {key}/{target}")
            check(target in regions, f"Unknown forward target: {target}")
            if target in regions:
                check(int(regions[target]["stage"]) == stage + 1, f"Non-forward edge: {key}/{target}")
        if 1 <= stage <= 3:
            check(bool(next_ids), f"Exploration dead end: {key}")
            check(int(region["ap"]) == values["region_ap"], f"Wrong region AP: {key}")
            check(region["family"] in family_ids, f"Unknown loot family: {key}")
        else:
            check(int(region["ap"]) == 0, f"Non-exploration AP: {key}")
        check(float(region["hp_mult"]) > 0 and float(region["atk_mult"]) > 0, f"Invalid region scale: {key}")
    routes: list[list[str]] = []

    def walk(key: str, path: list[str]) -> None:
        if key in path:
            check(False, f"Route cycle: {path + [key]}")
            return
        if key not in regions:
            return
        path = path + [key]
        if key == "castle":
            routes.append(path)
            return
        for target in ids(regions[key]["next_ids"]):
            walk(target, path)

    walk("village", [])
    check(bool(routes), "Castle unreachable")
    for route in routes:
        exploration = [r for r in route if 1 <= int(regions[r]["stage"]) <= 3]
        check(len(exploration) == values["exploration_regions_per_run"], f"Wrong route length: {route}")
        check(sum(int(regions[r]["ap"]) for r in route) == 18, f"Wrong AP total: {route}")
    check({r for route in routes for r in route} == set(regions), "Unreachable region")
    check(values["level_cap"] == 1 + values["exploration_regions_per_run"], "First-win level cap mismatch")
    for family in family_ids:
        earliest = min(int(r["stage"]) for r in regions.values() if r["family"] == family)
        check(earliest <= 2, f"Family unavailable until final region: {family}")
    check({r for r, v in regions.items() if v["initial_landmark"] == "1"} == {"briar", "ember", "frost", "castle"},
          "Landmark list differs from design")

    optional = [key for key, row in activities.items() if row["placement"] == "optional"]
    check(len(optional) == 5 and len(activities) == 7, "Activity recipe must be 2 fixed + 5 optional pool")
    check({key for key, row in activities.items() if row["placement"] == "fixed"} == {"rest", "dungeon"},
          "Missing guaranteed camp/dungeon")
    for key, activity in activities.items():
        check(0 < int(activity["ap_cost"]) <= values["region_ap"], f"Invalid AP cost: {key}")
        if key in optional:
            check(int(activity["draw_weight"]) > 0 and int(activity["limit_per_region"]) == 1,
                  f"Invalid optional activity: {key}")
    recipes = list(itertools.combinations(optional, int(values["optional_activities"])))
    first_recipes = [recipe for recipe in recipes if "recruit" in recipe]
    check(bool(first_recipes), "No recipe supports guaranteed first-area recruit")
    start_cost = int(activities["recruit"]["ap_cost"]) + 2 * int(activities["dungeon"]["ap_cost"]) + int(activities["rest"]["ap_cost"])
    check(start_cost == values["region_ap"], "Recruit + two dungeons + rest budget fails")
    check(values["region_ap"] // int(activities["dungeon"]["ap_cost"]) == 3, "Three-repeat budget assumption fails")

    for row in units.values():
        check(int(row["hp"]) > 0 and int(row["atk"]) > 0 and int(row["armor"]) >= 0, f"Invalid unit stats: {row['id']}")
    for row in affixes.values():
        check(set(ids(row["slots"])) <= set(gear), f"Invalid affix slot: {row['id']}")
        check(float(row["weight"]) > 0, f"Invalid affix weight: {row['id']}")
    for row in skills.values():
        check(row["owner"] in units, f"Unknown skill owner: {row['id']}")
        check(int(row["cooldown_actions"]) >= 0, f"Invalid skill cooldown: {row['id']}")
    check(len([s for s in skills.values() if s["owner"] == "hero"]) == 3, "Three hero actives required")
    allowed = {"party_heal_pct", "hero_heal_pct", "gold", "hero_hp_cost", "gear_choice_fine", "gear_random_normal",
               "next_hero_atk_pct", "next_enemy_hp_pct", "next_enemy_atk_pct", "next_hero_shield", "next_enemy_armor_flat"}
    check(sum(row["phase"] == "M1" for row in events.values()) == 6, "M1 requires six events")
    check(sum(row["phase"] == "M2" for row in events.values()) == 6, "M2 adds six events")
    for row in events.values():
        check(row["phase"] in {"M1", "M2"}, f"Invalid event phase: {row['id']}")
        for branch in ("outcome_a", "outcome_b"):
            for effect in row[branch].split(";"):
                operation, amount = effect.split(":")
                value = float(amount)
                check(operation in allowed, f"Unknown event effect: {row['id']}/{operation}")
                check(math.isfinite(value), f"Non-finite event value: {row['id']}")
                if branch == "outcome_b":
                    check(operation != "hero_hp_cost" and not (operation == "gold" and value < 0),
                          f"Fallback branch charges resources: {row['id']}")
                if operation in {"party_heal_pct", "hero_heal_pct"}:
                    check(0 < value <= 100, f"Invalid event healing: {row['id']}")

    return {"status": "PASS" if not errors else "FAIL", "checks": checks,
            "markdown_files": len(documents), "local_links": link_count,
            "archive_originals": len(manifest), "csv_tables": len(list(DATA.glob('*.csv'))),
            "legal_routes": len(routes), "activity_recipes": len(recipes),
            "first_area_recipes": len(first_recipes), "errors": errors,
            "scope": "Static document/data integrity only; no runtime, playtest or balance verification."}


if __name__ == "__main__":
    try:
        result = main()
    except (KeyError, ValueError, OSError, csv.Error) as exc:
        result = {"status": "FAIL", "errors": [str(exc)], "checks_before_error": checks}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)
