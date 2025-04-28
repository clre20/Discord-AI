import discord
from discord.ext import commands
import google.generativeai as genai
import sys
import os
import asyncio
import json
import requests

# -------------------- 設定 --------------------
API_KEY = "{你的 Gemini api}"  # Gemini AI Token
BOT_TOKEN = "{你機器人的 token}" # Discord Bot Token
COMMAND_PREFIX = "*"
MEMORY_DIR = "memory"
MODE_FILE = os.path.join(MEMORY_DIR, "mode.json")
DEFAULT_MODEL = "gemini-2.0-flash-lite"

# -------------------- 啟用模型驗證 --------------------
# 可用的 Gemini 模型列表 (用於驗證)
VALID_MODELS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro-latest",
]

CLOUDFLARE_MODES = [
    "llama-3-8b",
    "deepseek-r1",
    "gemma-7b",
]

# -------------------- 權限設定 --------------------
intents = discord.Intents.default()
intents.message_content = True  # 允許讀取訊息內容
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# -------------------- 記憶體和模式檔案檢查 --------------------
if not os.path.exists(MEMORY_DIR):
    try:
        os.makedirs(MEMORY_DIR)
        print(f"已建立記憶體資料夾: {MEMORY_DIR}")
    except OSError as e:
        print(f"建立記憶體資料夾失敗: {e}")
        sys.exit(100) # 無法建立資料夾則停止

# -------------------- 對話記憶 --------------------
def get_memory_filepath(user_id):
    return os.path.join(MEMORY_DIR, f"{user_id}.json")

def load_memory(user_id):
    memory_file = get_memory_filepath(user_id)
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"警告：記憶檔案 {memory_file} 格式錯誤，將其視為空記憶。")
            return []
        except Exception as e:
            print(f"載入記憶失敗 ({user_id}): {e}")
            return []
    else:
        return []

