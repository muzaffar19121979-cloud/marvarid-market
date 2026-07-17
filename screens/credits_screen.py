# screens/credits_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.credits import CreditManager


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.credit_manager = CreditManager()
    
    def on_enter(self):
        self.load_credits()
    
    def load_credits(self):
        credits = self.credit_manager.get_active_credits()
        self.ids.credit_list.clear_widgets()
        
        if not credits:
            self.ids.credit_list.add_widget(
                MDLabel(text="Ҳеч қандай фаол қарз топилмади", halign="center")
            )
            return
        
        for c in credits:
            item = TwoLineListItem(
                text=f"{c[1]}: {c[4]:,.0f} сўм | Қолди: {c[6]:,.0f}",
                secondary_text=f"Тўланган: {c[5]:,.0f} | Муддат: {c[7]}",
                on_release=lambda x, cid=c[0]: self._show_payment_dialog(cid)
            )
            if len(c) > 8 and c[8] == 'overdue':
                item.theme_text_color = "Error"
            self.ids.credit_list.add_widget(item)
    
    def _show_payment_dialog(self, credit_id):
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=150
        )
        
        amount_input = MDTextField(
            hint_text="Тўлов суммаси",
            input_filter='float',
            size_hint_y=None, height=48
        )
        content.add_widget(amount_input)
        
        dialog = MDDialog(
            title="💵 Қарз тўлаш",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ТЎЛАШ", on_release=lambda x: self._process_payment(
                    credit_id, amount_input.text, dialog
                ))
            ]
        )
        dialog.open()
    
    def _process_payment(self, credit_id, amount_text, dialog):
        try:
            amount = float(amount_text or 0)
            if amount <= 0:
                self._show_msg("Хатолик", "Сумма 0 дан катта бўлиши керак!")
                return
            
            result, message = self.credit_manager.add_payment(credit_id, amount)
            dialog.dismiss()
            self.load_credits()
            self._show_msg("✅ Муваффақият" if result else "❌ Хатолик", message)
        except ValueError:
            self._show_msg("Хатолик", "Тўғри сумма киритинг!")
    
    def _show_msg(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()