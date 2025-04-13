import traceback
from asyncio import get_running_loop
from io import BytesIO
from functools import partial

from googletrans import Translator
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR, bot as USER

def convert(text, lang):
    audio = BytesIO()
    try:
        # For Indian female voice, we use:
        # lang='en' - English
        # tld='co.in' - Indian domain
        # This combination sometimes produces Indian-accented English
        
        # For Hindi text, use lang='hi'
        actual_lang = 'hi' if lang == 'hi' else 'en'
        tts = gTTS(text, lang=actual_lang, tld='co.in')
        
        audio.name = f"tts_{actual_lang}.mp3"
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except Exception as e:
        raise Exception(f"TTS Error: {str(e)}")

@Client.on_message(filters.command(["tts"], prefixes=f"{HNDLR}"))
async def text_to_speech(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("💡 Please reply to a text message!")
    if not message.reply_to_message.text:
        return await message.reply_text("💡 Please reply to a text message!")
        
    m = await message.reply_text("🔁 Processing Indian female voice...")
    text = message.reply_to_message.text
    
    try:
        loop = get_running_loop()
        translator = Translator()
        
        # Detect language but force Indian English ('en') or Hindi ('hi')
        try:
            detected = translator.detect(text)
            lang = detected.lang if detected.confidence > 0.5 else 'en'
            # Use Hindi if detected, otherwise use English with Indian accent
            lang = 'hi' if lang == 'hi' else 'en'
        except:
            lang = 'en'  # Default to Indian English
        
        convert_func = partial(convert, text=text, lang=lang)
        audio = await loop.run_in_executor(None, convert_func)
        
        await message.reply_audio(audio)
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Error: {str(e)}")
        traceback.print_exc()
    finally:
        if 'audio' in locals():
            audio.close()
