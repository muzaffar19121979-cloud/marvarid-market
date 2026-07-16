# screens/cash_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem

from modules.cash import CashManager
from screens.dialog_mixin import DialogMixin
from config import get_cash_type_name

TYPE_NAMES = {
    'give': 'Бердик',
    'take': 'Олдик',
    'income': 'Кирим',
    'expense': 'Чиқим'
}

class CashScreen(Screen, DialogMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cash_manager = CashManager()
        self.dialog = None
    
    def on_enter(self):
        self.load_cash()
    
    def load_cash(self):
        debts = self.cash_manager.get_all_cash_debts()
        self.ids.cash_list.clear_widgets()
        for d in debts:
            type_text = TYPE_NAMES.get(d[2], d[2])
            desc_text = f" | {d[4]}" if d[4] else ""
            self.ids.cash_list.add_widget(
                OneLineListItem(
                    text=f"{d[1]}: {type_text} {d[3]:,.0f} сўм{desc_text}"
                )
            )
    
    def show_add_dialog(self):
        content = MDBoxLayout(
            MDTextField(
                id='counterparty',
                hint_text="Контрагент",
                size_hint_y=None,
                height=48
            ),
            MDTextField(
                id='amount',
                hint_text="Сумма",
                input_filter='float',
                size_hint_y=None,
                height=48
            ),
            MDTextField(
                id='desc',
                hint_text="Изоҳ",
                size_hint_y=None,
                height=48
            ),
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint_y=None,
            height=220
        )
        
        self.dialog = MDDialog(
            title="Нақд операция қўшиш",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: self.dialog.dismiss()),
                MDRectangleFlatButton(text="ҚЎШИШ", on_release=lambda x: self.add_cash(content))
            ]
        )
        self.dialog.open()
    
    def add_cash(self, content):
        try:
            counterparty = content.ids.counterparty.text.strip()
            amount = float(content.ids.amount.text or 0)
            desc = content.ids.desc.text.strip()
            
            if not counterparty or amount <= 0:
                self.show_error("Тўғри маълумот киритинг!")
                return
            
            result, message = self.cash_manager.add_cash_debt(counterparty, 'give', amount, desc)
            if result:
                self.dialog.dismiss()
                self.load_cash()
                self.show_success("Операция қўшилди!")
            else:
                self.show_error(message)
        except ValueError:
            self.show_error("Сумма тўғри киритилмаган!")
        except Exception as e:
            self.show_error(str(e))
    def load_cash(self):
        debts = self.cash_manager.get_all_cash_debts()
        self.ids.cash_list.clear_widgets()
        for d in debts:
            type_text = get_cash_type_name(d[2])  # CASH_TYPES ўрнига
            desc_text = f" | {d[4]}" if d[4] else ""
            self.ids.cash_list.add_widget(
                OneLineListItem(
                    text=f"{d[1]}: {type_text} {d[3]:,.0f} сўм{desc_text}"
                )
            )