# type: ignore
# database.py - Singleton паттерн билан
import sqlite3
import os

_db_instance = None

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            # Платформага қараб тўғри йўлни аниқлаш
            try:
                from kivy.utils import platform as kv_platform
                if kv_platform == 'android':
                    try:
                        from android.storage import app_storage_path
                        db_dir = app_storage_path()
                    except ImportError:
                        # Android Storage API мавжуд бўлмаса, апк папкасини ишлатиш
                        db_dir = os.path.dirname(os.path.abspath(__file__))
                else:
                    db_dir = os.path.dirname(os.path.abspath(__file__))
            except ImportError:
                db_dir = os.path.dirname(os.path.abspath(__file__))
            
            db_path = os.path.join(db_dir, 'dukon.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                barcode TEXT UNIQUE,
                purchase_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                quantity REAL DEFAULT 0,
                min_quantity REAL DEFAULT 0,
                measurement_type TEXT DEFAULT 'dona' CHECK(measurement_type IN ('dona', 'kg')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity REAL,
                sale_price REAL,
                total_amount REAL,
                payment_type TEXT,
                customer_name TEXT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                operator TEXT,
                measurement_type TEXT DEFAULT 'dona',
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT,
                product_id INTEGER,
                quantity REAL,
                total_amount REAL,
                paid_amount REAL DEFAULT 0,
                remaining_amount REAL,
                deadline DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                measurement_type TEXT DEFAULT 'dona',
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                counterparty TEXT NOT NULL,
                type TEXT CHECK(type IN ('give', 'take', 'income', 'expense')),
                amount REAL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                description TEXT,
                expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                operator TEXT
            )
        ''')
        
        # Индекслар
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_credit_customer ON credit_sales(customer_name, phone)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date)')
        
        self.conn.commit()
    
    def execute(self, query, params=(), commit=True):
        try:
            self.cursor.execute(query, params)
            if commit:
                self.conn.commit()
            return self.cursor
        except Exception as e:
            print(f"Database execute error: {e}")
            raise
    
    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_all_dict(self, query, params=()):
        """Сўзлик кўринишида қайтариш"""
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        if not rows:
            return []
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def fetch_one_dict(self, query, params=()):
        """Битта ёзувни сўзлик кўринишида қайтариш"""
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))
    
    def close(self):
        if self.conn:
            self.conn.close()


def get_db():
    """Database Singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def close_db():
    """Singleton'ни ёпиш"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None