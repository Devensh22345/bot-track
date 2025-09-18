import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient
from datetime import datetime, timezone
from config import API_ID, API_HASH, MONGO_URI

async def create_clone(bot_token, owner_id, owner_notify_id):
    bot_id = bot_token.split(":")[0]
    bot = Client(f"clone_{bot_id}", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token)
    mongo = MongoClient(MONGO_URI)
    db = mongo["multi_clone_bot"]
    users_col = db["users"]
    stats_col = db["stats"]

    @bot.on_message(filters.command("start"))
    async def start_handler(client, message):
        user = message.from_user
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        is_premium = bool(getattr(user, "is_premium", False))

        # Save user
        users_col.update_one(
            {"user_id": user.id, "bot_id": bot_id},
            {"$set": {"name": user.first_name or "", "is_premium": is_premium, "start_date": today, "bot_id": bot_id}},
            upsert=True
        )

        # Avoid duplicate counting
        already_counted = stats_col.find_one({"bot_id": bot_id, "date": today, "users": {"$in": [user.id]}})
        if not already_counted:
            stats_col.update_one(
                {"bot_id": bot_id, "date": today},
                {"$inc": {"premium_count" if is_premium else "nonpremium_count": 1},
                 "$set": {"month": month},
                 "$push": {"users": user.id}},
                upsert=True
            )

        # Notify owner
        status = "🌟 Premium" if is_premium else "👤 Free"
        await client.send_message(owner_notify_id, f"{status} User Started Bot\nName: {user.first_name}\nID: {user.id}\nBot: {bot_id}")

        await message.reply_text("✅ You started the bot!")

    @bot.on_message(filters.command("report") & filters.user(owner_notify_id))
    async def report_handler(client, message):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        daily = stats_col.find_one({"bot_id": bot_id, "date": today}) or {}
        daily_report = f"📊 Daily Report ({today})\n🌟 Premium: {daily.get('premium_count',0)}\n👤 Free: {daily.get('nonpremium_count',0)}"
        monthly_stats = list(stats_col.find({"bot_id": bot_id, "month": month}))
        lines = [f"📅 Monthly Report ({month})"]
        total_premium = total_free = 0
        for r in sorted(monthly_stats, key=lambda x: x["date"]):
            lines.append(f"{r['date']} → 🌟 {r.get('premium_count',0)} | 👤 {r.get('nonpremium_count',0)}")
            total_premium += r.get('premium_count',0)
            total_free += r.get('nonpremium_count',0)
        lines.append(f"📊 TOTAL: 🌟 {total_premium} | 👤 {total_free}")
        await message.reply_text(daily_report + "\n\n" + "\n".join(lines))

    await bot.start()
    print(f"🚀 Clone bot {bot_id} running for owner {owner_id}")
    return bot
