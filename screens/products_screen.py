# screens/products_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from datetime import datetime
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.products import ProductManager
from modules.printer import PrinterManager
from modules.label_printer import LabelPrinter


class ProductsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_manager = ProductManager()
        self.printer_manager = PrinterManager()
        self.label_printer = LabelPrinter()
        self.selected_product = None
    
    def on_enter(self):
        self.load_products()
    
    def load_products(self):
        products = self.product_manager.get_all_products()
        self.ids.product_list.clear_widgets()
        
        for p in products:
            unit = 'кг' if (len(p) > 7 and p[7] == 'kg') else 'дона'
            item = OneLineListItem(
                text=f"{p[1]} - Кириш: {p[3]:,.0f} | Сотиш: {p[4]:,.0f} | {p[5]:.2f} {unit}",
                on_release=lambda x, product=p: self.show_product_actions(product)
            )
            self.ids.product_list.add_widget(item)
    
    def show_product_actions(self, product):
        self.selected_product = product
        
        unit = 'кг' if (len(product) > 7 and product[7] == 'kg') else 'дона'
        
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=200
        )
        
        content.add_widget(MDLabel(
            text=f"📦 {product[1]}\n💰 Сотиш: {product[4]:,.0f} сўм\n📊 Омбор: {product[5]:.2f} {unit}",
            halign="center", font_style="H6"
        ))
        
        dialog = MDDialog(
            title="Маҳсулот амаллари",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="✏️ ТАҲРИРЛАШ", on_release=lambda x: self._show_edit_dialog(product, dialog)),
                MDRectangleFlatButton(text="🏷️ ЭТИКЕТКА", on_release=lambda x: self._show_label_dialog(product, dialog)),
                MDRectangleFlatButton(text="🗑 ЎЧИРИШ", on_release=lambda x: self._delete_product(product[0], dialog)),
                MDRectangleFlatButton(text="❌ ЁПИШ", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()
    
    # ========== ТАҲРИРЛАШ ==========
    def _show_edit_dialog(self, product, parent_dialog):
        parent_dialog.dismiss()
        
        content = MDBoxLayout(
            orientation='vertical', spacing=6, padding=15,
            size_hint_y=None, height=480
        )
        
        name_input = MDTextField(text=product[1], hint_text="Номи *", size_hint_y=None, height=44)
        content.add_widget(name_input)
        
        barcode_input = MDTextField(text=product[2] or '', hint_text="Штрих-код", size_hint_y=None, height=44)
        content.add_widget(barcode_input)
        
        purchase_input = MDTextField(text=str(product[3] or 0), hint_text="Кириш нархи", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(purchase_input)
        
        sale_input = MDTextField(text=str(product[4] or 0), hint_text="Сотиш нархи", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(sale_input)
        
        qty_input = MDTextField(text=str(product[5] or 0), hint_text="Миқдор", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(qty_input)
        
        min_qty_input = MDTextField(text=str(product[6] or 0), hint_text="Мин. миқдор", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(min_qty_input)
        
        current_type = product[7] if len(product) > 7 else 'dona'
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        type_layout.add_widget(MDLabel(text="Тури:", halign="center", size_hint_x=0.3))
        
        dona_check = MDCheckbox(active=(current_type == 'dona'), size_hint_x=0.1)
        type_layout.add_widget(dona_check)
        type_layout.add_widget(MDLabel(text="Дона", halign="left", size_hint_x=0.2))
        
        kg_check = MDCheckbox(active=(current_type == 'kg'), size_hint_x=0.1)
        type_layout.add_widget(kg_check)
        type_layout.add_widget(MDLabel(text="Кг", halign="left", size_hint_x=0.2))
        
        dona_check.bind(active=lambda cb, val: setattr(kg_check, 'active', not val) if val else None)
        kg_check.bind(active=lambda cb, val: setattr(dona_check, 'active', not val) if val else None)
        
        content.add_widget(type_layout)
        
        scroll = ScrollView(size_hint_y=0.9)
        scroll.add_widget(content)
        
        container = MDBoxLayout(orientation='vertical', size_hint_y=None, height=400)
        container.add_widget(scroll)
        
        dialog = MDDialog(
            title="✏️ Маҳсулотни таҳрирлаш",
            type="custom",
            content_cls=container,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="САҚЛАШ", on_release=lambda x: self._save_edit(
                    product[0], name_input.text, barcode_input.text,
                    purchase_input.text, sale_input.text, qty_input.text,
                    min_qty_input.text, dona_check, kg_check, dialog
                ))
            ]
        )
        dialog.open()
    
    def _save_edit(self, pid, name, barcode, purchase, sale, qty, min_qty, dona_check, kg_check, dialog):
        try:
            measurement = 'kg' if kg_check.active else 'dona'
            result, message = self.product_manager.update_product(
                pid, name.strip(), barcode.strip(),
                float(purchase or 0), float(sale or 0),
                float(min_qty or 0), measurement
            )
            if result:
                diff = float(qty or 0) - self.product_manager.get_product_by_id(pid)[5]
                if diff != 0:
                    self.product_manager.update_quantity(pid, diff)
                dialog.dismiss()
                self.load_products()
                self._show_msg("✅ Муваффақият", "Янгиланди!")
            else:
                self._show_msg("❌ Хатолик", message)
        except Exception as e:
            self._show_msg("❌ Хатолик", str(e))
    
    # ========== ЎЧИРИШ ==========
    def _delete_product(self, product_id, dialog):
        dialog.dismiss()
        result, message = self.product_manager.delete_product(product_id)
        self.load_products()
        self._show_msg("✅ Муваффақият" if result else "❌ Хатолик", message)
    
    # ========== ЭТИКЕТКА ==========
    def _show_label_dialog(self, product, parent_dialog):
        """Этикетка диалоги"""
        parent_dialog.dismiss()
        
        try:
            name = product[1]
            barcode_code = product[2] or f"{product[0]:06d}"
            price = product[4]
            measurement_type = product[7] if len(product) > 7 else 'dona'
            
            # Этикетка матни
            preview_text = self.label_printer.get_label_preview_text(
                product_name=name,
                price=price,
                barcode_code=barcode_code,
                measurement_type=measurement_type
            )
            
            content = MDBoxLayout(
                orientation='vertical', spacing=10, padding=15,
                size_hint_y=None, height=320
            )
            
            content.add_widget(MDLabel(
                text=preview_text,
                halign="center",
                font_style="Body1"
            ))
            
            # Ўлчам танлаш
            size_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            size_layout.add_widget(MDLabel(text="Ўлчам:", halign="center", size_hint_x=0.3))
            
            size_spinner = Spinner(
                text='30x45',
                values=['30x45', '40x30', '50x30', '58x40', '60x40', '80x50'],
                size_hint_x=0.7
            )
            size_layout.add_widget(size_spinner)
            content.add_widget(size_layout)
            
            dialog = MDDialog(
                title="🏷️ Этикетка",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRectangleFlatButton(text="❌ БЕКОР", on_release=lambda x: dialog.dismiss()),
                    MDRectangleFlatButton(text="📄 КЎРИШ", on_release=lambda x: self._preview_label(
                        name, price, barcode_code, measurement_type, size_spinner.text, dialog
                    )),
                    MDRectangleFlatButton(text="🖨️ ЧОП ЭТИШ", on_release=lambda x: self._do_print_label(
                        name, price, barcode_code, measurement_type, size_spinner.text, dialog
                    ))
                ]
            )
            dialog.open()
            
        except Exception as e:
            self._show_msg("❌ Хатолик", f"Этикетка:\n{str(e)}")
    
    def _preview_label(self, name, price, barcode_code, measurement_type, size, dialog):
        """Этикеткани расм сифатида кўриш"""
        dialog.dismiss()
        
        try:
            img_path, msg = self.label_printer.create_label_image(
                product_name=name,
                price=price,
                barcode_code=barcode_code,
                size=size,
                measurement_type=measurement_type
            )
            
            if img_path:
                try:
                    os.startfile(img_path)
                    self._show_msg("📄 Этикетка", "Расм очилди!")
                except Exception:
                    self._show_msg("📄 Этикетка", f"Файл: {os.path.basename(img_path)}")
            else:
                self._show_msg("❌ Хатолик", msg)
                
        except Exception as e:
            self._show_msg("❌ Хатолик", str(e))
    
    def _do_print_label(self, name, price, barcode_code, measurement_type, size, dialog):
        """Этикеткани чоп этиш"""
        dialog.dismiss()
        
        try:
            # Аввал расм яратиш
            img_path, msg = self.label_printer.create_label_image(
                product_name=name,
                price=price,
                barcode_code=barcode_code,
                size=size,
                measurement_type=measurement_type
            )
            
            # Принтерга чоп этиш
            result, message = self.printer_manager.print_label(
                product_name=name,
                price=price,
                barcode=barcode_code,
                quantity=1,
                measurement_type=measurement_type
            )
            
            if img_path:
                try:
                    os.startfile(img_path)
                except Exception:
                    pass
            
            self._show_msg("🖨️ Чоп этиш", message if result else f"❌ {message}")
            
        except Exception as e:
            self._show_msg("❌ Хатолик", str(e))
    
    # ========== ЯНГИ МАҲСУЛОТ ==========
    def show_add_dialog(self):
        content = MDBoxLayout(
            orientation='vertical', spacing=6, padding=15,
            size_hint_y=None, height=480
        )
        
        name_input = MDTextField(hint_text="Номи *", size_hint_y=None, height=44)
        content.add_widget(name_input)
        
        barcode_input = MDTextField(hint_text="Штрих-код", size_hint_y=None, height=44)
        content.add_widget(barcode_input)
        
        purchase_input = MDTextField(text="0", hint_text="Кириш нархи", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(purchase_input)
        
        sale_input = MDTextField(text="0", hint_text="Сотиш нархи", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(sale_input)
        
        qty_input = MDTextField(text="0", hint_text="Миқдор", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(qty_input)
        
        min_qty_input = MDTextField(text="0", hint_text="Мин. миқдор", input_filter='float', size_hint_y=None, height=44)
        content.add_widget(min_qty_input)
        
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        type_layout.add_widget(MDLabel(text="Тури:", halign="center", size_hint_x=0.3))
        
        dona_check = MDCheckbox(active=True, size_hint_x=0.1)
        type_layout.add_widget(dona_check)
        type_layout.add_widget(MDLabel(text="Дона", halign="left", size_hint_x=0.2))
        
        kg_check = MDCheckbox(active=False, size_hint_x=0.1)
        type_layout.add_widget(kg_check)
        type_layout.add_widget(MDLabel(text="Кг", halign="left", size_hint_x=0.2))
        
        dona_check.bind(active=lambda cb, val: setattr(kg_check, 'active', not val) if val else None)
        kg_check.bind(active=lambda cb, val: setattr(dona_check, 'active', not val) if val else None)
        
        content.add_widget(type_layout)
        
        scroll = ScrollView(size_hint_y=0.9)
        scroll.add_widget(content)
        
        container = MDBoxLayout(orientation='vertical', size_hint_y=None, height=400)
        container.add_widget(scroll)
        
        dialog = MDDialog(
            title="➕ ЯНГИ МАҲСУЛОТ",
            type="custom",
            content_cls=container,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self._add_product(
                    name_input.text, barcode_input.text,
                    purchase_input.text, sale_input.text, qty_input.text,
                    min_qty_input.text, dona_check, kg_check, dialog
                ))
            ]
        )
        dialog.open()
    
    def _add_product(self, name, barcode, purchase, sale, qty, min_qty, dona_check, kg_check, dialog):
        try:
            measurement = 'kg' if kg_check.active else 'dona'
            if not name.strip():
                self._show_msg("❌ Хатолик", "Ном киритинг!")
                return
            
            result, message = self.product_manager.add_product(
                name.strip(), barcode.strip(),
                float(purchase or 0), float(sale or 0),
                float(qty or 0), float(min_qty or 0), measurement
            )
            if result:
                dialog.dismiss()
                self.load_products()
                self._show_msg("✅ Муваффақият", "Қўшилди!")
            else:
                self._show_msg("❌ Хатолик", message)
        except Exception as e:
            self._show_msg("❌ Хатолик", str(e))
    
    def _show_msg(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()