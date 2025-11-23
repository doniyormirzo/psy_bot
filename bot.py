import telebot
from telebot import types
server = Flask(psy bot)
# =========================
#  SOZLAMALAR
# =========================

API_TOKEN = "8436935672:AAGc_mYCtMHuJ81hS2miBoSpx0ttZf9nHkU"  # psixolog-bot tokeni
ADMIN_ID = 6117354188  # Sizning Telegram ID'ingiz

# Mijoz yozishi uchun profil va ijtimoiy tarmoqlar
TELEGRAM_PROFILE_URL = "https://t.me/mirzavaliyev"
INSTAGRAM_URL = "https://instagram.com/doniyor__mirzo"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# =========================
#  HOLATLAR
# =========================

STATE_NAME = "name"
STATE_CATEGORY = "category"
STATE_TEST = "test"
STATE_PROBLEM = "problem"
STATE_PHONE_CHOICE = "phone_choice"
STATE_PHONE_TEXT = "phone_text"
STATE_SESSION_TYPE = "session_type"
STATE_TIME_SLOT = "time_slot"
STATE_TIME_CUSTOM = "time_custom"

# Foydalanuvchi ma'lumotlari
# chat_id -> dict
user_data = {}


def init_user(chat_id: int):
    user_data[chat_id] = {
        "state": None,
        "name": None,
        "category": None,
        "test": None,          # {"key", "index", "answers", "score", "level"}
        "problem": None,
        "phone": None,
        "session_type": None,  # "individual" / "group"
        "time_slot": None,
    }


def set_state(chat_id: int, state: str):
    if chat_id not in user_data:
        init_user(chat_id)
    user_data[chat_id]["state"] = state


def get_state(chat_id: int):
    if chat_id not in user_data:
        init_user(chat_id)
    return user_data[chat_id]["state"]


# =========================
#  KATEGORIYALAR VA TESTLAR
# =========================

LIKERT_OPTIONS = [
    "1. Umuman to‘g‘ri kelmaydi",
    "2. Ba’zan bo‘ladi",
    "3. Tez-tez shunday bo‘ladi",
    "4. Juda tez-tez / deyarli doim",
]

