# modules/printer.py
import os
import tempfile
from datetime import datetime
import platform
import subprocess

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A6, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import win32api
    import win32print
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import asyncio
    from bleak import BleakScanner, BleakClient
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

from config import (
    SHOP_NAME, SHOP_ADDRESS, SHOP_PHONE, SHOP_WEBSITE,
    RECEIPT_WIDTH, LABEL_WIDTH, LABEL_HEIGHT,
    PRINTER_TYPE, BLUETOOTH_PRINTER_NAME, PRINTER_ENCODING,
    RECEIPT_SHOW_LOGO, RECEIPT_SHOW_ADDRESS, RECEIPT_SHOW_PHONE,
    RECEIPT_SHOW_WEBSITE, RECEIPT_SHOW_OPERATOR, RECEIPT_SHOW_FOOTER,
    RECEIPT_FOOTER, OPERATOR_NAME,
    FONT_PATHS, SUMATRA_PATHS
)

_font_registered = False
_font_name = 'Helvetica'


class BluetoothPrinter:
    """Bluetooth принтер билан ишлаш"""
    
    def __init__(self, device_name="HERELABEL"):
        self.device_name = device_name
        self.client = None
        self.address = None
        self.write_char_uuid = None
    
    def discover_device(self):
        if not BLEAK_AVAILABLE:
            return False
        
        try:
            async def scan():
                devices = await BleakScanner.discover(timeout=10)
                for device in devices:
                    if device.name and self.device_name.lower() in device.name.lower():
                        self.address = device.address
                        return True
                return False
            
            return asyncio.run(scan())
        except Exception as e:
            print(f"❌ Қидиришда хатолик: {e}")
            return False
    
    def connect(self):
        if not BLEAK_AVAILABLE:
            return False
        
        if self.client and self.client.is_connected:
            return True
        
        if not self.address:
            if not self.discover_device():
                return False
        
        try:
            async def connect_device():
                self.client = BleakClient(self.address)
                await self.client.connect()
                
                services = await self.client.get_services()
                for service in services:
                    for char in service.characteristics:
                        if 'write' in char.properties or 'write-without-response' in char.properties:
                            self.write_char_uuid = char.uuid
                            return True
                return False
            
            result = asyncio.run(connect_device())
            if result:
                self._send_raw(b'\x1B' + b'@')
                print(f"✅ Принтерга уланилди: {self.device_name}")
            return result
        except Exception as e:
            print(f"❌ Уланишда хатолик: {e}")
            return False
    
    def disconnect(self):
        if self.client and self.client.is_connected:
            try:
                asyncio.run(self.client.disconnect())
            except Exception:
                pass
            finally:
                self.client = None
                self.write_char_uuid = None
    
    def _send_raw(self, data):
        if not self.client or not self.client.is_connected:
            return False
        if not self.write_char_uuid:
            return False
        
        try:
            async def send():
                await self.client.write_gatt_char(self.write_char_uuid, data)
                return True
            return asyncio.run(send())
        except Exception as e:
            print(f"❌ Жўнатишда хатолик: {e}")
            return False
    
    def send_text(self, text):
        return self._send_raw(text.encode(PRINTER_ENCODING, errors='ignore'))
    
    def is_connected(self):
        return self.client is not None and self.client.is_connected


