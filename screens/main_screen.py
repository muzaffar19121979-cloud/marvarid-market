from kivy.uix.screenmanager import Screen

class MainScreen(Screen):
    def open_sales(self):
        self.manager.current = 'sales'
    def open_products(self):
        self.manager.current = 'products'
    def open_credits(self):
        self.manager.current = 'credits'
    def open_cash(self):
        self.manager.current = 'cash'
    def open_report(self):
        self.manager.current = 'report'