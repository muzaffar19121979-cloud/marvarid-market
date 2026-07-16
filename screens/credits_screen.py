# screens/credits_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

from modules.credits import CreditManager
from screens.dialog_mixin import DialogMixin


class CreditsScreen(Screen, DialogMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.credit_manager = CreditManager()
    
    def on_enter(self):
        self.credit_manager.update_overdue_credits()
        self.load_credits()
    
    def load_credits(self):
        credits = self.credit_manager.get_active_credits()
        self.ids.credit_list.clear_widgets()
        
        if not credits:
            self.ids.credit_list.add_widget(
                MDLabel(
                    text="Ҳеч қандай фаол қарз топилмади",
                    halign="center",
                    theme_text_color="Secondary"
                )
            )
            return
        
        for c in credits:
            name = c[1]
            total = c[4]
            paid = c[5]
            remaining = c[6]
            deadline = c[7]
            status = c[8]
            
            item = TwoLineListItem(
                text=f"{name}: {total:,.0f} сўм | Қолди: {remaining:,.0f}",
                secondary_text=f"Тўланган: {paid:,.0f} | Муддат: {deadline}",
                on_release=lambda x, cid=c[0]: self.show_credit_actions(cid)
            )
            
            if status == 'overdue':
                item.theme_text_color = "Error"
            
            self.ids.credit_list.add_widget(item)
    
    def show_credit_actions(self, credit_id):
        """Қарз амаллари диалоги"""
        self.show_confirm(
            f"Қарз ID: {credit_id}\n\nТўлов қилишни истайсизми?",
            on_yes=lambda: self.show_payment_dialog(credit_id),
            title="Қарз амаллари",
            yes_text="💵 ТЎЛОВ",
            no_text="❌ ЁПИШ"
        )
    
    def show_payment_dialog(self, credit_id):
        """Тўлов диалоги"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=20,
            size_hint_y=None,
            height=150
        )
        
        amount_input = MDTextField(
            hint_text="Тўлов суммаси",
            input_filter='float',
            size_hint_y=None,
            height=48
        )
        content.add_widget(amount_input)
        
        dialog = MDDialog(
            title="💵 Қарз тўлаш",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ТЎЛАШ", on_release=lambda x: self.process_payment(
                    credit_id, amount_input.text, dialog
                ))
            ]
        )
        dialog.open()
    
    def process_payment(self, credit_id, amount_text, dialog):
        """Тўловни қайта ишлаш"""
        try:
            amount = float(amount_text or 0)
            if amount <= 0:
                self.show_error("Сумма 0 дан катта бўлиши керак!")
                return
            
            result, message = self.credit_manager.add_payment(credit_id, amount)
            dialog.dismiss()
            
            if result:
                self.load_credits()
                self.show_success(message)
            else:
                self.show_error(message)
                
        except ValueError:
            self.show_error("Тўғри сумма киритинг!")
        except Exception as e:
            self.show_error(str(e))