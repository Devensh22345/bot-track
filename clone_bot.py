import sys
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup
from pymongo import MongoClient
from datetime import datetime, timezone
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
start_col = db["start_messages"]

# Temporary state for /setstart
pending_start_setup = {}

# ===== /setstart COMMAND =====
@bot.on_message(filters.command("setstart") & filters.user(OWNER_ID))
async def setstart_cmd(client, message):
    pending_start_setup[OWNER_ID] = True
    await message.reply_text(
        "📌 Send me the start message now.\n"
        "Supported types: text, photo, video, document.\n"
        "You can attach inline buttons too."
    )

# ===== Capture owner message for start message =====
@bot.on_message(filters.private)
async def capture_start_msg(client, message):
    if message.from_user.id != OWNER_ID or not pending_start_setup.get(OWNER_ID):
        return

    data = {"bot_id": BOT_ID, "owner_id": OWNER_ID, "buttons": [], "created_at": datetime.now(timezone.utc)}

    # Save inline buttons if exist
    if message.reply_markup:
        for row in message.reply_markup.inline_keyboard:
            data["buttons"].append([{"text": btn.text, "url": btn.url} for btn in row])

    # Determine type
    if message.text:
        data["type"] = "text"
        data["content"] = message.text
    elif message.photo:
        data["type"] = "photo"
        data["content"] = message.photo.file_id
        data["caption"] = message.caption or ""
    elif message.video:
        data["type"] = "video"
        data["content"] = message.video.file_id
        data["caption"] = message.caption or ""
    elif message.document:
        data["type"] = "document"
        data["content"] = message.document.file_id
        data["caption"] = message.caption or ""
    else:
        return await message.reply_text("❌ Unsupported message type.")

    start_col.update_one({"bot_id": BOT_ID}, {"$set": data}, upsert=True)
    pending_start_setup.pop(OWNER_ID)
    await message.reply_text("✅ Start message saved successfully!")

# ===== /start HANDLER =====
@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user
    is_premium = bool(getattr(user, 'is_premium', False))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = datetime.now(timezone.utc).strftime("%Y-%m")

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

    # Avoid duplicate counting per day
    already_counted = stats_col.find_one({
        "bot_id": BOT_ID,
        "date": today,
        "users": {"$in": [user.id]}
    })

    if not already_counted:
        stats_col.update_one(
            {"bot_id": BOT_ID, "date": today},
            {
                "$inc": {"premium_count" if is_premium else "nonpremium_count": 1},
                "$set": {"month": month},
                "$push": {"users": user.id}
            },
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
        logging.info(f"Could not send owner message: {e}")

    # Send custom start message if exists
    start_msg = start_col.find_one({"bot_id": BOT_ID})
    if start_msg:
        buttons = InlineKeyboardMarkup(start_msg.get("buttons", [])) if start_msg.get("buttons") else None
        if start_msg["type"] == "text":
            await message.reply_text(start_msg["content"], reply_markup=buttons)
        elif start_msg["type"] == "photo":
            await message.reply_photo(start_msg["content"], caption=start_msg.get("caption",""), reply_markup=buttons)
        elif start_msg["type"] == "video":
            await message.reply_video(start_msg["content"], caption=start_msg.get("caption",""), reply_markup=buttons)
        elif start_msg["type"] == "document":
            await message.reply_document(start_msg["content"], caption=start_msg.get("caption",""), reply_markup=buttons)
    else:
        await message.reply_text("✅ You started the bot!")

# ===== /report HANDLER =====
@bot.on_message(filters.command("report") & filters.user(OWNER_ID))
async def report_handler(client, message):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = datetime.now(timezone.utc).strftime("%Y-%m")

    daily = stats_col.find_one({"bot_id": BOT_ID, "date": today}) or {}
    daily_report = (
        f"📊 Daily Report ({today})\n"
        f"🌟 Premium: {daily.get('premium_count', 0)}\n"
        f"👤 Free: {daily.get('nonpremium_count', 0)}"
    )

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

# ===== RUN BOT =====
if __name__ == '__main__':
    print(f"🚀 Clone Bot {BOT_ID} running for owner {OWNER_ID}")
    bot.run()
