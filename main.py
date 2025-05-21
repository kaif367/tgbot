import os
import asyncio
from telethon import TelegramClient, events
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")  # path to your .session file (without .session extension)
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID"))

# Pyrogram bot (for handling user commands)
bot = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Telethon client (for messaging @QuotexPartnerBot)
tele_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Dictionary to map user_id -> trader_id (to track who asked what)
pending_requests = {}

@bot.on_message(filters.private & filters.text)
async def handle_trader_id(client: Client, message: Message):
    user_id = message.from_user.id
    trader_id = message.text.strip()

    if not trader_id.isdigit():
        await message.reply("❌ Please send a valid Trader ID (numbers only).")
        return

    # Save mapping for future reference
    pending_requests[user_id] = trader_id

    await message.reply("🔍 Checking your ID with Quotex... Please wait 5-10 seconds.")

    # Send to affiliate bot using Telethon
    async with tele_client:
        await tele_client.send_message("@QuotexPartnerBot", trader_id)

@tele_client.on(events.NewMessage(from_users=254263373))  # QuotexPartnerBot's user ID
async def handle_affiliate_reply(event):
    response = event.raw_text

    for user_id, trader_id in pending_requests.items():
        if trader_id in response:
            if "under your link" in response and ("deposited" in response or "Deposit amount" in response):
                invite_link = await bot.create_chat_invite_link(chat_id=VIP_CHANNEL_ID, member_limit=1)
                await bot.send_message(user_id, f"✅ Verified! Here's your VIP link: {invite_link.invite_link}")
            else:
                await bot.send_message(user_id, "❌ Sorry, you are not in our affiliate or haven't deposited yet.")
            del pending_requests[user_id]
            break

async def main():
    await tele_client.start()
    await bot.start()
    print("Bot is running...")
    await asyncio.gather(
        tele_client.run_until_disconnected(),
        asyncio.Event().wait()  # Keeps Pyrogram bot alive
    )

if __name__ == "__main__":
    asyncio.run(main())
