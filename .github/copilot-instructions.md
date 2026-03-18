# Copilot Instructions

## Project Overview

Interactive console app that converts text to speech using Microsoft Edge's TTS engine (`edge-tts`) and plays audio via `pygame`. Primary language is Traditional Chinese (Taiwan).

## Architecture

- `tts.py` — Single-file async app. `speak()` handles TTS generation + playback via temp MP3 files. `main()` runs the interactive input loop.
- TTS engine: `edge_tts.Communicate` — async, streams audio from Microsoft Edge's online TTS service.
- Audio playback: `pygame.mixer` — loads and plays the generated MP3.
- Default voice: `zh-TW-HsiaoChenNeural` (Taiwan Mandarin, female).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python tts.py
```

## Conventions

- All user-facing strings are in Traditional Chinese (繁體中文).
- Async-first: use `asyncio` for all I/O-bound operations.
- Temp files are created for audio playback and cleaned up in `finally` blocks.
