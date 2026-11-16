# 3D Video Studio — asepyans

A code-driven 3D cartoon Shorts workspace. Build vertical animated stories with Three.js, frame-by-frame browser rendering, timed captions, voiceover alignment, sound design, and render QA.

## Core capabilities

- Nine-stage production flow with approval checkpoints: topic, script, visual bible, look development, storyboard, preview, voice timing, act-by-act build, and final QA.
- 3D cast, sets, props, vehicles, camera motion, transitions, captions, and audio pipeline.
- Reference Short analysis and comparison tools.
- Geometry checks for framing, clipping, text visibility, camera movement, and character rig limitations.
- Starter project template and setup utility.

## Requirements

- Node.js 18+
- Python 3.9+
- FFmpeg
- Git
- Cartesia account for voice generation (optional if using another voice workflow)

On Windows, run setup commands in Git Bash.

## Setup

From the repository root:

```bash
bash setup.sh
```

The setup installs the Three.js engine dependencies, Playwright/Chromium, Python tooling, and the word-timing model. The model download is large and occurs only once.

## Start a production

Use the `/3d-video-studio` skill command in Claude Code, or work directly with the engine tools.

Example prompts:

```text
/3d-video-studio Give me three story ideas for a 60-second 3D cartoon Short.
/3d-video-studio Create a Short about why restaurants started using pagers.
/3d-video-studio Analyze this reference Short and create a new story with a different topic.
```

The workflow pauses at review checkpoints so you can approve or revise each stage.

## Useful tools

| Tool | Purpose |
|---|---|
| `tools/analyze_ref.py` | Analyze reference video metrics |
| `tools/ref_profile.py` | Build a reference profile |
| `tools/rig_check.py` | Flag script actions that exceed character-rig capabilities |
| `tools/look_score.py` | Evaluate look-development sheets |
| `tools/sbs_sheet.py` | Create side-by-side review sheets |
| `tools/compare_video.py` | Compare output against a reference |
| `tools/short_planner.py` | Generate a structured act/shot timing plan from a topic |

## Project structure

- `SKILL.md` — production workflow and approval gates
- `story/` — topic, script, hook, and voice guidance
- `look/` — visual style and visual bible
- `engine/` — Three.js renderer, cast, sets, audio, and starter template
- `tools/` — analysis, planning, and QA utilities
- `kit/` — local render and Python runtime dependencies

## Third-party notices

Some audio DSP and QA components are used under their respective licenses. See the license notices shipped alongside those components, including `engine/audio/LICENSE-third-party.txt`.

The project retains required third-party license and attribution notices.