# Discord-AI
---
# Discord AI Bot 說明文件

這是一個基於 Discord API 和 Gemini AI (Google Generative AI) 的機器人，支援不同 AI 模型切換與記憶對話功能。

## 1. 安裝必要套件

在使用此機器人前，需要安裝一些 Python 套件：
```bash
pip install discord.py google-generativeai requests asyncio
```

如果你的環境沒有 `pip`，請先安裝 Python，並確認 `pip` 正常工作。

## 2. 設定環境

在 `bot.py` 文件內，請修改以下設定：

### (1) 設定 API Key
請替換 `你的 Gemini api` 為你的 Google Gemini AI API 金鑰。
```python
API_KEY = "你的_Gemini_api_key"
```

如果你使用 Cloudflare AI Workers，也需替換 `url` 參數為你的 API 端點：
```python
url = "https://example.com"
```
!!請搭配專用的[Cloudflare-Workers-AI](https://github.com/clre20/Cloudflare-Workers-AI) 使用

### (2) 設定 Discord Bot Token
請替換 `你的_Discord_Bot_token` 為你的 Discord 機器人 Token：
```python
BOT_TOKEN = "你的_Discord_Bot_token"
```
如果沒有 Discord Bot，請先到 [Discord Developer Portal](https://discord.com/developers/applications) 建立機器人。

### (3) 設定指令前綴
如果你想修改機器人的指令前綴：
```python
COMMAND_PREFIX = "*"
```

## 3. 啟動機器人

執行 Python 程式：
```bash
python bot.py
```
如果成功啟動，終端機應該會顯示：
```
機器人已啟動，身分： <Bot_Name>
指令前綴: *
記憶體資料夾: memory
模型設定檔: memory/mode.json
預設模型: 
支援的模型:
```

## 4. 主要功能

### (1) AI 對話
在 Discord 群組中 @機器人，它會使用 Gemini AI 或 Cloudflare AI 回覆訊息。

### (2) 記憶對話
機器人會記住過去的對話，存儲在 `memory` 資料夾內，以提供記憶功能。

### (3) 切換 AI 模型
使用指令：
```
*mode <模型名>
```
可選模型：
- Gemini: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash-lite` 等。
- Cloudflare AI: {依據設定}。

### (4) 刪除記憶
指令：
```
*del
```
清除用戶的對話記錄。

### (5) 檢查機器人延遲
指令：
```
*ping
```
查看機器人的網路延遲。
