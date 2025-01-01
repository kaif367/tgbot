import time
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, CallbackContext, filters
import pytz

# Telegram Bot Token
BOT_TOKEN = "7465621422:AAF2r_BY8G0liV8AntpmwBaFZa-HklXyAPo"
CHAT_ID = "-1002497408675"  # Replace with your group/channel ID

# Initialize Bot
bot = Bot(token=BOT_TOKEN)

# Parse Signals from Admin Message
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
            send_signal(signal)

# Send Signal Message
def send_signal(signal):
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
    bot.send_message(chat_id=CHAT_ID, text=message)

# Handle Admin Messages
def handle_message(update: Update, context: CallbackContext):
    if update.message.chat_id == int(CHAT_ID):  # Ensure message is from the correct group/channel
        message = update.message.text
        if "Quotex Pair" in message:  # Detect signal list
            signals = parse_signal_list(message)
            bot.send_message(chat_id=CHAT_ID, text="✅ Signal list received. Scheduling signals...")
            schedule_signals(signals)

# Main Function
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Message Handler
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

