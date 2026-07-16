# screens/products/product_labels.py
from datetime import datetime
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.spinner import Spinner

SIZE_MAP = {
    '30x50 (Кундаланг)': '30x50',
    '50x30 (Стандарт)': '50x30',
    'small (40x30)': 'small',
    'medium (58x40)': 'medium',
    'large (80x50)': 'large',
    'custom (60x40)': 'custom'
}


class ProductLabelsMixin:
    """Этикетка билан ишлаш"""
    
    def show_label_options_for_selected(self):
        """Танланган маҳсулот учун этикетка"""
        if self.selected_product:
            self._show_label_options(self.selected_product, None)
        else:
            self._show_message("⚠️ Огоҳлантириш", "Илтимос, аввал маҳсулотни танланг!")
    
    def _show_label_options(self, product, parent_dialog):
        """Этикетка вариантлари"""
        if parent_dialog:
            parent_dialog.dismiss()
        
        from kivymd.uix.boxlayout import MDBoxLayout
        
        content = MDBoxLayout(
            orientation='vertical', spacing=8, padding=15,
            size_hint_y=None, height=320
        )
        
        content.add_widget(MDLabel(
            text=f"🏷️ {product[1]}",
            halign="center", font_style="H6"
        ))
        
        size_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        size_layout.add_widget(MDLabel(text="Ўлчам:", halign="center", size_hint_x=0.3))
        size_spinner = Spinner(text='50x30 (Стандарт)', values=list(SIZE_MAP.keys()), size_hint_x=0.7)
        size_layout.add_widget(size_spinner)
        content.add_widget(size_layout)
        
        copies_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        copies_layout.add_widget(MDLabel(text="Нусха:", halign="center", size_hint_x=0.3))
        copies_spinner = Spinner(text='1', values=['1', '2', '3', '4', '5', '10'], size_hint_x=0.7)
        copies_layout.add_widget(copies_spinner)
        content.add_widget(copies_layout)
        
        company_input = MDTextField(hint_text="Компания номи", text="MARVARID", size_hint_y=None, height=48)
        content.add_widget(company_input)
        
        expiry_input = MDTextField(hint_text="Яроқлилик муддати", text="2026-12-31", size_hint_y=None, height=48)
        content.add_widget(expiry_input)
        
        dialog = MDDialog(
            title="🏷️ ЭТИКЕТКА СОЗЛАШ",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="📄 КЎРСАТ", on_release=lambda x: self._preview_label(
                    product, size_spinner.text, copies_spinner.text, company_input.text, expiry_input.text, dialog
                )),
                MDRectangleFlatButton(text="🖨️ ЧОП ЭТИШ", on_release=lambda x: self._print_label_action(
                    product, size_spinner.text, copies_spinner.text, company_input.text, expiry_input.text, dialog
                ))
            ]
        )
        dialog.open()
    
    def _build_product_data(self, product, company, expiry):
        """Этикетка учун маълумотлар"""
        return {
            'product_id': product[0],
            'name': product[1],
            'price': product[4],
            'barcode': product[2] or '',
            'purchase_price': product[3],
            'quantity': product[5],
            'measurement_type': product[7] if len(product) > 7 else 'dona',
            'shop_name': company,
            'expiry_date': expiry,
            'date': datetime.now().strftime('%d.%m.%Y')
        }
    
    def _preview_label(self, product, size, copies, company, expiry, dialog):
        """Этикеткани кўрсатиш"""
        if dialog:
            dialog.dismiss()
        
        label_size = SIZE_MAP.get(size, '50x30')
        product_data = self._build_product_data(product, company, expiry)
        result, message = self.label_printer.preview_label(product_data, label_size)
        
        self._show_message("🏷️ Этикетка" if result else "Хатолик", message)
    
    def _print_label_action(self, product, size, copies, company, expiry, dialog):
        """Этикеткани чоп этиш"""
        if dialog:
            dialog.dismiss()
        
        label_size = SIZE_MAP.get(size, '50x30')
        product_data = self._build_product_data(product, company, expiry)
        result, message = self.label_printer.print_label(product_data, label_size, int(copies))
        
        self._show_message("🖨️ Чоп этиш" if result else "Хатолик", message)