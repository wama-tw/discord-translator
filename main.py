import discord
from dotenv import load_dotenv
import os
import fasttext
import argostranslate.package
import argostranslate.translate

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 載入 fastText 語言偵測模型
FASTTEXT_MODEL_PATH = "lid.176.bin"
if not os.path.exists(FASTTEXT_MODEL_PATH):
    raise FileNotFoundError(
        "請先下載 fastText 模型：wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    )
ft_model = fasttext.load_model(FASTTEXT_MODEL_PATH)


# 安裝語言包（一次性載入 langpacks 中的 .argosmodel）
def install_argos_models():
    model_dir = "langpacks"
    if not os.path.exists(model_dir):
        print(f"⚠️ 找不到語言包資料夾 {model_dir}，請建立並放入 .argosmodel 檔案")
        return
    for filename in os.listdir(model_dir):
        if filename.endswith(".argosmodel"):
            filepath = os.path.join(model_dir, filename)
            argostranslate.package.install_from_path(filepath)


install_argos_models()
installed_languages = argostranslate.translate.get_installed_languages()
print([l.code for l in installed_languages])  # 列出已安裝語言包的語言代碼


# 偵測語言（用 fasttext）
def detect_language(text):
    lang, confidence = ft_model.predict(text)
    lang = lang[0].replace("__label__", "")
    return lang, confidence[0]


# Argos Translate 翻譯文字
def translate_text(text, from_lang, to_lang):
    from_lang_obj = None
    to_lang_obj = None
    for lang in installed_languages:
        if lang.code == from_lang:
            from_lang_obj = lang
        if lang.code == to_lang:
            to_lang_obj = lang
    if from_lang_obj and to_lang_obj:
        translation = from_lang_obj.get_translation(to_lang_obj)
        return translation.translate(text)
    return None


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message):
    print(f"Received message: {message.content} from {message.author}")
    if message.author.bot:
        return

    text = message.content
    if not text.strip():
        print("⚠️ 空訊息，略過")
        return

    lang, conf = detect_language(text)
    print(f"🧠 Detected: {lang} ({conf:.2f})")

    if conf < 0.6:
        print("⚠️ 信心度不足，略過翻譯")
        return

    # 判斷翻譯方向（根據實際語言包調整，這裡假設 zh）
    if lang.startswith("en"):
        from_lang = "en"
        to_lang = "zh"
    elif lang.startswith("zh"):
        from_lang = "zh"
        to_lang = "en"
    else:
        print("⛔ 不支援的語言，略過")
        return

    translated = translate_text(text, from_lang, to_lang)
    if not translated:
        print(f"❌ 翻譯失敗：{from_lang} → {to_lang}")
        return
    if translated.lower() != text.lower():
        await message.channel.send(
            f"🈯 翻譯（{from_lang} → {to_lang}）：\n```{translated}```")


if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("請在 .env 中設定 BOT_TOKEN")
    client.run(token)
