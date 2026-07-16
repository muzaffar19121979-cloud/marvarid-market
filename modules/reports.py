# modules/reports.py
from database import get_db
from datetime import datetime

class ReportManager:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
        
        # Lazy import ва Singleton Database узатиш
        from modules.sales import SalesManager
        from modules.credits import CreditManager
        from modules.cash import CashManager
        from modules.products import ProductManager
        
        self.sales_manager = SalesManager(db=self.db)
        self.credit_manager = CreditManager(db=self.db)
        self.cash_manager = CashManager(db=self.db)
        self.product_manager = ProductManager(db=self.db)
    
    def get_daily_report(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            sales = self.sales_manager.get_daily_sales(date)
            sales_total = self.sales_manager.get_daily_total(date)
            expenses = self.cash_manager.get_daily_expenses(date)
            expense_total = self.cash_manager.get_daily_expense_total(date)
            active_credits = self.credit_manager.get_active_credits()
            credit_summary = self.credit_manager.get_credit_summary()
            low_stock = self.product_manager.get_low_stock_products()
            
            return {
                'date': date,
                'sales': sales,
                'sales_total': sales_total,
                'expenses': expenses,
                'expense_total': expense_total,
                'active_credits': active_credits,
                'credit_summary': credit_summary,
                'low_stock': low_stock,
                'profit': (sales_total['total'] if sales_total else 0) - expense_total
            }
        except Exception as e:
            return {'error': str(e)}