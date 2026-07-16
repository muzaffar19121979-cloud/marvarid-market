# config.py
# ========== БРЕНД МАЪЛУМОТЛАРИ ==========
SHOP_NAME = "MARVARID market"
SHOP_ADDRESS = "Denov tumani, Ko'zichog'li mfy"
SHOP_PHONE = "+998885500221"
SHOP_WEBSITE = "www.marvarid.uz"

# ========== ТЎЛОВ СОЗЛАМАЛАРИ ==========
FLEXIBLE_PAYMENT = True
NEGOTIABLE_PRICE = True

# ========== ЧЕК ВА ЭТИКЕТКА ==========
RECEIPT_FOOTER = "Rahmat! Yana tashrif buyuring!"
LABEL_FOOTER = "MARVARID - Sifat va ishonch"

# ========== ВАЛЮТА ==========
CURRENCY = "so'm"
CURRENCY_SYMBOL = "сўм"

# ========== ДАСТУР СОЗЛАМАЛАРИ ==========
APP_NAME = "MARVARID market"
APP_VERSION = "2.0.0"
OPERATOR_NAME = "Operator 1"

# ========== ОМБОР СОЗЛАМАЛАРИ ==========
MIN_STOCK_ALERT = 5

# ========== ПРИНТЕР СОЗЛАМАЛАРИ ==========
RECEIPT_WIDTH = 55        # mm
LABEL_WIDTH = 50          # mm
LABEL_HEIGHT = 30         # mm

# Принтер тури: "bluetooth" ёки "usb"
PRINTER_TYPE = "bluetooth"
BLUETOOTH_PRINTER_NAME = "HERELABEL"
PRINTER_ENCODING = "cp1251"
PRINTER_CHARS_PER_LINE = 32

# ========== ЧЕК КЎРИНИШИ ==========
RECEIPT_SHOW_LOGO = True
RECEIPT_SHOW_ADDRESS = True
RECEIPT_SHOW_PHONE = True
RECEIPT_SHOW_WEBSITE = True
RECEIPT_SHOW_OPERATOR = True
RECEIPT_SHOW_FOOTER = True

# ========== QR-КОД СОЗЛАМАЛАРИ ==========
QR_CODE_ONLY_ID = True
QR_CODE_SIZE = 300
QR_SCAN_TIMEOUT = 30  # сония

# ========== ЭТИКЕТКА ЎЛЧАМЛАРИ ==========
LABEL_SIZES = {
    '30x50': {'width': 50, 'height': 30, 'name': '30x50 (Кундаланг)', 'landscape': True},
    'small': {'width': 40, 'height': 30, 'name': 'Кичик', 'landscape': False},
    '50x30': {'width': 50, 'height': 30, 'name': 'Стандарт', 'landscape': False},
    'medium': {'width': 58, 'height': 40, 'name': 'Ўрта', 'landscape': False},
    'large': {'width': 80, 'height': 50, 'name': 'Катта', 'landscape': False},
    'custom': {'width': 60, 'height': 40, 'name': 'Мослаштирилган', 'landscape': False},
}

# ========== ЭКРАН СОЗЛАМАЛАРИ ==========
# Компьютер учун
DESKTOP_WIDTH = 1024
DESKTOP_HEIGHT = 600
DESKTOP_COLS = 2
DESKTOP_PADDING = 15
DESKTOP_SPACING = 15
DESKTOP_FONT_TITLE = "28sp"
DESKTOP_FONT_BUTTON = "22sp"
DESKTOP_FONT_TEXT = "16sp"
DESKTOP_BUTTON_HEIGHT = "56dp"

# Планшет учун
TABLET_COLS = 2
TABLET_PADDING = 15
TABLET_SPACING = 15
TABLET_FONT_TITLE = "28sp"
TABLET_FONT_BUTTON = "22sp"
TABLET_FONT_TEXT = "16sp"
TABLET_BUTTON_HEIGHT = "56dp"

# Смартфон учун
PHONE_COLS = 1
PHONE_PADDING = 10
PHONE_SPACING = 8
PHONE_FONT_TITLE = "20sp"
PHONE_FONT_BUTTON = "18sp"
PHONE_FONT_TEXT = "14sp"
PHONE_BUTTON_HEIGHT = "48dp"

# ========== ТИЛ СОЗЛАМАЛАРИ ==========
LANGUAGE = "uz"  # uz, ru, en

