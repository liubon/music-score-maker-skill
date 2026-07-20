#!/usr/bin/env python3
"""Validate the portable skill package and smoke-test its bundled builders."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "music-score-maker"
SKILL_MD = SKILL / "SKILL.md"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
    )


def validate_frontmatter(text: str) -> None:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    frontmatter = match.group(1)
    assert re.search(r"^name:\s*music-score-maker\s*$", frontmatter, re.MULTILINE)
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    assert description and len(description.group(1).strip()) >= 40


def validate_relative_links(text: str) -> None:
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        path = (SKILL / target).resolve()
        assert path.is_relative_to(SKILL.resolve()), target
        assert path.exists(), f"missing referenced file: {target}"


def smoke_test_builders() -> None:
    spec = {
        "title": "Portable Skill Smoke Test",
        "key": {"fifths": 0, "mode": "major"},
        "time": {"beats": 4, "beat_type": 4},
        "tempo": 80,
        "parts": [
            {
                "id": "P1",
                "name": "Melody",
                "clef": "treble",
                "midi_program": 65,
                "measures": [
                    {
                        "number": 1,
                        "events": [
                            {"pitch": "C4", "duration": "1"},
                            {"pitch": "D4", "duration": "1"},
                            {"pitch": "E4", "duration": "1"},
                            {"pitch": "G4", "duration": "1"},
                        ],
                    }
                ],
            }
        ],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        score_json = temp / "score.json"
        musicxml = temp / "score.musicxml"
        midi = temp / "score.mid"
        score_json.write_text(json.dumps(spec), encoding="utf-8")

        build = SKILL / "scripts" / "build_score.py"
        inspect = SKILL / "scripts" / "inspect_musicxml.py"
        validated = run(sys.executable, str(build), str(score_json), "--validate-only")
        assert "VALID:" in validated.stdout
        run(
            sys.executable,
            str(build),
            str(score_json),
            "--output",
            str(musicxml),
            "--midi",
            str(midi),
        )
        inspected = run(sys.executable, str(inspect), str(musicxml))
        assert "VALID:" in inspected.stdout
        assert ET.parse(musicxml).getroot().tag == "score-partwise"
        assert midi.read_bytes().startswith(b"MThd")

        tie_spec = {
            "title": "MIDI Tie Regression",
            "time": {"beats": 4, "beat_type": 4},
            "parts": [{
                "id": "P1",
                "name": "Alto Saxophone",
                "midi_program": 65,
                "measures": [
                    {"number": 1, "events": [{"pitch": "C4", "duration": "4", "tie": "start", "velocity": 80}]},
                    {"number": 2, "events": [{"pitch": "C4", "duration": "4", "tie": "stop", "velocity": 80}]},
                ],
            }],
        }
        tie_json = temp / "tie.json"
        tie_xml = temp / "tie.musicxml"
        tie_midi = temp / "tie.mid"
        tie_json.write_text(json.dumps(tie_spec), encoding="utf-8")
        run(sys.executable, str(build), str(tie_json), "--output", str(tie_xml), "--midi", str(tie_midi))
        payload = tie_midi.read_bytes()
        assert payload.count(bytes([0x90, 60, 80])) == 1, "tied notes must have one MIDI note-on"
        assert payload.count(bytes([0x80, 60, 0])) == 1, "tied notes must have one MIDI note-off"


def main() -> None:
    assert SKILL_MD.is_file()
    text = SKILL_MD.read_text(encoding="utf-8")
    validate_frontmatter(text)
    validate_relative_links(text)

    forbidden = ("/Users/", "Documents/New project", "bytedance", "晴天")
    for path in SKILL.rglob("*"):
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="ignore")
            assert not any(value in content for value in forbidden), path

    smoke_test_builders()
    print("PASS: portable skill structure, links, privacy scan, MusicXML, and MIDI")


if __name__ == "__main__":
    main()
