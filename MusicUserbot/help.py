import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from config import HNDLR, SUDO_USERS


@Client.on_message(filters.command(["help"], prefixes=f"{HNDLR}"))
async def help(client, m: Message):
    await m.delete()
    HELP = f"""
<b>👋 Hey {m.from_user.mention}!

🛠 MUSIC PLAYER HELP MENU

⚡ COMMAND FOR EVERYONE
• {HNDLR}play [song title | youtube links | reply audio file] - to play the song
• {HNDLR}videoplay [video title | youtube links | reply video file] - to play video
• {HNDLR}playlist to view playlists
• {HNDLR}id - to view user id
• {HNDLR}video - video title | yt link to find the video
• {HNDLR}song - title track | yt link to find songs
• {HNDLR}help - to see a list of commands
• {HNDLR}join- to join | to the group

⚡COMMANDS FOR SUDO USER
• {HNDLR}ping - to check status
• {HNDLR}eval - to manage bots
• {HNDLR}restart - to restart MusicUserbot

⚡ COMMAND TO ALL ADMIN
• {HNDLR}resume - to resume playing the song or video
• {HNDLR}pause - to pause playing a song or video
• {HNDLR}skip - to skip a song or video
• {HNDLR}end - to end playback</b>
"""
    await m.reply(HELP)