# Har bir kategoriya uchun 5 ta diagnostika savoli, qo'llab-quvvatlash va mashqlar
CATEGORY_TESTS = {
    "Depressiya": {
        "key": "depressiya",
        "questions": [
            "So‘nggi haftalarda kayfiyatingiz ko‘pincha tushkun va zerikarli bo‘lib qolganini his qilasizmi?",
            "Oldin yoqimli bo‘lgan mashg‘ulotlar hozir sizga qiziq va zavqli tuyulmayaptimi?",
            "Odatdagidan ko‘ra tez-tez charchoq, holsizlik sezayotgan bo‘lsangiz, bu sizga tanishmi?",
            "Kelajak haqida o‘ylaganingizda umidsizlik yoki qo‘rquv his qilasizmi?",
            "O‘zingizni boshqa odamlardan yomonroq, arzimasroq deb his qiladigan paytlaringiz bo‘ladimi?",
        ],
        "support": (
            "Siz his qilayotgan og‘ir kayfiyat va charchoq — ko‘p insonlar boshidan o‘tkazadigan holat. "
            "Bu sizning zaifligingiz emas, balki yordamga muhtoj bo‘lganingizni ko‘rsatadigan signal. "
            "Siz bu holatda yolg‘iz emassiz va men sizni tushunishga va qo‘llab-quvvatlashga tayyorman."
        ),
        "exercise": (
            "🔹 Mashq 1: Har kuni kechqurun kamida 3 ta 'minnatdorchilik sababini' yozing "
            "(bugun nimadan mamnun bo‘ldingiz?).\n"
            "🔹 Mashq 2: Kun davomida 10–15 daqiqa sekin yurib, nafasga e’tibor qaratgan holda sayr qiling. "
            "Telefonni olib yurmaslikka harakat qiling.\n"
        ),
    },
    "Stress": {
        "key": "stress",
        "questions": [
            "Oxirgi vaqtlarda tanangizda taranglik (bo‘yin, yelka, bel) tez-tez seziladimi?",
            "Uyqusizlik yoki uyqu sifatining yomonlashishi sizni bezovta qiladimi?",
            "Kun davomida vazifalarni ulgurmayapman degan ichki shoshilish holati bo‘ladimi?",
            "Asabiylashish, tez jahli chiqish holatlari kuchayganini sezayapsizmi?",
            "Dam olayotganingizda ham ish, o‘qish yoki muammolar haqida o‘ylashni to‘xtata olmay qolgan paytlar bo‘ladimi?",
        ],
        "support": (
            "Stress — organizmning zo‘riqishga javobi. U butunlay yomon narsa emas, "
            "lekin uzoq davom etsa ruhiy va jismoniy salomatlikka ta’sir qilishi mumkin. "
            "Siz hozir aynan shu holatni tartibga keltirish yo‘lida birinchi qadamni qo‘ydingiz."
        ),
        "exercise": (
            "🔹 Mashq 1: '4-7-8' nafas mashqi — 4 soniyada nafas oling, 7 soniya ushlab turing, "
            "8 soniyada asta chiqarib yuboring. Buni 5–7 marotaba takrorlang.\n"
            "🔹 Mashq 2: Vazifalaringizni 3 guruhga bo‘ling: 'Bugun', 'Bu hafta', 'Keyinroq'. "
            "Hammasini birdan qilish shart emasligini o‘zingizga eslating.\n"
        ),
    },
    "Oilaviy muammo": {
        "key": "oilaviy",
        "questions": [
            "Oilada so‘nggi paytlarda tushunmovchiliklar tez-tez sodir bo‘ladimi?",
            "Suhbatlar ko‘pincha janjal yoki ranjish bilan yakunlanadigan holatlar bo‘ladimi?",
            "Oilangizda sizni tinglashmayapti yoki tushunishmayapti degan his bor-mi?",
            "Oilaviy qarorlar ko‘proq bosim yoki majburlik orqali qabul qilinadi deb o‘ylaysizmi?",
            "Uyga qaytayotganda o‘zingizni xotirjam emas, balki bezovta his qiladigan paytlar bo‘ladimi?",
        ],
        "support": (
            "Oilaviy munosabatlar murakkab va nozik jarayon. Muammolar paydo bo‘lishi — "
            "bu oilaning yomonligi emas, balki ehtiyotkorlik va ochiq muloqotga ehtiyoj borligini bildiradi. "
            "Siz bu holatni yaxshilashni xohlayotganingizning o‘zi juda katta qadriyat."
        ),
        "exercise": (
            "🔹 Mashq 1: Oiladagi bir kishiga bugun minnatdorchilik bildiruvchi kichik xabar yoki gap ayting "
            "(hatto kichik narsa uchun bo‘lsa ham).\n"
            "🔹 Mashq 2: Kelgusidagi suhbatda 'Sen ...' o‘rniga 'Men o‘zimni ... his qilyapman' "
            "degan jumlalarni qo‘llashga harakat qiling.\n"
        ),
    },
    "Kasbga yo'naltirish": {
        "key": "career",
        "questions": [
            "Hozirgi kasb yoki yo‘nalish sizni to‘liq qoniqtirmayotganini his qilasizmi?",
            "Kelajakdagi kasbingiz haqida o‘ylaganda ko‘proq chalkashlik va noaniqlik seziladimi?",
            "O‘zingizning kuchli tomonlaringizni aniq nomlash sizga qiyinmi?",
            "Atrofdagilar fikri kasb tanlashingizga kuchli ta’sir ko‘rsatayotgandek tuyuladimi?",
            "Ish / o‘qish jarayonida 'men o‘z joyimda emasman' degan fikr keladimi?",
        ],
        "support": (
            "Kasb tanlash — hayotimizdagi eng muhim qarorlardan biri. Noaniqlik va ikkilanish "
            "bu jarayonning tabiiy qismidir. Muhimi, siz o‘zingizni yaxshiroq tushunishga va "
            "ongli tanlovga intilmoqdasiz — bu juda muhim qadamdIr."
        ),
        "exercise": (
            "🔹 Mashq 1: Qog‘ozga 3 ustun yozing: 'Nimalarni yaxshi qilaman', 'Nimalar menga yoqadi', "
            "'Qaysi muammolarni hal qilishni xohlayman'. Har biriga kamida 5 tadan yozib chiqing.\n"
            "🔹 Mashq 2: Biror kasb egasi bilan qisqa suhbat tashkil qilishga harakat qiling "
            "(online bo‘lsa ham) va ulardan kundalik ish jarayoni haqida so‘rang.\n"
        ),
    },
    "Ijtimoiy munosabatlar": {
        "key": "social",
        "questions": [
            "Yangi odamlar bilan tanishish sizga qiyin yoki noqulay tuyuladimi?",
            "Jamoat joylarida (guruh, tadbir) gapirishdan oldin kuchli hayajon seziladimi?",
            "Ko‘pincha 'boshqalar meni baholayapti' degan fikr keladimi?",
            "Do‘stlaringizga yoki yaqinlaringizga yordam so‘rab murojaat qilish sizga og‘irmi?",
            "Ba’zan o‘zingizni yolg‘iz yoki hech kim tushunmaydigandek his qilasizmi?",
        ],
        "support": (
            "Ijtimoiy munosabatlarda qiynalish — bu kamchilik emas, shunchaki o‘rganilishi va "
            "rivojlantirilishi mumkin bo‘lgan ko‘nikmalar borligini ko‘rsatadi. "
            "Siz o‘zingizni tushunishga va munosabatlarni yaxshilashga intilayotganingiz juda qadrli."
        ),
        "exercise": (
            "🔹 Mashq 1: Har kuni kamida bitta insonga salom berib, qisqa suhbat boshlashga harakat qiling "
            "(masalan: 'Qalaysiz?', 'Bugun kayfiyatingiz qanday?').\n"
            "🔹 Mashq 2: O‘zingiz haqida 5 ta ijobiy sifat yozing va ularni kun davomida o‘qib chiqing.\n"
        ),
    },
    "Farzand tarbiyasi": {
        "key": "parenting",
        "questions": [
            "Bola(laringiz) bilan muloqot qilganda tez-tez asabiylashib, ovozingizni ko‘tarib yuborasizmi?",
            "Farzandingiz sizni tinglamayotgandek yoki ataylab qarshi qilayotgandek tuyuladimi?",
            "Qanday tarbiya usuli to‘g‘ri ekaniga ko‘p shubhalanasizmi?",
            "Boshqa ota-onalar bilan o‘zingizni taqqoslab, 'men yaxshi ota/ona emasman' degan fikr keladimi?",
            "Farzand bilan sifatli vaqt o‘tkazishga vaqt yoki energiya yetishmasligini sezayapsizmi?",
        ],
        "support": (
            "Farzand tarbiyasi hech kimni 'ideal' darajada bilmaydigan, doimiy o‘rganish jarayoni. "
            "Siz o‘ylayotgan, izlayotgan va savol berayotganingizning o‘zi — mas’uliyatli ota-ona ekaningizni ko‘rsatadi."
        ),
        "exercise": (
            "🔹 Mashq 1: Har kuni farzandingiz bilan kamida 10–15 daqiqa faqat unga bag‘ishlangan "
            "vaqtingiz bo‘lsin (telefon, televizorsiz). Masalan, suhbat, o‘yin yoki kitob o‘qish.\n"
            "🔹 Mashq 2: Bolaga tanbeh berish o‘rniga, bir vaziyatda faqat uning hissiyotini nomlashga "
            "harakat qiling: 'Senga hozir adolatsizdek tuyulyapti, to‘g‘rimi?'.\n"
        ),
    },
    "Bolalar psixologiyasi": {
        "key": "child_psych",
        "questions": [
            "Bolada kayfiyat o‘zgarishlari (tez yig‘lash, jahli chiqish) ko‘payganini sezayapsizmi?",
            "Uxlash, ovqatlanish odatlarida jiddiy o‘zgarishlar bormi?",
            "Bog‘cha yoki maktabga borishdan bosh tortish, kuchli qarshilik holatlari bormi?",
            "Bola tez-tez 'qorqinchli tush' ko‘rishi yoki turli qo‘rquvlar haqida gapiradimi?",
            "Bolangiz bilan hissiy yaqinlik (ochiq suhbat, ishonch) yetarli emasdek tuyuladimi?",
        ],
        "support": (
            "Bolalar hissiyotini tushunish va izohlash har doim ham oson emas. "
            "Sizning farzandingiz holatiga e’tibor qaratayotganingiz va yordam izlayotganingiz — "
            "unda sog‘lom rivojlanish uchun juda katta imkoniyat yaratadi."
        ),
        "exercise": (
            "🔹 Mashq 1: Bolaga har kuni 'Bugun seni nimadan xursand bo‘ldi?' va "
            "'Nimadan xafa bo‘lding?' degan ikki savolni bering.\n"
            "🔹 Mashq 2: Bolaning hissiyotini rasm orqali ifoda etishni taklif qiling "
            "('Kayfiyatingni chizib ko‘rsat'). Rasm orqali suhbatlashishga harakat qiling.\n"
        ),
    },
    "Moliyaviy muammolar": {
        "key": "finance",
        "questions": [
            "Pul masalasi haqida o‘ylaganda kuchli bezovtalik yoki qo‘rquv seziladimi?",
            "Oxirgi oylar davomida xarajatlar va daromadlarni nazorat qilish qiyinlashdimi?",
            "Pul yetmay qolganda o‘zingizni ayblash yoki uyalish holatlari bo‘ladimi?",
            "Moliyaviy qarorlarni ko‘pincha shoshilinch yoki hissiyot bilan qabul qilasizmi?",
            "Moliyaviy rejangiz (yaqin 3–6 oy uchun) aniq emasdek tuyuladimi?",
        ],
        "support": (
            "Moliyaviy qiyinchiliklar ko‘p insonlar hayotida uchraydi va bu faqat iqtisodiy emas, "
            "balki hissiy zo‘riqishni ham keltirib chiqaradi. Siz bu haqida o‘ylayotganingiz va yordam so‘rayotganingiz "
            "– vaziyatni barqarorlashtirish yo‘lida muhim qadam."
        ),
        "exercise": (
            "🔹 Mashq 1: Bir hafta davomida hamma xarajatlaringizni yozib boring. "
            "Faqat kuzatish, o‘zingizni ayblamasdan.\n"
            "🔹 Mashq 2: 'Majburiy', 'Muhim', 'Keyinroq bo‘lsa bo‘ladi' degan 3 toifaga xarajatlarni ajratib chiqing.\n"
        ),
    },
    "Boshqa": {
        "key": "other",
        "questions": [
            "Sizni bezovta qilayotgan muammo aniq nomlash qiyin bo‘lgandek tuyuladimi?",
            "Kayfiyat, motivatsiya yoki munosabatlaringizda 'nimadir joyida emas' degan umumiy his bormi?",
            "Ba’zan tushuntirib bo‘lmaydigan ichki bo‘shlik yoki ma’nosizlik hissi bo‘ladimi?",
            "O‘zingizni tushuntirishga harakat qilganingizda, boshqalar unchalik tushunmaydigandek ko‘rinyaptimi?",
            "Yordam so‘rash sizga biroz qiyin, lekin hozir bu qadamni baribir qilayotgan bo‘lsangiz, bu sizga tanishmi?",
        ],
        "support": (
            "Ba’zan muammoni aniq nomlashning o‘zi ham qiyin bo‘ladi. "
            "Bu sizning holatingiz 'to‘g‘ri emas' degani emas — shunchaki chuqurroq tushunishga ehtiyoj borligini bildiradi. "
            "Biz suhbat davomida bu holatni birgalikda aniqlashtira olamiz."
        ),
        "exercise": (
            "🔹 Mashq 1: Qog‘ozga 'Meni hozir eng ko‘p bezovta qilayotgan 3 narsa' deb yozing va ularni tartiblang.\n"
            "🔹 Mashq 2: Har kuni 10 daqiqa vaqtni faqat o‘zingizga ajrating "
            "(telefon va chalg‘ituvchi narsalarsiz) va kayfiyatingizni yozib boring.\n"
        ),
    },
}

