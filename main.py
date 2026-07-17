# main.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform

from config import SHOP_NAME

# Экранларни хавфсиз юклаш
try:
    from screens.main_screen import MainScreen
    from screens.sales_screen import SalesScreen
    from screens.products_screen import ProductsScreen
    from screens.credits_screen import CreditsScreen
    from screens.cash_screen import CashScreen
    from screens.report_screen import ReportScreen
    SCREENS_OK = True
except Exception as e:
    print(f"Screen xatolik: {e}")
    SCREENS_OK = False

# Экран ўлчамлари
if platform == 'android':
    COLS = 1
    FONT_TITLE = "18sp"
    FONT_BTN = "14sp"
    FONT_TEXT = "12sp"
    PAD = 8
    SPACE = 6
else:
    Window.size = (1024, 600)
    COLS = 2
    FONT_TITLE = "28sp"
    FONT_BTN = "22sp"
    FONT_TEXT = "16sp"
    PAD = 15
    SPACE = 15

KV = f'''
ScreenManager:
    MainScreen:
        name: 'main'
    SalesScreen:
        name: 'sales'
    ProductsScreen:
        name: 'products'
    CreditsScreen:
        name: 'credits'
    CashScreen:
        name: 'cash'
    ReportScreen:
        name: 'report'

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: {PAD}
        spacing: {SPACE}
        
        MDLabel:
            text: "✦ {SHOP_NAME} ✦"
            font_style: "H3"
            halign: "center"
            size_hint_y: 0.15
            font_size: "{FONT_TITLE}"
        
        GridLayout:
            cols: {COLS}
            spacing: {SPACE}
            size_hint_y: 0.70
            
            MDRectangleFlatButton:
                text: "🛒 SOTISH"
                on_release: root.open_sales()
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "📦 MAXSULOTLAR"
                on_release: root.open_products()
                md_bg_color: 0.20, 0.55, 0.86, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "📝 QARZLAR"
                on_release: root.open_credits()
                md_bg_color: 0.90, 0.49, 0.13, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "💰 NAQD PUL"
                on_release: root.open_cash()
                md_bg_color: 0.95, 0.61, 0.07, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "📊 HISOBOT"
                on_release: root.open_report()
                md_bg_color: 0.61, 0.35, 0.71, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "❌ CHIQISH"
                on_release: app.stop()
                md_bg_color: 0.80, 0.20, 0.20, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1

<SalesScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        MDLabel:
            text: "🛒 Sotish ekrani"
            halign: "center"
            font_style: "H4"

<ProductsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        MDLabel:
            text: "📦 Maxsulotlar ekrani"
            halign: "center"
            font_style: "H4"

<CreditsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        MDLabel:
            text: "📝 Qarzlar ekrani"
            halign: "center"
            font_style: "H4"

<CashScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        MDLabel:
            text: "💰 Naqd pul ekrani"
            halign: "center"
            font_style: "H4"

<ReportScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        MDLabel:
            text: "📊 Hisobot ekrani"
            halign: "center"
            font_style: "H4"
'''

class DukonApp(MDApp):
    def build(self):
        try:
            self.title = f"✦ {SHOP_NAME} ✦"
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.theme_style = "Light"
            return Builder.load_string(KV)
        except Exception as e:
            print(f"Build xatolik: {e}")

if __name__ == '__main__':
    DukonApp().run()