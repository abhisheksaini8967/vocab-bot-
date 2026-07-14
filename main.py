import os
import json
import random
import logging
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Railway Variables se token dynamically load hoga
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1786928328

# Global In-Memory List (Superfast aur Railway deployment chalu rehte tak safe)
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
        welcome_text += "\n\n👑 <b>Admin Control Active:</b>\nSaare words ek sath copy karke direct chat me send kar dein, bot apne aap bulk add kar lega!"
        
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

# 👑 Automatic Bulk Detector (Bina kisi command jhanjhat ke, list milte hi khud save karega)
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text.strip()
    
    # Ignore regular commands like /start or /quiz
    if text.startswith('/'):
        return

    lines = text.split('\n')
    added_count = 0
    
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue
            
        try:
            parts = line.split("|")
            word = parts[0].strip()
            meaning = parts[1].strip()
            explanation = parts[2].strip() if len(parts) > 2 else "Koi detail uplabdh nahi hai."

            if word and meaning:
                next_id = len(WORDS_DATA)
                WORDS_DATA.append({
                    "id": next_id,
                    "word": word,
                    "meaning": meaning,
                    "explanation": explanation
                })
                added_count += 1
        except Exception:
            continue

    if added_count > 0:
        refresh_words_map()
        await update.message.reply_text(
            f"🚀 <b>Kamal Ho Gaya Bhai!</b>\n\nEk sath <b>{added_count}</b> naye words successfully database me jod diye gaye hain!\n"
            f"📚 Ab aapke bot me total <b>{len(WORDS_DATA)}</b> words ho chuke hain.\n\n"
            f"Ab aap shanti se <b>/quiz</b> chala kar khel sakte hain!",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("⚠️ Mujhe is message me koi bhi valid list format (`Word | Meaning`) nahi mila.")

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message or update.callback_query.message
    if not WORDS_DATA:
        await target.reply_text("⚠️ Abhi bot me koi words nahi hain. Kripya pehle apni poori list direct chat me send karke jodein.")
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
        raise ValueError("BOT_TOKEN missing!")
        
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(next_word_handler, pattern="^next_question$"))
    application.add_handler(CallbackQueryHandler(button_click, pattern=r"^ans|"))
    
    # Text message handler to catch full copied lists automatically
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    logger.info("Bot service running safely...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