CATEGORIES_ORDER = list(CATEGORY_TESTS.keys())


def build_main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚀 Boshlash")
    return kb


def build_category_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Depressiya", "Stress")
    kb.row("Oilaviy muammo", "Kasbga yo'naltirish")
    kb.row("Ijtimoiy munosabatlar", "Farzand tarbiyasi")
    kb.row("Bolalar psixologiyasi", "Moliyaviy muammolar")
    kb.add("Boshqa")
    return kb


def build_likert_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(LIKERT_OPTIONS[0])
    kb.row(LIKERT_OPTIONS[1])
    kb.row(LIKERT_OPTIONS[2])
    kb.row(LIKERT_OPTIONS[3])
    return kb


def build_session_type_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row("👤 Individual seans", "👥 Jamoaviy (guruh) seans")
    return kb


def build_time_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row("⏰ Kunduzgi 10:00–12:00")
    kb.row("🌙 Kechki 20:00–22:00")
    kb.add("📝 O‘zimga qulay vaqtni yozaman")
    return kb


# =========================
#  /start HANDLER
# =========================

@bot.message_handler(commands=["start"])
def start_handler(message: types.Message):
    chat_id = message.chat.id
    init_user(chat_id)

    intro = (
        "Assalomu alaykum!\n\n"
        "<b>Men Doniyorbek Mirzavaliyev – amaliy psixolog.</b>\n"
        "Bu bot orqali siz o‘zingizni xavfsiz va hurmatga asoslangan onlayn makonda his qilishingiz mumkin.\n\n"
        "Men quyidagi yo‘nalishlarda ishlayman:\n"
        "• kayfiyat pasayishi, depressiya, tashvishlar\n"
        "• stress va charchoq\n"
        "• oilaviy va munosabatlardagi qiyinchiliklar\n"
        "• farzand tarbiyasi va bolalar psixologiyasi\n"
        "• kasb tanlash, o‘zini anglash\n"
        "• moliyaviy qiyinchiliklarga ruhiy moslashish va boshqalar.\n\n"
        "Eslatma: bu bot — dastlabki psixologik qo‘llab-quvvatlash va diagnostika uchun. "
        "To‘liq seanslar esa jonli muloqotda, Telegram orqali o‘tkaziladi.\n\n"
        "Tayyor bo‘lsangiz, pastdagi tugmani bosing."
    )

    bot.send_message(chat_id, intro, reply_markup=build_main_menu())
    set_state(chat_id, STATE_NAME)


