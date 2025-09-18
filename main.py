from pyrogram import Client, filters
from pymongo import MongoClient
import subprocess, shlex
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
        {"$set": {"bot_token": bot_token, "owner_id": owner_id, "created_at": __import__('datetime').datetime.utcnow()}},
        upsert=True
    )

    await message.reply_text(f"✅ Bot cloned!\n\n🤖 Bot ID: `{bot_id}`\nOwner: `{owner_id}`")

    # Run clone bot in background (spawn new process)
    try:
        # Use shlex to avoid issues with spaces
        subprocess.Popen(["python3", "clone_bot.py", bot_token, str(owner_id)])
    except Exception as e:
        await message.reply_text(f"⚠️ Failed to start clone process: {e}")

if __name__ == '__main__':
    print("🚀 Main Bot Running...")
    main.run()
