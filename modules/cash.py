# modules/cash.py
from database import get_db
from datetime import datetime

class CashManager:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
    
    def add_cash_debt(self, counterparty, debt_type, amount, description=""):
        if debt_type not in ('give', 'take', 'income', 'expense'):
            debt_type = 'give'
        
        query = "INSERT INTO cash_debts (counterparty, type, amount, description) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute(query, (counterparty, debt_type, amount, description))
            return True, "Қўшилди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def get_all_cash_debts(self):
        return self.db.fetch_all("SELECT * FROM cash_debts ORDER BY date DESC")
    
    def add_expense(self, category, amount, description, operator="Operator 1"):
        query = "INSERT INTO expenses (category, amount, description, operator) VALUES (?, ?, ?, ?)"
        try:
            self.db.execute(query, (category, amount, description, operator))
            return True, "Харажат қўшилди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def get_daily_expenses(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        return self.db.fetch_all("SELECT * FROM expenses WHERE DATE(expense_date) = ? ORDER BY expense_date DESC", (date,))
    
    def get_daily_expense_total(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        result = self.db.fetch_one("SELECT SUM(amount) FROM expenses WHERE DATE(expense_date) = ?", (date,))
        return result[0] if result and result[0] else 0
    
    def get_expense_categories(self):
        return self.db.fetch_all("SELECT DISTINCT category FROM expenses ORDER BY category")