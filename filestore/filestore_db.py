from pymongo import MongoClient
from info import MONGO_URI, DATABASE_NAME2, FILE_STORE_CHANNEL

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME2]
collection = db["files"]

async def save_file(msg):
    file_id = msg.id
    channel_id = str(FILE_STORE_CHANNEL)

    # Check if file already exists
    if collection.find_one({"_id": file_id}):
        return False, None

    file_data = {
        "_id": file_id,
        "channel_id": channel_id
    }

    collection.insert_one(file_data)
    link = f"https://t.me/{channel_id.replace('-100', '')}/{file_id}"
    return True, link