# =========================
#  TEXT HANDLER
# =========================

@bot.message_handler(content_types=["text"])
def text_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = get_state(chat_id)

    if text == "/start":
        start_handler(message)
        return

    if state == STATE_NAME:
        handle_name(message, text)
    elif state == STATE_CATEGORY:
        handle_category(message, text)
    elif state == STATE_TEST:
        handle_test_answer(message, text)
    elif state == STATE_PROBLEM:
        handle_problem(message, text)
    elif state == STATE_PHONE_CHOICE:
        handle_phone_choice(message, text)
    elif state == STATE_PHONE_TEXT:
        handle_phone_text(message, text)
    elif state == STATE_SESSION_TYPE:
        handle_session_type(message, text)
    elif state == STATE_TIME_SLOT:
        handle_time_slot(message, text)
    elif state == STATE_TIME_CUSTOM:
        handle_time_custom(message, text)
    else:
        bot.send_message(chat_id, "Iltimos, /start ni bosib suhbatni qaytadan boshlang.")


# =========================
#  1-BOSQICH: ISM
# =========================

def handle_name(message: types.Message, text: str):
    chat_id = message.chat.id

    if text == "🚀 Boshlash":
        bot.send_message(chat_id, "Sizni tanishib olishdan boshlaymiz.\n\nIsmingizni yozing:")
        return

    user_data[chat_id]["name"] = text

    bot.send_message(
        chat_id,
        f"Rahmat, {text}.\n\n"
        "Endi sizni qaysi yo‘nalish ko‘proq bezovta qilayotganini tanlang.",
        reply_markup=build_category_keyboard(),
    )
    set_state(chat_id, STATE_CATEGORY)


