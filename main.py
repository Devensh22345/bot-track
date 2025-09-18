from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
import subprocess
from config import API_ID, API_HASH, MAIN_BOT_TOKEN, MONGO_URI

# Init main bot
main = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=MAIN_BOT_TOKEN)
mongo = MongoClient(MONGO_URI)
db = mongo["multi_clone_bot"]
clones_col = db["clones"]


@main.on_message(filters.command("clone") & filters.private)
async def clone_handler(client, message):
    # Usage: /clone <BOT_TOKEN>
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /clone <BOT_TOKEN> (in private chat)")

    bot_token = message.command[1].strip()
    if ':' not in bot_token:
        return await message.reply_text("❌ Invalid token format. Make sure it's BOT_TOKEN:XXXX")

    bot_id = bot_token.split(':')[0]
    owner_id = message.from_user.id

    # Save clone info
    clones_col.update_one(
        {"bot_id": bot_id},
        {"$set": {
            "bot_token": bot_token,
            "owner_id": owner_id,
            "created_at": __import__('datetime').datetime.utcnow()
        }},
        upsert=True
    )

    await message.reply_text(f"✅ Bot cloned!\n\n🤖 Bot ID: `{bot_id}`\nOwner: `{owner_id}`")

    # Run clone bot in background (spawn new process)
    try:
        subprocess.Popen(["python3", "clone_bot.py", bot_token, str(owner_id)])
    except Exception as e:
        await message.reply_text(f"⚠️ Failed to start clone process: {e}")


@main.on_message(filters.command("mybots") & filters.private)
async def mybots_handler(client, message):
    """Show all user’s cloned bots with unlink buttons"""
    owner_id = message.from_user.id
    bots = list(clones_col.find({"owner_id": owner_id}))

    if not bots:
        return await message.reply_text("ℹ️ You don’t have any linked bots.")

    keyboard = []
    for b in bots:
        bot_id = b["bot_id"]
        keyboard.append([InlineKeyboardButton(f"❌ Unlink {bot_id}", callback_data=f"unlink:{bot_id}")])

    await message.reply_text(
        "🤖 Your Cloned Bots:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@main.on_callback_query(filters.regex(r"^unlink:(.+)"))
async def unlink_callback(client, callback_query: CallbackQuery):
    """Handle unlink button clicks"""
    owner_id = callback_query.from_user.id
    bot_id = callback_query.data.split(":")[1]

    result = clones_col.delete_one({"owner_id": owner_id, "bot_id": bot_id})

    if result.deleted_count > 0:
        await callback_query.message.edit_text(f"❌ Bot `{bot_id}` unlinked successfully.")
    else:
        await callback_query.answer("⚠️ No such bot found.", show_alert=True)


@main.on_message(filters.command("unlink_all") & filters.private)
async def unlink_all_handler(client, message):
    """Unlink all bots at once"""
    owner_id = message.from_user.id
    result = clones_col.delete_many({"owner_id": owner_id})

    if result.deleted_count > 0:
        await message.reply_text(f"❌ All your {result.deleted_count} cloned bots have been unlinked.")
    else:
        await message.reply_text("ℹ️ You don’t have any linked bots.")


if __name__ == '__main__':
    print("🚀 Main Bot Running...")
    main.run()
