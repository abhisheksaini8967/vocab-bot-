import os
import json
import random
import logging
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway Variables se dynamic load hoga
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1786928328

# Local Array Storage (Server reset hone tak data temporary rakhega, pure safety ke sath)
WORDS_DATA = []
WORDS_BY_ID = {}

def refresh_words_map():
    global WORDS_BY_ID
    WORDS_BY_ID = {item["id"]: item for item in WORDS_DATA}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["score"] = 0
    context.user_data["total_attempted"] = 0
    context.user_data["remaining"] = []
    context.user_data["current_question_answered"] = False
    
    welcome_text = "👋 <b>Swagat hai!</b>\n\nVocabulary quiz shuru karne ke liye <b>/quiz</b> type karein."
    if update.effective_user.id == ADMIN_ID:
        welcome_text += "\n\n👑 <b>Admin Control Active:</b>\nNaya word jodne ke liye aise type karein:\n<code>/add Word | Meaning | Explanation</code>"
        
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Aapke paas words add karne ki permission nahi hai.")
        return

    text = " ".join(context.args)
    if not text or "|" not in text:
        await update.message.reply_text(
            "⚠️ <b>Galat Format!</b>\n\nKripya is tarah se likhein:\n<code>/add Word | Meaning | Explanation</code>",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        parts = text.split("|")
        word = parts[0].strip()
        meaning = parts[1].strip()
        explanation = parts[2].strip() if len(parts) > 2 else "Koi detail uplabdh nahi hai."

        if not word or not meaning:
            await update.message.reply_text("⚠️ Word aur Meaning dono likhna zaroori hai.")
            return

        # Simple In-Memory Addition (Superfast & No File Crash)
        next_id = len(WORDS_DATA)
        WORDS_DATA.append({
            "id": next_id,
            "word": word,
            "meaning": meaning,
            "explanation": explanation
        })
        refresh_words_map()

        await update.message.reply_text(
            f"✅ <b>Word Successfully Added!</b>\n\n"
            f"📝 <b>Word:</b> <code>{escape(word)}</code>\n"
            f"🎯 <b>Meaning:</b> {escape(meaning)}\n"
            f"💡 <b>Explanation:</b> {escape(explanation)}\n\n"
            f"📚 Ab total <b>{len(WORDS_DATA)}</b> words ho chuke hain.",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Kuch gadhbadh hui. Kripya check karke dobara try karein.")

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message or update.callback_query.message
    if not WORDS_DATA:
        await target.reply_text("⚠️ Abhi bot me koi words nahi hain. Kripya pehle Admin <code>/add</code> command se words jodein.", parse_mode=ParseMode.HTML)
        return
    
    remaining = context.user_data.get("remaining", [])
    if not remaining:
        remaining = list(WORDS_BY_ID.keys())
        random.shuffle(remaining)
        
    word_id = remaining.pop()
    context.user_data["remaining"] = remaining
    context.user_data["current_question_answered"] = False
    
    correct_item = WORDS_BY_ID[word_id]
    correct_word = escape(correct_item["word"])
    correct_meaning = correct_item["meaning"]
    
    other_meanings = list(set(
        item["meaning"] for item in WORDS_DATA if item["meaning"] != correct_meaning
    ))
    
    while len(other_meanings) < 3:
        other_meanings.append(f"Galat Option {len(other_meanings) + 1}")
        
    wrong_options = random.sample(other_meanings, 3)
    options = wrong_options + [correct_meaning]
    random.shuffle(options)
    
    keyboard = []
    for opt in options:
        is_correct = "1" if opt == correct_meaning else "0"
        salt = random.randint(1000, 9999)
        callback_data = f"ans|{is_correct}|{word_id}|{salt}"
        keyboard.append([InlineKeyboardButton(opt, callback_data=callback_data)])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    question_text = f"❓ <b>Word:</b> <code>{correct_word}</code>\n\nIs shabd ka sahi hindi arth kya hai? Neeche diye gaye options me se chunein:"
    await target.reply_text(question_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_quiz_question(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data_parts = query.data.split("|")
    if data_parts[0] != "ans":
        return
    is_correct = data_parts[1]
    word_id = int(data_parts[2])
    
    if context.user_data.get("current_question_answered", False):
        await query.answer("⚠️ Aap is sawal ka jawab pehle hi de chuke hain!", show_alert=False)
        return
    context.user_data["current_question_answered"] = True
    await query.answer()
    
    target_item = WORDS_BY_ID.get(word_id)
    if not target_item:
        await query.edit_message_text("⚠️ Data nahi mila. Kripya /quiz dobara type karein.")
        return
    correct_word = escape(target_item["word"])
    correct_meaning = escape(target_item["meaning"])
    explanation = escape(target_item.get("explanation") or "Explanation available nahi hai.")
    
    context.user_data["total_attempted"] = context.user_data.get("total_attempted", 0) + 1
    if is_correct == "1":
        context.user_data["score"] = context.user_data.get("score", 0) + 1
        status_text = "✅ <b>Bilkul sahi jawab!</b>"
    else:
        status_text = f"❌ <b>Galat jawab!</b>\n\n🎯 <b>Sahi uttar:</b> {correct_meaning}"
        
    score = context.user_data["score"]
    total = context.user_data["total_attempted"]
    result_text = f"❓ <b>Word:</b> <code>{correct_word}</code>\n\n{status_text}\n💡 <b>Explanation:</b> {explanation}\n\n🏆 <b>Score:</b> <code>{score}/{total}</code>"
    
    next_keyboard = [[InlineKeyboardButton("➡️ Next Word", callback_data="next_question")]]
    next_markup = InlineKeyboardMarkup(next_keyboard)
    await query.edit_message_text(text=result_text, reply_markup=next_markup, parse_mode=ParseMode.HTML)

async def next_word_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"Error deleting old quiz message: {e}")
    await send_quiz_question(update, context)

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN variable missing!")
        
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("add", add_word))
    application.add_handler(CallbackQueryHandler(next_word_handler, pattern="^next_question$"))
    application.add_handler(CallbackQueryHandler(button_click, pattern=r"^ans|"))
    
    logger.info("Bot service running perfectly on cloud infrastructure...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
