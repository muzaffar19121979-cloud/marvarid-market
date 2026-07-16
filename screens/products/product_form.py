# screens/products/product_form.py
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton

MEASUREMENT_NAMES = {'dona': 'Дона', 'kg': 'Кг'}


class ProductFormMixin:
    """Маҳсулот формаси билан ишлаш"""
    
    def _build_product_form(self, product=None):
        """Маҳсулот формасини яратиш"""
        from kivymd.uix.boxlayout import MDBoxLayout
        
        content = MDBoxLayout(
            orientation='vertical', spacing=8, padding=15,
            size_hint_y=None, height=520
        )
        
        is_edit = product is not None
        
        name_input = MDTextField(
            text=product[1] if is_edit else '',
            hint_text="Маҳсулот номи *",
            size_hint_y=None, height=48
        )
        content.add_widget(name_input)
        
        barcode_input = MDTextField(
            text=product[2] or '' if is_edit else '',
            hint_text="Штрих-код",
            size_hint_y=None, height=48
        )
        content.add_widget(barcode_input)
        
        purchase_input = MDTextField(
            text=str(product[3] if is_edit and product[3] else 0),
            hint_text="Кириш нархи",
            input_filter='float',
            size_hint_y=None, height=48
        )
        content.add_widget(purchase_input)
        
        sale_input = MDTextField(
            text=str(product[4] if is_edit and product[4] else 0),
            hint_text="Сотиш нархи",
            input_filter='float',
            size_hint_y=None, height=48
        )
        content.add_widget(sale_input)
        
        quantity_input = MDTextField(
            text=str(product[5] if is_edit and product[5] else 0),
            hint_text="Миқдор",
            input_filter='float',
            size_hint_y=None, height=48
        )
        content.add_widget(quantity_input)
        
        min_qty_input = MDTextField(
            text=str(product[6] if is_edit and product[6] else 0),
            hint_text="Минимал миқдор",
            input_filter='float',
            size_hint_y=None, height=48
        )
        content.add_widget(min_qty_input)
        
        current_type = product[7] if is_edit and len(product) > 7 else 'dona'
        type_layout, dona_check, kg_check = self._build_measurement_selector(current_type)
        content.add_widget(type_layout)
        
        content.name_input = name_input
        content.barcode_input = barcode_input
        content.purchase_input = purchase_input
        content.sale_input = sale_input
        content.quantity_input = quantity_input
        content.min_qty_input = min_qty_input
        content.dona_check = dona_check
        content.kg_check = kg_check
        
        return content
    
    def _build_measurement_selector(self, current_type='dona'):
        """Ўлчов турини танлаш"""
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        type_layout.add_widget(MDLabel(text="Ўлчов тури:", halign="center", size_hint_x=0.3))
        
        dona_check = MDCheckbox(active=(current_type == 'dona'), size_hint_x=0.1)
        type_layout.add_widget(dona_check)
        type_layout.add_widget(MDLabel(text="Дона", halign="left", size_hint_x=0.2))
        
        kg_check = MDCheckbox(active=(current_type == 'kg'), size_hint_x=0.1)
        type_layout.add_widget(kg_check)
        type_layout.add_widget(MDLabel(text="Кг", halign="left", size_hint_x=0.2))
        
        dona_check.bind(active=lambda cb, val: setattr(kg_check, 'active', not val) if val else None)
        kg_check.bind(active=lambda cb, val: setattr(dona_check, 'active', not val) if val else None)
        
        return type_layout, dona_check, kg_check
    
    def _show_edit_dialog(self, product, parent_dialog):
        """Маҳсулотни таҳрирлаш диалоги"""
        if parent_dialog:
            parent_dialog.dismiss()
        
        content = self._build_product_form(product)
        
        dialog = MDDialog(
            title=f"✏️ Маҳсулотни таҳрирлаш (ID: {product[0]})",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="САҚЛАШ", on_release=lambda x: self._save_edited_product(product[0], content, dialog))
            ]
        )
        dialog.open()
    
    def _save_edited_product(self, product_id, content, dialog):
        """Таҳрирланган маҳсулотни сақлаш"""
        try:
            name = content.name_input.text.strip()
            barcode = content.barcode_input.text.strip()
            purchase = float(content.purchase_input.text or 0)
            sale = float(content.sale_input.text or 0)
            quantity = float(content.quantity_input.text or 0)
            min_qty = float(content.min_qty_input.text or 0)
            measurement_type = 'kg' if content.kg_check.active else 'dona'
            
            if not name:
                self._show_message("Хатолик", "Маҳсулот номи киритилиши шарт!")
                return
            
            result, message = self.product_manager.update_product(
                product_id, name, barcode, purchase, sale, min_qty, measurement_type
            )
            
            if not result:
                self._show_message("Хатолик", message)
                return
            
            product = self.product_manager.get_product_by_id_dict(product_id)
            if product and product['quantity'] != quantity:
                diff = quantity - product['quantity']
                self.product_manager.update_quantity(product_id, diff)
            
            dialog.dismiss()
            self.load_products()
            self._show_message("Муваффақият", f"'{name}' маҳсулоти янгиланди!")
            
        except ValueError:
            self._show_message("Хатолик", "Нарх ва миқдорлар сон бўлиши керак!")
        except Exception as e:
            self._show_message("Хатолик", str(e))
    
    def _confirm_delete(self, product, parent_dialog):
        """Ўчиришни тасдиқлаш"""
        if parent_dialog:
            parent_dialog.dismiss()
        
        dialog = MDDialog(
            title="🗑 Маҳсулотни ўчириш",
            text=f"'{product[1]}' маҳсулотини ўчиришга ишончингиз комилми?\n\n⚠️ Бу амални қайтариб бўлмайди!",
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ҲА, ЎЧИР", on_release=lambda x: self._delete_product(product[0], dialog))
            ]
        )
        dialog.open()
    
    def _delete_product(self, product_id, dialog):
        """Маҳсулотни ўчириш"""
        result, message = self.product_manager.delete_product(product_id)
        dialog.dismiss()
        self.load_products()
        self._show_message("Муваффақият" if result else "Хатолик", message)
    
    def show_add_dialog(self):
        """Янги маҳсулот қўшиш диалоги"""
        content = self._build_product_form()
        
        dialog = MDDialog(
            title="➕ ЯНГИ МАҲСУЛОТ ҚЎШИШ",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self._add_product(content, dialog))
            ]
        )
        dialog.open()
    
    def _add_product(self, content, dialog):
        """Маҳсулотни базага қўшиш"""
        try:
            name = content.name_input.text.strip()
            barcode = content.barcode_input.text.strip()
            purchase = float(content.purchase_input.text or 0)
            sale = float(content.sale_input.text or 0)
            quantity = float(content.quantity_input.text or 0)
            min_qty = float(content.min_qty_input.text or 0)
            measurement_type = 'kg' if content.kg_check.active else 'dona'
            
            if not name:
                self._show_message("Хатолик", "Маҳсулот номи киритилиши шарт!")
                return
            
            result, message = self.product_manager.add_product(
                name, barcode, purchase, sale, quantity, min_qty, measurement_type
            )
            
            if result:
                dialog.dismiss()
                self.load_products()
                unit = 'кг' if measurement_type == 'kg' else 'дона'
                self._show_message("Муваффақият", f"'{name}' қўшилди! ({unit})")
            else:
                self._show_message("Хатолик", message)
                
        except ValueError:
            self._show_message("Хатолик", "Нарх ва миқдорлар сон бўлиши керак!")
        except Exception as e:
            self._show_message("Хатолик", str(e))
    
    def _show_product_history(self, product, dialog):
        """Маҳсулот тарихини кўрсатиш"""
        dialog.dismiss()
        measurement_text = 'Кг' if (len(product) > 7 and product[7] == 'kg') else 'Дона'
        
        dialog = MDDialog(
            title=f"📊 {product[1]} тарихи",
            text=f"🆔 ID: {product[0]}\n"
                 f"📦 Номи: {product[1]}\n"
                 f"📋 Штрих-код: {product[2] or 'Йўқ'}\n"
                 f"💰 Кириш нархи: {product[3]:,.0f} сўм\n"
                 f"💰 Сотиш нархи: {product[4]:,.0f} сўм\n"
                 f"📊 Омборда: {product[5]:.2f}\n"
                 f"📏 Тури: {measurement_text}",
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()