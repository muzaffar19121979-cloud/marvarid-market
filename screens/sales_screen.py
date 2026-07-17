# screens/sales_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.products import ProductManager
from modules.sales import SalesManager


class SalesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.total_amount = 0
        self.product_manager = ProductManager()
        self.sales_manager = SalesManager()
    
    def on_enter(self):
        self.load_products()
        self.update_cart_display()
    
    def load_products(self, search_text=""):
        self.ids.product_list.clear_widgets()
        
        try:
            if search_text:
                products = self.product_manager.search_product(search_text)
            else:
                products = self.product_manager.get_all_products()
            
            for p in products:
                unit = 'кг' if (len(p) > 7 and p[7] == 'kg') else 'дона'
                item = OneLineListItem(
                    text=f"{p[1]} - {p[4]:,.0f} сўм/{unit} (қолди: {p[5]:.2f})",
                    on_release=lambda x, pid=p[0], name=p[1], price=p[4], qty=p[5]: 
                        self._show_quantity_dialog(pid, name, price, qty)
                )
                self.ids.product_list.add_widget(item)
        except Exception as e:
            self._show_msg("Хатолик", str(e))
    
    def _show_quantity_dialog(self, product_id, name, price, available):
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=200
        )
        
        content.add_widget(MDLabel(
            text=f"{name}\n{price:,.0f} сўм\nМавжуд: {available:.2f}",
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
            title="Миқдорни танланг",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self._add_to_cart(
                    product_id, name, price, float(qty_input.text or 1), available, dialog
                ))
            ]
        )
        dialog.open()
    
    def _add_to_cart(self, product_id, name, price, quantity, available, dialog):
        if quantity <= 0:
            return
        if quantity > available:
            self._show_msg("Хатолик", f"Фақат {available:.2f} мавжуд!")
            return
        
        self.cart.append({
            'id': product_id,
            'name': name,
            'price': price,
            'quantity': quantity
        })
        
        dialog.dismiss()
        self.update_cart_display()
        self.load_products()
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.update_cart_display()
    
    def clear_cart(self):
        self.cart = []
        self.update_cart_display()
    
    def update_cart_display(self):
        self.ids.cart_list.clear_widgets()
        self.total_amount = 0
        
        for i, item in enumerate(self.cart):
            total = item['price'] * item['quantity']
            self.total_amount += total
            
            item_widget = OneLineListItem(
                text=f"{item['name']} x {item['quantity']:.2f} = {total:,.0f} сўм",
                on_release=lambda x, idx=i: self.remove_from_cart(idx)
            )
            self.ids.cart_list.add_widget(item_widget)
        
        self.ids.total_label.text = f"Жами: {self.total_amount:,.0f} сўм"
    
    def process_single_payment(self, payment_type):
        if not self.cart:
            self._show_msg("Хатолик", "Саватча бўш!")
            return
        
        success = True
        for item in self.cart:
            result, message = self.sales_manager.add_sale(
                item['id'], item['quantity'], item['price'],
                payment_type, "", "Operator"
            )
            if not result:
                self._show_msg("Хатолик", message)
                success = False
                break
        
        if success:
            pay_names = {'cash': 'Нақд', 'card': 'Пластик'}
            msg = f"Жами: {self.total_amount:,.0f} сўм\nТўлов: {pay_names.get(payment_type, payment_type)}"
            self._show_msg("✅ Муваффақият", msg)
            self.cart = []
            self.update_cart_display()
            self.load_products()
    
    def _show_msg(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()