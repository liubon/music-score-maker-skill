#!/usr/bin/env python3
"""Build validated MusicXML and optional MIDI from a compact JSON score spec."""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PITCH_RE = re.compile(r"^([A-Ga-g])([#b]{0,2})(-?\d+)$")
TYPE_MAP = {
    Fraction(4): ("whole", 0),
    Fraction(3): ("half", 1),
    Fraction(2): ("half", 0),
    Fraction(3, 2): ("quarter", 1),
    Fraction(1): ("quarter", 0),
    Fraction(3, 4): ("eighth", 1),
    Fraction(1, 2): ("eighth", 0),
    Fraction(3, 8): ("16th", 1),
    Fraction(1, 4): ("16th", 0),
    Fraction(3, 16): ("32nd", 1),
    Fraction(1, 8): ("32nd", 0),
    Fraction(1, 16): ("64th", 0),
}
CLEFS = {
    "treble": ("G", "2"),
    "bass": ("F", "4"),
    "alto": ("C", "3"),
    "tenor": ("C", "4"),
}
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


class ScoreError(ValueError):
    pass


def duration(value: Any) -> Fraction:
    try:
        if isinstance(value, float):
            return Fraction(str(value))
        return Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise ScoreError(f"invalid duration {value!r}") from exc


def parse_pitch(value: str) -> tuple[str, int, int]:
    match = PITCH_RE.match(value)
    if not match:
        raise ScoreError(f"invalid pitch {value!r}; use syntax like C4, F#3, or Bb5")
    step, accidental, octave = match.groups()
    alter = accidental.count("#") - accidental.count("b")
    return step.upper(), alter, int(octave)


def midi_note(value: str) -> int:
    step, alter, octave = parse_pitch(value)
    note = (octave + 1) * 12 + SEMITONES[step] + alter
    if not 0 <= note <= 127:
        raise ScoreError(f"pitch {value!r} is outside MIDI range")
    return note


def event_pitches(event: dict[str, Any]) -> list[str]:
    kinds = sum(("pitch" in event, "pitches" in event, bool(event.get("rest"))))
    if kinds != 1:
        raise ScoreError("each event must contain exactly one of pitch, pitches, or rest=true")
    if event.get("rest"):
        return []
    pitches = event.get("pitches", [event.get("pitch")])
    if not isinstance(pitches, list) or not pitches:
        raise ScoreError("pitches must be a non-empty list")
    for value in pitches:
        parse_pitch(value)
    return pitches


def validate(spec: dict[str, Any]) -> tuple[int, list[str]]:
    errors: list[str] = []
    if not str(spec.get("title", "")).strip():
        errors.append("title is required")
    parts = spec.get("parts")
    if not isinstance(parts, list) or not parts:
        errors.append("parts must be a non-empty list")
        return 1, errors
    time = spec.get("time", {})
    try:
        beats = int(time.get("beats", 4))
        beat_type = int(time.get("beat_type", 4))
        expected = Fraction(beats * 4, beat_type)
        if beats <= 0 or beat_type <= 0 or beat_type & (beat_type - 1):
            errors.append("time.beats must be positive and beat_type must be a positive power of two")
    except (TypeError, ValueError, ZeroDivisionError):
        expected = Fraction(4)
        errors.append("invalid time signature")
    ids: set[str] = set()
    denominators: list[int] = []
    for p_index, part in enumerate(parts, 1):
        pid = str(part.get("id", f"P{p_index}"))
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_.-]*$", pid) or pid in ids:
            errors.append(f"part {p_index}: id {pid!r} must be unique and XML-safe")
        ids.add(pid)
        if part.get("clef", "treble") not in CLEFS:
            errors.append(f"part {pid}: unsupported clef {part.get('clef')!r}")
        measures = part.get("measures")
        if not isinstance(measures, list) or not measures:
            errors.append(f"part {pid}: measures must be a non-empty list")
            continue
        for m_index, measure in enumerate(measures, 1):
            total = Fraction(0)
            events = measure.get("events", [])
            if not isinstance(events, list):
                errors.append(f"part {pid} measure {m_index}: events must be a list")
                continue
            for e_index, event in enumerate(events, 1):
                try:
                    dur = duration(event.get("duration"))
                    if dur <= 0:
                        raise ScoreError("duration must be positive")
                    denominators.append(dur.denominator)
                    event_pitches(event)
                    if event.get("tie") not in (None, "start", "stop", "continue"):
                        raise ScoreError("tie must be start, stop, or continue")
                except (ScoreError, AttributeError) as exc:
                    errors.append(f"part {pid} measure {m_index} event {e_index}: {exc}")
                    continue
                total += dur
            if not measure.get("implicit") and total != expected:
                errors.append(
                    f"part {pid} measure {measure.get('number', m_index)}: duration {total} "
                    f"does not equal expected {expected}; use implicit=true only for a genuine short measure"
                )
    divisions = 1
    for denominator in denominators:
        divisions = math.lcm(divisions, denominator)
    if divisions > 960:
        errors.append(f"required divisions value {divisions} is too large; simplify duration fractions")
    return divisions, errors


