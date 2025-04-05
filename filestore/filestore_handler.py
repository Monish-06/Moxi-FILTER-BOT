from pyrogram import Client, filters
from pyrogram.types import Message
from filestore.filestore_db import save_file

from info import FILE_STORE_CHANNEL  # Define this in info.py

@Client.on_message(filters.private & filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message: Message):
    file_msg = await message.forward(FILE_STORE_CHANNEL)
    success, link = await save_file(file_msg)
    if success:
        await message.reply(f"Your file is saved!\nLink: `{link}`")
    else:
        await message.reply("Failed to save file or already saved.")
