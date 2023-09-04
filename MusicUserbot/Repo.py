


import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from config import HNDLR, SUDO_USERS


@Client.on_message(filters.command(["repo"], prefixes=f"{HNDLR}"))
async def repo(client, m: Message):
    await m.delete()
    REPO = f"""
<b>👋 Hey {m.from_user.mention}!

🗃️ Music And Video Player UserBot

🔰 Telegram UserBot To Play Songs And Videos In Telegram Voice Chat.

👩‍💻 Brought To You By
• [Piyush](https://t.me/JoinIndianNavy_007)

📝 Requirements
• Python 3.8+
• FFMPEG
• Nodejs v16+

[MusicUserbot repo](https://github.com/CoderXPiyush/MusicUserbot)

📝 Required Variables
• `API_ID` - Get From [my.telegram.org](https://my.telegram.org)
• `API_HASH` - Get From [my.telegram.org](https://my.telegram.org)
• `SESSION` - Session String Pyrogram.
• `SUDO_USER` - Telegram Account ID Used As Admin
• `HNDLR` - Handler to run your userbot

"""
    await m.reply(REPO, disable_web_page_preview=True)
