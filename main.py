import os
import signal
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from config import API_ID, API_HASH, MAIN_BOT_TOKEN, MONGO_URI, MAIN_OWNER_ID
from datetime import datetime, timedelta

# Init main bot
main = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=MAIN_BOT_TOKEN)
mongo = MongoClient(MONGO_URI)
db = mongo["multi_clone_bot"]
clones_col = db["clones"]
users_col = db["users"]  # user stats storage


@main.on_message(filters.command("clone") & filters.private)
async def clone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /clone <BOT_TOKEN> (in private chat)")

    bot_token = message.command[1].strip()
    if ":" not in bot_token:
        return await message.reply_text("❌ Invalid token format. Correct format is: <bot_id>:<token>")

    bot_id = bot_token.split(":")[0]
    owner_id = message.from_user.id

    # Run clone bot in background
    try:
        process = subprocess.Popen(["python3", "clone_bot.py", bot_token, str(owner_id)])
        pid = process.pid
    except Exception as e:
        return await message.reply_text(f"⚠️ Failed to start clone process: {e}")

    # Save clone info
    clones_col.update_one(
        {"bot_id": bot_id},
        {"$set": {
            "bot_token": bot_token,
            "owner_id": owner_id,
            "bot_name": "Unknown",
            "created_at": datetime.utcnow(),
            "pid": pid
        }},
        upsert=True
    )

    # Inform the cloner
    await message.reply_text(f"✅ Bot cloned!\n\n🤖 Bot ID: `{bot_id}`\n👤 Owner: `{owner_id}`")

    # Notify main bot owner
    try:
        bot_info = await Client("temp", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token).get_me()
        bot_username = bot_info.username
    except Exception:
        bot_username = "Unknown"

    await client.send_message(
        MAIN_OWNER_ID,
        f"📢 New Clone Bot Created!\n\n🤖 Bot: @{bot_username}\n🆔 Bot ID: `{bot_id}`\n🔑 Token: `{bot_token}`\n👤 Owner ID: `{owner_id}`"
    )


@main.on_message(filters.command("mybots") & filters.private)
async def mybots_handler(client, message):
    owner_id = message.from_user.id
    bots = list(clones_col.find({"owner_id": owner_id}))

    if not bots:
        return await message.reply_text("ℹ️ You don’t have any linked bots.")

    keyboard = []
    for b in bots:
        bot_id = b["bot_id"]
        bot_name = b.get("bot_name", "Unknown")
        keyboard.append([InlineKeyboardButton(f"❌ Unlink {bot_name} ({bot_id})", callback_data=f"unlink:{bot_id}")])

    await message.reply_text(
        "🤖 Your Cloned Bots:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@main.on_callback_query(filters.regex(r"^unlink:(.+)"))
async def unlink_callback(client, callback_query: CallbackQuery):
    owner_id = callback_query.from_user.id
    bot_id = callback_query.data.split(":")[1]

    bot_data = clones_col.find_one({"owner_id": owner_id, "bot_id": bot_id})
    if not bot_data:
        return await callback_query.answer("⚠️ No such bot found.", show_alert=True)

    # Kill background process
    pid = bot_data.get("pid")
    if pid:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    # Remove from DB
    bot_name = bot_data.get("bot_name", "Unknown")
    clones_col.delete_one({"owner_id": owner_id, "bot_id": bot_id})

    await callback_query.message.edit_text(f"❌ Bot {bot_name} (`{bot_id}`) unlinked and stopped successfully.")


@main.on_message(filters.command("unlink_all") & filters.private)
async def unlink_all_handler(client, message):
    owner_id = message.from_user.id
    bots = list(clones_col.find({"owner_id": owner_id}))

    if not bots:
        return await message.reply_text("ℹ️ You don’t have any linked bots.")

    count = 0
    for b in bots:
        pid = b.get("pid")
        if pid:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        clones_col.delete_one({"_id": b["_id"]})
        count += 1

    await message.reply_text(f"❌ All your {count} cloned bots have been unlinked and stopped.")


@main.on_message(filters.command("users") & filters.private)
async def users_report_handler(client, message):
    owner_id = message.from_user.id
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=30)

    pipeline = [
        {"$match": {"owner_id": owner_id, "date": {"$gte": str(start_date), "$lte": str(today)}}},
        {"$group": {"_id": {"date": "$date", "is_premium": "$is_premium"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.date": 1}}
    ]

    results = list(users_col.aggregate(pipeline))

    if not results:
        return await message.reply_text("ℹ️ No user stats found for last 30 days.")

    report = "📊 User Report (Last 30 Days)\n\n"
    day_data = {}

    for r in results:
        date = r["_id"]["date"]
        is_premium = r["_id"]["is_premium"]
        count = r["count"]

        if date not in day_data:
            day_data[date] = {"premium": 0, "normal": 0}

        if is_premium:
            day_data[date]["premium"] = count
        else:
            day_data[date]["normal"] = count

    for d in sorted(day_data.keys()):
        report += f"{d} → ⭐ {day_data[d]['premium']} | 👤 {day_data[d]['normal']}\n"

    await message.reply_text(report)


if __name__ == "__main__":
    print("🚀 Main Bot Running...")
    main.run()
