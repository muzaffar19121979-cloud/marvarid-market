# screens/products_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem

from modules.products import ProductManager
from modules.printer import PrinterManager
from modules.label_printer import LabelPrinter
from screens.dialog_mixin import DialogMixin
from screens.products.product_form import ProductFormMixin
from screens.products.product_labels import ProductLabelsMixin
from screens.products.product_qr import ProductQRMixin

try:
    from modules.qr_scanner import BarcodeScanner
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    BarcodeScanner = None


class ProductsScreen(Screen, DialogMixin, ProductFormMixin, ProductLabelsMixin, ProductQRMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_manager = ProductManager()
        self.printer_manager = PrinterManager()
        self.label_printer = LabelPrinter()
        self.barcode_scanner = BarcodeScanner() if QR_AVAILABLE else None
        self.selected_product = None
        self.selected_product_id = None
    
    def on_enter(self):
        self.load_products()
    
    def load_products(self):
        products = self.product_manager.get_all_products()
        self.ids.product_list.clear_widgets()
        
        for p in products:
            measurement_type = p[7] if len(p) > 7 else 'dona'
            unit = 'кг' if measurement_type == 'kg' else 'дона'
            qty = p[5] if p[5] else 0
            min_qty = p[6] if p[6] else 0
            
            item = OneLineListItem(
                text=f"{p[1]} - Кириш: {p[3]:,.0f} | Сотиш: {p[4]:,.0f} | {qty:.2f} {unit} | Мин: {min_qty:.2f}",
                on_release=lambda x, product=p: self.show_product_actions(product)
            )
            self.ids.product_list.add_widget(item)
    
    def show_product_actions(self, product):
        self.selected_product = product
        self.selected_product_id = product[0]
        
        measurement_type = product[7] if len(product) > 7 else 'dona'
        unit = 'кг' if measurement_type == 'kg' else 'дона'
        
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=280
        )
        
        content.add_widget(MDLabel(
            text=f"📦 {product[1]}\n"
                 f"💰 Сотиш: {product[4]:,.0f} сўм\n"
                 f"📊 Омборда: {product[5]:.2f} {unit}\n"
                 f"🆔 ID: {product[0]}",
            halign="center", font_style="H6"
        ))
        
        dialog = MDDialog(
            title="Маҳсулот амаллари",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="✏️ ТАҲРИРЛАШ", on_release=lambda x: self._show_edit_dialog(product, dialog)),
                MDRectangleFlatButton(text="🗑 ЎЧИРИШ", on_release=lambda x: self._confirm_delete(product, dialog)),
                MDRectangleFlatButton(text="🏷️ ЭТИКЕТКА", on_release=lambda x: self._show_label_options(product, dialog)),
                MDRectangleFlatButton(text="📊 ТАРИХ", on_release=lambda x: self._show_product_history(product, dialog)),
                MDRectangleFlatButton(text="❌ ЁПИШ", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()