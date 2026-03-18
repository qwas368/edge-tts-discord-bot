import tempfile
import edge_tts

VOICE = "zh-TW-HsiaoChenNeural"  # 台灣中文女聲


async def generate_tts(text: str, voice: str = VOICE) -> str:
    """將文字轉成語音 MP3 檔案，回傳暫存檔路徑。呼叫者負責刪除檔案。"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(tmp_path)
    return tmp_path
