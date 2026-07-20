# Music delivery quality gates

Use these gates for every generated score. Structural validity is necessary but does not prove musical fidelity.

## 1. Lock the source

Record the exact target before making notes:

| Field | Required value |
|---|---|
| Identity | work title, artist/composer, performer or arrangement |
| Version | studio, live, cover, karaoke, edit, or user-provided file |
| Locator | URL or local path; SHA-256 for a local file |
| Timing | visible duration and access date |
| Musical baseline | concert key, tuning, meter, tempo or tempo map |

Do not combine evidence from different versions without identifying the difference. A score preview may help with pitch spelling or form, but it does not override the user's chosen recording.

## 2. Declare the scope

- **Full transcription**: follows the complete target recording after repeats are unfolded. Target and score duration should normally agree within 5%.
- **Condensed practice arrangement**: intentionally shortens or removes sections. Put `condensed practice arrangement` in the title or source note and report the shortened form.
- **Excerpt**: identify timestamps or measure boundaries.

Repeat signs reduce printed length, not musical duration. Calculate unfolded duration and make audition MIDI follow the repeat plan, or name it `linear preview` and disclose that it does not.

## 3. Validate at five source checkpoints

Compare the score and locked recording side by side at these points:

1. opening and first melodic entry
2. first verse phrase
3. build or pre-chorus transition
4. chorus opening and highest/most distinctive phrase
5. final cadence and ending duration

At each checkpoint verify pitch sequence and octave; onset, length, syncopation, ties, pickups, and rests; phrase boundaries and breath opportunities; and repeats, interludes, alternate endings, or omissions. Do not infer high melody confidence from matching key and contour alone.

## 4. Wind-part sanity checks

- Zero written rests is a hard warning and normally a failure.
- Eight or more consecutive rest-free measures requires source evidence or an explicit circular-breathing instruction.
- Preserve rests that define phrasing; do not turn them into held or repeated notes merely to fill a bar.
- Check sounding range separately from written range.
- Add breath marks only where musically supported.

## 5. Transposition and MIDI checks

- Compare exact MIDI note numbers, not pitch classes. A nine-semitone error and a three-semitone error can have the same pitch class but differ by an octave.
- For an E-flat alto saxophone part with `transpose = -9`, sounding MIDI pitch must equal written MIDI pitch minus 9 for every note.
- The user-facing audition MIDI should normally be sounding pitch and use an appropriate General MIDI program. Label written-pitch MIDI explicitly.
- Verify note count, starts, durations, tempo, time signature, program change, pitch range, and end time.
- If the printed score uses repeats, produce an unfolded audition MIDI or clearly disclose a linear preview.

## 6. Status vocabulary

- `artifact-valid`: files parse, measures balance, and PDF renders
- `playback-validated`: exact transposition, tempo, program, range, and timing pass
- `source-checked arrangement`: all five checkpoints were compared, with disclosed simplifications
- `full transcription verified`: complete form and duration match the locked recording and uncertain passages were resolved

If only the first gate passes, say `technically valid, musically unverified`. Avoid `official`, `exact`, `calibrated`, or `finished` unless their evidence exists.

## 7. Regression checklist

Before delivery, explicitly rule out these common failures:

- wrong recording or mixed versions
- right pitch class in the wrong octave
- piano-default MIDI presented as sax playback
- simplified repeated rhythm cells presented as transcription
- no rests or impossible breath spans
- printed repeat signs not reflected in playback duration
- compact form presented as a full song
- sparse or clipped PDF layout
- stale output reused under a new filename
