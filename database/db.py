from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI

client = AsyncIOMotorClient(DATABASE_URI)
db = client["moxi_filter_bot"]  # You can change the name if you want

missed_db = db["missed_filters"]
