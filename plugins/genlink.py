import re, os, json, base64, logging
from utils import temp
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    replied = message.reply_to_message
    if not replied:
        vj = await bot.ask(chat_id=message.from_user.id, text="Now send me your message which you want to store.")
        replied = vj  # Use the message sent by the user

    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("Send me only video, audio, or document.")

    if message.has_protected_content and message.chat.id not in ADMINS:
        return await message.reply("okDa")

    # Forward the file to the file store channel
    forwarded = await replied.forward(FILE_STORE_CHANNEL)

    # Unpack using the forwarded message file_id
    result = unpack_new_file_id(getattr(forwarded, file_type.value).file_id)
    file_id = result[0]
    ref = result[1] if len(result) > 1 else None

    if not ref:
        return await message.reply_text("This file cannot be linked right now. Try forwarding it to me again.")

    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    await message.reply(f"Here is your Link:\nhttps://t.me/{temp.U_NAME}?start={outstr}")

@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    if " " not in message.text:
        return await message.reply("Use correct format.\nExample <code>/batch https://t.me/VJ_Botz/10 https://t.me/VJ_Botz/20</code>.")

    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample <code>/batch https://t.me/VJ_Botz/10 https://t.me/VJ_Botz/20</code>.")

    cmd, first, last = links
    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    
    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')
    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id  = int(("-100" + f_chat_id))

    match = regex.match(last)
    if not match:
        return await message.reply('Invalid link')
    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id  = int(("-100" + l_chat_id))

    if f_chat_id != l_chat_id:
        return await message.reply("Chat IDs do not match.")

    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply('This may be a private channel/group. Make me an admin there to index files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid link specified.')
    except Exception as e:
        return await message.reply(f'Error - {e}')

    sts = await message.reply("Generating link for your message.\nThis may take time depending on the number of messages.")

    if chat_id in FILE_STORE_CHANNEL:
    # Forward all files one-by-one to FILE_STORE_CHANNEL
    outlist = []
    og_msg = 0

    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        if msg.empty or msg.service or not msg.media:
            continue
        try:
            forwarded = await msg.forward(FILE_STORE_CHANNEL)
            file_type = forwarded.media
            file = getattr(forwarded, file_type.value)
            caption = getattr(forwarded, 'caption', '')
            if caption:
                caption = caption.html
            file = {
                "file_id": file.file_id,
                "caption": caption,
                "title": getattr(file, "file_name", ""),
                "size": file.file_size,
                "protect": cmd.lower().strip() == "/pbatch",
            }
            og_msg += 1
            outlist.append(file)
        except Exception as e:
            print(f"Error forwarding message: {e}")
            continue

    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)

    post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json", caption="⚠️ Generated for file store.")
    os.remove(f"batchmode_{message.from_user.id}.json")

    file_id, ref = unpack_new_file_id(post.document.file_id)
    return await sts.edit(f"Here is your link\nContains `{og_msg}` files.\nhttps://t.me/{temp.U_NAME}?start=BATCH-{file_id}")

    FRMT = "Generating Link...\nTotal Messages: `{total}`\nDone: `{current}`\nRemaining: `{rem}`\nStatus: `{sts}`"

    outlist = []
    og_msg = 0
    tot = 0

    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if msg.empty or msg.service:
            continue
        if not msg.media:
            continue
        try:
            file_type = msg.media
            file = getattr(msg, file_type.value)
            caption = getattr(msg, 'caption', '')
            if caption:
                caption = caption.html
            if file:
                file = {
                    "file_id": file.file_id,
                    "caption": caption,
                    "title": getattr(file, "file_name", ""),
                    "size": file.file_size,
                    "protect": cmd.lower().strip() == "/pbatch",
                }
                og_msg += 1
                outlist.append(file)
        except:
            pass
        
    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)

    post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json", caption="⚠️ Generated for file store.")
    os.remove(f"batchmode_{message.from_user.id}.json")

    file_id, ref = unpack_new_file_id(post.document.file_id)
    await sts.edit(f"Here is your link\nContains `{og_msg}` files.\nhttps://t.me/{temp.U_NAME}?start=BATCH-{file_id}")
