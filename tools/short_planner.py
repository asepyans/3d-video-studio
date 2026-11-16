#!/usr/bin/env python3
"""Create a lightweight act/shot timing outline for a vertical 3D Short.

Example:
  python tools/short_planner.py --topic "Why restaurants started using pagers" --duration 60
  python tools/short_planner.py --topic "The invention of the dash cam" --duration 90 --shot-seconds 5 --output plan.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ACTS = [
    ("HOOK", "Introduce the unusual behavior and its immediate payoff."),
    ("ESCALATION", "Raise the stakes through increasingly visual beats."),
    ("REVEAL", "Let the invention solve the problem; finish with a memorable loop."),
]


def build_plan(topic: str, duration: float, shot_seconds: float) -> dict:
    if not topic.strip():
        raise ValueError("Topic must not be empty.")
    if duration <= 0 or shot_seconds <= 0:
        raise ValueError("Duration and shot length must be greater than zero.")

    # Divide the complete runtime into three acts without losing fractional seconds.
    boundaries = [0.0, duration / 3, (duration * 2) / 3, duration]
    acts = []
    shot_index = 1

    for act_idx, (name, intent) in enumerate(ACTS):
        start, end = boundaries[act_idx], boundaries[act_idx + 1]
        shots = []
        cursor = start
        while cursor < end - 1e-9:
            shot_end = min(cursor + shot_seconds, end)
            shots.append({
                "shot": shot_index,
                "start_sec": round(cursor, 3),
                "end_sec": round(shot_end, 3),
                "duration_sec": round(shot_end - cursor, 3),
                "beat_prompt": f"Visual beat for: {topic}",
                "camera_setup": "Choose a setup that clearly frames the story beat.",
                "caption": "",
                "voiceover": "",
                "sfx": [],
            })
            shot_index += 1
            cursor = shot_end

        acts.append({
            "act": act_idx + 1,
            "name": name,
            "start_sec": round(start, 3),
            "end_sec": round(end, 3),
            "intent": intent,
            "shots": shots,
        })

    return {
        "format": "3D Video Studio shot plan",
        "topic": topic.strip(),
        "aspect_ratio": "9:16",
        "fps": 30,
        "duration_sec": round(duration, 3),
        "act_count": len(acts),
        "shot_count": shot_index - 1,
        "acts": acts,
        "notes": [
            "Replace beat_prompt, caption, voiceover, camera_setup, and sfx with story-specific details.",
            "Shot boundaries are contiguous and cover the full requested runtime.",
            "Use the project's visual bible and rig checks before building scenes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="Story topic or working title")
    parser.add_argument("--duration", type=float, default=60, help="Total runtime in seconds (default: 60)")
    parser.add_argument("--shot-seconds", type=float, default=4, help="Target shot length (default: 4)")
    parser.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")
    args = parser.parse_args()

    try:
        plan = build_plan(args.topic, args.duration, args.shot_seconds)
    except ValueError as exc:
        parser.error(str(exc))

    rendered = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Created {args.output} ({plan['shot_count']} shots, {plan['duration_sec']} s)")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
