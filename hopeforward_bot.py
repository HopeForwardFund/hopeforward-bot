import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, PreCheckoutQueryHandler, filters, ContextTypes
 
# =============================================

TOKEN = "8889945966:AAEzDqu0OpKq71w1NHczLUvUb5541nxXqsI"  # токен от @BotFather
# =============================================
 
logging.basicConfig(level=logging.INFO)
 
TEXTS = {
    'en': {
        'welcome': "❤️ *Welcome to HopeForward Fund*\n\n🌍 We deliver food, medicine and education to people in need around the world.\n\n100% of every donation reaches those who need it most.\n\n*Choose your donation amount:*",
        'choose': "Choose amount:",
        'custom': "✏️ Enter custom amount",
        'custom_ask': "💬 Enter your amount in Stars (e.g. 50):",
        'pay': "💛 Donate {} ⭐ Now",
        'thanks': "🙏 *Thank you for your kindness!*\n\nYour donation of {} ⭐ will make a real difference.\n\n*Together, we can make a difference* ❤️",
        'impact': {
            50: "🍽️ Feeds a child for a day",
            100: "📚 School supplies",
            250: "💊 Week of medicine",
            500: "🧥 Winter clothing",
            1000: "📦 Emergency food kit",
            2500: "🌟 Month of support"
        },
        'select_lang': "🌍 Choose language / Выберите язык / اختر اللغة",
    },
    'ru': {
        'welcome': "❤️ *Добро пожаловать в HopeForward Fund*\n\n🌍 Мы доставляем еду, лекарства и образование нуждающимся по всему миру.\n\n100% каждого пожертвования доходит до тех, кто в этом нуждается.\n\n*Выберите сумму пожертвования:*",
        'choose': "Выберите сумму:",
        'custom': "✏️ Введите свою сумму",
        'custom_ask': "💬 Введите сумму в Stars (например 50):",
        'pay': "💛 Пожертвовать {} ⭐",
        'thanks': "🙏 *Спасибо за вашу доброту!*\n\nВаше пожертвование {} ⭐ изменит чью-то жизнь.\n\n*Вместе мы можем изменить мир* ❤️",
        'impact': {
            50: "🍽️ Еда для ребёнка на день",
            100: "📚 Школьные принадлежности",
            250: "💊 Лекарства на неделю",
            500: "🧥 Зимняя одежда",
            1000: "📦 Набор продуктов",
            2500: "🌟 Месяц поддержки"
        },
        'select_lang': "🌍 Choose language / Выберите язык / اختر اللغة",
    },
    'ar': {
        'welcome': "❤️ *مرحباً بك في HopeForward Fund*\n\n🌍 نوصل الغذاء والدواء والتعليم للمحتاجين حول العالم.\n\n100% من تبرعك يصل مباشرة لمن يحتاجه.\n\n*اختر مبلغ تبرعك:*",
        'choose': "اختر المبلغ:",
        'custom': "✏️ أدخل مبلغاً آخر",
        'custom_ask': "💬 أدخل المبلغ بالنجوم (مثال: 50):",
        'pay': "💛 تبرع بـ {} ⭐",
        'thanks': "🙏 *شكراً لك على كرمك!*\n\nتبرعك بـ {} ⭐ سيحدث فرقاً حقيقياً.\n\n*معاً يمكننا صنع الفارق* ❤️",
        'impact': {
            50: "🍽️ طعام طفل ليوم",
            100: "📚 مستلزمات مدرسية",
            250: "💊 دواء لأسبوع",
            500: "🧥 ملابس شتوية",
            1000: "📦 طرد غذائي طارئ",
            2500: "🌟 شهر من الدعم"
        },
        'select_lang': "🌍 Choose language / Выберите язык / اختر اللغة",
    }
}
 
user_langs = {}
user_states = {}
 
def get_lang(user_id):
    return user_langs.get(user_id, 'en')
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    await update.message.reply_text(
        TEXTS['en']['select_lang'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
 
async def show_donation_menu(update, user_id, lang):
    t = TEXTS[lang]
    amounts = [50, 100, 250, 500, 1000, 2500]
    keyboard = []
    row = []
    for i, amt in enumerate(amounts):
        impact = t['impact'][amt]
        btn = InlineKeyboardButton(f"{amt}⭐ — {impact}", callback_data=f"amount_{amt}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(t['custom'], callback_data="custom")])
    keyboard.append([InlineKeyboardButton("🌍 Language", callback_data="change_lang")])
 
    if update.callback_query:
        await update.callback_query.message.reply_text(
            t['welcome'],
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            t['welcome'],
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
 
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
 
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_langs[user_id] = lang
        await show_donation_menu(update, user_id, lang)
 
    elif data == "change_lang":
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
             InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
        ]
        await query.message.reply_text(
            TEXTS['en']['select_lang'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
 
    elif data.startswith("amount_"):
        amount = int(data.split("_")[1])
        lang = get_lang(user_id)
        t = TEXTS[lang]
        keyboard = [
            [InlineKeyboardButton(t['pay'].format(amount), callback_data=f"pay_{amount}")],
            [InlineKeyboardButton("◀️ Back", callback_data=f"lang_{lang}")]
        ]
        impact = t['impact'].get(amount, "")
        await query.message.reply_text(
            f"✅ *{amount} ⭐* — {impact}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
 
    elif data.startswith("pay_"):
        amount = int(data.split("_")[1])
        lang = get_lang(user_id)
        t = TEXTS[lang]
        await context.bot.send_invoice(
            chat_id=user_id,
            title="HopeForward Fund — Donation",
            description=t['impact'].get(amount, f"Donation of {amount} Stars"),
            payload=f"donate_{amount}",
            currency="XTR",  # Telegram Stars
            prices=[LabeledPrice(label="Donation", amount=amount)]
        )
 
    elif data == "custom":
        lang = get_lang(user_id)
        user_states[user_id] = "awaiting_custom"
        await query.message.reply_text(TEXTS[lang]['custom_ask'])
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_states.get(user_id) == "awaiting_custom":
        try:
            amount = int(update.message.text.strip())
            if amount < 1:
                raise ValueError
            user_states.pop(user_id)
            lang = get_lang(user_id)
            t = TEXTS[lang]
            keyboard = [[InlineKeyboardButton(t['pay'].format(amount), callback_data=f"pay_{amount}")]]
            await update.message.reply_text(
                f"✅ *{amount} ⭐*",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await update.message.reply_text("❌ Введите число (например 50)")
 
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)
 
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    amount = update.message.successful_payment.total_amount
    await update.message.reply_text(
        TEXTS[lang]['thanks'].format(amount),
        parse_mode='Markdown'
    )
 
def main():
    if TOKEN == "ВСТАВЬТЕ_ТОКЕН_БОТА_СЮДА":
        print("❌ Вставьте токен бота в переменную TOKEN!")
        return
 
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ HopeForward Fund Bot запущен!")
    app.run_polling()
 
if __name__ == "__main__":
    main()
