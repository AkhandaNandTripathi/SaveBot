import asyncio
import time
import os
import logging

from pyrogram.enums import ParseMode, MessageMediaType
from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, FloodWait
from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot, video_metadata
from telethon import events

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.INFO)
logging.getLogger("telethon").setLevel(logging.INFO)

user_chat_ids = {}

def thumbnail(sender):
    return f'{sender}.jpg' if os.path.exists(f'{sender}.jpg') else 'thumb.jpg'

async def copy_message_with_chat_id(client, sender, chat_id, message_id):
    target_chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.copy_message(target_chat_id, chat_id, message_id)
    except Exception as e:
        error_message = f"Error occurred while sending message to chat ID {target_chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {target_chat_id} and restart the process after /cancel")

async def send_message_with_chat_id(client, sender, message, parse_mode=None):
    chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.send_message(chat_id, message, parse_mode=parse_mode)
    except Exception as e:
        error_message = f"Error occurred while sending message to chat ID {chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {chat_id} and restart the process after /cancel")

@bot.on(events.NewMessage(incoming=True, pattern='/setchat'))
async def set_chat_id(event):
    try:
        chat_id = int(event.raw_text.split(" ", 1)[1])
        user_chat_ids[event.sender_id] = chat_id
        await event.reply("Chat ID set successfully!")
    except (ValueError, IndexError):
        await event.reply("Invalid chat ID!")

async def send_video_with_chat_id(client, sender, path, caption, duration, hi, wi, thumb_path, upm):
    chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.send_video(
            chat_id=chat_id,
            video=path,
            caption=caption,
            supports_streaming=True,
            duration=duration,
            height=hi,
            width=wi,
            thumb=thumb_path,
            progress=progress_for_pyrogram,
            progress_args=(
                client,
                '**__Uploading: [PragyanCoder](https://t.me/PragyanCoder)__**\n ',
                upm,
                time.time()
            )
        )
    except Exception as e:
        error_message = f"Error occurred while sending video to chat ID {chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {chat_id} and restart the process after /cancel")

async def send_document_with_chat_id(client, sender, path, caption, thumb_path, upm):
    chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.send_document(
            chat_id=chat_id,
            document=path,
            caption=caption,
            thumb=thumb_path,
            progress=progress_for_pyrogram,
            progress_args=(
                client,
                '**__Uploading:__**\n**__Bot made by [PragyanCoder](https://t.me/PragyanCoder)__**',
                upm,
                time.time()
            )
        )
    except Exception as e:
        error_message = f"Error occurred while sending document to chat ID {chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {chat_id} and restart the process after /cancel")

async def check(userbot, client, link):
    logging.info(link)
    msg_id = 0
    try:
        msg_id = int(link.split("/")[-1])
    except ValueError:
        if '?single' not in link:
            return False, "**Invalid Link!**"
        link_ = link.split("?single")[0]
        msg_id = int(link_.split("/")[-1])
    if 't.me/c/' in link:
        try:
            chat = int('-100' + str(link.split("/")[-2]))
            await userbot.get_messages(chat, msg_id)
            return True, None
        except (ValueError, ChatIdInvalid):
            return False, "**Invalid Link!**"
        except Exception as e:
            logging.info(e)
            return False, "Have you joined the channel?"
    else:
        try:
            chat = str(link.split("/")[-2])
            await client.get_messages(chat, msg_id)
            return True, None
        except Exception as e:
            logging.info(e)
            return False, "Maybe bot is banned from the chat, or your link is invalid!"

