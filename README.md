# Edge TTS Discord Bot

Discord Bot，透過 Microsoft Edge TTS 引擎，自動將指定文字頻道的訊息轉成語音，在語音頻道即時播放。

## 功能

- `/invite #頻道` — Bot 加入你所在的語音頻道，並開始監聽指定文字頻道的訊息
- `/leave` — Bot 離開語音頻道並停止監聽
- 訊息自動排隊，依序播放，不會互相覆蓋
- 每個伺服器（Guild）獨立運作

## 前置需求

- [Python 3.10+](https://www.python.org/downloads/)
- [FFmpeg](https://ffmpeg.org/download.html)（discord.py 語音播放需要）
- [Discord Bot Token](https://discord.com/developers/applications)

## 安裝

```bash
# 複製專案
git clone https://github.com/your-username/edge-tts-discord-bot.git
cd edge-tts-discord-bot

# 安裝 Python 依賴
pip install -r requirements.txt

# 建立環境變數檔案
cp .env.example .env
# 編輯 .env，填入你的 Discord Bot Token
```

### 安裝 FFmpeg

**Windows：**
```bash
winget install Gyan.FFmpeg
```

**macOS：**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian)：**
```bash
sudo apt install ffmpeg
```

## 使用方式

```bash
python bot.py
```

Bot 上線後，在 Discord 中：

1. 先加入一個語音頻道
2. 輸入 `/invite #文字頻道名稱` 邀請 Bot 加入
3. 在被監聽的文字頻道中發送訊息，Bot 會自動唸出來
4. 輸入 `/leave` 讓 Bot 離開

## 專案結構

```
├── bot.py              # Discord Bot 主程式
├── tts.py              # TTS 模組（edge-tts 語音生成）
├── requirements.txt    # Python 依賴清單
├── .env.example        # 環境變數範例
└── .gitignore
```

## Discord Bot 設定

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications) 建立應用程式
2. 在 **Bot** 頁面中，開啟 **Message Content Intent**
3. 在 **OAuth2 > URL Generator** 中，勾選 `bot` 和 `applications.commands`
4. Bot Permissions 勾選：`Connect`、`Speak`、`Read Messages/View Channels`
5. 複製產生的 URL，邀請 Bot 加入你的伺服器

## 授權

MIT License
