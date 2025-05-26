from MoxiFILTERBOT.database.db import missed_db
from pymongo import DESCENDING

async def add_missing_filter(group_id: int, keyword: str):
    await missed_db.update_one(
        {"group_id": group_id, "keyword": keyword.lower()},
        {"$inc": {"count": 1}},
        upsert=True
    )

async def get_top_missing(group_id: int, limit=10):
    return await missed_db.find({"group_id": group_id}).sort("count", DESCENDING).to_list(length=limit)
