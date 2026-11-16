#!/usr/bin/env python3
"""Validate JSON output from tools/short_planner.py or a compatible shot plan.

Usage:
  python tools/validate_plan.py plan.json
  python tools/validate_plan.py plan.json --strict
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP = ("topic", "duration_sec", "act_count", "shot_count", "acts")
REQUIRED_SHOT = ("shot", "start_sec", "end_sec", "duration_sec", "beat_prompt")


def validate(plan: Any, tolerance: float = 0.01, strict: bool = False) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return ["Plan root must be a JSON object."]

    for key in REQUIRED_TOP:
        if key not in plan:
            errors.append(f"Missing required top-level key: {key}")

    if errors:
        return errors

    duration = plan.get("duration_sec")
    acts = plan.get("acts")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
        errors.append("duration_sec must be a positive number.")
        return errors
    if not isinstance(acts, list) or not acts:
        errors.append("acts must be a non-empty array.")
        return errors

    if plan.get("act_count") != len(acts):
        errors.append(f"act_count says {plan.get('act_count')}, but acts contains {len(acts)} entries.")

    all_shots: list[dict[str, Any]] = []
    expected_act_start = 0.0

    for act_index, act in enumerate(acts, start=1):
        if not isinstance(act, dict):
            errors.append(f"Act {act_index} must be an object.")
            continue

        for key in ("act", "name", "start_sec", "end_sec", "shots"):
            if key not in act:
                errors.append(f"Act {act_index} is missing '{key}'.")

        act_start, act_end, shots = act.get("start_sec"), act.get("end_sec"), act.get("shots")
        if not isinstance(act_start, (int, float)) or not isinstance(act_end, (int, float)):
            errors.append(f"Act {act_index} start_sec/end_sec must be numeric.")
            continue
        if act_end <= act_start:
            errors.append(f"Act {act_index} has a non-positive duration.")
        if abs(act_start - expected_act_start) > tolerance:
            errors.append(f"Act {act_index} starts at {act_start:.3f}s; expected {expected_act_start:.3f}s.")
        expected_act_start = act_end

        if not isinstance(shots, list) or not shots:
            errors.append(f"Act {act_index} must contain a non-empty shots array.")
            continue

        expected_shot_start = float(act_start)
        for shot in shots:
            if not isinstance(shot, dict):
                errors.append(f"Act {act_index} contains a shot that is not an object.")
                continue
            missing = [key for key in REQUIRED_SHOT if key not in shot]
            if missing:
                errors.append(f"Act {act_index} shot missing fields: {', '.join(missing)}.")
                continue

            start, end, shot_duration = shot["start_sec"], shot["end_sec"], shot["duration_sec"]
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (start, end, shot_duration)):
                errors.append(f"Shot {shot.get('shot')} has non-numeric timing values.")
                continue
            if end <= start:
                errors.append(f"Shot {shot.get('shot')} ends at or before it starts.")
            if abs((end - start) - shot_duration) > tolerance:
                errors.append(f"Shot {shot.get('shot')} duration field does not match its boundaries.")
            if abs(start - expected_shot_start) > tolerance:
                errors.append(f"Shot {shot.get('shot')} starts at {start:.3f}s; expected {expected_shot_start:.3f}s (gap or overlap).")
            if start < act_start - tolerance or end > act_end + tolerance:
                errors.append(f"Shot {shot.get('shot')} falls outside Act {act_index} boundaries.")
            if not isinstance(shot["beat_prompt"], str) or not shot["beat_prompt"].strip():
                errors.append(f"Shot {shot.get('shot')} beat_prompt must be a non-empty string.")
            expected_shot_start = end
            all_shots.append(shot)

        if abs(expected_shot_start - act_end) > tolerance:
            errors.append(f"Act {act_index} shots end at {expected_shot_start:.3f}s, not at act end {act_end:.3f}s.")

    if abs(expected_act_start - duration) > tolerance:
        errors.append(f"Acts end at {expected_act_start:.3f}s, not at total duration {duration:.3f}s.")

    if plan.get("shot_count") != len(all_shots):
        errors.append(f"shot_count says {plan.get('shot_count')}, but found {len(all_shots)} shots.")

    if len(all_shots) < 6:
        warnings.append("Plan has fewer than six shots; consider increasing visual variety.")
    if strict:
        errors.extend(warnings)
    else:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Path to shot-plan JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as validation errors")
    args = parser.parse_args()

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except OSError as exc:
        parser.error(f"Cannot read {args.plan}: {exc}")
    except json.JSONDecodeError as exc:
        parser.error(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")

    errors = validate(plan, strict=args.strict)
    if errors:
        print("PLAN INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PLAN VALID — {plan['shot_count']} shots, {plan['duration_sec']} seconds, {plan['act_count']} acts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
