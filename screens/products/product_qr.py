# screens/products/product_qr.py
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

try:
    from modules.qr_scanner import BarcodeScanner
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    BarcodeScanner = None


class ProductQRMixin:
    """QR код билан ишлаш"""
    
    def show_scan_dialog(self):
        """QR код ўқиш диалоги"""
        if not QR_AVAILABLE:
            self._show_message("⚠️ Маълумот",
                "QR сканер учун OpenCV ўрнатилмаган!\n\nЎрнатиш учун:\npip install opencv-python")
            return
        
        content = MDBoxLayout(
            orientation='vertical', spacing=10, padding=20,
            size_hint_y=None, height=350
        )
        
        content.add_widget(MDLabel(
            text="📷 QR-кодни ўқиш усулини танланг:\n\n"
                 "📌 СКАНЕР (клавиатура):\n"
                 "   - Матн майдонига курсорни қўйинг\n"
                 "   - QR-кодни сканер қилинг\n\n"
                 "📷 КАМЕРА:\n"
                 "   - Камера очилади\n"
                 "   - QR-кодни камерага кўрсатинг",
            halign="center", font_style="Body1"
        ))
        
        scan_input = MDTextField(
            hint_text="🔍 Сканер орқали ўқиш...",
            font_size="16sp", mode="round", multiline=False,
            size_hint_y=None, height=48
        )
        scan_input.bind(text=self._on_scanner_input)
        content.add_widget(scan_input)
        
        dialog = MDDialog(
            title="📷 QR КОД ЎҚИШ",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="📷 КАМЕРА", on_release=lambda x: self._start_camera_scan(dialog)),
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()
    
    def _on_scanner_input(self, instance, value):
        """Сканердан келган маълумотни қайта ишлаш"""
        if not value or len(value) < 1:
            return
        
        try:
            product_id = int(value.strip())
            product = self.product_manager.get_product_by_id(product_id)
            
            if product:
                self.show_product_actions(product)
                instance.text = ""
            else:
                self._show_message("Хатолик", f"ID {product_id} бўйича маҳсулот топилмади!")
        except ValueError:
            if QR_AVAILABLE and self.barcode_scanner:
                parsed_data = self.barcode_scanner.parse_scanner_input(value)
                if parsed_data and parsed_data.get('name'):
                    self._show_parsed_data(parsed_data)
    
    def _start_camera_scan(self, dialog):
        """Камера орқали сканерлаш"""
        if not QR_AVAILABLE or not self.barcode_scanner:
            dialog.dismiss()
            self._show_message("Хатолик", "QR сканер мавжуд эмас!")
            return
        
        dialog.dismiss()
        
        import threading
        def scan_thread():
            try:
                raw_data, message = self.barcode_scanner.scan_from_camera()
                if raw_data:
                    parsed_data = self.barcode_scanner.parse_data(raw_data)
                    Clock.schedule_once(lambda dt: self._show_parsed_data(parsed_data), 0)
                else:
                    Clock.schedule_once(lambda dt: self._show_message("Маълумот", message), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_message("Хатолик", str(e)), 0)
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def _show_parsed_data(self, parsed_data):
        """Парс қилинган маълумотни кўрсатиш"""
        if not parsed_data.get('name'):
            return
        
        content = self._build_product_form()
        content.name_input.text = parsed_data.get('name', '')
        content.barcode_input.text = parsed_data.get('barcode', '')
        content.purchase_input.text = str(parsed_data.get('purchase_price', 0))
        content.sale_input.text = str(parsed_data.get('price', 0))
        content.quantity_input.text = str(parsed_data.get('quantity', 1))
        
        if parsed_data.get('measurement_type') == 'kg':
            content.kg_check.active = True
            content.dona_check.active = False
        
        dialog = MDDialog(
            title="📥 QR-коддан маҳсулот кирим қилиш",
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(text="БЕКОР", on_release=lambda x: dialog.dismiss()),
                MDRectangleFlatButton(text="КИРИМ ҚИЛИШ", on_release=lambda x: self._add_product(content, dialog))
            ]
        )
        dialog.open()