def add_text(parent: ET.Element, tag: str, text: Any, **attrs: str) -> ET.Element:
    child = ET.SubElement(parent, tag, attrs)
    child.text = str(text)
    return child


def add_harmony(measure: ET.Element, symbol: str) -> None:
    harmony = ET.SubElement(measure, "harmony")
    # Keep the user's complete symbol visible while providing a conservative MusicXML root.
    root_match = re.match(r"^([A-G])([#b]?)(.*)$", symbol.strip())
    if root_match:
        root = ET.SubElement(harmony, "root")
        add_text(root, "root-step", root_match.group(1))
        if root_match.group(2):
            add_text(root, "root-alter", 1 if root_match.group(2) == "#" else -1)
    kind = add_text(harmony, "kind", "other")
    kind.set("text", symbol)


def add_note(measure: ET.Element, pitch_value: str | None, dur: Fraction, divisions: int,
             chord: bool, event: dict[str, Any]) -> None:
    note = ET.SubElement(measure, "note")
    if chord:
        ET.SubElement(note, "chord")
    if pitch_value is None:
        ET.SubElement(note, "rest")
    else:
        step, alter, octave = parse_pitch(pitch_value)
        pitch = ET.SubElement(note, "pitch")
        add_text(pitch, "step", step)
        if alter:
            add_text(pitch, "alter", alter)
        add_text(pitch, "octave", octave)
    add_text(note, "duration", int(dur * divisions))
    type_info = TYPE_MAP.get(dur)
    if type_info:
        add_text(note, "type", type_info[0])
        for _ in range(type_info[1]):
            ET.SubElement(note, "dot")
    tie = event.get("tie")
    tie_types = ("stop", "start") if tie == "continue" else ((tie,) if tie else ())
    for tie_type in tie_types:
        ET.SubElement(note, "tie", type=tie_type)
    if tie_types:
        notations = ET.SubElement(note, "notations")
        for tie_type in tie_types:
            ET.SubElement(notations, "tied", type=tie_type)
    if event.get("lyric") is not None and not chord:
        lyric = ET.SubElement(note, "lyric")
        add_text(lyric, "syllabic", event.get("syllabic", "single"))
        add_text(lyric, "text", event["lyric"])


def build_musicxml(spec: dict[str, Any], divisions: int, output: Path) -> None:
    root = ET.Element("score-partwise", version="4.0")
    work = ET.SubElement(root, "work")
    add_text(work, "work-title", spec["title"])
    identification = ET.SubElement(root, "identification")
    for role in ("composer", "arranger"):
        if spec.get(role):
            add_text(identification, "creator", spec[role], type=role)
    if spec.get("source_note"):
        add_text(identification, "source", spec["source_note"])
    encoding = ET.SubElement(identification, "encoding")
    add_text(encoding, "software", "music-score-maker build_score.py")
    part_list = ET.SubElement(root, "part-list")
    for index, part in enumerate(spec["parts"], 1):
        pid = str(part.get("id", f"P{index}"))
        score_part = ET.SubElement(part_list, "score-part", id=pid)
        add_text(score_part, "part-name", part.get("name", pid))
        midi_instrument = ET.SubElement(score_part, "midi-instrument", id=f"{pid}-I1")
        add_text(midi_instrument, "midi-channel", min(index, 16))
        add_text(midi_instrument, "midi-program", int(part.get("midi_program", 0)) + 1)
    key = spec.get("key", {})
    time = spec.get("time", {})
    for index, part in enumerate(spec["parts"], 1):
        pid = str(part.get("id", f"P{index}"))
        part_el = ET.SubElement(root, "part", id=pid)
        for m_index, measure_data in enumerate(part["measures"], 1):
            measure = ET.SubElement(part_el, "measure", number=str(measure_data.get("number", m_index)))
            if measure_data.get("implicit"):
                measure.set("implicit", "yes")
            if m_index == 1:
                attributes = ET.SubElement(measure, "attributes")
                add_text(attributes, "divisions", divisions)
                key_el = ET.SubElement(attributes, "key")
                add_text(key_el, "fifths", int(key.get("fifths", 0)))
                add_text(key_el, "mode", key.get("mode", "major"))
                time_el = ET.SubElement(attributes, "time")
                add_text(time_el, "beats", int(time.get("beats", 4)))
                add_text(time_el, "beat-type", int(time.get("beat_type", 4)))
                if part.get("transpose") is not None:
                    transpose = ET.SubElement(attributes, "transpose")
                    add_text(transpose, "chromatic", int(part["transpose"]))
                clef = ET.SubElement(attributes, "clef")
                sign, line = CLEFS[part.get("clef", "treble")]
                add_text(clef, "sign", sign)
                add_text(clef, "line", line)
                direction = ET.SubElement(measure, "direction", placement="above")
                direction_type = ET.SubElement(direction, "direction-type")
                metronome = ET.SubElement(direction_type, "metronome")
                add_text(metronome, "beat-unit", "quarter")
                add_text(metronome, "per-minute", spec.get("tempo", 120))
                ET.SubElement(direction, "sound", tempo=str(spec.get("tempo", 120)))
            for event in measure_data.get("events", []):
                if event.get("chord_symbol"):
                    add_harmony(measure, str(event["chord_symbol"]))
                dur = duration(event["duration"])
                pitches = event_pitches(event)
                if not pitches:
                    add_note(measure, None, dur, divisions, False, event)
                else:
                    for p_index, pitch_value in enumerate(pitches):
                        add_note(measure, pitch_value, dur, divisions, p_index > 0, event)
        # MusicXML uses one part element per score part.
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)


