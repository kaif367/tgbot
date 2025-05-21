from pyrogram import Client, filters
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("test_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private)
async def echo(client, message):
    print(f"[TEST] Message from {message.from_user.id}: {message.text}")
    await message.reply("Hello! I got your message.")

app.run()
