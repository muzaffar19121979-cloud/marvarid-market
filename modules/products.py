# modules/products.py
from database import get_db

class ProductManager:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
    
    def add_product(self, name, barcode, purchase_price, sale_price, quantity, min_quantity=0, measurement_type='dona'):
        if measurement_type not in ('dona', 'kg'):
            measurement_type = 'dona'
        
        query = '''
            INSERT INTO products 
            (name, barcode, purchase_price, sale_price, quantity, min_quantity, measurement_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            self.db.execute(query, (name, barcode, purchase_price, sale_price, quantity, min_quantity, measurement_type))
            return True, "Маҳсулот қўшилди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def get_all_products(self):
        return self.db.fetch_all("SELECT * FROM products ORDER BY name")
    
    def get_product_by_id(self, product_id):
        return self.db.fetch_one("SELECT * FROM products WHERE id = ?", (product_id,))
    
    def get_product_by_id_dict(self, product_id):
        return self.db.fetch_one_dict("SELECT * FROM products WHERE id = ?", (product_id,))
    
    def get_product_by_barcode(self, barcode):
        return self.db.fetch_one("SELECT * FROM products WHERE barcode = ?", (barcode,))
    
    def update_quantity(self, product_id, quantity_change):
        try:
            current = self.db.fetch_one("SELECT quantity FROM products WHERE id = ?", (product_id,))
            if current and current[0] + quantity_change < 0:
                return False, f"Омборда етарли маҳсулот йўқ! Мавжуд: {current[0]}"
            
            self.db.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (quantity_change, product_id))
            return True, "OK"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def update_product(self, product_id, name, barcode, purchase_price, sale_price, min_quantity, measurement_type):
        if measurement_type not in ('dona', 'kg'):
            measurement_type = 'dona'
        
        query = '''
            UPDATE products 
            SET name=?, barcode=?, purchase_price=?, sale_price=?, min_quantity=?, measurement_type=?
            WHERE id=?
        '''
        try:
            self.db.execute(query, (name, barcode, purchase_price, sale_price, min_quantity, measurement_type, product_id))
            return True, "Маҳсулот янгиланди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def delete_product(self, product_id):
        try:
            sales = self.db.fetch_one("SELECT COUNT(*) FROM sales WHERE product_id = ?", (product_id,))
            if sales and sales[0] > 0:
                return False, "Бу маҳсулот сотилган, ўчириб бўлмайди!"
            
            self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return True, "Маҳсулот ўчирилди!"
        except Exception as e:
            return False, f"Хатолик: {str(e)}"
    
    def get_low_stock_products(self):
        return self.db.fetch_all("SELECT * FROM products WHERE quantity <= min_quantity")
    
    def search_product(self, keyword):
        query = "SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ?"
        return self.db.fetch_all(query, (f'%{keyword}%', f'%{keyword}%'))