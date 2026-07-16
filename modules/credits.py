# modules/credits.py
from database import get_db
from datetime import datetime, timedelta

class CreditManager:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
    
    def add_credit_sale(self, customer_name, phone, product_id, quantity, total_amount, measurement_type='dona', deadline_days=30):
        deadline = (datetime.now() + timedelta(days=deadline_days)).strftime('%Y-%m-%d')
        query = '''
            INSERT INTO credit_sales 
            (customer_name, phone, product_id, quantity, total_amount, paid_amount, remaining_amount, deadline, measurement_type)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)
        '''
        try:
            self.db.execute(query, (customer_name, phone, product_id, quantity, total_amount, total_amount, deadline, measurement_type))
            return True, "Қарзга сотилди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def get_active_credits(self):
        return self.db.fetch_all("SELECT * FROM credit_sales WHERE status IN ('active', 'overdue') ORDER BY created_at DESC")
    
    def get_credit_summary(self):
        query = '''
            SELECT 
                COUNT(*) as total_count,
                SUM(total_amount) as total_debt,
                SUM(paid_amount) as total_paid,
                SUM(remaining_amount) as total_remaining
            FROM credit_sales
            WHERE status IN ('active', 'overdue')
        '''
        return self.db.fetch_one_dict(query)
    
    def add_payment(self, credit_id, amount):
        try:
            credit = self.db.fetch_one("SELECT * FROM credit_sales WHERE id = ?", (credit_id,))
            if not credit:
                return False, "Қарз топилмади!"
            
            new_paid = credit[5] + amount
            new_remaining = credit[6] - amount
            
            if new_remaining <= 0:
                self.db.execute("UPDATE credit_sales SET paid_amount=?, remaining_amount=0, status='paid' WHERE id=?", (new_paid, credit_id))
            else:
                self.db.execute("UPDATE credit_sales SET paid_amount=?, remaining_amount=? WHERE id=?", (new_paid, new_remaining, credit_id))
            
            return True, "Тўлов қабул қилинди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def update_overdue_credits(self):
        today = datetime.now().strftime('%Y-%m-%d')
        query = "UPDATE credit_sales SET status='overdue' WHERE status='active' AND deadline < ?"
        self.db.execute(query, (today,))
    
    def search_by_customer(self, name_or_phone):
        query = """
            SELECT * FROM credit_sales 
            WHERE (customer_name LIKE ? OR phone LIKE ?) AND status != 'paid'
        """
        return self.db.fetch_all(query, (f'%{name_or_phone}%', f'%{name_or_phone}%'))