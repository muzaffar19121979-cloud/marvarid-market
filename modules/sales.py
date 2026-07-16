# modules/sales.py
from database import get_db
from datetime import datetime

class SalesManager:
    def __init__(self, db=None, product_manager=None):
        self.db = db if db is not None else get_db()
        self.product_manager = product_manager
    
    def _get_product_manager(self):
        if self.product_manager is None:
            from modules.products import ProductManager
            self.product_manager = ProductManager(db=self.db)
        return self.product_manager
    
    def add_sale(self, product_id, quantity, sale_price, payment_type, customer_name="", operator="Operator 1", measurement_type='dona'):
        pm = self._get_product_manager()
        product = pm.get_product_by_id(product_id)
        if not product:
            return False, "Маҳсулот топилмади"
        
        if product[5] < quantity:
            return False, f"Омборда етарли маҳсулот йўқ. Мавжуд: {product[5]}"
        
        if measurement_type == 'dona' and quantity != int(quantity):
            return False, "Дона маҳсулот учун бутун сон киритинг!"
        
        total_amount = sale_price * quantity
        
        query = '''
            INSERT INTO sales 
            (product_id, quantity, sale_price, total_amount, payment_type, customer_name, operator, measurement_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            self.db.execute(query, (product_id, quantity, sale_price, total_amount, payment_type, customer_name, operator, measurement_type))
            
            result, msg = pm.update_quantity(product_id, -quantity)
            if not result:
                return False, msg
            
            return True, "Сотинди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def get_daily_sales(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        query = '''
            SELECT s.*, p.name as product_name, p.purchase_price
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE DATE(s.sale_date) = ?
            ORDER BY s.sale_date DESC
        '''
        return self.db.fetch_all(query, (date,))
    
    def get_daily_total(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        query = '''
            SELECT 
                COALESCE(SUM(s.total_amount), 0) as total,
                COALESCE(SUM(CASE WHEN s.payment_type = 'cash' THEN s.total_amount ELSE 0 END), 0) as cash_total,
                COALESCE(SUM(CASE WHEN s.payment_type = 'card' THEN s.total_amount ELSE 0 END), 0) as card_total,
                COALESCE(SUM(CASE WHEN s.payment_type = 'credit' THEN s.total_amount ELSE 0 END), 0) as credit_total,
                COALESCE(SUM((s.sale_price - p.purchase_price) * s.quantity), 0) as total_profit
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE DATE(s.sale_date) = ?
        '''
        return self.db.fetch_one_dict(query, (date,))
    
    def get_sales_by_product(self, product_id, days=30):
        query = """
            SELECT * FROM sales 
            WHERE product_id = ? AND sale_date >= DATE('now', ?) 
            ORDER BY sale_date DESC
        """
        return self.db.fetch_all(query, (product_id, f'-{days} days'))