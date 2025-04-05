from pymongo import MongoClient
from info import MONGO_URI, FDATABASE_NAME, FILE_STORE_CHANNEL

client = MongoClient(MONGO_URI)
db = client[FDATABASE_NAME]
collection = db["filestore"]

async def save_file(msg):
    file_id = msg.id
    channel_id = FILE_STORE_CHANNEL  # Should be like -1001234567890

    if collection.find_one({"_id": file_id}):
        return False, None

    collection.insert_one({
        "_id": file_id,
        "channel_id": channel_id
    })

    # Generate link
    link = f"https://t.me/c/{str(channel_id)[4:]}/{file_id}"
    return True, link
