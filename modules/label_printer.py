# modules/label_printer.py
import os
import tempfile
from datetime import datetime

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from config import SHOP_NAME


class LabelPrinter:
    """Этикетка яратиш ва чоп этиш"""
    
    def __init__(self, shop_name=None):
        self.shop_name = shop_name or SHOP_NAME
        self.temp_dir = tempfile.gettempdir()
        
        # Этикетка ўлчамлари (мм)
        self.sizes = {
            '30x45': {'width': 45, 'height': 30, 'name': '30x45 мм'},
            '40x30': {'width': 40, 'height': 30, 'name': '40x30 мм'},
            '50x30': {'width': 50, 'height': 30, 'name': '50x30 мм'},
            '58x40': {'width': 58, 'height': 40, 'name': '58x40 мм'},
            '60x40': {'width': 60, 'height': 40, 'name': '60x40 мм'},
            '80x50': {'width': 80, 'height': 50, 'name': '80x50 мм'},
        }
    
    def generate_barcode_image(self, code, width_mm=45, height_mm=25):
        """Штрих-код расмини яратиш"""
        if not BARCODE_AVAILABLE:
            return None, "barcode кутубхонаси йўқ"
        
        try:
            # CODE128 штрих-код
            code128 = barcode.get('code128', str(code), writer=ImageWriter())
            
            # Вақтинчалик файл
            filename = os.path.join(self.temp_dir, f"barcode_{datetime.now().strftime('%H%M%S')}.png")
            
            # Расм ўлчами (300 DPI)
            dpi = 200
            width_px = int(width_mm * dpi / 25.4)
            height_px = int(height_mm * dpi / 25.4)
            
            options = {
                'module_width': 0.2,
                'module_height': height_px * 0.6 / dpi * 25.4,
                'quiet_zone': 1,
                'font_size': 8,
                'text_distance': 3,
                'dpi': dpi
            }
            
            code128.save(filename, options=options)
            return filename, "OK"
            
        except Exception as e:
            return None, str(e)
    
    def create_label_image(self, product_name, price, barcode_code, 
                          size='30x45', measurement_type='dona'):
        """Этикетка расмини яратиш"""
        if not PIL_AVAILABLE:
            return None, "PIL кутубхонаси йўқ"
        
        try:
            size_config = self.sizes.get(size, self.sizes['30x45'])
            width_mm = size_config['width']
            height_mm = size_config['height']
            
            dpi = 200
            width_px = int(width_mm * dpi / 25.4)
            height_px = int(height_mm * dpi / 25.4)
            
            # Оқ фон
            img = Image.new('RGB', (width_px, height_px), 'white')
            draw = ImageDraw.Draw(img)
            
            # Шрифтлар (кичик ўлчамда)
            try:
                font_small = ImageFont.truetype("arial.ttf", 10)
                font_medium = ImageFont.truetype("arial.ttf", 12)
                font_large = ImageFont.truetype("arialbd.ttf", 16)
            except Exception:
                font_small = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_large = ImageFont.load_default()
            
            # Do'kon номи
            draw.text((5, 2), self.shop_name, fill='black', font=font_small)
            
            # Чизиқ
            draw.line([(5, 16), (width_px - 5, 16)], fill='black', width=1)
            
            # Маҳсулот номи
            unit = 'кг' if measurement_type == 'kg' else 'дона'
            draw.text((5, 20), product_name[:20], fill='black', font=font_medium)
            
            # Нарх
            draw.text((5, 38), f"{price:,.0f} сўм / {unit}", fill='black', font=font_large)
            
            # Штрих-код
            barcode_img, msg = self.generate_barcode_image(barcode_code, width_mm - 6, 10)
            if barcode_img:
                bc = Image.open(barcode_img)
                bc = bc.resize((width_px - 10, 40))
                img.paste(bc, (5, height_px - 50))
                os.remove(barcode_img)
            
            # Сана
            draw.text((5, height_px - 12), datetime.now().strftime('%d.%m.%Y'), fill='black', font=font_small)
            
            # Сақлаш
            filename = os.path.join(self.temp_dir, f"label_{datetime.now().strftime('%H%M%S')}.png")
            img.save(filename, 'PNG')
            return filename, "OK"
            
        except Exception as e:
            return None, str(e)
    
    def get_label_preview_text(self, product_name, price, barcode_code, 
                               measurement_type='dona'):
        """Этикетка матнли кўриниши"""
        unit = 'кг' if measurement_type == 'kg' else 'дона'
        
        text = (
            f"✦ {self.shop_name} ✦\n"
            f"─────────────────────\n"
            f"  {product_name[:18]}\n"
            f"  {price:,.0f} сўм / {unit}\n"
            f"─────────────────────\n"
            f"  Штрих-код: {barcode_code}\n"
            f"─────────────────────\n"
            f"  {datetime.now().strftime('%d.%m.%Y')}\n"
        )
        return text