class PrinterManager:
    def __init__(self, shop_name=None):
        self.temp_dir = tempfile.gettempdir()
        self.os_name = platform.system()
        self.shop_name = shop_name or SHOP_NAME
        self.shop_address = SHOP_ADDRESS
        self.shop_phone = SHOP_PHONE
        self.shop_website = SHOP_WEBSITE
        self.font_name = self._register_font()
        self.receipt_width = RECEIPT_WIDTH
        self.label_width = LABEL_WIDTH
        self.label_height = LABEL_HEIGHT
        self.printer_type = PRINTER_TYPE
        self.encoding = PRINTER_ENCODING
        self.operator = OPERATOR_NAME
        
        self.bluetooth = None
        if PRINTER_TYPE == "bluetooth" and BLEAK_AVAILABLE:
            self.bluetooth = BluetoothPrinter(BLUETOOTH_PRINTER_NAME)
        
        self.default_printer = None
        if self.os_name == 'Windows' and WIN32_AVAILABLE:
            try:
                self.default_printer = win32print.GetDefaultPrinter()
            except Exception:
                pass
    
    def _register_font(self):
        global _font_registered, _font_name
        
        if _font_registered:
            return _font_name
        
        if not REPORTLAB_AVAILABLE:
            _font_registered = True
            return _font_name
        
        for font_path in FONT_PATHS:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                    _font_name = 'CustomFont'
                    _font_registered = True
                    return _font_name
                except Exception:
                    continue
        
        _font_registered = True
        return _font_name
    
    # ========== BLUETOOTH ЧЕК ==========
    def print_receipt_bluetooth(self, cart_items, total_amount, payment_type,
                                customer_name="", cash=0, card=0, credit=0,
                                paid_amount=0, change_amount=0, negotiated_price=0):
        if not self.bluetooth:
            return False, "Bluetooth принтер мавжуд эмас!"
        
        if not self.bluetooth.connect():
            return False, "Принтерга уланиб бўлмади!"
        
        try:
            ESC = b'\x1B'
            GS = b'\x1D'
            LF = b'\x0A'
            
            self.bluetooth._send_raw(ESC + b'a' + b'\x01')
            self.bluetooth.send_text(f"{self.shop_name}\n")
            
            if RECEIPT_SHOW_ADDRESS:
                self.bluetooth.send_text(f"{self.shop_address}\n")
            if RECEIPT_SHOW_PHONE:
                self.bluetooth.send_text(f"Tel: {self.shop_phone}\n")
            
            self.bluetooth._send_raw(LF)
            self.bluetooth._send_raw(ESC + b'a' + b'\x00')
            self.bluetooth.send_text("-" * 32 + "\n")
            
            self.bluetooth.send_text(f"Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            if RECEIPT_SHOW_OPERATOR:
                self.bluetooth.send_text(f"Operator: {self.operator}\n")
            
            if customer_name:
                self.bluetooth.send_text(f"Mijoz: {customer_name}\n")
            
            self.bluetooth.send_text("-" * 32 + "\n")
            
            for item in cart_items:
                name = item.get('name', '')[:20]
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                total = price * quantity
                unit = item.get('unit', 'дона')
                
                self.bluetooth.send_text(f"{name}\n")
                self.bluetooth.send_text(f"  {quantity:.2f} {unit} x {price:,.0f} = {total:,.0f}\n")
            
            self.bluetooth.send_text("-" * 32 + "\n")
            
            self.bluetooth._send_raw(ESC + b'E' + b'\x01')
            self.bluetooth.send_text(f"JAMI: {total_amount:,.0f} so'm\n")
            self.bluetooth._send_raw(ESC + b'E' + b'\x00')
            
            if negotiated_price > 0 and negotiated_price != total_amount:
                self.bluetooth.send_text(f"Kelishuv: {negotiated_price:,.0f} so'm\n")
            
            if payment_type == 'mixed':
                if cash > 0:
                    self.bluetooth.send_text(f"Naqd: {cash:,.0f} so'm\n")
                if card > 0:
                    self.bluetooth.send_text(f"Plastik: {card:,.0f} so'm\n")
                if credit > 0:
                    self.bluetooth.send_text(f"Qarzga: {credit:,.0f} so'm\n")
                    if customer_name:
                        self.bluetooth.send_text(f"Mijoz: {customer_name}\n")
            else:
                payment_names = {'cash': 'Naqd', 'card': 'Plastik', 'credit': 'Qarzga'}
                pay_text = payment_names.get(payment_type, payment_type)
                self.bluetooth.send_text(f"To'lov: {pay_text} - {total_amount:,.0f} so'm\n")
            
            if paid_amount > 0:
                self.bluetooth.send_text(f"Berilgan: {paid_amount:,.0f} so'm\n")
                if change_amount > 0:
                    self.bluetooth.send_text(f"Qaytim: {change_amount:,.0f} so'm\n")
            
            self.bluetooth.send_text("=" * 32 + "\n")
            
            self.bluetooth._send_raw(ESC + b'a' + b'\x01')
            self.bluetooth.send_text("\n✦ RAHMAT! ✦\n")
            if RECEIPT_SHOW_FOOTER:
                self.bluetooth.send_text(f"{RECEIPT_FOOTER}\n")
            
            if RECEIPT_SHOW_WEBSITE:
                self.bluetooth.send_text(f"Web: {self.shop_website}\n")
            
            self.bluetooth._send_raw(GS + b'V' + b'\x00')
            
            self.bluetooth.disconnect()
            return True, "✅ Чек Bluetooth орқали чоп этилди!"
            
        except Exception as e:
            self.bluetooth.disconnect()
            return False, f"❌ Чек чоп этишда хатолик: {str(e)}"
    
    # ========== PDF ЧЕК ==========
    def create_receipt_pdf(self, cart_items, total_amount, payment_type,
                           customer_name="", cash=0, card=0, credit=0,
                           paid_amount=0, change_amount=0, negotiated_price=0):
        if not REPORTLAB_AVAILABLE:
            return False, "reportlab ўрнатилмаган!"
        
        try:
            page_width = self.receipt_width * mm
            base_height = 60
            item_height = 6 * len(cart_items)
            payment_height = 15
            page_height = (base_height + item_height + payment_height) * mm
            
            filename = os.path.join(
                self.temp_dir,
                f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            c = canvas.Canvas(filename, pagesize=(page_width, page_height))
            width = page_width
            height = page_height
            
            y = height - 8 * mm
            
            c.setFont(self.font_name, 14)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, y, f"✦ {self.shop_name} ✦")
            y -= 6 * mm
            
            c.setFont(self.font_name, 8)
            c.setFillColor(colors.HexColor('#666666'))
            if RECEIPT_SHOW_ADDRESS:
                c.drawCentredString(width / 2, y, self.shop_address[:25])
                y -= 4 * mm
            if RECEIPT_SHOW_PHONE:
                c.drawCentredString(width / 2, y, f"Tel: {self.shop_phone}")
                y -= 5 * mm
            
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            c.line(3 * mm, y, width - 3 * mm, y)
            y -= 4 * mm
            
            c.setFont(self.font_name, 10)
            c.setFillColor(colors.black)
            c.drawString(3 * mm, y, f"Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            y -= 4.5 * mm
            
            if RECEIPT_SHOW_OPERATOR:
                c.drawString(3 * mm, y, f"Operator: {self.operator}")
                y -= 4.5 * mm
            
            if customer_name:
                c.drawString(3 * mm, y, f"Mijoz: {customer_name[:15]}")
                y -= 4.5 * mm
            
            c.line(3 * mm, y, width - 3 * mm, y)
            y -= 4 * mm
            
            c.setFont(self.font_name, 10)
            c.setFillColor(colors.black)
            
            for item in cart_items:
                name = item.get('name', '')[:18]
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                total = price * quantity
                unit = item.get('unit', 'дона')
                
                c.drawString(3 * mm, y, name)
                right_text = f"{quantity:.2f}{unit[:3]} x {price:,.0f} = {total:,.0f}"
                c.drawRightString(width - 3 * mm, y, right_text)
                y -= 5 * mm
            
            c.line(3 * mm, y, width - 3 * mm, y)
            y -= 4 * mm
            
            c.setFont(self.font_name, 14)
            c.setFillColor(colors.black)
            c.drawString(3 * mm, y, "JAMI:")
            c.drawRightString(width - 3 * mm, y, f"{total_amount:,.0f} so'm")
            y -= 6 * mm
            
            if negotiated_price > 0 and negotiated_price != total_amount:
                c.setFont(self.font_name, 10)
                c.setFillColor(colors.HexColor('#E67E22'))
                c.drawString(3 * mm, y, "Kelishuv:")
                c.drawRightString(width - 3 * mm, y, f"{negotiated_price:,.0f} so'm")
                y -= 4.5 * mm
            
            c.setFont(self.font_name, 10)
            c.setFillColor(colors.black)
            
            if payment_type == 'mixed':
                if cash > 0:
                    c.drawString(3 * mm, y, "Naqd:")
                    c.drawRightString(width - 3 * mm, y, f"{cash:,.0f} so'm")
                    y -= 4.5 * mm
                if card > 0:
                    c.drawString(3 * mm, y, "Plastik:")
                    c.drawRightString(width - 3 * mm, y, f"{card:,.0f} so'm")
                    y -= 4.5 * mm
                if credit > 0:
                    c.drawString(3 * mm, y, "Qarzga:")
                    c.drawRightString(width - 3 * mm, y, f"{credit:,.0f} so'm")
                    y -= 4.5 * mm
                    if customer_name:
                        c.drawString(3 * mm, y, f"Mijoz: {customer_name[:15]}")
                        y -= 4.5 * mm
            else:
                payment_names = {'cash': 'Naqd', 'card': 'Plastik', 'credit': 'Qarzga'}
                pay_text = payment_names.get(payment_type, payment_type)
                c.drawString(3 * mm, y, f"To'lov: {pay_text}")
                c.drawRightString(width - 3 * mm, y, f"{total_amount:,.0f} so'm")
                y -= 4.5 * mm
                
                if payment_type == 'credit' and customer_name:
                    c.drawString(3 * mm, y, f"Mijoz: {customer_name[:15]}")
                    y -= 4.5 * mm
            
            if paid_amount > 0:
                c.drawString(3 * mm, y, "Berilgan:")
                c.drawRightString(width - 3 * mm, y, f"{paid_amount:,.0f} so'm")
                y -= 4.5 * mm
                if change_amount > 0:
                    c.setFillColor(colors.HexColor('#27AE60'))
                    c.drawString(3 * mm, y, "Qaytim:")
                    c.drawRightString(width - 3 * mm, y, f"{change_amount:,.0f} so'm")
                    c.setFillColor(colors.black)
                    y -= 4.5 * mm
            
            y -= 2 * mm
            c.setStrokeColor(colors.HexColor('#999999'))
            c.line(3 * mm, y, width - 3 * mm, y)
            y -= 4 * mm
            
            c.setFont(self.font_name, 14)
            c.setFillColor(colors.HexColor('#E74C3C'))
            c.drawCentredString(width / 2, y, "✦ RAHMAT! ✦")
            y -= 5.5 * mm
            
            if RECEIPT_SHOW_FOOTER:
                c.setFont(self.font_name, 10)
                c.setFillColor(colors.HexColor('#666666'))
                c.drawCentredString(width / 2, y, RECEIPT_FOOTER)
                y -= 4.5 * mm
            
            if RECEIPT_SHOW_WEBSITE:
                c.setFont(self.font_name, 8)
                c.setFillColor(colors.HexColor('#999999'))
                c.drawCentredString(width / 2, y, f"Web: {self.shop_website}")
            
            c.save()
            return True, filename
            
        except Exception as e:
            return False, f"PDF яратишда хатолик: {str(e)}"
    
    # ========== PDF ЧОП ЭТИШ ==========
    def _print_pdf_windows(self, filename):
        try:
            if WIN32_AVAILABLE:
                win32api.ShellExecute(0, "print", filename, None, ".", 0)
                return True, "✅ Чек чоп этилди!"
        except Exception:
            pass
        
        for sumatra_path in SUMATRA_PATHS:
            if os.path.exists(sumatra_path):
                try:
                    subprocess.run(
                        [sumatra_path, "-print-to-default", "-silent", filename],
                        timeout=30, check=True, capture_output=True
                    )
                    return True, "✅ Чек чоп этилди! (SumatraPDF)"
                except Exception:
                    continue
        
        try:
            ps_command = f'Start-Process -FilePath "{filename}" -Verb Print'
            subprocess.run(
                ["powershell", "-Command", ps_command],
                timeout=30, check=True, capture_output=True
            )
            return True, "✅ Чек чоп этилди! (PowerShell)"
        except Exception:
            pass
        
        try:
            os.startfile(filename)
            return True, "📄 Чек PDF очилди! Чоп этиш учун Ctrl+P босинг"
        except Exception as e:
            return False, f"Чекни очиб бўлмади: {str(e)}"
    
    def _print_pdf_other(self, filename):
        try:
            if self.os_name == 'Darwin':
                subprocess.run(['open', filename], timeout=10)
            elif self.os_name == 'Linux':
                subprocess.run(['xdg-open', filename], timeout=10)
            else:
                os.startfile(filename)
            return True, "📄 Чек PDF очилди!"
        except Exception as e:
            return False, f"Чекни очиб бўлмади: {str(e)}"
    
    # ========== АСОСИЙ МЕТОДЛАР ==========
    def print_receipt(self, cart_items, total_amount, payment_type,
                      customer_name="", cash=0, card=0, credit=0,
                      paid_amount=0, change_amount=0, negotiated_price=0):
        
        if self.printer_type == "bluetooth" and self.bluetooth:
            result, message = self.print_receipt_bluetooth(
                cart_items, total_amount, payment_type,
                customer_name, cash, card, credit,
                paid_amount, change_amount, negotiated_price
            )
            if result:
                return True, message
        
        result, filename = self.create_receipt_pdf(
            cart_items, total_amount, payment_type,
            customer_name, cash, card, credit,
            paid_amount, change_amount, negotiated_price
        )
        
        if not result:
            return False, filename
        
        if self.os_name == 'Windows':
            return self._print_pdf_windows(filename)
        else:
            return self._print_pdf_other(filename)
    
    def print_label(self, product_name, price, barcode="", quantity=1, measurement_type='dona'):
        unit = 'кг' if measurement_type == 'kg' else 'дона'
        cart_items = [{
            'name': product_name,
            'price': price,
            'quantity': quantity,
            'measurement_type': measurement_type,
            'unit': unit
        }]
        return self.print_receipt(cart_items, price * quantity, 'cash', '', price * quantity, 0, 0)
    
    def get_printer_status(self):
        status = []
        
        if self.os_name == 'Windows' and WIN32_AVAILABLE:
            try:
                printer_name = win32print.GetDefaultPrinter()
                status.append(f"✅ Windows принтер: {printer_name}")
            except Exception:
                status.append("❌ Windows принтер топилмади!")
        
        if self.printer_type == "bluetooth":
            if BLEAK_AVAILABLE and self.bluetooth:
                if self.bluetooth.is_connected():
                    status.append(f"🟢 Bluetooth: Уланган ({BLUETOOTH_PRINTER_NAME})")
                else:
                    status.append(f"🔴 Bluetooth: Уланмаган ({BLUETOOTH_PRINTER_NAME})")
            else:
                status.append("❌ Bluetooth қўллаб-қувватланмайди")
        
        if REPORTLAB_AVAILABLE:
            status.append("✅ PDF яратиш: Тайёр")
        else:
            status.append("❌ PDF яратиш: reportlab ўрнатилмаган")
        
        return "\n".join(status)
    
    def test_print(self):
        test_items = [
            {'name': 'Test mahsulot', 'price': 10000, 'quantity': 1, 'unit': 'дона'}
        ]
        return self.print_receipt(test_items, 10000, 'cash', '', 10000, 0, 0)