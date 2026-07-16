# modules/label_printer.py
import os
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from config import SHOP_NAME, LABEL_FOOTER, LABEL_SIZES
import subprocess
import platform
import json

from config import SHOP_NAME, LABEL_FOOTER

try:
    import qrcode
    from PIL import Image
    import io
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("⚠️ QR-код учун qrcode ўрнатилмаган! pip install qrcode pillow")


class LabelPrinter:
    # __init__ да:
    def __init__(self, shop_name=None):
        self.temp_dir = tempfile.gettempdir()
        self.shop_name = shop_name or SHOP_NAME
        self.font_name = self._register_font()
        self.os_name = platform.system()
        self.label_sizes = LABEL_SIZES  # config.py дан олиш
        
        self.label_sizes = {
            '30x50': {'width': 50, 'height': 30, 'name': '30x50 (Кундаланг)', 'landscape': True},
            'small': {'width': 40, 'height': 30, 'name': 'Кичик', 'landscape': False},
            '50x30': {'width': 50, 'height': 30, 'name': 'Стандарт', 'landscape': False},
            'medium': {'width': 58, 'height': 40, 'name': 'Ўрта', 'landscape': False},
            'large': {'width': 80, 'height': 50, 'name': 'Катта', 'landscape': False},
            'custom': {'width': 60, 'height': 40, 'name': 'Мослаштирилган', 'landscape': False},
        }
        
        # Фақат қора-оқ ранглар
        self.colors = {
            'black': colors.black,
            'white': colors.white,
            'grey': colors.HexColor('#666666'),
            'light_grey': colors.HexColor('#999999'),
        }
    
    def _register_font(self):
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/verdana.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/timesbd.ttf",
            "C:/Windows/Fonts/georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                    return 'CustomFont'
                except:
                    continue
        return 'Helvetica'
    
    def _generate_qr_code(self, product_id, size=400):
        """QR-код яратиш - АНИҚ ВА КАТТА"""
        if not QRCODE_AVAILABLE:
            return None
        
        try:
            qr_text = str(product_id)
            
            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=12,
                border=2,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # ҚОРА-ОҚ (аниқ)
            qr_img = qr.make_image(
                fill_color="black",
                back_color="white"
            ).convert('RGB')
            
            qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
            
            img_bytes = io.BytesIO()
            qr_img.save(img_bytes, format='PNG', dpi=(300, 300))
            img_bytes.seek(0)
            
            return ImageReader(img_bytes)
            
        except Exception as e:
            print(f"QR-код яратишда хатолик: {e}")
            return None
    
    def get_label_size(self, label_size):
        if label_size in self.label_sizes:
            return self.label_sizes[label_size]
        return self.label_sizes['50x30']
    
    def create_label_pdf(self, product_data, label_size='50x30', copies=1):
        """Этикетка PDF - ҚОРА-ОҚ, ТАРТИБЛИ"""
        size = self.get_label_size(label_size)
        is_landscape = size.get('landscape', False)
        
        if is_landscape:
            width = size['height'] * mm
            height = size['width'] * mm
            page_size = landscape((width, height))
        else:
            width = size['width'] * mm
            height = size['height'] * mm
            page_size = (width, height)
        
        filename = os.path.join(
            self.temp_dir, 
            f"label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        c = canvas.Canvas(filename, pagesize=page_size)
        actual_width, actual_height = page_size
        
        # ===== ФОН (ОҚ) =====
        c.setFillColor(colors.white)
        c.rect(0, 0, actual_width, actual_height, fill=True)
        
        # ===== ЧЕГАРА (КУЛРАНГ) =====
        margin = 2.5 * mm
        c.setStrokeColor(self.colors['grey'])
        c.setLineWidth(0.3)
        c.rect(margin, margin, actual_width - 2*margin, actual_height - 2*margin)
        
        # ===== ЮҚОРИ ҚИСМИ =====
        # Бренд (марказ)
        c.setFont(self.font_name, 8)
        c.setFillColor(self.colors['black'])
        shop_name = product_data.get('shop_name', self.shop_name)
        c.drawCentredString(actual_width/2, actual_height - 5*mm, f"✦ {shop_name} ✦")
        
        # Сана (ўнг томон)
        c.setFont(self.font_name, 6)
        c.setFillColor(self.colors['grey'])
        c.drawRightString(actual_width - 4*mm, actual_height - 4*mm, 
                         datetime.now().strftime('%d.%m.%Y'))
        
        # ===== ЎРТА ҚИСМИ (МАҲСУЛОТ) =====
        # Маҳсулот номи
        c.setFont(self.font_name, 11 if not is_landscape else 9)
        c.setFillColor(self.colors['black'])
        name = product_data.get('name', '')[:22]
        c.drawString(4*mm, actual_height - 9*mm, name)
        
        # Нарх (катта)
        c.setFont(self.font_name, 15 if not is_landscape else 15)
        c.setFillColor(self.colors['black'])
        price = product_data.get('price', 0)
        c.drawString(4*mm, actual_height - 17*mm, f"{price:,.0f} so'm")
        
        # ===== QR-КОД =====
        qr_size_mm = 15 if not is_landscape else 13
        qr_size = qr_size_mm * mm
        
        qr_x = actual_width - qr_size - 4*mm
        qr_y = 4*mm
        
        product_id = product_data.get('product_id', 0)
        qr_image = self._generate_qr_code(product_id, int(qr_size_mm * 4))
        if qr_image:
            try:
                c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
            except:
                pass
        
        # ===== ШТРИХ-КОД (QR КОД ОСТИДА) =====
        barcode = product_data.get('barcode', '')
        if barcode:
            c.setFont(self.font_name, 5)
            c.setFillColor(self.colors['grey'])
            c.drawRightString(actual_width - 4*mm, 4*mm, f"Kod: {barcode[:15]}")
        
        # ===== ФУТЕР (ПАСТДА) =====
        c.setFont(self.font_name, 5)
        c.setFillColor(self.colors['grey'])
        c.drawCentredString(actual_width/2, 3*mm, LABEL_FOOTER[:30])
        
        c.save()
        return filename
    
    def create_multiple_labels(self, products_data, label_size='50x30'):
        """Бир нечта этикеткани битта PDF га жойлаш"""
        size = self.get_label_size(label_size)
        is_landscape = size.get('landscape', False)
        
        if is_landscape:
            width = size['height'] * mm
            height = size['width'] * mm
            actual_width, actual_height = landscape((width, height))
        else:
            width = size['width'] * mm
            height = size['height'] * mm
            actual_width, actual_height = width, height
        
        page_width, page_height = A4
        cols = int(page_width // (actual_width + 3*mm))
        rows = int(page_height // (actual_height + 3*mm))
        labels_per_page = cols * rows
        
        filename = os.path.join(
            self.temp_dir, 
            f"labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        c = canvas.Canvas(filename, pagesize=A4)
        
        for idx, product in enumerate(products_data):
            if idx > 0 and idx % labels_per_page == 0:
                c.showPage()
            
            page_idx = idx % labels_per_page
            row = page_idx // cols
            col = page_idx % cols
            
            x = 3*mm + col * (actual_width + 3*mm)
            y = page_height - 3*mm - (row + 1) * (actual_height + 3*mm)
            
            self._draw_label_on_page(c, product, x, y, actual_width, actual_height, is_landscape)
        
        c.save()
        return filename
    
    def _draw_label_on_page(self, c, product_data, x, y, width, height, is_landscape):
        """Бетга этикетка чизиш"""
        # Фон
        c.setFillColor(colors.white)
        c.rect(x, y, width, height, fill=True)
        
        # Чегара
        margin = 2 * mm
        c.setStrokeColor(self.colors['grey'])
        c.setLineWidth(0.3)
        c.rect(x + margin, y + margin, width - 2*margin, height - 2*margin)
        
        # Бренд (марказ)
        c.setFont(self.font_name, 6)
        c.setFillColor(self.colors['black'])
        shop_name = product_data.get('shop_name', self.shop_name)
        c.drawCentredString(x + width/2, y + height - 3.5*mm, f"✦ {shop_name} ✦")
        
        # Сана
        c.setFont(self.font_name, 4)
        c.setFillColor(self.colors['grey'])
        c.drawRightString(x + width - 3*mm, y + height - 3.5*mm, 
                         datetime.now().strftime('%d.%m.%Y'))
        
        # Маҳсулот номи
        c.setFont(self.font_name, 8 if not is_landscape else 7)
        c.setFillColor(self.colors['black'])
        name = product_data.get('name', '')[:18]
        c.drawString(x + 3*mm, y + height - 7.5*mm, name)
        
        # Нарх
        c.setFont(self.font_name, 16 if not is_landscape else 13)
        c.setFillColor(self.colors['black'])
        price = product_data.get('price', 0)
        c.drawString(x + 3*mm, y + height - 14*mm, f"{price:,.0f}")
        
        # QR-код
        qr_size = 11 * mm
        product_id = product_data.get('product_id', 0)
        qr_image = self._generate_qr_code(product_id, 140)
        if qr_image:
            qr_x = x + width - qr_size - 3*mm
            qr_y = y + 3*mm
            try:
                c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
            except:
                pass
        
        # Штрих-код
        barcode = product_data.get('barcode', '')
        if barcode:
            c.setFont(self.font_name, 4)
            c.setFillColor(self.colors['grey'])
            c.drawString(x + 3*mm, y + 3*mm, barcode[:12])
        
        # Футер
        c.setFont(self.font_name, 4)
        c.setFillColor(self.colors['grey'])
        c.drawCentredString(x + width/2, y + 3*mm, LABEL_FOOTER[:20])
    
    def print_label(self, product_data, label_size='50x30', copies=1):
        if copies > 1:
            products_list = [product_data] * copies
            filename = self.create_multiple_labels(products_list, label_size)
        else:
            filename = self.create_label_pdf(product_data, label_size)
        return self._print_pdf(filename)
    
    def print_labels_batch(self, products_list, label_size='50x30'):
        filename = self.create_multiple_labels(products_list, label_size)
        return self._print_pdf(filename)
    
    def _print_pdf(self, filename):
        try:
            if self.os_name == 'Windows':
                try:
                    import win32api
                    win32api.ShellExecute(0, "print", filename, None, ".", 0)
                    return True, "✅ Этикетка чоп этиш жараёни бошланди!"
                except:
                    pass
                
                try:
                    subprocess.run([
                        "powershell", 
                        "-Command", 
                        f"Start-Process -FilePath '{filename}' -Verb Print"
                    ], timeout=30)
                    return True, "✅ Этикетка чоп этиш жараёни бошланди! (PowerShell)"
                except:
                    pass
                
                os.startfile(filename)
                return True, f"📄 Этикетка PDF файли очилди."
            else:
                os.startfile(filename)
                return True, "📄 Этикетка PDF файли очилди."
        except Exception as e:
            return False, f"❌ Чоп этишда хатолик: {str(e)}"
    
    def preview_label(self, product_data, label_size='50x30'):
        filename = self.create_label_pdf(product_data, label_size)
        try:
            os.startfile(filename)
            return True, f"📄 Этикетка очилди: {os.path.basename(filename)}"
        except:
            return False, "❌ Этикеткани очиб бўлмади!"