# pyright: reportMissingImports=false
# main.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.utils import platform

from config import SHOP_NAME

# Android рухсатлари + landscape
if platform == 'android':
    Window.orientation = 'landscape'
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
            Permission.BLUETOOTH_CONNECT,
            Permission.ACCESS_FINE_LOCATION,
        ])
    except Exception:
        pass
    
# Экранларни юклаш
from screens.main_screen import MainScreen
from screens.sales_screen import SalesScreen
from screens.products_screen import ProductsScreen
from screens.credits_screen import CreditsScreen
from screens.cash_screen import CashScreen
from screens.report_screen import ReportScreen

# Горизонтал режим
COLS = 2
FONT_TITLE = "18sp"
FONT_BTN = "15sp"
FONT_BTN_SMALL = "13sp"
FONT_TEXT = "13sp"
PAD = 6
SPACE = 5

if platform != 'android':
    Window.size = (1024, 600)

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
            font_style: "H5"
            halign: "center"
            size_hint_y: 0.1
            font_size: "{FONT_TITLE}"
        
        GridLayout:
            cols: {COLS}
            spacing: {SPACE}
            size_hint_y: 0.78
            
            MDRectangleFlatButton:
                text: "SOTISH"
                on_release: root.open_sales()
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "MAXSULOTLAR"
                on_release: root.open_products()
                md_bg_color: 0.20, 0.55, 0.86, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "QARZLAR"
                on_release: root.open_credits()
                md_bg_color: 0.90, 0.49, 0.13, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "NAQD PUL"
                on_release: root.open_cash()
                md_bg_color: 0.95, 0.61, 0.07, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "HISOBOT"
                on_release: root.open_report()
                md_bg_color: 0.61, 0.35, 0.71, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1
            
            MDRectangleFlatButton:
                text: "CHIQISH"
                on_release: app.stop()
                md_bg_color: 0.80, 0.20, 0.20, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN}"
                size_hint: 1, 1

<SalesScreen>:
    BoxLayout:
        orientation: 'horizontal'
        padding: 2
        spacing: 2
        
        # Чап - махсулотлар
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.42
            spacing: 2
            
            MDTopAppBar:
                title: "SOTISH"
                left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
                md_bg_color: 0.15, 0.68, 0.38, 1
                elevation: 2
                size_hint_y: 0.08
            
            MDTextField:
                id: search
                hint_text: "Qidirish / Skaner"
                font_size: "{FONT_TEXT}"
                size_hint_y: 0.08
                mode: "round"
                on_text: root.load_products(self.text)
                
            ScrollView:
                MDList:
                    id: product_list
        
        # Урта - саватча
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.38
            spacing: 2
            
            MDLabel:
                text: "SAVATCHA"
                halign: "center"
                font_style: "H6"
                size_hint_y: 0.05
                font_size: "{FONT_BTN}"
            
            ScrollView:
                MDList:
                    id: cart_list
            
            MDLabel:
                id: total_label
                text: "Jami: 0 so'm"
                halign: "center"
                font_style: "H6"
                size_hint_y: 0.06
                font_size: "{FONT_BTN}"
        
        # Унг - тугмалар
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.20
            spacing: 2
            padding: 2
            
            MDRectangleFlatButton:
                text: "NAQD"
                on_release: root.process_single_payment('cash')
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"
            
            MDRectangleFlatButton:
                text: "PLASTIK"
                on_release: root.process_single_payment('card')
                md_bg_color: 0.20, 0.55, 0.86, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"
            
            MDRectangleFlatButton:
                text: "QARZ"
                on_release: root.process_credit_sale()
                md_bg_color: 0.90, 0.49, 0.13, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"
            
            MDRectangleFlatButton:
                text: "CHEK"
                on_release: root.reprint_last_receipt()
                md_bg_color: 0.61, 0.35, 0.71, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"
            
            MDRectangleFlatButton:
                text: "TOZALASH"
                on_release: root.clear_cart()
                md_bg_color: 0.80, 0.20, 0.20, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"

<ProductsScreen>:
    BoxLayout:
        orientation: 'horizontal'
        padding: 6
        spacing: 4
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.78
            
            MDTopAppBar:
                title: "MAXSULOTLAR"
                left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
                md_bg_color: 0.20, 0.55, 0.86, 1
                elevation: 2
                size_hint_y: 0.08
            
            ScrollView:
                MDList:
                    id: product_list
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.22
            padding: 3
            spacing: 3
            
            MDRectangleFlatButton:
                text: "YANGI MAXSULOT"
                on_release: root.show_add_dialog()
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"

<CreditsScreen>:
    BoxLayout:
        orientation: 'horizontal'
        padding: 6
        spacing: 4
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
            
            MDTopAppBar:
                title: "QARZLAR"
                left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
                md_bg_color: 0.90, 0.49, 0.13, 1
                elevation: 2
                size_hint_y: 0.08
            
            ScrollView:
                MDList:
                    id: credit_list

<CashScreen>:
    BoxLayout:
        orientation: 'horizontal'
        padding: 6
        spacing: 4
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.78
            
            MDTopAppBar:
                title: "NAQD PUL"
                left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
                md_bg_color: 0.95, 0.61, 0.07, 1
                elevation: 2
                size_hint_y: 0.08
            
            ScrollView:
                MDList:
                    id: cash_list
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.22
            padding: 3
            
            MDRectangleFlatButton:
                text: "OPERATSIYA QUSHISH"
                on_release: root.show_add_dialog()
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_BTN_SMALL}"

<ReportScreen>:
    BoxLayout:
        orientation: 'horizontal'
        padding: 6
        spacing: 4
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
            
            MDTopAppBar:
                title: "HISOBOT"
                left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
                md_bg_color: 0.61, 0.35, 0.71, 1
                elevation: 2
                size_hint_y: 0.08
            
            ScrollView:
                MDLabel:
                    id: report_label
                    text: "Yuklanmoqda..."
                    halign: "left"
                    size_hint_y: None
                    text_size: self.width, None
                    height: self.texture_size[1]
                    padding: 12
                    font_size: "{FONT_TEXT}"
'''

class DukonApp(MDApp):
    def build(self):
        self.title = f"✦ {SHOP_NAME} ✦"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

if __name__ == '__main__':
    DukonApp().run()