# screens/sales_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.products import ProductManager
from modules.sales import SalesManager
from modules.credits import CreditManager
from modules.printer import PrinterManager


class SalesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.total_amount = 0
        self.product_manager = ProductManager()
        self.sales_manager = SalesManager()
        self.credit_manager = CreditManager()
        self.printer_manager = PrinterManager()
        self.last_receipt_data = {}
    
    def on_enter(self):
        self.load_products()
        self.update_cart_display()
        Clock.schedule_once(lambda dt: setattr(self.ids.search, 'focus', True), 0.3)
    
    def load_products(self, search_text=""):
        self.ids.product_list.clear_widgets()
        
        try:
            if search_text:
                products = self.product_manager.search_product(search_text)
            else:
                products = self.product_manager.get_all_products()
            
            for p in products:
                measurement_type = p[7] if len(p) > 7 else 'dona'
                unit = 'кг' if measurement_type == 'kg' else 'дона'
                
                item = OneLineListItem(
                    text=f"{p[1]} - {p[4]:,.0f} сўм/{unit} (қолди: {p[5]:.2f})",
                    on_release=lambda x, pid=p[0], name=p[1], price=p[4], qty=p[5], mtype=measurement_type: 
                        self._show_quantity_dialog(pid, name, price, qty, mtype)
                )
                self.ids.product_list.add_widget(item)
        except Exception as e:
            self._show_msg("Хатолик", str(e))
    
    def _show_quantity_dialog(self, product_id, name, price, available, measurement_type):
        unit = 'кг' if measurement_type == 'kg' else 'дона'
        
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=200
        )
        
        content.add_widget(MDLabel(
            text=f"{name}\n{price:,.0f} сўм/{unit}\nМавжуд: {available:.2f} {unit}",
            halign="center", font_style="H6"
        ))
        
        qty_input = MDTextField(
            hint_text="Миқдор",
            input_filter='float',
            text="1",
            size_hint_y=None, height=48
        )
        content.add_widget(qty_input)
        
        dialog = MDDialog(
            title=f"Миқдорни танланг ({unit})",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self._add_to_cart(
                    product_id, name, price, float(qty_input.text or 1), available, measurement_type, dialog
                ))
            ]
        )
        dialog.open()
    
    def _add_to_cart(self, product_id, name, price, quantity, available, measurement_type, dialog):
        if quantity <= 0:
            return
        
        if quantity > available:
            self._show_msg("Хатолик", f"Фақат {available:.2f} мавжуд!")
            return
        
        # Агар саватчада бўлса, миқдорни ошириш
        for item in self.cart:
            if item['id'] == product_id:
                new_qty = item['quantity'] + quantity
                if new_qty > available:
                    self._show_msg("Хатолик", f"Жами {new_qty} талаб қилинмоқда, фақат {available:.2f} мавжуд!")
                    return
                item['quantity'] = new_qty
                dialog.dismiss()
                self.update_cart_display()
                self.load_products()
                return
        
        unit = 'кг' if measurement_type == 'kg' else 'дона'
        self.cart.append({
            'id': product_id,
            'name': name,
            'price': price,
            'quantity': quantity,
            'measurement_type': measurement_type,
            'unit': unit
        })
        
        dialog.dismiss()
        self.update_cart_display()
        self.load_products()
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.update_cart_display()
    
    def clear_cart(self):
        if not self.cart:
            return
        self.cart = []
        self.update_cart_display()
    
    def update_cart_display(self):
        self.ids.cart_list.clear_widgets()
        self.total_amount = 0
        
        for i, item in enumerate(self.cart):
            total = item['price'] * item['quantity']
            self.total_amount += total
            
            item_widget = OneLineListItem(
                text=f"{item['name']} x {item['quantity']:.2f} {item['unit']} = {total:,.0f} сўм",
                on_release=lambda x, idx=i: self.remove_from_cart(idx)
            )
            self.ids.cart_list.add_widget(item_widget)
        
        self.ids.total_label.text = f"Жами: {self.total_amount:,.0f} сўм"
    
    # ========== ТЎЛОВ УСУЛЛАРИ ==========
    def process_single_payment(self, payment_type):
        if not self.cart:
            self._show_msg("Хатолик", "Саватча бўш!")
            return
        
        success = True
        for item in self.cart:
            result, message = self.sales_manager.add_sale(
                item['id'], item['quantity'], item['price'],
                payment_type, "", "Operator", item['measurement_type']
            )
            if not result:
                self._show_msg("Хатолик", f"{item['name']}: {message}")
                success = False
                break
        
        if success:
            self.last_receipt_data = {
                'cart_items': [item.copy() for item in self.cart],
                'total_amount': self.total_amount,
                'payment_type': payment_type,
                'customer_name': '',
                'cash': self.total_amount if payment_type == 'cash' else 0,
                'card': self.total_amount if payment_type == 'card' else 0,
                'credit': 0,
                'paid_amount': 0,
                'change_amount': 0,
                'negotiated_price': 0
            }
            
            pay_names = {'cash': 'Нақд', 'card': 'Пластик'}
            msg = f"Жами: {self.total_amount:,.0f} сўм\nТўлов: {pay_names.get(payment_type, payment_type)}"
            
            # Чекни чоп этишга уриниш
            self._print_receipt()
            
            self.cart = []
            self.update_cart_display()
            self.load_products()
            self._show_msg("✅ Муваффақият", msg)
    
    def process_credit_sale(self):
        if not self.cart:
            self._show_msg("Хатолик", "Саватча бўш!")
            return
        
        content = MDBoxLayout(
            orientation='vertical', spacing=6, padding=20,
            size_hint_y=None, height=220
        )
        
        content.add_widget(MDLabel(
            text=f"Жами: {self.total_amount:,.0f} сўм",
            halign="center", font_style="H6"
        ))
        
        customer_input = MDTextField(
            hint_text="Мижоз номи *",
            size_hint_y=None, height=48
        )
        content.add_widget(customer_input)
        
        phone_input = MDTextField(
            hint_text="Телефон",
            size_hint_y=None, height=48
        )
        content.add_widget(phone_input)
        
        deadline_input = MDTextField(
            text="30",
            hint_text="Муддат (кун)",
            input_filter='int',
            size_hint_y=None, height=48
        )
        content.add_widget(deadline_input)
        
        dialog = MDDialog(
            title="📝 Қарзга сотиш",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="САҚЛАШ", on_release=lambda x: self._save_credit(
                    dialog, customer_input.text.strip(), phone_input.text.strip(), int(deadline_input.text or 30)
                ))
            ]
        )
        dialog.open()
    
    def _save_credit(self, dialog, customer, phone, deadline_days):
        if not customer:
            self._show_msg("Хатолик", "Мижоз номини киритинг!")
            return
        
        try:
            for item in self.cart:
                item_total = item['price'] * item['quantity']
                self.credit_manager.add_credit_sale(
                    customer, phone, item['id'], item['quantity'],
                    item_total, item['measurement_type'], deadline_days
                )
            
            self.last_receipt_data = {
                'cart_items': [item.copy() for item in self.cart],
                'total_amount': self.total_amount,
                'payment_type': 'credit',
                'customer_name': customer,
                'cash': 0,
                'card': 0,
                'credit': self.total_amount,
                'paid_amount': 0,
                'change_amount': 0,
                'negotiated_price': 0
            }
            
            dialog.dismiss()
            
            # Чекни чоп этишга уриниш
            self._print_receipt()
            
            msg = f"Қарзга сотилди!\n👤 {customer}\n💰 {self.total_amount:,.0f} сўм\n📅 {deadline_days} кун"
            self._show_msg("✅ Муваффақият", msg)
            self.cart = []
            self.update_cart_display()
            self.load_products()
            
        except Exception as e:
            self._show_msg("Хатолик", str(e))
    
    # ========== ЧЕК ЧОП ЭТИШ ==========
    def _print_receipt(self):
        """Чекни чоп этиш"""
        data = self.last_receipt_data
        if not data:
            return
        
        try:
            result, message = self.printer_manager.print_receipt(
                data['cart_items'], data['total_amount'], data['payment_type'],
                data['customer_name'], data['cash'], data['card'], data['credit'],
                data['paid_amount'], data['change_amount'], data['negotiated_price']
            )
            if not result:
                print(f"Чоп этиш: {message}")
        except Exception as e:
            print(f"Чоп этишда хатолик: {e}")
    
    def reprint_last_receipt(self):
        """Охирги чекни қайта чоп этиш"""
        if not self.last_receipt_data:
            self._show_msg("Хатолик", "Чек маълумотлари топилмади!")
            return
        
        data = self.last_receipt_data
        try:
            result, message = self.printer_manager.print_receipt(
                data['cart_items'], data['total_amount'], data['payment_type'],
                data['customer_name'], data['cash'], data['card'], data['credit'],
                data['paid_amount'], data['change_amount'], data['negotiated_price']
            )
            self._show_msg("🖨️ Чоп этиш", message if not result else "✅ Чек чоп этилди!")
        except Exception as e:
            self._show_msg("Хатолик", str(e))
    
    def _show_msg(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()