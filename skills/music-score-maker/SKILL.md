---
name: music-score-maker
description: Research, analyze, transcribe, arrange, and generate playable sheet music from a song title, artist, recording, link, audio file, melody description, or musical idea. Use when the user asks to find or understand a song and create printable PDF notation, beginner arrangements, transposing-instrument parts, lead sheets, chord charts, MusicXML, MIDI, or notation-ready score data, including “给我生成这首歌的乐谱”, “扒谱”, “转成五线谱”, “初学者版本”, “萨克斯谱”, or questions about using the resulting MIDI with an electronic wind instrument.
---

# Music Score Maker

Turn a named or described piece into a researched, traceable, playable score. Keep MusicXML as the canonical editable source, but treat a verified PDF as the primary user-facing deliverable whenever the user wants to read, practice, or print the music. Treat MIDI as an optional audition or controller aid, not as a substitute for notation or audio.

## Workflow

### 1. Resolve the target

Identify the exact work, version, artist, recording, live/studio variant, and requested arrangement. Ask only when ambiguity would materially change the notes. Otherwise use these defaults and state them:

- arrangement: melody with chord symbols
- key: recording/original key
- difficulty: beginner-friendly when the user describes themselves as a beginner; otherwise intermediate
- format: printable PDF plus MusicXML; MIDI only when useful
- scope: complete form when evidence is adequate

If the user supplies audio, a score, notation, or a link, treat it as the primary target artifact.

Lock the target before transcribing. Record a version fingerprint containing the URL or local filename, visible title/performer, duration, and access date; add a file hash when the target is local. Never silently mix the studio release, a live performance, a cover, and an existing arrangement. A newly supplied recording starts a new score version unless the user explicitly asks to preserve the old target.

### 2. Research before writing

Search the web for the exact title plus artist/composer and recording version. Use primary or authoritative sources for identity, credits, release/version, key, tempo, meter, and form. Read [references/research-and-rights.md](references/research-and-rights.md) before researching a copyrighted or commercially released work.

Do not download pirated scores, bypass paywalls, or present a third-party transcription as newly generated work. Preserve source URLs and distinguish observed facts from musical inference.

### 3. Build a musical model

Determine, in order:

1. tonal center, mode, tuning, meter, pickup, and tempo
2. form and measure count
3. harmonic rhythm and chord progression
4. melody pitches, rhythm, phrasing, lyrics alignment, and range
5. bass motion, accompaniment texture, articulations, and dynamics when requested

Cross-check uncertain passages against more than one lawful clue when possible. Mark approximations explicitly. Never invent precision: if the source is insufficient, offer a chord chart, short excerpt, or clearly labeled arrangement instead of claiming an exact transcription.

Choose and record one scope before encoding:

- `full transcription`: the unfolded score follows the complete target recording, including pickups, rests, repeated verses, interludes, and ending
- `condensed practice arrangement`: selected sections or repeated material are shortened for practice and must be labeled as condensed in the title/source note

For a full transcription, compare the unfolded score or audition-MIDI duration with the target recording. A mismatch above 5% is a failure until the form, tempo map, pickup, fermatas, and repeats are explained. A condensed arrangement may be shorter, but must report both durations and may not be described as complete or exact.

For a transposing instrument, model concert pitch and written pitch separately. Confirm the instrument and transposition from an authoritative source. Preserve the recording key when the user wants to play with the original track, then write the correctly transposed part.

For a beginner arrangement:

- keep the written range comfortable and idiomatic; prefer octave displacement over changing key when accompaniment compatibility matters
- reduce avoidable extreme-register notes, awkward leaps, decorative complexity, and page-turn hazards
- retain recognizable melody and rhythm unless simplification is requested
- disclose octave shifts, omissions, simplifications, or key changes
- favor larger, less crowded notation over maximizing notes per page
- preserve phrase rests and breath opportunities; do not fill unknown or sustained passages with repeated notes merely to make every measure add up

### 4. Encode the score

Read [references/score-spec.md](references/score-spec.md). Create a JSON score specification, then run:

Resolve `SKILL_DIR` to the directory containing this `SKILL.md`; do not assume the current working directory is the skill directory.

```bash
python3 "$SKILL_DIR/scripts/build_score.py" score.json --output song.musicxml --midi song.mid
```

Use separate parts for simultaneous independent lines such as piano right/left hand or SATB voices. The bundled builder supports a sequential rhythmic stream per part, rests, chord stacks, lyrics, ties, key/time signatures, tempo, transposition metadata, MusicXML, and MIDI.

For notation that needs tuplets, multiple voices on one staff, cross-staff notation, percussion, guitar tablature, repeats/endings, or detailed engraving, generate or edit MusicXML directly after using the builder for the basic structure.

### 5. Render a readable PDF

When the user wants a score to open, read, practice, or print, generate a PDF in addition to the editable source. Use the PDF skill when available and follow its rendering and inspection requirements.

