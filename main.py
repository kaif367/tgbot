import os
import asyncio
from telethon import TelegramClient, events
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")  # no .session extension
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID"))

bot = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
tele_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

pending_requests = {}

# Always reply to /start for testing
@bot.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    print(f"[LOG] /start received from {message.from_user.id}")
    await message.reply("👋 Welcome! Send your Quotex Trader ID to verify.")

# Debug all private messages
@bot.on_message(filters.private & filters.text)
async def handle_any_message(client: Client, message: Message):
    print(f"[LOG] Message from {message.from_user.id}: {message.text}")
    trader_id = message.text.strip()

    if not trader_id.isdigit():
        await message.reply("❌ Please send a valid Trader ID (numbers only).")
        return

    pending_requests[message.from_user.id] = trader_id
    await message.reply("🔍 Checking your ID with Quotex... Please wait a moment.")

    async with tele_client:
        print(f"[LOG] Sending Trader ID {trader_id} to @QuotexPartnerBot")
        await tele_client.send_message("@QuotexPartnerBot", trader_id)

@tele_client.on(events.NewMessage(from_users=254263373))
async def quotex_response_handler(event):
    response = event.raw_text
    print(f"[LOG] Received from QuotexPartnerBot: {response}")

    for user_id, trader_id in list(pending_requests.items()):
        if trader_id in response:
            if "under your link" in response.lower() and ("deposited" in response.lower() or "deposit amount" in response.lower()):
                try:
                    invite_link = await bot.create_chat_invite_link(chat_id=VIP_CHANNEL_ID, member_limit=1)
                    await bot.send_message(user_id, f"✅ Verified! Here’s your VIP link:\n{invite_link.invite_link}")
                except Exception as e:
                    print(f"[ERROR] Failed to send invite link: {e}")
                    await bot.send_message(user_id, "❌ Verified but failed to send invite link. Contact admin.")
            else:
                await bot.send_message(user_id, "❌ You are not under our affiliate or haven't deposited yet.")
            del pending_requests[user_id]
            break

async def main():
    await tele_client.start()
    await bot.start()
    print("[LOG] Bot started and running...")
    await asyncio.gather(
        asyncio.Event().wait(),
        tele_client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