def vlq(value: int) -> bytes:
    data = [value & 0x7F]
    value >>= 7
    while value:
        data.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(data))


def midi_track(events: list[tuple[int, int, bytes]]) -> bytes:
    payload = bytearray()
    previous = 0
    for tick, order, event in sorted(events, key=lambda item: (item[0], item[1])):
        payload.extend(vlq(tick - previous))
        payload.extend(event)
        previous = tick
    payload.extend(b"\x00\xff\x2f\x00")
    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def build_midi(spec: dict[str, Any], output: Path) -> None:
    ticks_per_quarter = 480
    tempo = max(1, int(spec.get("tempo", 120)))
    micros = round(60_000_000 / tempo)
    time = spec.get("time", {})
    beats, beat_type = int(time.get("beats", 4)), int(time.get("beat_type", 4))
    conductor = [
        (0, 0, b"\xff\x51\x03" + micros.to_bytes(3, "big")),
        (0, 0, b"\xff\x58\x04" + bytes([beats, int(math.log2(beat_type)), 24, 8])),
    ]
    tracks = [midi_track(conductor)]
    for index, part in enumerate(spec["parts"]):
        channel = index % 16
        if channel == 9:
            channel = 15
        name = str(part.get("name", part.get("id", f"P{index + 1}"))).encode("utf-8")
        events: list[tuple[int, int, bytes]] = [
            (0, 0, b"\xff\x03" + vlq(len(name)) + name),
            (0, 0, bytes([0xC0 | channel, int(part.get("midi_program", 0))])),
        ]
        tick = 0
        for measure in part["measures"]:
            for event in measure.get("events", []):
                length = round(float(duration(event["duration"])) * ticks_per_quarter)
                pitches = event_pitches(event)
                velocity = max(1, min(127, int(event.get("velocity", 80))))
                for pitch_value in pitches:
                    note = midi_note(pitch_value)
                    events.append((tick, 2, bytes([0x90 | channel, note, velocity])))
                    events.append((tick + length, 1, bytes([0x80 | channel, note, 0])))
                tick += length
        tracks.append(midi_track(events))
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), ticks_per_quarter)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(header + b"".join(tracks))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON score specification")
    parser.add_argument("--output", type=Path, help="output MusicXML path")
    parser.add_argument("--midi", type=Path, help="optional output MIDI path")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        divisions, errors = validate(spec)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 2
        print(f"VALID: {len(spec['parts'])} part(s), divisions={divisions}")
        if args.validate_only:
            return 0
        output = args.output or args.spec.with_suffix(".musicxml")
        build_musicxml(spec, divisions, output)
        print(f"WROTE: {output}")
        if args.midi:
            build_midi(spec, args.midi)
            print(f"WROTE: {args.midi}")
        return 0
    except (OSError, json.JSONDecodeError, ScoreError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
