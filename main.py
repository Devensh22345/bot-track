import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from config import API_ID, API_HASH, MAIN_BOT_TOKEN, MONGO_URI
from datetime import datetime

# --- Initialize ---
main = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=MAIN_BOT_TOKEN)
mongo = MongoClient(MONGO_URI)
db = mongo["multi_clone_bot"]
clones_col = db["clones"]

# --- Dictionary to hold running clone clients ---
running_clones = {}

# --- Clone functions ---
async def start_clone(bot_token, owner_id, bot_name="Unknown"):
    bot_id = bot_token.split(":")[0]
    if bot_id in running_clones:
        return

    clone_client = Client(f"clone_{bot_id}", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token)

    @clone_client.on_message(filters.command("start"))
    async def start_handler(client, message):
        await message.reply_text(f"✅ You started the bot `{bot_name}`!")

    await clone_client.start()
    running_clones[bot_id] = clone_client
    print(f"🚀 Clone bot {bot_name} ({bot_id}) started for owner {owner_id}")

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

# --- Main bot handlers ---
@main.on_message(filters.command("clone") & filters.private)
async def clone_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /clone <BOT_TOKEN>")

    bot_token = message.command[1].strip()
    if ":" not in bot_token:
        return await message.reply_text("❌ Invalid token format. Make sure it's BOT_TOKEN:XXXX")

    bot_id = bot_token.split(":")[0]
    owner_id = message.from_user.id
    bot_name = "Unknown"

    # Save to DB
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
    await message.reply_text(f"✅ Bot cloned!\n\n🤖 Bot: {bot_name} (`{bot_id}`)\n👤 Owner: `{owner_id}`")

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

# --- Startup ---
async def startup():
    await restart_all_clones()
    print("🚀 Main bot running with all clones active")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(startup())
    main.run()  # ✅ no argument here
