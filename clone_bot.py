import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from pyrogram import Client, filters
from config import API_ID, API_HASH, MONGO_URI

bot_token = sys.argv[1]
owner_id = int(sys.argv[2])

clone = Client("clone_bot", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token)
mongo = MongoClient(MONGO_URI)
db = mongo["multi_clone_bot"]
users_col = db["users"]


# -------- START HANDLER --------
@clone.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    is_premium = bool(user.is_premium)
    bot_id = (await client.get_me()).id
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Save user only once per day
    users_col.update_one(
        {"bot_id": bot_id, "user_id": user.id, "date": today},
        {"$set": {
            "is_premium": is_premium,
            "timestamp": datetime.utcnow()
        }},
        upsert=True
    )

    await message.reply_text("👋 Welcome! You have been logged.")


# -------- USERS REPORT --------
@clone.on_message(filters.command("users") & filters.private)
async def users_report(client, message):
    if message.from_user.id != owner_id:
        return await message.reply_text("⚠️ Only owner can use this command.")

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29)
    bot_id = (await client.get_me()).id

    pipeline = [
        {"$match": {"bot_id": bot_id, "date": {"$gte": start_date.strftime("%Y-%m-%d")}}},
        {"$group": {"_id": {"date": "$date", "is_premium": "$is_premium"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.date": 1}}
    ]
    stats = list(users_col.aggregate(pipeline))

    # Prepare daily data
    data_map = {}
    for s in stats:
        d = s["_id"]["date"]
        if d not in data_map:
            data_map[d] = {"premium": 0, "normal": 0}
        if s["_id"]["is_premium"]:
            data_map[d]["premium"] += s["count"]
        else:
            data_map[d]["normal"] += s["count"]

    # Build report
    report = "📊 User Report (Last 30 Days)\n\n"
    total_prem = total_norm = 0
    for i in range(30):
        d = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        prem = data_map.get(d, {}).get("premium", 0)
        norm = data_map.get(d, {}).get("normal", 0)
        total_prem += prem
        total_norm += norm
        report += f"🗓 {d} → ⭐ {prem} | 👤 {norm}\n"

    report += "\n📌 Monthly Summary\n"
    report += f"⭐ Premium: {total_prem}\n"
    report += f"👤 Free: {total_norm}\n"
    report += f"👥 Total: {total_prem + total_norm}"

    await message.reply_text(report)
