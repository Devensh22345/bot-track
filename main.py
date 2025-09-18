import asyncio
import logging
from datetime import datetime, timezone

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient

from config import API_ID, API_HASH, MAIN_BOT_TOKEN, MONGO_URI

logging.basicConfig(level=logging.INFO)

# --- Initialize main bot ---
main = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=MAIN_BOT_TOKEN)

mongo = MongoClient(MONGO_URI)
db = mongo["multi_clone_bot"]
clones_col = db["clones"]
users_col = db["users"]
stats_col = db["stats"]

# --- Dictionary to hold running clone clients ---
running_clones = {}

# ------------------ Clone Functions ------------------ #
async def start_clone(bot_token, owner_id, bot_name="Unknown"):
    bot_id = bot_token.split(":")[0]
    if bot_id in running_clones:
        return

    clone_client = Client(f"clone_{bot_id}", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token)

    # Handle /start for clone bots
    @clone_client.on_message(filters.command("start"))
    async def start_handler(client, message):
        user = message.from_user
        is_premium = bool(getattr(user, "is_premium", False))
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")

        # Save user info
        users_col.update_one(
            {"user_id": user.id, "bot_id": bot_id},
            {"$set": {
                "name": user.first_name or "",
                "is_premium": is_premium,
                "start_date": today,
                "bot_id": bot_id
            }},
            upsert=True
        )

        # Update stats
        already_counted = stats_col.find_one({
            "bot_id": bot_id,
            "date": today,
            "users": {"$in": [user.id]}
        })
        if not already_counted:
            stats_col.update_one(
                {"bot_id": bot_id, "date": today},
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
                owner_id,
                f"{status} User Started Bot\n\n👤 Name: {user.first_name or ''}\n🆔 ID: {user.id}\n🤖 Bot: {bot_id}"
            )
        except Exception as e:
            logging.info(f"Could not send owner message: {e}")

        await message.reply_text(f"✅ You started the bot `{bot_name}`!")

    # Start the clone client
    try:
        await clone_client.start()
        running_clones[bot_id] = clone_client
        print(f"🚀 Clone bot {bot_name} ({bot_id}) started for owner {owner_id}")
    except Exception as e:
        print(f"⚠️ Failed to start clone {bot_name} ({bot_id}): {e}")


async def stop_clone(bot_id):
    client = running_clones.get(bot_id)
    if client:
        await client.stop()
        running_clones.pop(bot_id, None)
        print(f"❌ Clone bot {bot_id} stopped")


async def restart_all_clones():
    all_clones = list(clones_col.find({}))
    for c in all_clones:
        await start_clone(c["bot_token"], c["owner_id"], c.get("bot_name", "Unknown"))


# ------------------ Main Bot Handlers ------------------ #
@main.on_message(filters.command("clone") & filters.private)
async def clone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /clone <BOT_TOKEN>")

    bot_token = message.command[1].strip()
    if ":" not in bot_token:
        return await message.reply_text("❌ Invalid token format.")

    bot_id = bot_token.split(":")[0]
    owner_id = message.from_user.id
    bot_name = "Unknown"

    # Save clone in DB
    clones_col.update_one(
        {"bot_id": bot_id},
        {"$set": {
            "bot_token": bot_token,
            "owner_id": owner_id,
            "bot_name": bot_name,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

    await start_clone(bot_token, owner_id, bot_name)
    await message.reply_text(f"✅ Bot cloned!\n🤖 Bot: {bot_name} (`{bot_id}`)\n👤 Owner: `{owner_id}`")


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

    await stop_clone(bot_id)
    clones_col.delete_one({"owner_id": owner_id, "bot_id": bot_id})
    await callback_query.message.edit_text(f"❌ Bot {bot_data.get('bot_name','Unknown')} ({bot_id}) unlinked and stopped successfully.")


@main.on_message(filters.command("unlink_all") & filters.private)
async def unlink_all_handler(client, message):
    owner_id = message.from_user.id
    bots = list(clones_col.find({"owner_id": owner_id}))

    if not bots:
        return await message.reply_text("ℹ️ You don’t have any linked bots.")

    for b in bots:
        await stop_clone(b["bot_id"])
        clones_col.delete_one({"_id": b["_id"]})

    await message.reply_text(f"❌ All your cloned bots have been unlinked and stopped.")


@main.on_message(filters.command("report") & filters.user(lambda _, __, msg: msg.from_user.id in [c["owner_id"] for c in clones_col.find()]))
async def report_handler(client, message):
    # Example: aggregate reports for all clones of this owner
    owner_id = message.from_user.id
    bots = list(clones_col.find({"owner_id": owner_id}))

    report_lines = []
    for b in bots:
        bot_id = b["bot_id"]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")

        daily = stats_col.find_one({"bot_id": bot_id, "date": today}) or {}
        report_lines.append(
            f"🤖 Bot {bot_id}\n🌟 Premium: {daily.get('premium_count',0)} | 👤 Free: {daily.get('nonpremium_count',0)}"
        )

    await message.reply_text("📊 Your Bots Report:\n" + "\n\n".join(report_lines))


# ------------------ Startup ------------------ #
async def main_async():
    await restart_all_clones()
    print("🚀 Main bot running with all clones active")
    await main.start()
    print("✅ Main bot is now listening for commands...")

    # Keep alive
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main_async())
