# Telegram Clone Bot System

This repo contains a **Main Bot** that allows users to clone their own Telegram bots by sending:
`/clone <BOT_TOKEN>` (in a private chat with the main bot). The main bot will spawn a clone process for the given token
and the clone will track /start events, save them to MongoDB and send logs to its owner.

## Files
- `main.py` - Main bot (clone manager)
- `clone_bot.py` - Clone bot logic (spawned per cloned bot)
- `config.py` - Fill in your API_ID, API_HASH, MAIN_BOT_TOKEN, MONGO_URI
- `Procfile` - For Heroku: runs the main bot as a worker
- `app.json` - Heroku app manifest (one-click deploy)
- `requirements.txt` - Python dependencies

## Deployment (Heroku)
1. Create a GitHub repo and push this project.
2. In Heroku, connect your GitHub repo and enable Automatic Deploys (or use Deploy button).
3. Set Config Vars in Heroku:
   - `API_ID`
   - `API_HASH`
   - `MAIN_BOT_TOKEN`
   - `MONGO_URI`
4. Deploy the app. The main bot will run as a worker process.

## Notes & Tips
- Each cloned bot process is spawned by the main bot using `subprocess.Popen(["python3","clone_bot.py", token, owner_id])`.
- Heroku's dynos may sleep or have process limits. For many clones, consider running clones on a VPS or queueing workers.
- Do NOT commit real tokens to public repos. Use Heroku Config Vars or other secret stores.
