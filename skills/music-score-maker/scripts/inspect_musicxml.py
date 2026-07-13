#!/usr/bin/env python3
"""Perform structural sanity checks on a generated MusicXML score."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("musicxml", type=Path)
    args = parser.parse_args()
    try:
        root = ET.parse(args.musicxml).getroot()
    except (OSError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if root.tag != "score-partwise":
        print(f"ERROR: expected score-partwise root, found {root.tag}", file=sys.stderr)
        return 2
    declared = {node.get("id") for node in root.findall("./part-list/score-part")}
    parts = root.findall("./part")
    actual = {node.get("id") for node in parts}
    errors: list[str] = []
    if not parts:
        errors.append("score has no parts")
    if declared != actual:
        errors.append(f"declared part IDs {sorted(declared)} do not match score parts {sorted(actual)}")
    note_count = rest_count = measure_count = 0
    for part in parts:
        measures = part.findall("./measure")
        measure_count += len(measures)
        if not measures:
            errors.append(f"part {part.get('id')} has no measures")
        for note in part.findall("./measure/note"):
            if note.find("rest") is not None:
                rest_count += 1
            else:
                note_count += 1
            duration = note.findtext("duration")
            if duration is None or int(duration) <= 0:
                errors.append(f"part {part.get('id')} contains a note with invalid duration")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(
        f"VALID: {len(parts)} part(s), {measure_count} measure(s), "
        f"{note_count} pitched note(s), {rest_count} rest(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