def save_memory(user_id, conversation):
    memory_file = get_memory_filepath(user_id)
    try:
        with open(memory_file, "w", encoding="utf8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"儲存記憶失敗 ({user_id}): {e}")

# -------------------- 模型模式設定 --------------------
def load_modes():
    if os.path.exists(MODE_FILE):
        try:
            with open(MODE_FILE, "r", encoding="utf8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"警告：模型設定檔 {MODE_FILE} 格式錯誤，將其視為空設定。")
            return {}
        except Exception as e:
            print(f"載入模型設定失敗: {e}")
            return {}
    else:
        return {}

def save_modes(modes_data):
    try:
        with open(MODE_FILE, "w", encoding="utf8") as f:
            json.dump(modes_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"儲存模型設定失敗: {e}")

# -------------------- Gemini AI API --------------------
def gemini(mode, prompt):
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(mode)
        response = model.generate_content(prompt)
        if response.candidates and response.candidates[0].content.parts:
            return response.text
        else:
            feedback_info = response.prompt_feedback or "未知原因"
            print(f"Gemini API 未提供有效回應。原因: {feedback_info}")
            return f"伺服器錯誤，請稍後再試或聯絡管理員。 [C_RW23]"
    except Exception as e:
        print(f"Gemini API 呼叫時發生錯誤：{e}")
        return f"伺服器錯誤，請稍後再試或聯絡管理員。 [G_DK48]"

# -------------------- Cloudflare AI API --------------------
def cloudflare(mode, prompt):
    try:
        url = f"https://example.com/{mode}"# 你 Cloudflare workers 的連結
        data = {
            "prompt": f"{prompt}"
        }
        # 發送 POST 請求
        response = requests.post(url, json=data)
        # 處理回應
        if response.status_code == 200:
            result = response.json()
            ai_reply_1 = result.get("response")
            ai_reply = ai_reply_1.get("response")

            return ai_reply
        else:
            print(f"錯誤-->{response.status_code}：{response.text}")
            return f"伺服器錯誤，請稍後再試或聯絡管理員。 [L_PO443_CO{response.status_code}]"
    except Exception as e:
        print(f"Cloudflare api 呼叫時發生錯誤: {e}")
        return f"伺服器錯誤，請稍後再試或聯絡管理員。 [Y_EB80]"

# -------------------- Bot 啟動 --------------------
@bot.event
async def on_ready():
    game = discord.Game(f'{COMMAND_PREFIX}help | AI on Duty')
    await bot.change_presence(status=discord.Status.online, activity=game)
    print(f"機器人已啟動，身分： {bot.user}")
    print(f"指令前綴: {COMMAND_PREFIX}")
    print(f"記憶體資料夾: {MEMORY_DIR}")
    print(f"模型設定檔: {MODE_FILE}")
    print(f"預設模型: {DEFAULT_MODEL}")
    print(f"支援的模型:")
    print(f"Gemini AI:")
    print(f"{', '.join(VALID_MODELS)}")
    print(f"ClRe20 AI:")
    print(f"{', '.join(CLOUDFLARE_MODES)}")
    print("-" * 20)

# -------------------- AI 對話觸發 --------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(COMMAND_PREFIX):
        await bot.process_commands(message)
        return

    if bot.user in message.mentions:
        say = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()
        if not say:
            await message.channel.send(f"哈囉！{message.author.mention} 需要我做什麼嗎？")
            return

        user_id = str(message.author.id)
        modes_data = load_modes()
        user_model = modes_data.get(user_id, DEFAULT_MODEL)

        # 載入並更新記憶
        conv_history = load_memory(user_id)
        conv_history.append({"role": "user", "parts": [say]})

        # 使用對話歷史構建 prompt
        #prompt_content = build_conversation_prompt(conv_history)
        prompt_content = conv_history

        async with message.channel.typing():
            if user_model in VALID_MODELS:
                bot_reply = gemini(user_model, prompt_content)
            elif user_model in CLOUDFLARE_MODES:
                bot_reply = cloudflare(user_model, prompt_content)

        if bot_reply and not bot_reply.startswith("伺服器錯誤"):
            conv_history.append({"role": "model", "parts": [bot_reply]})
            save_memory(user_id, conv_history)
        elif not bot_reply:
            bot_reply = "(AI 沒有產生回應)"

        # 分段傳送保證不超過 Discord 限制
        max_chars = 1990
        if len(bot_reply) > max_chars:
            start = 0
            while start < len(bot_reply):
                end = start + max_chars
                chunk = bot_reply[start:end]
                await message.channel.send(chunk)
                start = end
                await asyncio.sleep(0.5)
        else:
            #正常長度
            if bot_reply and bot_reply.strip():  # 確保 bot_reply 包含有效內容
                await message.channel.send(bot_reply)
            else:
                print("機器人嘗試向Discord傳送空白訊息")# [Z_HTT400_CO50006]
                await message.channel.send("可憐 AI都不想回應你  [Z_HTT400_CO50006]")

# -------------------- *mode 切換模型 --------------------
@bot.command(name='mode')
async def set_mode(ctx, *, model_input: str = None):
    user_id = str(ctx.author.id)
    if model_input is None:
        modes_data = load_modes()
        current = modes_data.get(user_id, DEFAULT_MODEL)
        gemini_opts = '`, `'.join(VALID_MODELS)
        cf_opts = '`, `'.join(CLOUDFLARE_MODES)
        await ctx.send(
            f"{ctx.author.mention} 您目前使用的模型：`{current}`\n"
            f"使用 `{COMMAND_PREFIX}mode <模型名>` 來切換。\n"
            f"可選 Gemini: `{gemini_opts}`\n可選 ClRe20: `{cf_opts}`"
        )
        return
    name = model_input.strip().strip('`')
    if name not in VALID_MODELS and name not in CLOUDFLARE_MODES:
        gemini_opts = '`, `'.join(VALID_MODELS)
        ocf_optsts = '`, `'.join(CLOUDFLARE_MODES)
        await ctx.send(f"{ctx.author.mention}不支援模型 `{name}`。\n可選 Gemini AI：\n`{gemini_opts}`\n可選 ClRe20 AI:\n`{ocf_optsts}`")
        return
    modes_data = load_modes()
    modes_data[user_id] = name
    save_modes(modes_data)
    await ctx.send(f"{ctx.author.mention} 已將模型設定為：`{name}`")

# -------------------- *del 刪除記憶 --------------------
@bot.command(name='del')
async def delete_memory(ctx):
    user_id = str(ctx.author.id)
    path = get_memory_filepath(user_id)
    if os.path.exists(path):
        try:
            os.remove(path)
            await ctx.send(f"{ctx.author.mention} 已刪除對話記錄。")
        except OSError as e:
            await ctx.send(f"刪除失敗: {e}")
    else:
        await ctx.send(f"{ctx.author.mention} 沒有可刪除的記憶檔案。")

# -------------------- *ping 取得延遲 --------------------
@bot.command(name='ping')
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f'Ping: {latency:.2f} ms')

# -------------------- 主程式入口 --------------------
if __name__ == '__main__':
    if not API_KEY or 'AIzaSy' not in API_KEY:
        print("錯誤：請設定您的 API_KEY")
        sys.exit(1)
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_DISCORD_BOT_TOKEN':
        print("錯誤：請設定您的 BOT_TOKEN")
        sys.exit(1)
    print("啟動機器人中...")
    bot.run(BOT_TOKEN)
