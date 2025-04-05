from pyrogram import Client, filters
from pyrogram.types import Message
from filestore.filestore_db import save_file

from info import FILE_STORE_CHANNEL  # This must be a valid channel ID (int, with -100)

@Client.on_message(filters.private & filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message: Message):
    try:
        # Forward the file to file store channel
        sent = await message.forward(FILE_STORE_CHANNEL)
        
        # Save the message ID of the forwarded file in DB
        success, link = await save_file(sent)

        if success:
            await message.reply(f"**Your file has been saved!**\nHere is your link:\n`{link}`")
        else:
            await message.reply("This file is already saved.")
    except Exception as e:
        await message.reply(f"Error: {e}")
