import os
import asyncio
import random
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from youtubesearchpython import VideosSearch
from config import HNDLR, bot, call_py
from MusicUserbot.helpers.queues import QUEUE, add_to_queue, get_queue

# Set cookies path (place your cookies.txt in this directory)
COOKIES_DIR = "cookies"
COOKIES_PATH = os.path.join(COOKIES_DIR, "cookies.txt")

# Create cookies directory if it doesn't exist
if not os.path.exists(COOKIES_DIR):
    os.makedirs(COOKIES_DIR)

ROCKSPHOTO = [
    "https://telegra.ph/file/613f681a511feb6d1b186.jpg",
    "https://telegra.ph/file/613f681a511feb6d1b186.jpg",
    "https://telegra.ph/file/613f681a511feb6d1b186.jpg",
    "https://telegra.ph/file/613f681a511feb6d1b186.jpg",
    "https://telegra.ph/file/613f681a511feb6d1b186.jpg",
]

IMAGE_THUMBNAIL = random.choice(ROCKSPHOTO)

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)

def has_cookies():
    return os.path.exists(COOKIES_PATH)

def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1)
        for r in search.result()["result"]:
            ytid = r["id"]
            if len(r["title"]) > 34:
                songname = r["title"][:35] + "..."
            else:
                songname = r["title"]
            url = f"https://www.youtube.com/watch?v={ytid}"
            duration = r["duration"]
        return [songname, url, duration]
    except Exception as e:
        print(e)
        return 0

