import os
import re
import time

from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from keep_alive import keep_alive

TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN_HERE"

# ✅ Full Abuse Word List (Hinglish + Hindi + English)
ABUSE_WORDS = [
    "chutiya", "chootiya", "chuya", "chutya", "chutiye", "chutiyo", "madrachod", "madarchod", "maderchod",
    "madar chod", "maa chod", "maachod", "maadarchod", "behenchod", "bahenchod", "behnchod", "behn ke lode",
    "behen ke laude", "muh me", "bahanchod", "bakchodi", "bakchod", "bhosdi", "bhosda", "bhosdika",
    "bhosada", "bhosdiwale", "bhosdi k", "bh0sdi", "gaand", "gand", "gandu", "g@ndu", "gaand mara", "gand fat",
    "gand mein danda", "lund", "loda", "lauda", "l0da", "laundiya", "launde", "bsdk", "bc", "mc", "muh me lele",
    "bkl", "kutta", "kutte", "kamine", "kamina", "harami", "kutti", "randi", "r@ndi", "lawde", "raand",
    "chod", "chodu", "chodi", "chodne", "chudai", "chuda", "chakke", "dada", "chakka", "chus", "chaka",
    "khandan", "raghel", "chudne", "chudunga", "chudwa", "chodte", "ganda", "gnda", "jhant", "jhantu",
    "jhantoo", "jhatu", "hidgi", "rndi", "randwe", "jhatt", "jhattt", "pela", "kali", "chuche", "bahan",
    "jhant ke", "jhantiyan", "jhantiyo", "moot", "mootna", "napunsak", "hijra", "pike", "doodh", "chucheon",
    "baap", "chuta", "chua", "hizra", "sexy", "sex", "porn", "nude", "suck", "sucking", "bitch", "baby",
    "loli pop", "lolipop", "b@tch", "bith", "bastard", "slut", "whore", "prostitute", "dogla", "wtf", "ki mar",
    "ki maar", "dogli", "motherfucker", "mother fucker", "mf", "fuck", "fuk", "fck", "gay", "gf", "fym",
    "lesbian", "transgender", "condomn", "danda", "choduga", "laudi", "pelunga", "pel dunga", "pelenge",
    "bhosdiwalee", "randii", "fad", "madhrchod", "andi bandi sandi", "andi mandi sandi", "chudwa", "baal",
    "maal", "fate", "randi rona", "condom", "kala", "ass", "asshole", "dick", "d!ck", "d!@k", "d@ck", "tatti",
    "gobar", "gaali", "gali", "marva", "gaandu", "chod diya", "chut", "bhosdike", "gad", "maarni", "lavde",
    "chusu", "mara", "land",
    # Hindi
    "चूतिया", "भोसड़ी", "मादरचोद", "भोसड़ीवाले", "चूत", "लौड़ा", "रंडी", "चुदाई", "झांट", "गांड", "बहनचोद",
    "माँ की", "चोद", "भोसडी", "मादर", "चुद", "चूतड़", "तेरी माँ", "तेरी बहन", "तू चोद", "माँ-बहन", "लंड",
    "भोसड़ीा", "भोसरी", "गांडू", "हरामी", "हरामखोर", "नपुंसक", "कांडोम", "मादरजात", "गांड मे", "माँ चोद्द दी"
]

# ✅ Spam Keywords
SPAM_WORDS = [
    "free", "buy now", "offer", "limited time", "subscribe", "join fast",
    "click here", "discount", "followers", "like for like", "promo", "visit",
    "earn", "earning", "referral", "loot", "cash", "join our", "group link",
    "sale", "dm us", "tap link", "grow fast", "100%", "crypto", "airdrop",
    "investment", "profit", "giveaway", "hot deal", "Join For Fun", "join this group for fun"
]

# ✅ Link Regex
LINK_REGEX = r"(http[s]?://\S+|t\.me/\S+|@[\w\d_]+)"

# ✅ Flooding tracking
user_message_times = {}

# ✅ Clean text to normalize symbols (e.g. ch*tiya → chutiya)
def clean_text(text: str) -> str:
    return re.sub(r'[^a-zA-Z]', '', text.lower())

# ✅ Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Namaste dosto! Main aapka ShieldBot hoon. 🤖 Spam aur abuse se raksha karunga!")

# ✅ Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    cleaned = clean_text(text)
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id

    # Flood Detection
    now = time.time()
    timestamps = user_message_times.get(user_id, [])
    timestamps = [t for t in timestamps if now - t < 6]
    timestamps.append(now)
    user_message_times[user_id] = timestamps

    if len(timestamps) >= 5:
        await mute_user(update, context, 10, "flooding the chat")
        return

    # Abuse Detection
    for word in ABUSE_WORDS:
        if word in cleaned:
            await mute_user(update, context, 15, "abusive language")
            return

    # Link Detection
    if re.search(LINK_REGEX, text):
        await mute_user(update, context, 10, "sending spam links")
        return

    # Spam Keyword Detection
    for spam in SPAM_WORDS:
        if spam in text:
            await mute_user(update, context, 10, "promotion or spam")
            return

# ✅ Mute & Delete Message
async def mute_user(update, context, minutes, reason):
    user = update.message.from_user
    chat_id = update.effective_chat.id
    await update.message.delete()
    until = int(time.time()) + (60 * minutes)

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{user.first_name} ko {minutes} minutes ke liye mute kiya gaya: {reason} 🚫"
        )
    except:
        await context.bot.send_message(chat_id=chat_id, text="❗ Bot failed to mute user. Is it admin?")

# ✅ Auto delete join/leave messages
async def delete_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

# ✅ Launch Bot
if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, delete_service_messages))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, delete_service_messages))
    print("✅ MyShieldBot is running...")
    app.run_polling()