# =========================
#  2-BOSQICH: KATEGORIYA
# =========================

def handle_category(message: types.Message, text: str):
    chat_id = message.chat.id

    if text not in CATEGORIES_ORDER:
        bot.send_message(chat_id, "Iltimos, pastdagi tugmalardan birini tanlang.")
        return

    cat_info = CATEGORY_TESTS[text]
    user_data[chat_id]["category"] = text
    user_data[chat_id]["test"] = {
        "key": cat_info["key"],
        "index": 0,
        "answers": [],
        "score": 0,
        "level": None,
    }

    bot.send_message(
        chat_id,
        "Avval qisqa diagnostika o‘tkazamiz.\n"
        "Har bir savolga o‘zingizga eng yaqin variantni tanlang.",
        reply_markup=build_likert_keyboard(),
    )

    send_next_test_question(chat_id)
    set_state(chat_id, STATE_TEST)


def send_next_test_question(chat_id: int):
    data = user_data[chat_id]
    cat_title = data["category"]
    test = data["test"]
    idx = test["index"]
    questions = CATEGORY_TESTS[cat_title]["questions"]

    if idx >= len(questions):
        finish_test(chat_id)
        return

    question_text = f"Savol {idx + 1} / {len(questions)}:\n{questions[idx]}"
    bot.send_message(chat_id, question_text, reply_markup=build_likert_keyboard())