async def ytdl(link):
    ytdl_cmd = [
        "yt-dlp",
        "-g",
        "-f",
        "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
    ]
    
    if has_cookies():
        ytdl_cmd.extend(["--cookies", COOKIES_PATH])
    
    ytdl_cmd.append(link)
    
    proc = await asyncio.create_subprocess_exec(
        *ytdl_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        error_msg = stderr.decode()
        if "Sign in to confirm you're not a bot" in error_msg:
            return 0, "YouTube authentication failed. Please update cookies.txt"
        return 0, error_msg

async def ytdl_video(link, quality):
    ytdl_cmd = [
        "yt-dlp",
        "-g",
        "-f",
        f"best[height<={quality}]",
    ]
    
    if has_cookies():
        ytdl_cmd.extend(["--cookies", COOKIES_PATH])
    
    ytdl_cmd.append(link)
    
    proc = await asyncio.create_subprocess_exec(
        *ytdl_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        error_msg = stderr.decode()
        if "Sign in to confirm you're not a bot" in error_msg:
            return 0, "YouTube authentication failed. Please update cookies.txt"
        return 0, error_msg

@Client.on_message(filters.command(["play"], prefixes=f"{HNDLR}"))
async def play(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    if replied:
        if replied.audio or replied.voice:
            await m.delete()
            huehue = await replied.reply("**✧ Processing Request..**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:35] + "..."
                else:
                    songname = replied.audio.file_name[:35] + "..."
                duration = convert_seconds(replied.audio.duration)
            elif replied.voice:
                songname = "Voice Note"
                duration = convert_seconds(replied.voice.duration)
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                await m.reply_photo(
                    photo=IMAGE_THUMBNAIL,
                    caption=f"""
**▶ Songs Queued To** `{pos}`
🏷 **Title:** [{songname}]({link})
⏱️ **Duration:** `{duration}`
💡 **Status:** `Playing`
🎧 **Requested By:** {m.from_user.mention}
""",
                )
            else:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(dl),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                await m.reply_photo(
                    photo=IMAGE_THUMBNAIL,
                    caption=f"""
**▶ Start Playing Songs**
🏷 **Title:** [{songname}]({link})
⏱️ **Duration:** `{duration}`
💡 **Status:** `Playing`
🎧 **Requested By:** {m.from_user.mention}
""",
                )
    else:
        if len(m.command) < 2:
            await m.reply("Reply to Audio Files or give something to Search")
        else:
            await m.delete()
            huehue = await m.reply("**✧ Searching for a song... Please be patient**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await huehue.edit("`Found Nothing for the Given Query`")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**YTDL ERROR ❌** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.delete()
                        await m.reply_photo(
                            photo=IMAGE_THUMBNAIL,
                            caption=f"""
**▶ Songs Queued To** `{pos}`
🏷 **Title:** [{songname}]({url})
⏱️ **Duration:** `{duration}`
💡 **Status:** `Playing`
🎧 **Requested By:** {m.from_user.mention}
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(ytlink),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await huehue.delete()
                            await m.reply_photo(
                                photo=IMAGE_THUMBNAIL,
                                caption=f"""
**▶ Start Playing Songs**
🏷️ **Title:** [{songname}]({url})
⏱️ **Duration** `{duration}`
💡 **Status:** `Playing`
🎧 **Requested By:** {m.from_user.mention}
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")

@Client.on_message(filters.command(["videoplay", "vplay"], prefixes=f"{HNDLR}"))
async def videoplay(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    if replied:
        if replied.video or replied.document:
            await m.delete()
            huehue = await replied.reply("**✧ Processing Videos....**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await huehue.edit("`Now Streaming in 720p`")
            
            try:
                if replied.video:
                    songname = replied.video.file_name[:70]
                elif replied.document:
                    songname = replied.document.file_name[:70]
            except BaseException:
                songname = "Video File"

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                await m.reply_photo(
                    photo=IMAGE_THUMBNAIL,
                    caption=f"""
**▶ Videos Queued To {pos}
🏷️ Title: [{songname}]({link})
💡 Status: Playing
🎧 Requested By: {m.from_user.mention}**
""",
                )
            else:
                if Q == 720:
                    hmmm = HighQualityVideo()
                elif Q == 480:
                    hmmm = MediumQualityVideo()
                elif Q == 360:
                    hmmm = LowQualityVideo()
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(dl, HighQualityAudio(), hmmm),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                await m.reply_photo(
                    photo=IMAGE_THUMBNAIL,
                    caption=f"""
**▶ Start Playing Video
🏷️ Title: [{songname}]({link})
💡 Status: Playing
🎧 Requested By: {m.from_user.mention}**
""",
                )
    else:
        if len(m.command) < 2:
            await m.reply("**Reply to Video Files or give something to Search**")
        else:
            await m.delete()
            huehue = await m.reply("**🔍 Searching... Please Wait**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            hmmm = HighQualityVideo()
            if search == 0:
                await huehue.edit("**Found Nothing for the Given Query**")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                hm, ytlink = await ytdl_video(url, Q)
                if hm == 0:
                    await huehue.edit(f"**YTDL ERROR ❌** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await huehue.delete()
                        await m.reply_photo(
                            photo=IMAGE_THUMBNAIL,
                            caption=f"""
**▶ Videos Queued To** `{pos}`
🏷️ **Title:** [{songname}]({url})
⏱️ **Duration:** `{duration}`
💡 **Status:** `Playing`
🎧 **Requested By:** {m.from_user.mention}
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(ytlink, HighQualityAudio(), hmmm),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await huehue.delete()
                            await m.reply_photo(
                                photo=IMAGE_THUMBNAIL,
                                caption=f"""
**▶ Start Playing Video**
🏷️ **Title:** [{songname}]({url})
⏱️ **Duration:** `{duration}`
💡 **Status:** `Playing`
🎧 **Requested By:** {m.from_user.mention}
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")

@Client.on_message(filters.command(["playfrom"], prefixes=f"{HNDLR}"))
async def playfrom(client, m: Message):
    chat_id = m.chat.id
    if len(m.command) < 2:
        await m.reply(f"**Usage:** \n\n`{HNDLR}playfrom [chat_id/username]`")
    else:
        args = m.text.split(maxsplit=1)[1]
        if ";" in args:
            chat = args.split(";")[0]
            limit = int(args.split(";")[1])
        else:
            chat = args
            limit = 10
        await m.delete()
        hmm = await m.reply(f"**✧ Taking {limit} Random Songs From {chat}**")
        try:
            async for x in bot.search_messages(chat, limit=limit, filter="audio"):
                location = await x.download()
                if x.audio.title:
                    songname = x.audio.title[:30] + "..."
                else:
                    songname = x.audio.file_name[:30] + "..."
                link = x.link
                if chat_id in QUEUE:
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                else:
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(location),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                    await m.reply_photo(
                        photo=IMAGE_THUMBNAIL,
                        caption=f"""
**▶ Start Playing Songs From {chat}
🏷️ Title: [{songname}]({link})
💡 Status: Playing
🎧 Requested By: {m.from_user.mention}**
""",
                    )
            await hmm.delete()
            await m.reply(f"**✧ Added {limit} Songs To Queue**")
        except Exception as e:
            await hmm.edit(f"**ERROR** \n`{e}`")

@Client.on_message(filters.command(["playlist", "queue"], prefixes=f"{HNDLR}"))
async def playlist(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await m.delete()
            await m.reply(
                f"**✧ NOW PLAYING:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",
                disable_web_page_preview=True,
            )
        else:
            QUE = f"**✧ NOW PLAYING:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**⏳ QUEUE LIST:**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                QUE = QUE + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`\n"
            await m.reply(QUE, disable_web_page_preview=True)
    else:
        await m.reply("**✧ Doesn't Play Anything...**")

@Client.on_message(filters.command(["cookies"], prefixes=f"{HNDLR}"))
async def check_cookies(client, m: Message):
    if has_cookies():
        await m.reply("✅ YouTube cookies are configured and working!")
    else:
        await m.reply("❌ No cookies.txt found. Some YouTube videos may not play.\n\n"
                     "To fix this:\n"
                     "1. Get the 'Get cookies.txt' browser extension\n"
                     "2. Log in to YouTube in your browser\n"
                     "3. Export cookies and save as `cookies/cookies.txt`")
