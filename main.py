import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from telethon import TelegramClient, events
from pyrogram.types import Message

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID"))
SESSION_NAME = os.getenv("SESSION_NAME")

# Pyrogram Bot
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Telethon Client
tele_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Store pending requests
pending_requests = {}

# START command response
@bot.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    await message.reply("👋 Welcome! Please send your Quotex Trader ID to check your status.")

# Handle text as trader ID
@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_trader_id(client: Client, message: Message):
    user_id = message.from_user.id
    trader_id = message.text.strip()

    if not trader_id.isdigit():
        await message.reply("❌ Please send a valid Trader ID (numbers only).")
        return

    pending_requests[user_id] = trader_id
    await message.reply("🔍 Checking your ID with Quotex... Please wait...")

    async with tele_client:
        await tele_client.send_message("@QuotexPartnerBot", trader_id)

# Handle reply from Quotex bot
@tele_client.on(events.NewMessage(from_users=254263373))  # Make sure this is correct
async def handle_affiliate_reply(event):
    response = event.raw_text

    for user_id, trader_id in pending_requests.items():
        if trader_id in response:
            if "under your link" in response and ("deposited" in response or "Deposit amount" in response):
                invite_link = await bot.create_chat_invite_link(chat_id=VIP_CHANNEL_ID, member_limit=1)
                await bot.send_message(user_id, f"✅ Verified! Here's your VIP link: {invite_link.invite_link}")
            else:
                await bot.send_message(user_id, "❌ Sorry, you're not under our link or haven’t deposited.")
            del pending_requests[user_id]
            break

# Main function
async def main():
    await tele_client.start()
    await bot.start()
    print("[✅] Bot is running and awaiting messages...")
    await asyncio.get_event_loop().create_future()  # Keeps alive

if __name__ == "__main__":
    asyncio.run(main())