async def get_msg(userbot, client, sender, edit_id, msg_link, i, file_n):
    edit = ""
    chat = ""
    msg_id = int(i)
    if msg_id == -1:
        await client.edit_message_text(sender, edit_id, "**Invalid Link!**")
        return None
    if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
        if "t.me/b" not in msg_link:
            chat = int('-100' + str(msg_link.split("/")[-2]))
        else:
            chat = int(msg_link.split("/")[-2])
        try:
            msg = await userbot.get_messages(chat_id=chat, message_ids=msg_id)
            logging.info(msg)
            if msg.service is not None:
                await client.delete_messages(chat_id=sender, message_ids=edit_id)
                return None
            if msg.empty is not None:
                await client.delete_messages(chat_id=sender, message_ids=edit_id)
                return None
            
            if msg.media and msg.media == MessageMediaType.WEB_PAGE:
                a = b = True
                edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                if any(tag in msg.text.html for tag in ['--', '**', '__', '~~', '||', '\n', '`']):
                    await send_message_with_chat_id(client, sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if any(tag in msg.text.markdown for tag in ['<b>', '<i>', '<em>', '<u>', '<s>', '<spoiler>', '<a href=>', '<pre', '<code>', '<emoji']):
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b:
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                await edit.delete()
                return None
            if not msg.media and msg.text:
                a = b = True
                edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                if any(tag in msg.text.html for tag in ['--', '**', '__', '~~', '||', '\n']):
                    await send_message_with_chat_id(client, sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if any(tag in msg.text.markdown for tag in ['<b>', '<i>', '<em>', '<u>', '<s>', '<spoiler>', '<a href=>', '<pre', '<code>', '<emoji']):
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b:
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                await edit.delete()
                return None
            if msg.media == MessageMediaType.POLL:
                await client.edit_message_text(sender, edit_id, 'Poll media cannot be saved')
                return
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**__Unrestricting__: __[PragyanCoder](https://t.me/PragyanCoder)__**\n ",
                    edit,
                    time.time()
                )
            )
            path = file
            await edit.delete()
            upm = await client.send_message(sender, '__Preparing to Upload!__')
            caption = str(file) if msg.caption is None else msg.caption
            file_ext = str(file).split(".")[-1]
            if file_ext in ['mkv', 'mp4', 'webm', 'mpe4', 'mpeg', 'ts', 'avi', 'flv', 'org']:
                if file_ext in ['webm', 'mkv', 'mpe4', 'mpeg', 'ts', 'avi', 'flv', 'org']:
                    path = str(file).split(".")[0] + ".mp4"
                    os.rename(file, path)
                    file = path
                data = video_metadata(file)
                duration = data["duration"]
                wi = data["width"]
                hi = data["height"]
                logging.info(data)
                if file_n:
                    path = f'/app/downloads/{file_n}' if '.' in file_n else f'/app/downloads/{file_n}.{file_ext}'
                    os.rename(file, path)
                    file = path
                try:
                    thumb_path = thumbnail(sender)
                except Exception as e:
                    logging.info(e)
                    thumb_path = None
                caption = f"{msg.caption}\n\n__Unrestricted by **[PragyanCoder](https://t.me/PragyanCoder)**__" if msg.caption else "__Unrestricted by **[PragyanCoder](https://t.me/PragyanCoder)**__"
                await send_video_with_chat_id(client, sender, path, caption, duration, hi, wi, thumb_path, upm)
            elif file_ext in ['jpg', 'jpeg', 'png', 'webp']:
                if file_n:
                    path = f'/app/downloads/{file_n}' if '.' in file_n else f'/app/downloads/{file_n}.{file_ext}'
                    os.rename(file, path)
                    file = path
                caption = f"{msg.caption}\n\n__Unrestricted by **[PragyanCoder](https://t.me/PragyanCoder)**__" if msg.caption else "__Unrestricted by **[PragyanCoder](https://t.me/PragyanCoder)**__"
                await upm.edit("__Uploading photo...__")
                await bot.send_file(sender, path, caption=caption)
            else:
                if file_n:
                    path = f'/app/downloads/{file_n}' if '.' in file_n else f'/app/downloads/{file_n}.{file_ext}'
                    os.rename(file, path)
                    file = path
                thumb_path = thumbnail(sender)
                caption = f"{msg.caption}\n\n__Unrestricted by **[PragyanCoder](https://t.me/PragyanCoder)**__" if msg.caption else "__Unrestricted by **[PragyanCoder](https://t.me/PragyanCoder)**__"
                await send_document_with_chat_id(client, sender, path, caption, thumb_path, upm)
            os.remove(file)
            await upm.delete()
            return None
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Bot is not in that channel/group. Send the invite link so that the bot can join.")
            return None
    else:
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat = msg_link.split("/")[-2]
        await copy_message_with_chat_id(client, sender, chat, msg_id)
        await edit.delete()
        return None

async def get_bulk_msg(userbot, client, sender, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    file_name = ''
    await get_msg(userbot, client, sender, x.id, msg_link, i, file_name)
