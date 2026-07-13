# Electronic wind instruments and MIDI

Use this checklist before claiming that an electronic wind instrument can “play MIDI.” That phrase can describe several different capabilities.

## Four capabilities to separate

1. **MIDI controller transmission**: Breath, fingering, bite, and keys send note/control data to a phone, tablet, computer, or hardware sound module.
2. **MIDI reception / sound-module behavior**: The instrument receives external MIDI messages and renders them through its internal sounds. This is separate from controller transmission and must be documented explicitly.
3. **Standard MIDI File playback**: The device can browse or load a `.mid` file and play it without a host application. This normally requires storage/file browsing or a documented SMF player; USB MIDI alone does not provide it.
4. **Bluetooth Audio**: Recorded audio from a phone plays through the instrument speaker or headphones. This is audio streaming, not Bluetooth MIDI.

## Research and answer pattern

- Identify the exact model and regional variant.
- Check the official owner manual and specifications for USB role, Bluetooth profiles, MIDI receive/transmit details, storage, and file playback.
- If receive behavior is undocumented, do not promise that the instrument works as an external sound module.
- Explain that `.mid` contains performance instructions, not recorded sound. It needs a synthesizer or sound source.
- Recommend the simplest workflow for the user's goal:
  - read/print: PDF
  - play along: phone audio or an exported MP3/WAV through Bluetooth Audio or headphones
  - practice tempo/notes: MIDI player or DAW on phone/computer
  - control software instruments: USB MIDI or Bluetooth MIDI from the wind controller

## Roland Aerophone GO AE-05 / AE-05C

The official manual documents USB MIDI data transfer with a computer, Bluetooth MIDI for compatible apps, and Bluetooth Audio playback from a phone. It does not document a standalone `.mid` file browser/player. Therefore:

- Do not say the AE-05C can load a `.mid` file and play it by itself.
- Present USB/Bluetooth MIDI primarily as communication with a host app or software instrument.
- For straightforward play-along practice, recommend phone audio paired to `AE-05 Audio`.
- For an E-flat alto-sax part, use the instrument's E-flat transpose setting and read the written part directly.
- Keep a caveat around external MIDI reception unless the exact firmware/manual explicitly confirms it.

Official sources:

- Owner's manual: https://static.roland.com/assets/media/pdf/AE-05_eng01_W.pdf
- Product/support specifications: https://www.roland.com/global/products/aerophone_go/support/
