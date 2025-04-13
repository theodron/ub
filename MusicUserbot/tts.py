import traceback
from asyncio import get_running_loop
from io import BytesIO
from functools import partial

from googletrans import Translator
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR, bot as USER

def convert(text, lang, gender="male"):
    audio = BytesIO()
    # Note: gTTS doesn't directly support gender parameter
    # Using different TLDs can sometimes affect voice characteristics
    tld = "com"  # Default (can try "co.uk" for different voice)
    if gender.lower() == "female":
        tld = "com.au"  # Example TLD that might sound more feminine
        
    tts = gTTS(text, lang=lang, tld=tld)
    audio.name = f"tts_{lang}.mp3"
    tts.write_to_fp(audio)
    audio.seek(0)  # Rewind the buffer
    return audio

@Client.on_message(filters.command(["tts"], prefixes=f"{HNDLR}"))
async def text_to_speech(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("💡 Please reply to a text message!")
    if not message.reply_to_message.text:
        return await message.reply_text("💡 Please reply to a text message!")
        
    m = await message.reply_text("🔁 Processing...")
    text = message.reply_to_message.text
    
    try:
        loop = get_running_loop()
        translator = Translator()
        # Detect language (fallback to English if detection fails)
        try:
            detected = translator.detect(text)
            lang = detected.lang if detected.confidence > 0.5 else "en"
        except:
            lang = "en"
        
        # Create partial function with all arguments
        convert_func = partial(convert, text=text, lang=lang, gender="male")
        
        # Run in executor without passing kwargs directly
        audio = await loop.run_in_executor(None, convert_func)
        
        await message.reply_audio(audio)
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Error: {str(e)}")
        traceback.print_exc()
    finally:
        if 'audio' in locals():
            audio.close()
