# modules/qr_scanner.py
import cv2
import numpy as np
import json
import re
from datetime import datetime

class BarcodeScanner:
    def __init__(self):
        self.cap = None
        self.qr_detector = cv2.QRCodeDetector()
        self.camera_available = self._check_camera()
        
        # Barcode детекторни текшириш
        try:
            self.barcode_detector = cv2.barcode.BarcodeDetector()
            self.barcode_available = True
        except:
            self.barcode_available = False
            print("⚠️ Barcode detector mavjud emas, faqat QR kod ishlaydi")
    
    def _check_camera(self):
        """Камера мавжудлигини текшириш"""
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False
    
    # ========== КАМЕРА ОРҚАЛИ ==========
    def scan_from_camera(self, timeout=30):
        """Камера орқали QR ва штрих-кодни сканер қилиш"""
        if not self.camera_available:
            return None, "Камера топилмади! Сканердан фойдаланинг."
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                return None, "Камера очилмади!"
            
            print("📷 Камера орқали сканерлаш бошланди...")
            print("📌 QR-код ёки штрих-кодни кўрсатинг")
            print("❌ Чиқиш учун 'q' тугмасини босинг")
            
            start_time = datetime.now()
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # 1. QR-кодни текшириш
                try:
                    qr_data, points, _ = self.qr_detector.detectAndDecode(frame)
                    
                    if qr_data and qr_data.strip():
                        self.cap.release()
                        cv2.destroyAllWindows()
                        return qr_data, "QR-код топилди! (камера)"
                except:
                    pass
                
                # 2. Штрих-кодни текшириш
                if self.barcode_available:
                    try:
                        barcode_data, barcode_points, barcode_type = self.barcode_detector.detectAndDecode(frame)
                        if barcode_data and len(barcode_data) > 0 and barcode_data[0]:
                            self.cap.release()
                            cv2.destroyAllWindows()
                            return barcode_data[0], f"Штрих-код топилди! (камера)"
                    except:
                        pass
                
                # Кодни кўрсатиш
                cv2.putText(frame, "📷 Kamera orqali skaner", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "❌ 'q' - chiqish", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('QR / Barcode Scanner (Kamera)', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                if (datetime.now() - start_time).seconds > timeout:
                    break
            
            self.cap.release()
            cv2.destroyAllWindows()
            return None, "Бекор қилинди!"
            
        except Exception as e:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            return None, f"Хатолик: {str(e)}"
    
    # ========== СКАНЕР ОРҚАЛИ (клавиатура) ==========
    def parse_scanner_input(self, raw_data):
        """Сканердан келган маълумотни парс қилиш"""
        return self.parse_data(raw_data)
    
    # ========== УМУМИЙ ПАРСЕР ==========
    def parse_data(self, raw_data):
        """QR ёки штрих-коддан маълумотларни парс қилиш"""
        result = {
            'name': '',
            'price': 0,
            'barcode': '',
            'quantity': 1,
            'purchase_price': 0,
            'measurement_type': 'dona',
            'code_type': 'unknown',
            'raw_data': raw_data
        }
        
        # 1. Штрих-код (фақат рақамлар)
        if raw_data.isdigit():
            result['barcode'] = raw_data
            result['code_type'] = 'barcode'
            return result
        
        # 2. JSON формат
        try:
            data = json.loads(raw_data)
            result['name'] = data.get('name', '')
            result['price'] = float(data.get('price', 0))
            result['barcode'] = data.get('barcode', '')
            result['quantity'] = float(data.get('quantity', 1))
            result['purchase_price'] = float(data.get('purchase_price', 0))
            result['measurement_type'] = data.get('measurement_type', 'dona')
            result['code_type'] = 'qr_json'
            return result
        except:
            pass
        
        # 3. URL формат
        if raw_data.startswith('http://') or raw_data.startswith('https://'):
            result['code_type'] = 'qr_url'
            return result
        
        # 4. Матн формат
        lines = raw_data.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['name', 'mahsulet', 'maxsulot', 'nom', 'nomi']:
                    result['name'] = value
                elif key in ['price', 'narx', 'narhi', 'sotish']:
                    try:
                        result['price'] = float(re.sub(r'[^0-9.]', '', value))
                    except:
                        pass
                elif key in ['barcode', 'shtrix', 'kod', 'code']:
                    result['barcode'] = value
                elif key in ['quantity', 'miqdor', 'dona']:
                    try:
                        result['quantity'] = float(re.sub(r'[^0-9.]', '', value))
                    except:
                        pass
                elif key in ['purchase', 'kirish']:
                    try:
                        result['purchase_price'] = float(re.sub(r'[^0-9.]', '', value))
                    except:
                        pass
                elif key in ['type', 'tur']:
                    if 'kg' in value.lower():
                        result['measurement_type'] = 'kg'
        
        if result['name']:
            result['code_type'] = 'qr_text'
        
        return result