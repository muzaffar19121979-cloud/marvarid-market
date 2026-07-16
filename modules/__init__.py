# modules/__init__.py
from modules.products import ProductManager
from modules.sales import SalesManager
from modules.credits import CreditManager
from modules.cash import CashManager
from modules.reports import ReportManager
from modules.printer import PrinterManager
from modules.label_printer import LabelPrinter

try:
    from modules.qr_scanner import BarcodeScanner
except ImportError:
    BarcodeScanner = None
    print("⚠️ QR сканер мавжуд эмас")

__all__ = [
    'ProductManager',
    'SalesManager',
    'CreditManager',
    'CashManager',
    'ReportManager',
    'PrinterManager',
    'LabelPrinter',
    'BarcodeScanner',
]