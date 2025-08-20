# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import pymongo
from info import OTHER_DB_URI, DATABASE_NAME
from pyrogram import enums
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(OTHER_DB_URI)
mydb = myclient[DATABASE_NAME]



async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text':str(text),
        'reply':str(reply_text),
        'btn':str(btn),
        'file':str(file),
        'alert':str(alert)
    }

    try:
        mycol.update_one({'text': str(text)},  {"$set": data}, upsert=True)
    except:
        logger.exception('Some error occured!', exc_info=True)
             
     

import base64
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    query = mycol.find({"text": name})

    try:
        for file in query:
            reply_text = file.get('reply', "")
            btn = file.get('btn', "[]")
            fileid = file.get('file', None)
            alert = file.get('alert', None)

            # ====== DOUBLE SECURE MINI APP BUTTON ======
            clip_link = file.get('clip_link')
            if clip_link:
                # Step 1: Base64 encode
                b64_link = base64.urlsafe_b64encode(clip_link.encode()).decode()
                # Create Mini App button
                miniapp_url = f"https://www.moxibeatz.fun/p/12.html?link={b64_link}"

                # Add second button below the first
                download_url = "https://t.me/c/2465511216/2"
                btn = [
                    [InlineKeyboardButton("🎬 Get Clip", url=miniapp_url)],   # First row
                ]

            return reply_text, btn, alert, fileid

        return None, None, None, None

    except Exception as e:
        print("Error in find_filter:", e)
        return None, None, None, None


        




async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    
    myquery = {'text':text }
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that filter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return

    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"All filters from {title} has been removed")
    except:
        await message.edit_text("Couldn't remove all filters from group!")
        return


async def count_filters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count()
    return False if count == 0 else count


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount += count

    totalcollections = len(collections)

    return totalcollections, totalcount










