#!/usr/bin/env python3
"""Export a 3D Video Studio shot plan JSON to a production-friendly CSV.

Usage:
  python tools/plan_to_csv.py plan.json
  python tools/plan_to_csv.py plan.json --output shot_sheet.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

FIELDS = (
    "shot", "act", "act_name", "start_sec", "end_sec", "duration_sec",
    "beat_prompt", "camera_setup", "caption", "voiceover", "sfx",
)


def rows_from_plan(plan: Any) -> list[dict[str, str]]:
    if not isinstance(plan, dict) or not isinstance(plan.get("acts"), list):
        raise ValueError("Plan must be a JSON object containing an 'acts' array.")

    rows: list[dict[str, str]] = []
    for act_index, act in enumerate(plan["acts"], start=1):
        if not isinstance(act, dict) or not isinstance(act.get("shots"), list):
            raise ValueError(f"Act {act_index} must be an object containing a 'shots' array.")
        act_number = act.get("act", act_index)
        act_name = str(act.get("name", ""))
        for shot in act["shots"]:
            if not isinstance(shot, dict):
                raise ValueError(f"Act {act_index} contains a shot that is not an object.")
            row: dict[str, str] = {}
            for field in FIELDS:
                value = shot.get(field, "")
                if field == "act":
                    value = act_number
                elif field == "act_name":
                    value = act_name
                elif field == "sfx" and isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                elif value is None:
                    value = ""
                row[field] = str(value)
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Path to shot-plan JSON")
    parser.add_argument("--output", type=Path, help="Write CSV to this path instead of stdout")
    args = parser.parse_args()

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        rows = rows_from_plan(plan)
    except OSError as exc:
        parser.error(f"Cannot read {args.plan}: {exc}")
    except json.JSONDecodeError as exc:
        parser.error(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    except ValueError as exc:
        parser.error(str(exc))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Created {args.output} ({len(rows)} shots)")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
