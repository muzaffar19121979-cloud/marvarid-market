# screens/report_screen.py
from kivy.uix.screenmanager import Screen
from datetime import datetime

from modules.sales import SalesManager
from modules.cash import CashManager
from modules.credits import CreditManager
from screens.dialog_mixin import DialogMixin


class ReportScreen(Screen, DialogMixin):
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
            text += "=" * 40 + "\n\n"
            text += f"Сана: {today}\n\n"
            
            if sales_total:
                total = sales_total['total'] or 0
                cash = sales_total['cash_total'] or 0
                card = sales_total['card_total'] or 0
                credit = sales_total['credit_total'] or 0
                profit = sales_total['total_profit'] or 0
                
                text += f"💰 Жами: {total:,.0f} сўм\n"
                text += f"💵 Нақд: {cash:,.0f} сўм\n"
                text += f"💳 Пластик: {card:,.0f} сўм\n"
                text += f"📝 Қарз: {credit:,.0f} сўм\n"
                text += f"📈 Фойда: {profit:,.0f} сўм\n\n"
            else:
                text += "💰 Сотувлар: 0 сўм\n\n"
            
            expense_total = expense_total or 0
            text += f"💸 Харажат: {expense_total:,.0f} сўм\n"
            
            net_profit = (sales_total['total_profit'] if sales_total else 0) - expense_total
            text += f"📊 Соф фойда: {net_profit:,.0f} сўм\n\n"
            
            if credit_summary:
                total_debt = credit_summary['total_debt'] or 0
                total_paid = credit_summary['total_paid'] or 0
                remaining = credit_summary['total_remaining'] or 0
                count = credit_summary['total_count'] or 0
                
                text += "📝 ҚАРЗЛАР ҲОЛАТИ\n"
                text += f"   Жами қарзлар: {count} та\n"
                text += f"   Умумий қарз: {total_debt:,.0f} сўм\n"
                text += f"   Тўланган: {total_paid:,.0f} сўм\n"
                text += f"   Қолган: {remaining:,.0f} сўм\n"
            else:
                text += "\n📝 Қарзлар мавжуд эмас"
            
            self.ids.report_label.text = text
            
        except Exception as e:
            self.ids.report_label.text = f"Хатолик: {str(e)}"
            self.show_error(f"Ҳисоботни юклашда хатолик: {str(e)}")