import asyncio
import os
import re
import discord
from discord import app_commands
from dotenv import load_dotenv
from tts import generate_tts

CHUNK_THRESHOLD = 100
# 會被 TTS 唸出但無語意的符號
STRIP_CHARS_RE = re.compile(r"[*#_~`|>\\]")

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 每個 guild 的狀態：監聽的文字頻道 ID 與語音播放佇列
guild_state: dict[int, dict] = {}


def split_text(text: str, threshold: int = CHUNK_THRESHOLD) -> list[str]:
    """每累積 threshold 字後，在下一個換行處截斷。"""
    lines = text.split("\n")
    chunks: list[str] = []
    current: list[str] = []
    length = 0

    for line in lines:
        current.append(line)
        length += len(line)
        if length >= threshold:
            chunks.append("\n".join(current))
            current = []
            length = 0

    if current:
        chunks.append("\n".join(current))
    return chunks


async def tts_worker(guild_id: int):
    """從佇列中取出訊息，依序轉語音並在語音頻道播放。播放時預先產生下一段音檔。"""
    state = guild_state[guild_id]
    queue: asyncio.Queue = state["queue"]

    while True:
        text = await queue.get()
        try:
            voice_client: discord.VoiceClient = state.get("voice_client")
            if not voice_client or not voice_client.is_connected():
                queue.task_done()
                continue

            mp3_path = await generate_tts(text)

            # 內層迴圈：播放當前音檔，同時預取下一段以減少中斷
            while True:
                prefetch_task = None
                try:
                    next_text = queue.get_nowait()
                    prefetch_task = asyncio.create_task(generate_tts(next_text))
                except asyncio.QueueEmpty:
                    pass

                try:
                    source = discord.FFmpegPCMAudio(mp3_path)
                    finished = asyncio.Event()
                    voice_client.play(source, after=lambda e: finished.set())
                    await finished.wait()
                finally:
                    os.unlink(mp3_path)

                queue.task_done()

                if prefetch_task is not None:
                    mp3_path = await prefetch_task
                else:
                    break
        except Exception as e:
            print(f"[TTS Worker 錯誤] {e}")


@tree.command(name="invite", description="加入你的語音頻道並監聽指定文字頻道的訊息")
@app_commands.describe(channel="要監聽的文字頻道")
async def invite(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ 你必須先加入一個語音頻道！", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    guild_id = interaction.guild_id

    # 如果已在語音頻道，先斷開
    if guild_id in guild_state and guild_state[guild_id].get("voice_client"):
        old_vc = guild_state[guild_id]["voice_client"]
        if old_vc.is_connected():
            await old_vc.disconnect()

    voice_client = await voice_channel.connect()

    # 初始化或更新 guild 狀態
    if guild_id not in guild_state:
        queue = asyncio.Queue()
        guild_state[guild_id] = {
            "voice_client": voice_client,
            "monitor_channel_id": channel.id,
            "queue": queue,
            "worker": asyncio.create_task(tts_worker(guild_id)),
        }
    else:
        guild_state[guild_id]["voice_client"] = voice_client
        guild_state[guild_id]["monitor_channel_id"] = channel.id

    await interaction.response.send_message(
        f"✅ 已加入 **{voice_channel.name}**，開始監聽 {channel.mention} 的訊息",
        ephemeral=True,
    )


@tree.command(name="leave", description="離開語音頻道並停止監聽")
async def leave(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    state = guild_state.get(guild_id)

    if not state or not state.get("voice_client"):
        await interaction.response.send_message("❌ 我目前沒有在任何語音頻道中", ephemeral=True)
        return

    if state["voice_client"].is_connected():
        await state["voice_client"].disconnect()

    # 取消 worker、清空佇列並清理狀態
    state["worker"].cancel()
    queue = state["queue"]
    while not queue.empty():
        try:
            queue.get_nowait()
            queue.task_done()
        except asyncio.QueueEmpty:
            break
    del guild_state[guild_id]

    await interaction.response.send_message("👋 已離開語音頻道並停止監聽", ephemeral=True)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot 已上線：{client.user}")


@client.event
async def on_message(message: discord.Message):
    # 忽略 bot 自己的訊息
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    if not guild_id:
        return

    state = guild_state.get(guild_id)
    if not state:
        return

    # 只處理被監聽的頻道
    if message.channel.id != state["monitor_channel_id"]:
        return

    text = STRIP_CHARS_RE.sub("", message.clean_content).strip()
    if text:
        for chunk in split_text(text):
            await state["queue"].put(chunk)


client.run(os.getenv("DISCORD_TOKEN"))
