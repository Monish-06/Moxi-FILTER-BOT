from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI

client = AsyncIOMotorClient(DATABASE_URI)
db = client["moxi_filter_bot"]
missed_db = db["missed_filters"]

async def add_missing_filter(group_id, keyword):
    keyword = keyword.strip().lower()
    existing = await missed_db.find_one({"group_id": group_id, "keyword": keyword})
    if existing:
        await missed_db.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"count": 1}}
        )
    else:
        await missed_db.insert_one({
            "group_id": group_id,
            "keyword": keyword,
            "count": 1
        })

async def get_top_missing(group_id, limit=10):
    return await missed_db.find({"group_id": group_id}).sort("count", -1).to_list(length=limit)

async def remove_missing_filter(group_id, keyword):
    keyword = keyword.strip().lower()
    result = await missed_db.delete_one({"group_id": group_id, "keyword": keyword})
    return result.deleted_count > 0
