# main.py
# pyright: reportMissingImports=false
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform

from config import (
    SHOP_NAME,
    DESKTOP_WIDTH, DESKTOP_HEIGHT,
    DESKTOP_COLS, DESKTOP_PADDING, DESKTOP_SPACING,
    DESKTOP_FONT_TITLE, DESKTOP_FONT_BUTTON, DESKTOP_FONT_TEXT, DESKTOP_BUTTON_HEIGHT,
    TABLET_COLS, TABLET_PADDING, TABLET_SPACING,
    TABLET_FONT_TITLE, TABLET_FONT_BUTTON, TABLET_FONT_TEXT, TABLET_BUTTON_HEIGHT,
    PHONE_COLS, PHONE_PADDING, PHONE_SPACING,
    PHONE_FONT_TITLE, PHONE_FONT_BUTTON, PHONE_FONT_TEXT, PHONE_BUTTON_HEIGHT,
    get_translation
)
from database import close_db

from screens.main_screen import MainScreen
from screens.sales_screen import SalesScreen
from screens.products_screen import ProductsScreen
from screens.credits_screen import CreditsScreen
from screens.cash_screen import CashScreen
from screens.report_screen import ReportScreen

# ========== ANDROID РУХСАТЛАРИ (хавфсиз) ==========
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.CAMERA,
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
            Permission.BLUETOOTH_CONNECT,
            Permission.ACCESS_FINE_LOCATION,
            Permission.INTERNET
        ])
    except Exception:
        pass  # Рухсат сўрашда хатолик бўлса ҳам дастур ишлайди

# ========== ЭКРАН ЎЛЧАМИНИ АНИҚЛАШ ==========
if platform == 'android' or platform == 'ios':
    Window.fullscreen = 'auto'
    if Window.width < 600:
        COLS = PHONE_COLS
        FONT_SIZE_TITLE = PHONE_FONT_TITLE
        FONT_SIZE_BUTTON = PHONE_FONT_BUTTON
        FONT_SIZE_TEXT = PHONE_FONT_TEXT
        PADDING = PHONE_PADDING
        SPACING = PHONE_SPACING
        BUTTON_HEIGHT = PHONE_BUTTON_HEIGHT
    else:
        COLS = TABLET_COLS
        FONT_SIZE_TITLE = TABLET_FONT_TITLE
        FONT_SIZE_BUTTON = TABLET_FONT_BUTTON
        FONT_SIZE_TEXT = TABLET_FONT_TEXT
        PADDING = TABLET_PADDING
        SPACING = TABLET_SPACING
        BUTTON_HEIGHT = TABLET_BUTTON_HEIGHT
else:
    Window.size = (DESKTOP_WIDTH, DESKTOP_HEIGHT)
    COLS = DESKTOP_COLS
    FONT_SIZE_TITLE = DESKTOP_FONT_TITLE
    FONT_SIZE_BUTTON = DESKTOP_FONT_BUTTON
    FONT_SIZE_TEXT = DESKTOP_FONT_TEXT
    PADDING = DESKTOP_PADDING
    SPACING = DESKTOP_SPACING
    BUTTON_HEIGHT = DESKTOP_BUTTON_HEIGHT

t = get_translation

# ========== KV DESIGN ==========
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
        padding: {PADDING}
        spacing: {SPACING}
        
        MDLabel:
            text: "✦ {SHOP_NAME} ✦"
            font_style: "H3"
            halign: "center"
            size_hint_y: 0.12
            theme_text_color: "Custom"
            text_color: 0.1, 0.3, 0.6, 1
            font_size: "{FONT_SIZE_TITLE}"
        
        MDLabel:
            text: "{t('app_title')}"
            font_style: "H5"
            halign: "center"
            size_hint_y: 0.08
            theme_text_color: "Custom"
            text_color: 0.3, 0.3, 0.3, 1
            font_size: "{FONT_SIZE_TEXT}"
        
        GridLayout:
            cols: {COLS}
            spacing: {SPACING}
            size_hint_y: 0.70
            
            MDRectangleFlatButton:
                text: "🛒 {t('sales')}"
                on_release: root.open_sales()
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_BUTTON}"
                size_hint: 1, 1
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "📦 {t('products')}"
                on_release: root.open_products()
                md_bg_color: 0.20, 0.55, 0.86, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_BUTTON}"
                size_hint: 1, 1
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "📝 {t('credits')}"
                on_release: root.open_credits()
                md_bg_color: 0.90, 0.49, 0.13, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_BUTTON}"
                size_hint: 1, 1
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "💰 {t('cash')}"
                on_release: root.open_cash()
                md_bg_color: 0.95, 0.61, 0.07, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_BUTTON}"
                size_hint: 1, 1
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "📊 {t('report')}"
                on_release: root.open_report()
                md_bg_color: 0.61, 0.35, 0.71, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_BUTTON}"
                size_hint: 1, 1
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "❌ {t('exit')}"
                on_release: app.stop()
                md_bg_color: 0.80, 0.20, 0.20, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_BUTTON}"
                size_hint: 1, 1
                line_color: 0, 0, 0, 0

<SalesScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 8
        spacing: 8
        
        MDTopAppBar:
            title: "🛒 {t('sales')}"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            md_bg_color: 0.15, 0.68, 0.38, 1
            elevation: 4
        
        BoxLayout:
            orientation: 'horizontal' if {COLS} == 2 else 'vertical'
            size_hint_y: 0.68
            spacing: 8
            
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.5 if {COLS} == 2 else 1
                size_hint_y: 1 if {COLS} == 2 else 0.5
                spacing: 5
                
                MDTextField:
                    id: search
                    hint_text: "🔍 {t('search')}"
                    font_size: "{FONT_SIZE_TEXT}"
                    size_hint_y: 0.1
                    mode: "round"
                    on_text: root.load_products(self.text)
                    
                ScrollView:
                    MDList:
                        id: product_list
            
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.5 if {COLS} == 2 else 1
                size_hint_y: 1 if {COLS} == 2 else 0.5
                spacing: 5
                
                MDLabel:
                    text: "🛍 {t('cart')}"
                    halign: "center"
                    font_style: "H6"
                    theme_text_color: "Custom"
                    text_color: 0.8, 0.2, 0.2, 1
                    size_hint_y: 0.08
                    font_size: "{FONT_SIZE_TEXT}"
                
                ScrollView:
                    MDList:
                        id: cart_list
                
                MDLabel:
                    id: total_label
                    text: "{t('total')}: 0 сўм"
                    halign: "center"
                    font_style: "H5"
                    theme_text_color: "Custom"
                    text_color: 0, 0.4, 0.2, 1
                    size_hint_y: 0.1
                    font_size: "{FONT_SIZE_TEXT}"
        
        BoxLayout:
            size_hint_y: 0.2
            spacing: 6
            padding: 5
            
            MDRectangleFlatButton:
                text: "💵 {t('cash_payment')}"
                on_release: root.process_single_payment('cash')
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "💳 {t('card_payment')}"
                on_release: root.process_single_payment('card')
                md_bg_color: 0.20, 0.55, 0.86, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "📝 {t('credit_payment')}"
                on_release: root.process_credit_only()
                md_bg_color: 0.90, 0.49, 0.13, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "🔄 {t('mixed_payment')}"
                on_release: root.process_mixed_payment()
                md_bg_color: 0.61, 0.35, 0.71, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "🗑 {t('clear_cart')}"
                on_release: root.clear_cart()
                md_bg_color: 0.80, 0.20, 0.20, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0

<ProductsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 8
        
        MDTopAppBar:
            title: "📦 {t('products')}"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            md_bg_color: 0.20, 0.55, 0.86, 1
            elevation: 4
        
        ScrollView:
            MDList:
                id: product_list
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.12
            spacing: 8
            padding: 5
            
            MDRectangleFlatButton:
                text: "📷 {t('qr_scanner')}"
                on_release: root.show_scan_dialog()
                size_hint_x: 0.33
                md_bg_color: 0.90, 0.49, 0.13, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "➕ {t('new_product')}"
                on_release: root.show_add_dialog()
                size_hint_x: 0.33
                md_bg_color: 0.15, 0.68, 0.38, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0
            
            MDRectangleFlatButton:
                text: "🏷️ {t('label')}"
                on_release: root.show_label_options_for_selected()
                size_hint_x: 0.33
                md_bg_color: 0.61, 0.35, 0.71, 1
                text_color: 1, 1, 1, 1
                font_size: "{FONT_SIZE_TEXT}"
                line_color: 0, 0, 0, 0

<CreditsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 8
        
        MDTopAppBar:
            title: "📝 {t('credits')}"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            md_bg_color: 0.90, 0.49, 0.13, 1
            elevation: 4
        
        ScrollView:
            MDList:
                id: credit_list

<CashScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 8
        
        MDTopAppBar:
            title: "💰 {t('cash')}"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            md_bg_color: 0.95, 0.61, 0.07, 1
            elevation: 4
        
        ScrollView:
            MDList:
                id: cash_list
        
        MDRectangleFlatButton:
            text: "➕ {t('add_operation')}"
            on_release: root.show_add_dialog()
            size_hint_y: 0.08
            md_bg_color: 0.15, 0.68, 0.38, 1
            text_color: 1, 1, 1, 1
            font_size: "{FONT_SIZE_TEXT}"
            line_color: 0, 0, 0, 0

<ReportScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 8
        
        MDTopAppBar:
            title: "📊 {t('report')}"
            left_action_items: [["arrow-left", lambda x: setattr(root.manager, 'current', 'main')]]
            md_bg_color: 0.61, 0.35, 0.71, 1
            elevation: 4
        
        ScrollView:
            MDLabel:
                id: report_label
                text: "{t('loading')}"
                halign: "left"
                font_style: "Body1"
                size_hint_y: None
                text_size: self.width, None
                height: self.texture_size[1]
                padding: 20
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                font_size: "{FONT_SIZE_TEXT}"
'''

# ========== APP ==========
class DukonApp(MDApp):
    def build(self):
        self.title = f"✦ {SHOP_NAME} ✦"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        if platform == 'android' or platform == 'ios':
            self.theme_cls.button_style = "RectangleButton"
        
        return Builder.load_string(KV)
    
    def on_stop(self):
        close_db()
        return super().on_stop()


if __name__ == '__main__':
    DukonApp().run()