# Тил таржималари
TRANSLATIONS = {
    'uz': {
        'app_title': 'ДУКОН БОШҚАРУВ ТИЗИМИ',
        'sales': 'СОТИШ',
        'products': 'МАҲСУЛОТЛАР',
        'credits': 'ҚАРЗЛАР',
        'cash': 'НАҚД ПУЛ',
        'report': 'ҲИСОБОТ',
        'exit': 'ЧИҚИШ',
        'search': 'Қидириш (сканер)',
        'cart': 'САВАТЧА',
        'total': 'Жами',
        'cash_payment': 'НАҚД',
        'card_payment': 'ПЛАСТИК',
        'credit_payment': 'КАРЗГА',
        'mixed_payment': 'АРАЛАШ',
        'clear_cart': 'БЎШАТ',
        'daily_report': 'КУНЛИК ҲИСОБОТ',
        'loading': 'Юкланмоқда...',
        'add_operation': 'ОПЕРАЦИЯ ҚЎШИШ',
        'qr_scanner': 'QR СКАНЕР',
        'new_product': 'ЯНГИ МАҲСУЛОТ',
        'label': 'ЭТИКЕТКА',
    },
    'ru': {
        'app_title': 'СИСТЕМА УПРАВЛЕНИЯ МАГАЗИНОМ',
        'sales': 'ПРОДАЖИ',
        'products': 'ТОВАРЫ',
        'credits': 'ДОЛГИ',
        'cash': 'НАЛИЧНЫЕ',
        'report': 'ОТЧЕТ',
        'exit': 'ВЫХОД',
        'search': 'Поиск (сканер)',
        'cart': 'КОРЗИНА',
        'total': 'Итого',
        'cash_payment': 'НАЛИЧНЫЕ',
        'card_payment': 'КАРТА',
        'credit_payment': 'В ДОЛГ',
        'mixed_payment': 'СМЕШАННЫЙ',
        'clear_cart': 'ОЧИСТИТЬ',
        'daily_report': 'ДНЕВНОЙ ОТЧЕТ',
        'loading': 'Загрузка...',
        'add_operation': 'ДОБАВИТЬ ОПЕРАЦИЮ',
        'qr_scanner': 'QR СКАНЕР',
        'new_product': 'НОВЫЙ ТОВАР',
        'label': 'ЭТИКЕТКА',
    },
    'en': {
        'app_title': 'SHOP MANAGEMENT SYSTEM',
        'sales': 'SALES',
        'products': 'PRODUCTS',
        'credits': 'CREDITS',
        'cash': 'CASH',
        'report': 'REPORT',
        'exit': 'EXIT',
        'search': 'Search (scanner)',
        'cart': 'CART',
        'total': 'Total',
        'cash_payment': 'CASH',
        'card_payment': 'CARD',
        'credit_payment': 'CREDIT',
        'mixed_payment': 'MIXED',
        'clear_cart': 'CLEAR',
        'daily_report': 'DAILY REPORT',
        'loading': 'Loading...',
        'add_operation': 'ADD OPERATION',
        'qr_scanner': 'QR SCANNER',
        'new_product': 'NEW PRODUCT',
        'label': 'LABEL',
    }
}

# ========== ЛОГОТИП ==========
LOGO_PATH = "logo.png"

# ========== МАЪЛУМОТЛАР БАЗАСИ ==========
DATABASE_NAME = "dukon.db"
DATABASE_BACKUP = True

# ========== ҲИСОБОТ СОЗЛАМАЛАРИ ==========
REPORT_SAVE_PATH = "reports/"
REPORT_AUTO_SAVE = True

# ========== ХАВФСИЗЛИК ==========
ADMIN_PASSWORD = "1234"

# ========== ТЕСТ РЕЖИМИ ==========
TEST_MODE = False

# ========== ҚАРЗ СОЗЛАМАЛАРИ ==========
DEFAULT_CREDIT_DEADLINE_DAYS = 30
CREDIT_STATUSES = {
    'active': 'Фаол',
    'overdue': 'Муддати ўтган',
    'paid': 'Тўланган',
    'cancelled': 'Бекор қилинган'
}

# ========== НАҚД ПУЛ ОПЕРАЦИЯЛАРИ ==========
CASH_TYPES = {
    'give': 'Бердик',
    'take': 'Олдик',
    'income': 'Кирим',
    'expense': 'Чиқим'
}

# ========== ТЎЛОВ ТУРЛАРИ ==========
PAYMENT_TYPES = {
    'cash': 'Нақд',
    'card': 'Пластик',
    'credit': 'Қарзга',
    'mixed': 'Аралаш'
}

# ========== ЎЛЧОВ БИРЛИКЛАРИ ==========
MEASUREMENT_TYPES = {
    'dona': 'Дона',
    'kg': 'Кг'
}

# ========== ФАЙЛ ЙЎЛЛАРИ ==========
FONT_PATHS = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/times.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/timesbd.ttf",
    "C:/Windows/Fonts/georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

# ========== SUMMATRA PDF ЙЎЛЛАРИ ==========
SUMATRA_PATHS = [
    "C:/Program Files/SumatraPDF/SumatraPDF.exe",
    "C:/Program Files (x86)/SumatraPDF/SumatraPDF.exe"
]

# ========== ADOBE READER ЙЎЛЛАРИ ==========
ADOBE_PATHS = [
    "C:/Program Files/Adobe/Acrobat Reader/AcroRd32.exe",
    "C:/Program Files (x86)/Adobe/Acrobat Reader/AcroRd32.exe"
]


# ========== ЁРДАМЧИ ФУНКЦИЯЛАР ==========
def get_translation(key, lang=None):
    """Таржимани олиш"""
    if lang is None:
        lang = LANGUAGE
    
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    return translations.get(key, key)


def get_payment_name(payment_type):
    """Тўлов тури номини олиш"""
    return PAYMENT_TYPES.get(payment_type, payment_type)


def get_measurement_name(measurement_type):
    """Ўлчов бирлиги номини олиш"""
    return MEASUREMENT_TYPES.get(measurement_type, measurement_type)


def get_cash_type_name(cash_type):
    """Нақд пул операцияси номини олиш"""
    return CASH_TYPES.get(cash_type, cash_type)


def get_credit_status_name(status):
    """Қарз статуси номини олиш"""
    return CREDIT_STATUSES.get(status, status)