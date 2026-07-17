# screens/cash_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.cash import CashManager


class CashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cash_manager = CashManager()
    
    def on_enter(self):
        self.load_cash()
    
    def load_cash(self):
        debts = self.cash_manager.get_all_cash_debts()
        self.ids.cash_list.clear_widgets()
        
        type_names = {'give': 'Бердик', 'take': 'Олдик', 'income': 'Кирим', 'expense': 'Чиқим'}
        
        for d in debts:
            type_text = type_names.get(d[2], d[2])
            desc = f" | {d[4]}" if d[4] else ""
            self.ids.cash_list.add_widget(
                OneLineListItem(text=f"{d[1]}: {type_text} {d[3]:,.0f} сўм{desc}")
            )
    
    def show_add_dialog(self):
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=10,
            size_hint_y=None, height=220
        )
        
        counterparty_input = MDTextField(hint_text="Контрагент", size_hint_y=None, height=48)
        content.add_widget(counterparty_input)
        
        amount_input = MDTextField(hint_text="Сумма", input_filter='float', size_hint_y=None, height=48)
        content.add_widget(amount_input)
        
        desc_input = MDTextField(hint_text="Изоҳ", size_hint_y=None, height=48)
        content.add_widget(desc_input)
        
        dialog = MDDialog(
            title="Нақд операция қўшиш",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self._add_cash(
                    counterparty_input.text, amount_input.text, desc_input.text, dialog
                ))
            ]
        )
        dialog.open()
    
    def _add_cash(self, counterparty, amount, desc, dialog):
        try:
            if not counterparty.strip():
                self._show_msg("Хатолик", "Контрагент киритинг!")
                return
            
            amt = float(amount or 0)
            if amt <= 0:
                self._show_msg("Хатолик", "Сумма 0 дан катта бўлиши керак!")
                return
            
            result, message = self.cash_manager.add_cash_debt(counterparty.strip(), 'give', amt, desc.strip())
            if result:
                dialog.dismiss()
                self.load_cash()
                self._show_msg("✅ Муваффақият", "Операция қўшилди!")
            else:
                self._show_msg("❌ Хатолик", message)
        except ValueError:
            self._show_msg("Хатолик", "Тўғри сумма киритинг!")
    
    def _show_msg(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()