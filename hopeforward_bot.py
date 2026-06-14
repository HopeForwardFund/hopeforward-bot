import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8889945966:AAEzDqu0OpKq71w1NHczLUvUb5541nxXqsI"
USDT_WALLET = "0x50E668eD4bb31F785404304E858205d0B93a4De3"
USDT_NETWORK = "ERC20 (Ethereum)"

logging.basicConfig(level=logging.INFO)

TEXTS = {
    'en': {
        'welcome': "❤️ *Welcome to HopeForward Fund*\n\n🌍 We deliver food, medicine and education to people in need around the world.\n\n100% of every donation reaches those who need it most.\n\n*Choose your donation amount:*",
        'custom': "✏️ Enter custom amount",
        'custom_ask': "💬 Enter your amount in USD (e.g. 15):",
        'payment_info': "💛 *Donate ${amount}*\n\n📋 *Send USDT to this address:*\n\n`{wallet}`\n\n🌐 *Network:* {network}\n\n⚠️ Send only USDT ERC20 to this address!\n\nAfter sending, your donation will reach those in need. Thank you! 🙏",
        'impacts': ["Meal for a child","School supplies","Week of medicine","Winter clothing","Emergency food kit","Month of support"],
        'select_lang': "🌍 Choose language / Выберите язык / اختر اللغة",
        'copied': "✅ Address copied! Send USDT and help change lives ❤️",
        'globe': "🌍 Accepted from anywhere in the world"
    },
    'ru': {
        'welcome': "❤️ *Добро пожаловать в HopeForward Fund*\n\n🌍 Мы доставляем еду, лекарства и образование нуждающимся по всему миру.\n\n100% каждого пожертвования доходит до тех, кто нуждается.\n\n*Выберите сумму пожертвования:*",
        'custom': "✏️ Введите свою сумму",
        'custom_ask': "💬 Введите сумму в долларах (например 15):",
        'payment_info': "💛 *Пожертвовать ${amount}*\n\n📋 *Отправьте USDT на этот адрес:*\n\n`{wallet}`\n\n🌐 *Сеть:* {network}\n\n⚠️ Отправляйте только USDT ERC20 на этот адрес!\n\nПосле отправки ваше пожертвование дойдёт до нуждающихся. Спасибо! 🙏",
        'impacts': ["Еда для ребёнка","Школьные принадлежности","Лекарства на неделю","Зимняя одежда","Набор продуктов","Месяц поддержки"],
        'select_lang': "🌍 Choose language / Выберите язык / اختر اللغة",
        'copied': "✅ Адрес скопирован! Отправьте USDT и помогите изменить жизни ❤️",
        'globe': "🌍 Принимаем пожертвования со всего мира"
    },
    'ar': {
        'welcome': "❤️ *مرحباً بك في HopeForward Fund*\n\n🌍 نوصل الغذاء والدواء والتعليم للمحتاجين حول العالم.\n\n100% من تبرعك يصل مباشرة لمن يحتاجه.\n\n*اختر مبلغ تبرعك:*",
        'custom': "✏️ أدخل مبلغاً آخر",
        'custom_ask': "💬 أدخل المبلغ بالدولار (مثال: 15):",
        'payment_info': "💛 *تبرع بـ ${amount}*\n\n📋 *أرسل USDT إلى هذا العنوان:*\n\n`{wallet}`\n\n🌐 *الشبكة:* {network}\n\n⚠️ أرسل USDT ERC20 فقط إلى هذا العنوان!\n\nبعد الإرسال، سيصل تبرعك إلى المحتاجين. شكراً! 🙏",
        'impacts': ["طعام طفل","مستلزمات مدرسية","دواء لأسبوع","ملابس شتوية","طرد غذائي","شهر من الدعم"],
        'select_lang': "🌍 Choose language / Выберите язык / اختر اللغة",
        'copied': "✅ تم نسخ العنوان! أرسل USDT وساعد في تغيير الحياة ❤️",
        'globe': "🌍 نقبل التبرعات من جميع أنحاء العالم"
    }
}

AMOUNTS = [5, 10, 25, 50, 100, 250]
user_langs = {}
user_states = {}

def get_lang(user_id):
    return user_langs.get(user_id, 'en')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
    ]]
    await update.message.reply_text(
        TEXTS['en']['select_lang'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_menu(update, user_id, lang):
    t = TEXTS[lang]
    impacts = t['impacts']
    keyboard = []
    row = []
    for i, amt in enumerate(AMOUNTS):
        btn = InlineKeyboardButton(f"${amt} — {impacts[i]}", callback_data=f"amount_{amt}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton(t['custom'], callback_data="custom")])
    keyboard.append([InlineKeyboardButton("🌍 Language", callback_data="change_lang")])

    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text(t['welcome'], parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_payment(update, amount, lang):
    t = TEXTS[lang]
    text = t['payment_info'].format(amount=amount, wallet=USDT_WALLET, network=USDT_NETWORK)
    keyboard = [
        [InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_{amount}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f"lang_{lang}")]
    ]
    await update.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_langs[user_id] = lang
        await show_menu(update, user_id, lang)

    elif data == "change_lang":
        keyboard = [[
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
        ]]
        await query.message.reply_text(TEXTS['en']['select_lang'], reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("amount_"):
        amount = int(data.split("_")[1])
        lang = get_lang(user_id)
        await show_payment(update, amount, lang)

    elif data.startswith("copy_"):
        amount = data.split("_")[1]
        lang = get_lang(user_id)
        await query.message.reply_text(
            f"`{USDT_WALLET}`\n\n{TEXTS[lang]['copied']}",
            parse_mode='Markdown'
        )

    elif data == "custom":
        lang = get_lang(user_id)
        user_states[user_id] = "awaiting_custom"
        await query.message.reply_text(TEXTS[lang]['custom_ask'])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_states.get(user_id) == "awaiting_custom":
        try:
            amount = float(update.message.text.strip())
            if amount < 1:
                raise ValueError
            user_states.pop(user_id)
            lang = get_lang(user_id)
            t = TEXTS[lang]
            text = t['payment_info'].format(amount=amount, wallet=USDT_WALLET, network=USDT_NETWORK)
            keyboard = [
                [InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_{amount}")],
                [InlineKeyboardButton("◀️ Back", callback_data=f"lang_{lang}")]
            ]
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await update.message.reply_text("❌ Please enter a valid number (e.g. 15)")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ HopeForward Bot running with USDT payments!")
    app.run_polling()

if __name__ == "__main__":
    main()
