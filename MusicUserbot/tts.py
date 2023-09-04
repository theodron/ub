import traceback
from asyncio import get_running_loop
from io import BytesIO

from googletrans import Translator
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR, bot as USER

def convert(text, lang, gender="male"):
    audio = BytesIO()
    tts = gTTS(text, lang=lang, tld=gender)  # 'tld' specifies the desired gender
    audio.name = lang + ".mp3"
    tts.write_to_fp(audio)
    return audio

@Client.on_message(filters.command(["tts"], prefixes=f"{HNDLR}"))
async def text_to_speech(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("💡 reply to some texts !")
    if not message.reply_to_message.text:
        return await message.reply_text("💡 reply to some texts !")
    m = await message.reply_text("🔁 Processing...")
    text = message.reply_to_message.text
    try:
        loop = get_running_loop()
        i = Translator().translate(text, dest="en")
        lang = i.src
        audio = await loop.run_in_executor(None, convert, text, lang, gender="male")  # Specify the desired gender here
        await message.reply_audio(audio)
        await m.delete()
        audio.close()
    except Exception as e:
        await m.edit(str(e))
        es = traceback.format_exc()
        print(es)
