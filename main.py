import discord
from dotenv import load_dotenv
import os

# 新增的套件
from langdetect import detect
import argostranslate.package
import argostranslate.translate

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 初始化 Argos Translate（確認已安裝語言包）
installed_languages = argostranslate.translate.get_installed_languages()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


def translate_text(text, from_lang, to_lang):
    try:
        for lang in installed_languages:
            if lang.code == from_lang:
                translation = lang.get_translation(from_lang, to_lang)
                return translation.translate(text)
    except Exception as e:
        print("Translation error:", e)
    return None


@client.event
async def on_message(message):
    print(f"Received message: {message.content} from {message.author}")
    if message.author.bot:
        print("Ignoring bot message")
        return

    original_text = message.content
    print(f"Original text: {original_text}")
    try:
        detected_lang = detect(original_text)
    except Exception as e:
        print("Language detection error:", e)
        return

    print(f"Detected language: {detected_lang}")

    if detected_lang.startswith("en"):
        target_lang = "zh"
    elif detected_lang.startswith("zh"):
        target_lang = "en"
    else:
        print("Unsupported language")
        return

    translated = translate_text(original_text, detected_lang, target_lang)
    print(f"Translated text: {translated}")
    if translated and translated.lower() != original_text.lower():
        await message.channel.send(
            f"🈯 翻譯（{detected_lang} → {target_lang}）：\n```{translated}```")


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN 環境變數未設定，請在 .env 檔案中加入 BOT_TOKEN=你的token")
    client.run(token)
