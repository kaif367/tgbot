from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import pytz

# Telegram Bot Token
BOT_TOKEN = "7465621422:AAF2r_BY8G0liV8AntpmwBaFZa-HklXyAPo"
CHANNEL_ID = "@GROWUPBINARY"  # Replace with your channel username or ID
PRIVATE_CHAT_IDS = ["-1002497408675"]  # Add user IDs or group IDs for private delivery

# Initialize Bot
bot = Bot(token=BOT_TOKEN)

# Parse Signals from Channel Message
def parse_signal_list(message):
    lines = message.split("\n")
    signals = []
    for line in lines:
        if "|" in line and "Quotex Pair" not in line:  # Ignore headers
            parts = line.split("|")
            pair = parts[1].strip()
            time_str = parts[2].strip()
            action = parts[3].strip()
            signals.append({"pair": pair, "time": time_str, "action": action})
    return signals

# Send Signal Message Privately
def send_signal_privately(signal):
    message = f"""
━━━━━━━━━━━━━
📊 LIVE SIGNAL GENERATED
━━━━━━━━━━━━━

🚀 PAIR - {signal['pair']}
⏰ ENTRY TIME - {signal['time']}
↕️ DIRECTION - {"UP 🟩" if signal['action'] == "CALL" else "DOWN 🟥"}

✅ 1 Step Auto-Martingale
🧔🏻 OWNER - @Kaifsaifi001
"""
    for chat_id in PRIVATE_CHAT_IDS:
        bot.send_message(chat_id=chat_id, text=message)

# Schedule and Send Signals
def schedule_signals(signals):
    current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
    for signal in signals:
        entry_time = datetime.strptime(signal["time"], "%H:%M")
        signal_time = current_time.replace(hour=entry_time.hour, minute=entry_time.minute, second=0)
        send_time = signal_time - timedelta(minutes=1)

        if send_time > current_time:
            time_diff = (send_time - current_time).total_seconds()
            time.sleep(time_diff)
            send_signal_privately(signal)

# Handle Channel Messages
def handle_channel_message(update: Update, context: CallbackContext):
    if update.channel_post and update.channel_post.chat.username == CHANNEL_ID.lstrip("@"):
        message = update.channel_post.text
        if "Quotex Pair" in message:  # Detect signal list
            signals = parse_signal_list(message)
            bot.send_message(chat_id=update.channel_post.chat_id, text="✅ Signal list received. Processing...")
            schedule_signals(signals)

# Main Function
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Channel Message Handler
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.chat_type.channel, handle_channel_message))

    # Start Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
