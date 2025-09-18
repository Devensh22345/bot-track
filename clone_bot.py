import sys
import logging
from pyrogram import Client, filters
from pymongo import MongoClient
from datetime import datetime
from config import API_ID, API_HASH, MONGO_URI

logging.basicConfig(level=logging.INFO)
# Args: BOT_TOKEN OWNER_ID
if len(sys.argv) < 3:
    print("Usage: python3 clone_bot.py <BOT_TOKEN> <OWNER_ID>")
    sys.exit(1)

BOT_TOKEN = sys.argv[1]
OWNER_ID = int(sys.argv[2])
BOT_ID = BOT_TOKEN.split(':')[0]

bot = Client(f"clone_{BOT_ID}", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo = MongoClient(MONGO_URI)
db = mongo["multi_clone_bot"]
users_col = db["users"]
stats_col = db["stats"]

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    is_premium = bool(getattr(user, 'is_premium', False))
    today = datetime.utcnow().strftime("%Y-%m-%d")
    month = datetime.utcnow().strftime("%Y-%m")

    # Save user
    users_col.update_one(
        {"user_id": user.id, "bot_id": BOT_ID},
        {"$set": {
            "name": user.first_name or '',
            "is_premium": is_premium,
            "start_date": today,
            "bot_id": BOT_ID
        }},
        upsert=True
    )

    # Update stats (per date)
    stats_col.update_one(
        {"bot_id": BOT_ID, "date": today},
        {"$inc": {"premium_count" if is_premium else "nonpremium_count": 1},
         "$set": {"month": month}},
        upsert=True
    )

    # Notify owner
    status = "🌟 Premium" if is_premium else "👤 Free"
    try:
        await client.send_message(
            OWNER_ID,
            f"{status} User Started Bot\n\n👤 Name: {user.first_name or ''}\n🆔 ID: {user.id}\n🤖 Bot: {BOT_ID}"
        )
    except Exception as e:
        # Owner may not accept messages from bot; ignore
        logging.info(f"Could not send owner message: {e}")

    await message.reply_text("✅ You started the bot!")


@bot.on_message(filters.command("report") & filters.user(OWNER_ID))
async def report_handler(client, message):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    month = datetime.utcnow().strftime("%Y-%m")

    # Today’s report
    daily = stats_col.find_one({"bot_id": BOT_ID, "date": today}) or {}
    daily_report = (
        f"📊 Daily Report ({today})\n"
        f"🌟 Premium: {daily.get('premium_count', 0)}\n"
        f"👤 Free: {daily.get('nonpremium_count', 0)}"
     )
                      

    # Monthly report with date breakdown
    monthly_stats = list(stats_col.find({"bot_id": BOT_ID, "month": month}))
    monthly_lines = [f"📅 Monthly Report ({month})\n"]

    total_premium = 0
    total_free = 0

    for record in sorted(monthly_stats, key=lambda x: x["date"]):
        date = record["date"]
        premium = record.get("premium_count", 0)
        free = record.get("nonpremium_count", 0)

        monthly_lines.append(f"🗓 {date} → 🌟 {premium} | 👤 {free}")
        total_premium += premium
        total_free += free

    monthly_lines.append("\n📊 TOTAL:")
    monthly_lines.append(f"🌟 Premium: {total_premium}")
    monthly_lines.append(f"👤 Free: {total_free}")

    monthly_report = "\n".join(monthly_lines)

    await message.reply_text(daily_report + "\n\n" + monthly_report)


if __name__ == '__main__':
    print(f"🚀 Clone Bot {BOT_ID} running for owner {OWNER_ID}")
    bot.run()
