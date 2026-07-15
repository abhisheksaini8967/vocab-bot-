import os
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

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1786928328

# 📚 Initial Words List (Pehle se loaded hain)
WORDS_DATA = [
  {"id": 0, "word": "Philanthropist", "meaning": "परोपकारी", "explanation": "दूसरों की मदद करने वाला"},
  {"id": 1, "word": "Epitaph", "meaning": "समाधि-लेख", "explanation": "कब्र पर लिखा जाने वाला संदेश"},
  {"id": 2, "word": "Obsolete", "meaning": "अप्रचलित", "explanation": "जो अब उपयोग में न हो या पुराना हो चुका हो"},
  {"id": 3, "word": "Illegible", "meaning": "अपठनीय", "explanation": "जिसे पढ़ना मुश्किल या असंभव हो, जैसे डॉक्टर की लिखावट"},
  {"id": 4, "word": "Inevitable", "meaning": "अनिवार्य / जो होना तय हो", "explanation": "जिसे टाला न जा सके"},
  {"id": 5, "word": "Aviary", "meaning": "पक्षी-घर", "explanation": "वह जगह जहाँ पक्षियों को रखा जाता है"},
  {"id": 6, "word": "Contemporary", "meaning": "समकालीन", "explanation": "एक ही समय के लोग या चीजें"},
  {"id": 7, "word": "Stoic", "meaning": "उदासीन / वैरागी", "explanation": "जो सुख-दुख में एक जैसा रहे और भावनाओं पर नियंत्रण रखे"},
  {"id": 8, "word": "Atheist", "meaning": "नास्तिक", "explanation": "जो भगवान पर विश्वास नहीं करता"},
  {"id": 9, "word": "Cartographer", "meaning": "मानचित्रकार", "explanation": "जो नक्शे यानी मैप्स बनाता है"},
  {"id": 10, "word": "Claustrophobia", "meaning": "बंद या छोटी जगहों से लगने वाला डर", "explanation": "सीमित या बंद स्थानों का अत्यधिक भय"},
  {"id": 11, "word": "Omniscient", "meaning": "सर्वज्ञानी", "explanation": "जिसे सब कुछ पता हो"},
  {"id": 12, "word": "Panacea", "meaning": "रामबाण इलाज", "explanation": "हर समस्या या बीमारी का एक ही इलाज"},
  {"id": 13, "word": "Polyglot", "meaning": "बहुभाषी", "explanation": "जो कई भाषाएं बोल सकता हो"},
  {"id": 14, "word": "Chronology", "meaning": "कालक्रम", "explanation": "घटनाओं को समय के सही क्रम में व्यवस्थित करना"},
  {"id": 15, "word": "Extempore", "meaning": "बिना तैयारी का भाषण", "explanation": "बिना किसी पूर्व तैयारी के तुरंत बोलना"},
  {"id": 16, "word": "Fastidious", "meaning": "तुनकमिज़ाज / जिसे खुश करना मुश्किल हो", "explanation": "जो छोटी-छोटी डिटेल्स पर ध्यान देता है"},
  {"id": 17, "word": "Utopia", "meaning": "आदर्श लोक", "explanation": "सपनों की एक आदर्श और परफेक्ट दुनिया"},
  {"id": 18, "word": "Amateur", "meaning": "शौकिया / नौसिखिया", "explanation": "जो किसी काम को प्रोफेशन के लिए नहीं बल्कि शौक के लिए करता है या एक्सपर्ट नहीं है"},
  {"id": 19, "word": "Ambidextrous", "meaning": "दोनों हाथों से काम करने में कुशल", "explanation": "जो दोनों हाथों का बराबर इस्तेमाल कर सके"},
  {"id": 20, "word": "Iconoclast", "meaning": "मूर्तिभंजक / स्थापित परंपराओं को तोड़ने वाला", "explanation": "जो पुरानी सोच या ट्रेडिशंस को चुनौती दे"},
  {"id": 21, "word": "Infallible", "meaning": "अचूक", "explanation": "जिससे कभी कोई गलती न हो"},
  {"id": 22, "word": "Altruist", "meaning": "परोपकारी / निस्वार्थ", "explanation": "जो अपने से ज्यादा दूसरों की भलाई के बारे में सोचे"},
  {"id": 23, "word": "Inaudible", "meaning": "जो सुनाई न दे", "explanation": "अश्रव्य"},
  {"id": 24, "word": "Lexicographer", "meaning": "शब्दकोश बनाने वाला", "explanation": "जो डिक्शनरी लिखता या कंपाइल करता है"},
  {"id": 25, "word": "Mercenary", "meaning": "किराये का सैनिक / स्वार्थी", "explanation": "जो सिर्फ पैसे के लिए काम करता हो"},
  {"id": 26, "word": "Misanthrope", "meaning": "मानव-द्वेषी", "explanation": "जो इंसानों या मानव जाति से नफ़रत करता हो"},
  {"id": 27, "word": "Nostalgia", "meaning": "अतीत की यादें / पुरानी यादों के लिए तड़प", "explanation": "पुरानी सुखद यादों को याद करने की मानसिक स्थिति"},
  {"id": 28, "word": "Amphibian", "meaning": "उभयचर", "explanation": "जो पानी और जमीन दोनों पर रह सकते हैं, जैसे मेंढक"},
  {"id": 29, "word": "Autobiography", "meaning": "आत्मकथा", "explanation": "खुद के द्वारा लिखी गई अपने जीवन की कहानी"},
  {"id": 30, "word": "Cannibal", "meaning": "नरभक्षी", "explanation": "जो इंसान का मांस खाता हो या अपनी ही प्रजाति को खाता हो"},
  {"id": 31, "word": "Chauffeur", "meaning": "निजी कार चालक", "explanation": "किसी अमीर व्यक्ति या लग्जरी कार का परमानेंट ड्राइवर"},
  {"id": 32, "word": "Entomology", "meaning": "कीटविज्ञान", "explanation": "कीड़े-मकौड़ों का अध्ययन"},
  {"id": 33, "word": "Insolvent", "meaning": "दिवालिया", "explanation": "जो अपना कर्ज चुकाने में असमर्थ हो"},
  {"id": 34, "word": "Kleptomania", "meaning": "चोरी करने की बीमारी / आदत", "explanation": "बिना जरूरत के भी चीजें चुराने की तीव्र इच्छा"},
  {"id": 35, "word": "Oligarchy", "meaning": "कुलीनतंत्र", "explanation": "कुछ शक्तिशाली या खास लोगों का शासन"},
  {"id": 36, "word": "Omnipotent", "meaning": "सर्वशक्तिमान", "explanation": "जिसके पास सारी शक्तियां हों"},
  {"id": 37, "word": "Philatelist", "meaning": "डाक टिकट बटोरने वाला", "explanation": "जिसे स्टैम्प्स कलेक्ट करने का शौक हो"},
  {"id": 38, "word": "Teetotaler", "meaning": "मद्यत्यागी", "explanation": "जो कभी भी अल्कोहल या शराब नहीं पीता"},
  {"id": 39, "word": "Versatile", "meaning": "बहुमुखी प्रतिभा का धनी", "explanation": "मल्टीटैलेंटेड इंसान जिसके पास कई तरह के हुनर हों"},
  {"id": 40, "word": "Anarchist", "meaning": "अराजकतावादी", "explanation": "जो किसी भी सरकार या नियम-कानून को नहीं मानता"},
  {"id": 41, "word": "Calligraphy", "meaning": "सुलेखन", "explanation": "सुंदर लिखावट या ब्यूटीफुल हैंडराइटिंग की कला"},
  {"id": 42, "word": "Constellation", "meaning": "नक्षत्र / तारागण", "explanation": "तारों का समूह जो एक निश्चित आकृति बनाता है"},
  {"id": 43, "word": "Gregarious", "meaning": "झुंड में रहने वाला / सामाजिक", "explanation": "जो समूह या गैंग में रहना पसंद करते हैं"},
  {"id": 44, "word": "Introvert", "meaning": "अंतर्मुखी", "explanation": "जो अकेले रहना पसंद करता है और ज्यादा सामाजिक नहीं होता"},
  {"id": 45, "word": "Orchard", "meaning": "फलों का बाग", "explanation": "जहाँ फलों के पेड़ उगाए जाते हैं"}
]

