import re
import os
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from keep_alive import keep_alive

# ── CONFIG: Put your BotFather token here ──
TOKEN = os.environ.get("BOT_TOKEN") or "YOUR_BOT_TOKEN_HERE"
# ──────────────────────────────────────────

# List of abusive words (will catch chutiya, ch*tiya, etc.)
BAD_WORDS = [
    "chutiya","madarchod","behenchod","mc","bc","bsdk",
    "bhosdike","lauda","loda","lund","randi","gandu","gand",
    "bkl","chodu"
]

def clean_text(text: str) -> str:
    # Remove everything except a–z to catch obfuscations
    return re.sub(r'[^a-zA-Z]', '', text.lower())

def delete_abuse(update: Update, context: CallbackContext):
    msg = update.message.text or ""
    cleaned = clean_text(msg)
    for word in BAD_WORDS:
        if word in cleaned:
            try:
                update.message.delete()
            except:
                pass
            return

def welcome(update: Update, context: CallbackContext):
    for user in update.message.new_chat_members:
        update.message.reply_text(
            f"👋 Welcome {user.first_name}! Please follow the group rules."
        )

def main():
    # Start the keep-alive web server (for Render/Replit)
    keep_alive()

    # Create the Updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, delete_abuse))

    # Start the bot
    updater.start_polling()
    print("🤖 Bot is running (v13.15)...")
    updater.idle()

if __name__ == "__main__":
    main()
    