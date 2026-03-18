# Copilot Instructions

## Project Overview

Discord Bot，透過 Microsoft Edge TTS 引擎將指定文字頻道的訊息自動轉成語音，在語音頻道播放。

## Architecture

- `bot.py` — Discord bot 主程式。處理 `/invest` 和 `/leave` slash commands、監聽訊息事件、管理語音連線與播放佇列。
- `tts.py` — TTS 模組。`generate_tts(text, voice)` 使用 `edge_tts.Communicate` 產生 MP3 暫存檔並回傳路徑，呼叫者負責刪除。
- `.env` — 存放 `DISCORD_TOKEN`（不進 git）。
- 每個 guild 維護獨立的 `guild_state`，包含 voice_client、監聽頻道 ID、asyncio.Queue 和 worker task。
- 語音播放透過 `FFmpegPCMAudio`，需要系統安裝 FFmpeg。

## Commands

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行 bot
python bot.py
```

## Conventions

- All user-facing strings are in Traditional Chinese (繁體中文).
- Async-first: use `asyncio` for all I/O-bound operations.
- Temp files are created for audio playback and cleaned up in `finally` blocks.

## Git Workflow

- 每次異動完成後都要 commit。
- Commit message 必須使用中文撰寫。