WORDS_BY_ID = {item["id"]: item for item in WORDS_DATA}

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
        welcome_text += "\n\n👑 <b>Admin Control Active:</b>\n- Ek word jodne ke liye: <code>/add Word | Meaning</code>\n- Ek sath bohot saare words jodne ke liye <code>/bulkadd</code> likhein fir agli line se list paste karein."
        
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

# 👑 1. Single word add karne ki command
async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = " ".join(context.args)
    if not text or "|" not in text:
        await update.message.reply_text("⚠️ Format: <code>/add Word | Meaning | Explanation</code>", parse_mode=ParseMode.HTML)
        return
    try:
        parts = text.split("|")
        word = parts[0].strip()
        meaning = parts[1].strip()
        explanation = parts[2].strip() if len(parts) > 2 else "Koi detail nahi hai."
        
        if word and meaning:
            next_id = len(WORDS_DATA)
            WORDS_DATA.append({"id": next_id, "word": word, "meaning": meaning, "explanation": explanation})
            refresh_words_map()
            await update.message.reply_text(f"✅ Added: <b>{escape(word)}</b> (Total: {len(WORDS_DATA)})", parse_mode=ParseMode.HTML)
    except Exception:
        await update.message.reply_text("❌ Error adding word.")

# 👑 2. Ek sath unlimited words jodne ki command (Bulk Add)
async def bulk_add_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    # Message se /bulkadd command ko hatana
    text = update.message.text.replace('/bulkadd', '').strip()
    if not text:
        await update.message.reply_text("⚠️ <b>Format Khali Hai!</b>\n\nCommand aise chalayein:\n<code>/bulkadd\nWord1 | Meaning1\nWord2 | Meaning2</code>", parse_mode=ParseMode.HTML)
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
            explanation = parts[2].strip() if len(parts) > 2 else "Koi detail nahi hai."

            if word and meaning:
                next_id = len(WORDS_DATA)
                WORDS_DATA.append({"id": next_id, "word": word, "meaning": meaning, "explanation": explanation})
                added_count += 1
        except Exception:
            continue

    if added_count > 0:
        refresh_words_map()
        await update.message.reply_text(f"🚀 <b>Balle Balle!</b> Ek sath <b>{added_count}</b> naye words successfully jud gaye!\n📚 Total Words: <b>{len(WORDS_DATA)}</b>")
    else:
        await update.message.reply_text("❌ Koi valid words nahi mile format me.")

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message or update.callback_query.message
    if not WORDS_DATA:
        await target.reply_text("⚠️ Bot me koi words nahi hain.")
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
        await query.answer("⚠️ Aap is sawal ka jawab pehle hi de chuke hain!")
        return
    context.user_data["current_question_answered"] = True
    await query.answer()
    
    target_item = WORDS_BY_ID.get(word_id)
    if not target_item:
        await query.edit_message_text("⚠️ Data nahi mila.")
        return
    correct_word = escape(target_item["word"])
    correct_meaning = escape(target_item["meaning"])
    explanation = escape(target_item.get("explanation") or "No details.")
    
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
    except Exception:
        pass
    await send_quiz_question(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("add", add_word))
    application.add_handler(CommandHandler("bulkadd", bulk_add_words)) # Bulk add command registered
    application.add_handler(CallbackQueryHandler(next_word_handler, pattern="^next_question$"))
    application.add_handler(CallbackQueryHandler(button_click, pattern=r"^ans|"))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
