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
RECEIPT_WIDTH = 55
LABEL_WIDTH = 50
LABEL_HEIGHT = 30

PRINTER_TYPE = "bluetooth"
BLUETOOTH_PRINTER_NAME = "M1-9372"
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
QR_SCAN_TIMEOUT = 30

# ========== ЭТИКЕТКА ЎЛЧАМЛАРИ ==========
LABEL_SIZES = {
    '30x50': {'width': 50, 'height': 30, 'name': '30x50 (Кундаланг)', 'landscape': True},
    'small': {'width': 40, 'height': 30, 'name': 'Кичик', 'landscape': False},
    '50x30': {'width': 50, 'height': 30, 'name': 'Стандарт', 'landscape': False},
    'medium': {'width': 58, 'height': 40, 'name': 'Ўрта', 'landscape': False},
    'large': {'width': 80, 'height': 50, 'name': 'Катта', 'landscape': False},
    'custom': {'width': 60, 'height': 40, 'name': 'Мослаштирилган', 'landscape': False},
}

# ========== ТИЛ СОЗЛАМАЛАРИ ==========
LANGUAGE = "uz"

# ========== ЛОГОТИП ==========
LOGO_PATH = "logo.png"

# ========== МАЪЛУМОТЛАР БАЗАСИ ==========
DATABASE_NAME = "dukon.db"
DATABASE_BACKUP = True

# ========== ҲИСОБОТ СОЗЛАМАЛАРИ ==========
REPORT_SAVE_PATH = "reports/"
REPORT_AUTO_SAVE = True

# ========== ҚАРЗ СОЗЛАМАЛАРИ ==========
DEFAULT_CREDIT_DEADLINE_DAYS = 30

# ========== ФАЙЛ ЙЎЛЛАРИ ==========
FONT_PATHS = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/times.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

SUMATRA_PATHS = [
    "C:/Program Files/SumatraPDF/SumatraPDF.exe",
    "C:/Program Files (x86)/SumatraPDF/SumatraPDF.exe"
]

ADOBE_PATHS = [
    "C:/Program Files/Adobe/Acrobat Reader/AcroRd32.exe",
    "C:/Program Files (x86)/Adobe/Acrobat Reader/AcroRd32.exe"
]