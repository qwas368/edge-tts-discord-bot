import asyncio
import tempfile
import os
import edge_tts
import pygame

VOICE = "zh-TW-HsiaoChenNeural"  # 台灣中文女聲

async def speak(text: str):
    """將文字轉成語音並播放"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(tmp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
    finally:
        os.unlink(tmp_path)


async def main():
    print("=== Edge TTS 文字轉語音 ===")
    print(f"目前語音: {VOICE}")
    print("輸入文字後按 Enter 即可播放語音，輸入 'quit' 離開\n")

    loop = asyncio.get_event_loop()
    while True:
        text = await loop.run_in_executor(None, lambda: input("請輸入文字> "))
        text = text.strip()
        if not text:
            continue
        if text.lower() == "quit":
            print("再見！")
            break
        await speak(text)


if __name__ == "__main__":
    asyncio.run(main())