def handle_test_answer(message: types.Message, text: str):
    chat_id = message.chat.id
    data = user_data[chat_id]
    test = data["test"]

    if text not in LIKERT_OPTIONS:
        bot.send_message(chat_id, "Iltimos, pastdagi javoblardan birini tanlang.")
        return

    score = LIKERT_OPTIONS.index(text) + 1  # 1 dan 4 gacha
    test["answers"].append(text)
    test["score"] += score
    test["index"] += 1

    send_next_test_question(chat_id)


def finish_test(chat_id: int):
    data = user_data[chat_id]
    cat_title = data["category"]
    cat_info = CATEGORY_TESTS[cat_title]
    test = data["test"]

    max_score = len(cat_info["questions"]) * 4
    ratio = test["score"] / max_score if max_score > 0 else 0

    if ratio < 0.35:
        level = "Quyi darajada ifodalangan simptomlar."
    elif ratio < 0.65:
        level = "O‘rtacha darajada ifodalangan simptomlar."
    else:
        level = "Kuchli ifodalangan simptomlar (batafsil ishlash tavsiya etiladi)."

    test["level"] = level

    bot.send_message(
        chat_id,
        f"Qisqa diagnostika yakunlandi.\n\n"
        f"<b>Natija:</b> {level}\n\n"
        f"{cat_info['support']}\n\n"
        f"{cat_info['exercise']}",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    bot.send_message(
        chat_id,
        "Endi iltimos, muammongizni imkon qadar batafsil yoritib bering.\n"
        "Nimalar sizni ko‘proq bezovta qilmoqda, qaysi vaziyatlar, fikrlar yoki hissiyotlar tez-tez paydo bo‘ladi?"
    )

    set_state(chat_id, STATE_PROBLEM)


# =========================
#  3-BOSQICH: MUAMMONI YOZISH
# =========================

def handle_problem(message: types.Message, text: str):
    chat_id = message.chat.id
    user_data[chat_id]["problem"] = text

    bot.send_message(
        chat_id,
        "Rahmat, siz holatingizni juda muhim tarzda ifoda etdingiz.\n"
        "Bu holatni yozib berishning o‘zi ham ichki yukni bir oz bo‘lsa ham yengillashtiradi.\n\n"
        "Endi bog‘lanish uchun telefon raqamingizni qoldiring.",
    )

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📞 Raqamni kontakt sifatida yuborish", request_contact=True))
    kb.add(types.KeyboardButton("📱 Raqamni qo‘lda yozaman"))

    bot.send_message(
        chat_id,
        "Quyidagi usullardan birini tanlang:",
        reply_markup=kb,
    )

    set_state(chat_id, STATE_PHONE_CHOICE)


# CONTACT HANDLER
@bot.message_handler(content_types=["contact"])
def contact_handler(message: types.Message):
    chat_id = message.chat.id
    state = get_state(chat_id)

    if state in [STATE_PHONE_CHOICE, STATE_PHONE_TEXT]:
        phone = message.contact.phone_number
        user_data[chat_id]["phone"] = phone
        ask_session_type(chat_id)


def handle_phone_choice(message: types.Message, text: str):
    chat_id = message.chat.id

    if text == "📱 Raqamni qo‘lda yozaman":
        bot.send_message(
            chat_id,
            "Iltimos, telefon raqamingizni quyidagicha yozing:\n"
            "+99890XXXXXXX",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        set_state(chat_id, STATE_PHONE_TEXT)
    else:
        if text.startswith("+") or text.replace(" ", "").isdigit():
            user_data[chat_id]["phone"] = text
            ask_session_type(chat_id)
        else:
            bot.send_message(chat_id, "Agar raqamni matn sifatida yubormoqchi bo‘lsangiz, uni to‘liq yozing yoki kontakt yuboring.")


def handle_phone_text(message: types.Message, text: str):
    chat_id = message.chat.id
    user_data[chat_id]["phone"] = text
    ask_session_type(chat_id)


# =========================
#  4-BOSQICH: SEANS TURINI TANLASH
# =========================

def ask_session_type(chat_id: int):
    bot.send_message(
        chat_id,
        "Qanday formatdagi seans sizga ma’qulroq?",
        reply_markup=build_session_type_keyboard(),
    )
    set_state(chat_id, STATE_SESSION_TYPE)


def handle_session_type(message: types.Message, text: str):
    chat_id = message.chat.id

    if text == "👤 Individual seans":
        user_data[chat_id]["session_type"] = "Individual"
    elif text == "👥 Jamoaviy (guruh) seans":
        user_data[chat_id]["session_type"] = "Jamoaviy (guruh)"
    else:
        bot.send_message(chat_id, "Iltimos, tugmalardan birini tanlang.")
        return

    bot.send_message(
        chat_id,
        "Endi seans uchun sizga qulay vaqtni tanlaymiz.",
        reply_markup=build_time_keyboard(),
    )
    set_state(chat_id, STATE_TIME_SLOT)


# =========================
#  5-BOSQICH: VAQTNI TANLASH
# =========================

def handle_time_slot(message: types.Message, text: str):
    chat_id = message.chat.id

    if text == "⏰ Kunduzgi 10:00–12:00":
        user_data[chat_id]["time_slot"] = "Kunduzgi 10:00–12:00"
        finish_intake(message)
    elif text == "🌙 Kechki 20:00–22:00":
        user_data[chat_id]["time_slot"] = "Kechki 20:00–22:00"
        finish_intake(message)
    elif text == "📝 O‘zimga qulay vaqtni yozaman":
        bot.send_message(
            chat_id,
            "Marhamat, sizga qulay bo‘lgan kun va soatni yozib qoldiring "
            "(masalan: 'Juma kuni 21:00', yoki 'Dushanba, 11:30').",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        set_state(chat_id, STATE_TIME_CUSTOM)
    else:
        bot.send_message(chat_id, "Iltimos, pastdagi tugmalardan birini tanlang.")


def handle_time_custom(message: types.Message, text: str):
    chat_id = message.chat.id
    user_data[chat_id]["time_slot"] = text
    finish_intake(message)


# =========================
#  YAKUNIY BOSQICH
# =========================

def finish_intake(message: types.Message):
    chat_id = message.chat.id
    data = user_data[chat_id]

    name = data["name"] or "Noma’lum"
    category = data["category"] or "Noma’lum"
    problem = data["problem"] or "Noma’lum"
    phone = data["phone"] or "Noma’lum"
    session_type = data["session_type"] or "Aniqlanmagan"
    time_slot = data["time_slot"] or "Aniqlanmagan"

    test = data.get("test") or {}
    test_level = test.get("level") or "Aniqlanmagan"
    test_answers = test.get("answers") or []

    username = message.from_user.username
    tg_profile = f"@{username}" if username else "username yo‘q"
    user_id = message.from_user.id

    # Admin uchun xabar
    test_ans_text = ""
    if test_answers:
        for i, ans in enumerate(test_answers, start=1):
            test_ans_text += f"{i}. {ans}\n"

    admin_text = (
        "🆕 Yangi psixologik murojaat\n\n"
        f"<b>Ism:</b> {name}\n"
        f"<b>Kategoriya:</b> {category}\n"
        f"<b>Qisqa diagnostika natijasi:</b> {test_level}\n\n"
        f"<b>Muammo tafsiloti:</b>\n{problem}\n\n"
        f"<b>Telefon:</b> {phone}\n"
        f"<b>Seans turi:</b> {session_type}\n"
        f"<b>Afzal vaqt:</b> {time_slot}\n\n"
        f"<b>Telegram:</b> {tg_profile}\n"
        f"<b>User ID:</b> {user_id}\n\n"
    )

    if test_ans_text:
        admin_text += "<b>Test javoblari (Likert):</b>\n" + test_ans_text

    try:
        bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        print("Admin'ga yuborishda xato:", e)

    # Foydalanuvchiga yakuniy xabarlar
    bot.send_message(
        chat_id,
        "Rahmat, barcha ma’lumotlar muvaffaqiyatli qabul qilindi.\n\n"
        "Siz tomonidan bo‘lingan fikr va his-tuyg‘ular juda qimmatli. "
        "Yaqqol ko‘rinib turibdiki, siz o‘z hayotingiz va ruhiy holatingizni yaxshilashga jiddiy qarayapsiz.",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    # Seans haqida ma'lumot va profil
    bot.send_message(
        chat_id,
        "Seans tafsilotlari, aniq vaqtni kelishib olish va boshqa savollar uchun "
        f"menga to‘g‘ridan-to‘g‘ri yozishingiz mumkin: <b>@mirzavaliyev</b>\n\n"
        f"👉 <a href=\"{TELEGRAM_PROFILE_URL}\">Telegram profilim</a>\n\n"
        "Suhbat davomida xavfsizlik, maxfiylik va hurmat asosiy tamoyil bo‘ladi.",
    )

    # Ijtimoiy tarmoqlar tugmalari
    social_kb = types.InlineKeyboardMarkup()
    social_kb.add(
        types.InlineKeyboardButton("Telegram", url=TELEGRAM_PROFILE_URL),
        types.InlineKeyboardButton("Instagram", url=INSTAGRAM_URL),
    )

    bot.send_message(
        chat_id,
        "Quyidagi ijtimoiy tarmoqlar orqali ham foydali kontent va psixologik materiallarni kuzatib borishingiz mumkin:",
        reply_markup=social_kb,
    )

    bot.send_message(
        chat_id,
        "Agar xohlasangiz, /start buyrug‘i orqali yana boshqa mavzu bo‘yicha murojaat qoldirishingiz mumkin."
    )

    init_user(chat_id)


# =========================
#  ISHGA TUSHIRISH
# =========================

import os
from flask import Flask, request
import telebot
# === WEBHOOK ROUTE-LAR ===

@server.route(f"/{API_TOKEN}", methods=['POST'])
def telegram_webhook():
    # Telegram yuborgan JSON ni o‘qib, TeleBot-ga beramiz
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@server.route("/")
def index():
    return "Psixolog-bot ishlayapti", 200


if __name__ == "__main__":
    # Render tomonidan beriladigan port
    port = int(os.environ.get("PORT", 5000))

    # Render avtomatik beradi: tashqi URL (https://psy-bot.onrender.com kabi)
    external_url = os.environ.get("RENDER_EXTERNAL_URL")

    if external_url:
        webhook_url = f"{external_url}/{"8436935672:AAGc_mYCtMHuJ81hS2miBoSpx0ttZf9nHkU"}"
        try:
            bot.remove_webhook()
        except Exception:
            pass
        bot.set_webhook(url=webhook_url)
        print("Webhook o‘rnatildi:", webhook_url)
    else:
        print("RENDER_EXTERNAL_URL topilmadi, webhook sozlanmadi")

    # Flask serverni ishga tushiramiz
    server.run(host="0.0.0.0", port=port)



