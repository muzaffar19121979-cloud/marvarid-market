# screens/sales_screen.py
import os
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from modules.products import ProductManager
from modules.sales import SalesManager
from modules.credits import CreditManager
from modules.printer import PrinterManager
from config import OPERATOR_NAME, get_payment_name
from screens.dialog_mixin import DialogMixin


class SalesScreen(Screen, DialogMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.total_amount = 0
        self.sales_manager = SalesManager()
        self.product_manager = ProductManager()
        self.credit_manager = CreditManager()
        self.printer_manager = PrinterManager()
        self.selected_product = None
        self.operator = OPERATOR_NAME
        self.last_receipt_data = {}
    
    def on_enter(self):
        self.load_products()
        self.update_cart_display()
    
    # ========== МАҲСУЛОТЛАР РЎЙХАТИ ==========
    def load_products(self, search_text=""):
        self.ids.product_list.clear_widgets()
        
        try:
            if search_text and search_text.isdigit():
                product_id = int(search_text)
                product = self.product_manager.get_product_by_id(product_id)
                
                if product:
                    quantity = product[5]
                    measurement = product[7] if len(product) > 7 else 'dona'
                    
                    if quantity > 0:
                        self.add_to_cart(product[0], product[1], product[4], 1, quantity, measurement)
                        self.ids.search.text = ""
                        self.show_success(f"{product[1]} саватчага қўшилди!")
                    else:
                        self.show_warning(f"{product[1]} омборда йўқ!")
                    return
                else:
                    self.show_error(f"ID {product_id} бўйича маҳсулот топилмади!")
                    return
            
            if search_text:
                products = self.product_manager.search_product(search_text)
            else:
                products = self.product_manager.get_all_products()
            
            for p in products:
                measurement = p[7] if len(p) > 7 else 'dona'
                unit = 'кг' if measurement == 'kg' else 'дона'
                item = OneLineListItem(
                    text=f"{p[1]} - {p[4]:,.0f} сўм/{unit} (қолди: {p[5]:.2f})",
                    on_release=lambda x, pid=p[0], name=p[1], price=p[4], available=p[5], mtype=measurement: 
                        self._show_quantity_dialog(pid, name, price, available, mtype)
                )
                self.ids.product_list.add_widget(item)
                
        except Exception as e:
            self.show_error(f"Маҳсулотларни юклашда хатолик: {str(e)}")
    
    # ========== МИҚДОР ТАНЛАШ ==========
    def _show_quantity_dialog(self, product_id, name, price, available, measurement_type):
        try:
            unit = 'кг' if measurement_type == 'kg' else 'дона'
            step = 0.1 if measurement_type == 'kg' else 1
            max_val = float(available)
            default_val = 0.1 if measurement_type == 'kg' else 1
            
            content = MDBoxLayout(
                orientation='vertical', spacing=10, padding=20,
                size_hint_y=None, height=250
            )
            
            content.add_widget(MDLabel(
                text=f"{name}\n{price:,.0f} сўм/{unit}\nМавжуд: {available:.2f} {unit}",
                halign="center", font_style="H6"
            ))
            
            qty_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
            qty_layout.add_widget(MDLabel(text=f"Миқдор ({unit}):", halign="center", size_hint_x=0.3))
            
            qty_spinner = Spinner(
                text=str(default_val),
                values=[str(round(i * step, 2)) for i in range(1, min(int(max_val / step) + 1, 100))],
                size_hint_x=0.3
            )
            qty_layout.add_widget(qty_spinner)
            
            qty_input = MDTextField(
                hint_text=f"0.1-{max_val:.1f}",
                input_filter='float',
                text=str(default_val),
                size_hint_x=0.4
            )
            qty_layout.add_widget(qty_input)
            content.add_widget(qty_layout)
            
            dialog = MDDialog(
                title=f"Миқдорни танланг ({unit})",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                    MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self.add_to_cart(
                        product_id, name, price,
                        float(qty_input.text or qty_spinner.text),
                        available, measurement_type, dialog
                    ))
                ]
            )
            dialog.open()
        except Exception as e:
            self.show_error(f"Диалог очишда хатолик: {str(e)}")
    
    # ========== САВАТЧА ==========
    def add_to_cart(self, product_id, name, price, quantity, available, measurement_type, dialog=None):
        if quantity <= 0:
            self.show_error("Миқдор 0 дан катта бўлиши керак!")
            return
        
        if measurement_type == 'dona' and quantity != int(quantity):
            self.show_error("Дона маҳсулот учун бутун сон киритинг!")
            return
        
        if quantity > available:
            self.show_error(f"Омборда фақат {available:.2f} мавжуд!")
            return
        
        for item in self.cart:
            if item['id'] == product_id:
                new_qty = item['quantity'] + quantity
                if new_qty > available:
                    self.show_error(f"Жами {new_qty} талаб қилинмоқда, фақат {available:.2f} мавжуд!")
                    return
                item['quantity'] = new_qty
                if dialog:
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
        
        if dialog:
            dialog.dismiss()
        self.update_cart_display()
        self.load_products()
    
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.update_cart_display()
    
    def clear_cart(self):
        if not self.cart:
            self.show_warning("Саватча аллақачон бўш!")
            return
        
        self.show_confirm(
            "Саватчани бўшатишга ишончингиз комилми?",
            on_yes=self._do_clear_cart
        )
    
    def _do_clear_cart(self, confirmed):
        if confirmed:
            self.cart = []
            self.update_cart_display()
            self.show_info("Саватча бўшатилди")
    
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
            self.show_error("Саватча бўш!")
            return
        
        if payment_type == 'credit':
            self.process_credit_only()
            return
        
        try:
            for item in self.cart:
                result, message = self.sales_manager.add_sale(
                    item['id'], item['quantity'], item['price'],
                    payment_type, "", self.operator, item['measurement_type']
                )
                if not result:
                    self.show_error(f"{item['name']}: {message}")
                    return
            
            self._save_receipt_data(
                payment_type=payment_type,
                cash=self.total_amount if payment_type == 'cash' else 0,
                card=self.total_amount if payment_type == 'card' else 0
            )
            
            pay_text = get_payment_name(payment_type)
            msg = f"💵 Жами: {self.total_amount:,.0f} сўм\n💳 Тўлов: {pay_text}"
            self._finish_sale(msg)
            
        except Exception as e:
            self.show_error(f"Тўловда хатолик: {str(e)}")
    
    def process_credit_only(self):
        if not self.cart:
            self.show_error("Саватча бўш!")
            return
        
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=250
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
            hint_text="Муддат (кун)",
            text="30",
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
                MDRectangleFlatButton(text="ТАСДИҚЛАШ", on_release=lambda x: self._confirm_credit(
                    dialog,
                    customer_input.text.strip(),
                    phone_input.text.strip(),
                    int(deadline_input.text or 30)
                ))
            ]
        )
        dialog.open()
    
    def _confirm_credit(self, dialog, customer, phone, deadline_days):
        if not customer:
            self.show_error("Мижоз номи киритилиши шарт!")
            return
        
        try:
            for item in self.cart:
                item_total = item['price'] * item['quantity']
                result, message = self.credit_manager.add_credit_sale(
                    customer, phone, item['id'], item['quantity'],
                    item_total, item['measurement_type'], deadline_days
                )
                if not result:
                    self.show_error(f"{item['name']}: {message}")
                    return
            
            self._save_receipt_data(
                payment_type='credit',
                customer_name=customer,
                credit=self.total_amount
            )
            
            dialog.dismiss()
            msg = f"💵 Жами: {self.total_amount:,.0f} сўм\n📅 Муддат: {deadline_days} кун\n👤 Мижоз: {customer}"
            self._finish_sale(msg)
            
        except Exception as e:
            self.show_error(f"Қарзга сотишда хатолик: {str(e)}")
    
    def process_mixed_payment(self):
        if not self.cart:
            self.show_error("Саватча бўш!")
            return
        
        screen_height = Window.height
        dialog_height = min(520, screen_height * 0.75)
        
        content = MDBoxLayout(
            orientation='vertical', spacing=8, padding=15,
            size_hint_y=None, height=dialog_height
        )
        
        content.add_widget(MDLabel(
            text=f"💵 Жами: {self.total_amount:,.0f} сўм\n📌 Келишув бўйича тўлов мумкин",
            halign="center", font_style="H6",
            size_hint_y=None, height=60
        ))
        
        negotiated_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=45)
        negotiated_layout.add_widget(MDLabel(text="Келишув:", halign="center", size_hint_x=0.3))
        negotiated_input = MDTextField(
            hint_text="Келишилган сумма",
            input_filter='float',
            text=str(self.total_amount),
            size_hint_x=0.7, font_size="14sp"
        )
        negotiated_layout.add_widget(negotiated_input)
        content.add_widget(negotiated_layout)
        
        paid_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=45)
        paid_layout.add_widget(MDLabel(text="Мижоз пули:", halign="center", size_hint_x=0.3))
        paid_input = MDTextField(
            hint_text="Мижоз берган сумма",
            input_filter='float',
            text="0",
            size_hint_x=0.7, font_size="14sp"
        )
        paid_layout.add_widget(paid_input)
        content.add_widget(paid_layout)
        
        cash_input = MDTextField(
            hint_text="Нақд суммаси",
            input_filter='float',
            text="0", font_size="14sp",
            size_hint_y=None, height=48
        )
        content.add_widget(cash_input)
        
        card_input = MDTextField(
            hint_text="Пластик суммаси",
            input_filter='float',
            text="0", font_size="14sp",
            size_hint_y=None, height=48
        )
        content.add_widget(card_input)
        
        customer_input = MDTextField(
            hint_text="Мижоз номи (қарзга бўлса)",
            font_size="14sp",
            size_hint_y=None, height=48
        )
        content.add_widget(customer_input)
        
        deadline_input = MDTextField(
            hint_text="Муддат (кун)",
            text="30",
            input_filter='int',
            font_size="14sp",
            size_hint_y=None, height=48
        )
        content.add_widget(deadline_input)
        
        dialog = MDDialog(
            title="💳 МОСЛАШУВЧАН ТЎЛОВ",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ТЎЛОВ", on_release=lambda x: self._confirm_flexible_payment(
                    dialog,
                    paid_input.text,
                    cash_input.text,
                    card_input.text,
                    customer_input.text.strip(),
                    int(deadline_input.text or 30),
                    negotiated_input.text
                ))
            ]
        )
        dialog.open()
    
    def _confirm_flexible_payment(self, dialog, paid_str, cash_str, card_str, 
                                   customer_name, deadline_days, negotiated_str):
        try:
            paid = float(paid_str) if paid_str else 0
            cash = float(cash_str) if cash_str else 0
            card = float(card_str) if card_str else 0
            negotiated = float(negotiated_str) if negotiated_str else self.total_amount
            
            if negotiated <= 0:
                negotiated = self.total_amount
            
            if negotiated > self.total_amount:
                self.show_error(f"Келишув суммаси жамидан ({self.total_amount:,.0f}) катта бўлмаслиги керак!")
                return
            
            change_amount = 0
            remaining = negotiated
            
            if paid > 0:
                if paid >= negotiated:
                    change_amount = paid - negotiated
                    cash = negotiated
                    card = 0
                    remaining = 0
                else:
                    remaining = negotiated - paid
                    cash = paid
                    card = 0
                    change_amount = 0
            else:
                total_paid = cash + card
                if total_paid == 0:
                    self.show_error("Ҳеч қандай тўлов киритилмаган!")
                    return
                remaining = negotiated - total_paid
            
            if remaining > 0:
                if not customer_name:
                    self.show_error("Қолган суммани қарзга ёзиш учун мижоз номини киритинг!")
                    return
                
                for item in self.cart:
                    item_total = item['price'] * item['quantity']
                    item_remaining = (item_total / self.total_amount) * remaining if self.total_amount > 0 else 0
                    
                    if item_remaining > 0:
                        result, message = self.credit_manager.add_credit_sale(
                            customer_name, "", item['id'], item['quantity'],
                            item_remaining, item['measurement_type'], deadline_days
                        )
                        if not result:
                            self.show_error(f"{item['name']}: {message}")
                            return
            
            for item in self.cart:
                result, message = self.sales_manager.add_sale(
                    item['id'], item['quantity'], item['price'],
                    'mixed', customer_name if remaining > 0 else "",
                    self.operator, item['measurement_type']
                )
                if not result:
                    self.show_error(f"{item['name']}: {message}")
                    return
            
            self._save_receipt_data(
                payment_type='mixed',
                customer_name=customer_name if remaining > 0 else "",
                cash=cash,
                card=card,
                credit=remaining if remaining > 0 else 0,
                paid_amount=paid if paid > 0 else 0,
                change_amount=change_amount,
                negotiated_price=negotiated
            )
            
            payment_details = []
            if cash > 0:
                payment_details.append(f"Нақд: {cash:,.0f} сўм")
            if card > 0:
                payment_details.append(f"Пластик: {card:,.0f} сўм")
            if remaining > 0:
                payment_details.append(f"Қарзга: {remaining:,.0f} сўм")
                payment_details.append(f"Мижоз: {customer_name}")
            if change_amount > 0:
                payment_details.append(f"Қайтарим: {change_amount:,.0f} сўм")
            
            msg = f"💵 Жами: {self.total_amount:,.0f} сўм\n"
            if negotiated != self.total_amount:
                msg += f"📝 Келишув: {negotiated:,.0f} сўм\n"
            msg += "📋 Тўлов:\n" + "\n".join(payment_details)
            
            dialog.dismiss()
            self._finish_sale(msg)
            
        except ValueError:
            self.show_error("Тўғри сон киритинг!")
        except Exception as e:
            self.show_error(f"Тўловда хатолик: {str(e)}")
    
    # ========== ЧЕК ==========
    def _save_receipt_data(self, **kwargs):
        self.last_receipt_data = {
            'cart_items': [item.copy() for item in self.cart],
            'total_amount': self.total_amount,
            'payment_type': kwargs.get('payment_type', 'cash'),
            'customer_name': kwargs.get('customer_name', ''),
            'cash': kwargs.get('cash', 0),
            'card': kwargs.get('card', 0),
            'credit': kwargs.get('credit', 0),
            'paid_amount': kwargs.get('paid_amount', 0),
            'change_amount': kwargs.get('change_amount', 0),
            'negotiated_price': kwargs.get('negotiated_price', 0)
        }
    
    def _finish_sale(self, message):
        self.cart = []
        self.update_cart_display()
        self.load_products()
        
        self.show_success_with_buttons(
            message,
            buttons_config=[
                {'text': '📄 ЧЕКНИ КЎРСАТ', 'callback': self._show_receipt_preview},
                {'text': '🖨️ ЧОП ЭТИШ', 'callback': self._print_receipt},
                {'text': 'OK', 'dismiss': True}
            ]
        )
    
    def _show_receipt_preview(self):
        try:
            data = self.last_receipt_data
            if not data:
                self.show_error("Чек маълумотлари топилмади!")
                return
            
            result, filename = self.printer_manager.create_receipt_pdf(
                data['cart_items'], data['total_amount'], data['payment_type'],
                data['customer_name'], data['cash'], data['card'], data['credit'],
                data['paid_amount'], data['change_amount'], data['negotiated_price']
            )
            
            if not result:
                self.show_error(filename)
                return
            
            os.startfile(filename)
            self.show_info(
                f"Чек PDF файли очилди!\n\n"
                f"📁 Файл: {os.path.basename(filename)}\n\n"
                f"💡 Чоп этиш учун Ctrl+P босинг"
            )
            
        except Exception as e:
            self.show_error(f"Чекни кўрсатишда хатолик: {str(e)}")
    
    def _print_receipt(self):
        try:
            data = self.last_receipt_data
            if not data:
                self.show_error("Чек маълумотлари топилмади!")
                return
            
            result, message = self.printer_manager.print_receipt(
                data['cart_items'], data['total_amount'], data['payment_type'],
                data['customer_name'], data['cash'], data['card'], data['credit'],
                data['paid_amount'], data['change_amount'], data['negotiated_price']
            )
            
            if result:
                self.show_success(message)
            else:
                result2, filename = self.printer_manager.create_receipt_pdf(
                    data['cart_items'], data['total_amount'], data['payment_type'],
                    data['customer_name'], data['cash'], data['card'], data['credit'],
                    data['paid_amount'], data['change_amount'], data['negotiated_price']
                )
                if result2:
                    os.startfile(filename)
                    self.show_info(
                        f"Чек PDF очилди!\n\n"
                        f"📁 Файл: {os.path.basename(filename)}\n\n"
                        f"💡 Чоп этиш учун Ctrl+P босинг"
                    )
                else:
                    self.show_error(message)
            
        except Exception as e:
            self.show_error(f"Чоп этишда хатолик: {str(e)}")