- Render through a notation engine that respects MusicXML layout. Do not create a fake score by drawing notes as plain text.
- Default to A4, readable staff size, clear title/instrument labels, measure numbers, sensible systems, and intentional page breaks.
- Prefer three to five systems per page for a beginner single-line part when that improves legibility.
- Place the final PDF under `output/pdf/` unless the environment requires another output directory.
- Render the finished PDF to images and inspect every page for clipping, overlap, missing glyphs, unreadable density, unintended blank pages, and a missing final barline.

### 6. Validate musically and structurally

Read [references/quality-gates.md](references/quality-gates.md). “The files open” and “the music is correct” are separate claims. Always pass the artifact gate first:

```bash
python3 "$SKILL_DIR/scripts/build_score.py" score.json --validate-only
python3 "$SKILL_DIR/scripts/inspect_musicxml.py" song.musicxml
```

Pass all three gates before calling a result accurate or finished:

1. **Artifact gate**: valid measure arithmetic, MusicXML, MIDI, PDF metadata, A4 layout, final barline, and no visual defects.
2. **Playback/transposition gate**: exact written-to-sounding pitches including octave, intended tempo/meter, sensible sounding range, correct General MIDI program, and repeats unfolded or explicitly disclosed.
3. **Source-fidelity gate**: at minimum compare the opening/first entry, verse, build, chorus peak, and ending against the locked recording for pitch, onset, duration, rests, and form.

When available:

- render the MusicXML with any available notation engine; do not require the user to own or use notation software
- audition the MIDI and check downbeats, phrase lengths, leaps, accidentals, octave placement, and chord/melody clashes
- inspect the first page and at least one dense or uncertain passage
- run PDF metadata inspection and confirm page count and paper size when a PDF is delivered
- compare the score's unfolded duration and section order with the locked recording
- treat zero rests or eight or more consecutive rest-free measures in a monophonic wind part as a failure unless the source clearly justifies continuous breathing or the score explicitly marks a circular-breathing passage
- verify the user-facing audition MIDI uses sounding pitch and an appropriate instrument program; a written-pitch MIDI may be retained only as a clearly named support file

Fix validation errors rather than suppressing them. A normal measure must equal the time-signature duration; mark genuine pickup or shortened measures with `implicit: true`.

If any source-fidelity checkpoint has not been checked, say `technically valid, musically unverified` rather than `accurate`, `calibrated`, or `finished`. Listening to the whole MIDI without a side-by-side source comparison is not sufficient evidence.

### 7. Explain MIDI and electronic instruments accurately

Read [references/electronic-wind-and-midi.md](references/electronic-wind-and-midi.md) when the user mentions an electronic wind instrument, MIDI playback, Bluetooth MIDI, USB MIDI, or asks whether a device can play a `.mid` file.

Never infer standalone MIDI-file playback merely from “USB MIDI” or “Bluetooth MIDI” support. Distinguish controller transmission, MIDI reception/sound-module behavior, Standard MIDI File playback, and Bluetooth Audio. Research the exact device from its official manual or specifications before giving device-specific instructions.

### 8. Deliver with provenance

Lead with the clickable PDF when one was requested. Treat the other files as supporting artifacts and explain them in plain language:

- `.pdf`: open, read, and print; normally the main deliverable
- `.musicxml`: editable notation source for score software; optional for ordinary players
- `.mid`: timed note/control instructions for audition, practice software, or a sound source; not recorded audio
- `.json`: internal reproducible source for the bundled builder; normally not needed by the player

Briefly report:

- exact version and arrangement assumptions
- key, meter, tempo, instrumentation, and difficulty
- sources used, with links
- confidence (`high`, `medium`, or `low`) separately for identity, pitch, rhythm, form, transposition, and ornamentation
- passages that are approximate or newly arranged
- beginner adaptations and written range when applicable
- whether MIDI is concert-sounding, written-pitch, or controller-oriented
- whether the score is full or condensed, its unfolded duration, the target duration, and how repeats are handled

Do not call the result an “official score” unless it is actually derived from an authorized official score and the user has the right to use it.

## Output quality rules

- Make every note intentional; do not fill unknown passages with arbitrary patterns.
- Do not replace unknown rhythm with a small set of repeating half/quarter/eighth-note cells and then label the result source-calibrated.
- Do not use cache-safe filenames or polished metadata to imply a new musical verification; provenance labels must reflect what was actually checked.
- Keep playable ranges and idiomatic writing for the requested instruments.
- Prefer enharmonic spellings consistent with the key and harmonic function.
- Put chord symbols at actual harmonic changes, not mechanically on every beat.
- Keep lyrics syllabified and aligned only when reliable lyric text is lawfully available.
- Include title, composer/artist, arranger/transcriber attribution, and a source/approximation note in metadata.
- Preserve editable source artifacts internally even when the user only needs the PDF.
- Do not burden a nontechnical player with notation-software instructions unless they ask to edit the score.
