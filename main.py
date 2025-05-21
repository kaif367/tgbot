import os
import asyncio
from telethon import TelegramClient, events
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# ENV variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")  # without .session
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID"))

# Pyrogram bot (handles user messages)
bot = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Telethon client (interacts with @QuotexPartnerBot)
tele_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Stores pending trader ID verifications
pending_requests = {}

@bot.on_message(filters.private & filters.text)
async def handle_user(client: Client, message: Message):
    user_id = message.from_user.id
    trader_id = message.text.strip()

    if not trader_id.isdigit():
        await message.reply("❌ Please send a valid Trader ID (numbers only).")
        return

    pending_requests[user_id] = trader_id
    await message.reply("🔍 Checking your Trader ID... please wait 5-10 seconds.")

    async with tele_client:
        print(f"[INFO] Sending ID {trader_id} to @QuotexPartnerBot")
        await tele_client.send_message("@QuotexPartnerBot", trader_id)

@tele_client.on(events.NewMessage(from_users=254263373))  # @QuotexPartnerBot user ID
async def handle_affiliate_response(event):
    response = event.raw_text
    print(f"[DEBUG] Received from QuotexPartnerBot: {response}")

    for user_id, trader_id in list(pending_requests.items()):
        if trader_id in response:
            if "under your link" in response.lower() and ("deposited" in response.lower() or "deposit amount" in response.lower()):
                try:
                    invite_link = await bot.create_chat_invite_link(chat_id=VIP_CHANNEL_ID, member_limit=1)
                    await bot.send_message(user_id, f"✅ Verified! Here's your VIP link: {invite_link.invite_link}")
                except Exception as e:
                    print(f"[ERROR] Couldn't send VIP link: {e}")
                    await bot.send_message(user_id, "❌ Verified but failed to send link. Please contact admin.")
            else:
                await bot.send_message(user_id, "❌ You are not under our affiliate or haven't deposited yet.")
            del pending_requests[user_id]
            break

async def main():
    await tele_client.start()
    await bot.start()
    print("[✅] Bot is running and awaiting messages...")

    # Keeps both Pyrogram and Telethon running
    await asyncio.gather(
        asyncio.Event().wait(),  # Keeps Pyrogram alive
        tele_client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
