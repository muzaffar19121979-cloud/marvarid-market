# screens/report_screen.py
from kivy.uix.screenmanager import Screen
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.sales import SalesManager
from modules.cash import CashManager
from modules.credits import CreditManager


class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sales_manager = SalesManager()
        self.cash_manager = CashManager()
        self.credit_manager = CreditManager()
    
    def on_enter(self):
        self.show_report()
    
    def show_report(self):
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            sales_total = self.sales_manager.get_daily_total(today)
            expense_total = self.cash_manager.get_daily_expense_total(today)
            credit_summary = self.credit_manager.get_credit_summary()
            
            text = "📅 КУНЛИК ҲИСОБОТ\n"
            text += "=" * 35 + "\n\n"
            text += f"Сана: {today}\n\n"
            
            if sales_total:
                total = sales_total.get('total', 0) or 0
                cash = sales_total.get('cash_total', 0) or 0
                card = sales_total.get('card_total', 0) or 0
                credit = sales_total.get('credit_total', 0) or 0
                profit = sales_total.get('total_profit', 0) or 0
                
                text += f"💰 Жами: {total:,.0f} сўм\n"
                text += f"💵 Нақд: {cash:,.0f} сўм\n"
                text += f"💳 Пластик: {card:,.0f} сўм\n"
                text += f"📝 Қарз: {credit:,.0f} сўм\n"
                text += f"📈 Фойда: {profit:,.0f} сўм\n\n"
            else:
                text += "💰 Сотувлар: 0 сўм\n\n"
            
            expense_total = expense_total or 0
            text += f"💸 Харажат: {expense_total:,.0f} сўм\n"
            text += f"📊 Соф фойда: {(sales_total.get('total_profit', 0) if sales_total else 0) - expense_total:,.0f} сўм\n\n"
            
            if credit_summary:
                text += "📝 ҚАРЗЛАР ҲОЛАТИ\n"
                text += f"   Жами: {credit_summary.get('total_count', 0) or 0} та\n"
                text += f"   Қарз: {credit_summary.get('total_debt', 0) or 0:,.0f} сўм\n"
                text += f"   Тўланган: {credit_summary.get('total_paid', 0) or 0:,.0f} сўм\n"
            else:
                text += "\n📝 Қарзлар мавжуд эмас"
            
            self.ids.report_label.text = text
            
        except Exception as e:
            self.ids.report_label.text = f"Хатолик: {str(e)}"