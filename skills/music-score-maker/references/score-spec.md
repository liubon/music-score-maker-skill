# Score JSON specification

## Minimal example

```json
{
  "title": "Example Tune",
  "composer": "Composer Name",
  "arranger": "Transcribed by Codex",
  "source_note": "Fresh transcription; measures 5-8 approximate.",
  "key": {"fifths": 0, "mode": "major"},
  "time": {"beats": 4, "beat_type": 4},
  "tempo": 96,
  "parts": [
    {
      "id": "P1",
      "name": "Melody",
      "clef": "treble",
      "midi_program": 0,
      "measures": [
        {
          "number": 1,
          "events": [
            {"pitch": "C4", "duration": "1", "chord_symbol": "C"},
            {"pitch": "D4", "duration": "1"},
            {"pitches": ["E4", "G4"], "duration": "2", "lyric": "song"}
          ]
        }
      ]
    }
  ]
}
```

`duration` is measured in quarter-note units. Use integers, decimals, or fractions: `4` = whole, `2` = half, `1` = quarter, `1/2` = eighth, `1/4` = sixteenth. Common dotted values such as `3/2` and `3/4` are recognized. Avoid float rounding by preferring strings.

## Top-level fields

| Field | Required | Meaning |
|---|---:|---|
| `title` | yes | Score title |
| `composer` | no | Composer/songwriter/artist credit |
| `arranger` | no | Transcriber or arranger credit |
| `source_note` | no | Provenance and approximation note |
| `key.fifths` | no | MusicXML circle-of-fifths value, -7 through 7; default 0 |
| `key.mode` | no | `major`, `minor`, or another MusicXML mode; default `major` |
| `time.beats` | no | Beats per measure; default 4 |
| `time.beat_type` | no | Beat unit denominator; default 4 |
| `tempo` | no | Quarter-note BPM; default 120 |
| `parts` | yes | One or more parts |

## Part fields

- `id`: unique XML-safe ID such as `P1`
- `name`: displayed part name
- `clef`: `treble`, `bass`, `alto`, or `tenor`
- `midi_program`: General MIDI program from 0 through 127
- `transpose`: optional chromatic transposition integer for transposing-instrument metadata
- `measures`: ordered measure list

Use separate parts when musical lines sound independently at the same time. A single part is one sequential rhythmic stream with optional same-onset chord stacks.

## Measure and event fields

A measure contains `number`, optional `implicit`, and `events`.

Each event must be exactly one of:

- note: `{"pitch": "F#4", "duration": "1"}`
- chord stack: `{"pitches": ["C4", "E4", "G4"], "duration": "2"}`
- rest: `{"rest": true, "duration": "1/2"}`

Optional event fields:

- `lyric`: one lyric syllable attached to the first note
- `syllabic`: `single`, `begin`, `middle`, or `end`
- `chord_symbol`: chord text such as `Am7`, `F/C`, or `G7(b9)`
- `tie`: `start`, `stop`, or `continue`
- `velocity`: MIDI velocity 1 through 127

Pitch syntax is scientific pitch notation: `C4`, `F#3`, `Bb5`, `C##4`, `Ebb4`.

## Measure validation

Expected quarter-note duration is `beats * 4 / beat_type`. For 6/8 this is 3 quarter notes; for 3/4 it is 3. Every ordinary measure must equal the expected value. Set `implicit: true` only for genuine pickups, split bars, or shortened final measures.
