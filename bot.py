import asyncio
import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from tts import generate_tts

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 每個 guild 的狀態：監聽的文字頻道 ID 與語音播放佇列
guild_state: dict[int, dict] = {}


async def tts_worker(guild_id: int):
    """從佇列中取出訊息，依序轉語音並在語音頻道播放。"""
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
            try:
                source = discord.FFmpegPCMAudio(mp3_path)
                finished = asyncio.Event()
                voice_client.play(source, after=lambda e: finished.set())
                await finished.wait()
            finally:
                os.unlink(mp3_path)
        except Exception as e:
            print(f"[TTS Worker 錯誤] {e}")
        finally:
            queue.task_done()


@tree.command(name="invest", description="加入你的語音頻道並監聽指定文字頻道的訊息")
@app_commands.describe(channel="要監聽的文字頻道")
async def invest(interaction: discord.Interaction, channel: discord.TextChannel):
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

    # 取消 worker 並清理狀態
    state["worker"].cancel()
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

    text = message.clean_content.strip()
    if text:
        await state["queue"].put(text)


client.run(os.getenv("DISCORD_TOKEN"))
