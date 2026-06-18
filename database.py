import gspread
import json
import logging
from typing import List, Optional
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from models import Flower, Order, OrderStatus
from config import GOOGLE_SHEETS_ID, GOOGLE_CREDENTIALS_JSON, GOOGLE_CREDENTIALS_FILE

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.sheet = None
        self._orders = {}
        self._order_counter = 0
        self._init_connection()
        self._init_sheets()
    
    def _init_connection(self):
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = None
            
            if GOOGLE_CREDENTIALS_JSON:
                creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            elif GOOGLE_CREDENTIALS_FILE:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    GOOGLE_CREDENTIALS_FILE, scope
                )
            else:
                logger.warning("Google Sheets credentials not found, using in-memory storage")
                return
            
            self.client = gspread.authorize(credentials)
            logger.info("Connected to Google Sheets")
            
        except Exception as e:
            logger.error(f"Google Sheets connection error: {e}")
            self.client = None
    
    def _init_sheets(self):
        if not self.client or not GOOGLE_SHEETS_ID:
            return
            
        try:
            self.sheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
            
            required_sheets = ['orders', 'flowers', 'users']
            existing = [ws.title for ws in self.sheet.worksheets()]
            
            for sheet_name in required_sheets:
                if sheet_name not in existing:
                    ws = self.sheet.add_worksheet(title=sheet_name, rows=100, cols=20)
                    if sheet_name == 'orders':
                        ws.append_row(['ID', 'UserID', 'UserName', 'UserPhone', 'FlowerID', 
                                     'FlowerName', 'Price', 'Address', 'DeliveryDate', 
                                     'DeliveryTime', 'Comment', 'Status', 'CreatedAt', 'UpdatedAt'])
                    elif sheet_name == 'flowers':
                        ws.append_row(['ID', 'Name', 'Price', 'Description', 'Image', 'Category', 'InStock'])
                    elif sheet_name == 'users':
                        ws.append_row(['UserID', 'Username', 'FirstName', 'LastName', 'Phone', 'Address', 'IsManager'])
            
            logger.info("Sheets initialized")
            
        except Exception as e:
            logger.error(f"Sheet init error: {e}")
    
    def get_flowers(self, category: Optional[str] = None) -> List[Flower]:
        try:
            if self.sheet:
                ws = self.sheet.worksheet('flowers')
                data = ws.get_all_values()
                if len(data) <= 1:
                    return self._get_default_flowers()
                
                flowers = []
                for row in data[1:]:
                    if not row or not row[0]:
                        continue
                    flower = Flower(
                        id=int(row[0]),
                        name=row[1],
                        price=int(row[2]),
                        description=row[3],
                        image=row[4] if len(row) > 4 else "",
                        category=row[5] if len(row) > 5 else "other",
                        in_stock=row[6].lower() == 'true' if len(row) > 6 else True
                    )
                    if not category or flower.category == category:
                        flowers.append(flower)
                return flowers
            
        except Exception as e:
            logger.error(f"Error getting flowers: {e}")
        
        return self._get_default_flowers()
    
    def _get_default_flowers(self) -> List[Flower]:
        return [
            Flower(1, "Алые розы", 2500, "Классический букет из 51 алой розы", "", "roses"),
            Flower(2, "Белые розы", 3000, "Нежный букет из белых роз", "", "roses"),
            Flower(3, "Экзотический микс", 4500, "Орхидеи, протеи и экзотические цветы", "", "exotic"),
            Flower(4, "Полевой букет", 2000, "Ромашки, васильки и полевые цветы", "", "field"),
            Flower(5, "Свадебный букет", 5000, "Изысканный свадебный букет", "", "wedding"),
            Flower(6, "Праздничный букет", 3500, "Яркий праздничный букет", "", "holiday"),
        ]
    
    def get_flower(self, flower_id: int) -> Optional[Flower]:
        for flower in self.get_flowers():
            if flower.id == flower_id:
                return flower
        return None
    
    def create_order(self, order: Order) -> str:
        import uuid
        if not order.id:
            order.id = str(uuid.uuid4())[:8]
        
        order.created_at = datetime.now()
        order.updated_at = datetime.now()
        
        # Сохраняем в память
        self._orders[order.id] = order
        self._order_counter += 1
        
        try:
            if self.sheet:
                ws = self.sheet.worksheet('orders')
                ws.append_row([
                    order.id,
                    order.user_id,
                    order.user_name,
                    order.user_phone,
                    order.flower.id,
                    order.flower.name,
                    order.flower.price,
                    order.address,
                    order.delivery_date,
                    order.delivery_time,
                    order.comment or '',
                    order.status.value,
                    order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    order.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
                logger.info(f"Order {order.id} saved to Google Sheets")
            else:
                logger.info(f"Order {order.id} saved to memory")
                
        except Exception as e:
            logger.error(f"Error saving order to Google Sheets: {e}")
            # Заказ уже сохранён в памяти
        
        return order.id
    
    def get_orders(self, user_id: Optional[int] = None) -> List[Order]:
        # Сначала пробуем получить из Google Sheets
        try:
            if self.sheet:
                ws = self.sheet.worksheet('orders')
                data = ws.get_all_values()
                if len(data) > 1:
                    orders = []
                    for row in data[1:]:
                        if not row or not row[0]:
                            continue
                        
                        flower = Flower(
                            id=int(row[4]) if row[4] else 0,
                            name=row[5] if len(row) > 5 else "",
                            price=int(row[6]) if len(row) > 6 and row[6] else 0,
                            description="",
                            image="",
                            category=""
                        )
                        
                        order = Order(
                            id=row[0],
                            user_id=int(row[1]) if row[1] else 0,
                            user_name=row[2] if len(row) > 2 else "",
                            user_phone=row[3] if len(row) > 3 else "",
                            flower=flower,
                            address=row[7] if len(row) > 7 else "",
                            delivery_date=row[8] if len(row) > 8 else "",
                            delivery_time=row[9] if len(row) > 9 else "",
                            comment=row[10] if len(row) > 10 else None,
                            status=OrderStatus(row[11]) if len(row) > 11 and row[11] else OrderStatus.NEW,
                            created_at=datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S') if len(row) > 12 and row[12] else None,
                            updated_at=datetime.strptime(row[13], '%Y-%m-%d %H:%M:%S') if len(row) > 13 and row[13] else None
                        )
                        
                        if not user_id or order.user_id == user_id:
                            orders.append(order)
                    
                    # Обновляем память
                    for o in orders:
                        self._orders[o.id] = o
                    
                    return sorted(orders, key=lambda x: x.created_at or datetime.now(), reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting orders from Google Sheets: {e}")
        
        # Возвращаем из памяти
        orders = list(self._orders.values())
        if user_id:
            orders = [o for o in orders if o.user_id == user_id]
        return sorted(orders, key=lambda x: x.created_at or datetime.now(), reverse=True)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        # Сначала проверяем память
        if order_id in self._orders:
            return self._orders[order_id]
        
        # Ищем в Google Sheets
        try:
            if self.sheet:
                ws = self.sheet.worksheet('orders')
                data = ws.get_all_values()
                for row in data[1:]:
                    if row and row[0] == order_id:
                        flower = Flower(
                            id=int(row[4]) if row[4] else 0,
                            name=row[5] if len(row) > 5 else "",
                            price=int(row[6]) if len(row) > 6 and row[6] else 0,
                            description="",
                            image="",
                            category=""
                        )
                        order = Order(
                            id=row[0],
                            user_id=int(row[1]) if row[1] else 0,
                            user_name=row[2] if len(row) > 2 else "",
                            user_phone=row[3] if len(row) > 3 else "",
                            flower=flower,
                            address=row[7] if len(row) > 7 else "",
                            delivery_date=row[8] if len(row) > 8 else "",
                            delivery_time=row[9] if len(row) > 9 else "",
                            comment=row[10] if len(row) > 10 else None,
                            status=OrderStatus(row[11]) if len(row) > 11 and row[11] else OrderStatus.NEW,
                            created_at=datetime.strptime(row[12], '%Y-%m-%d %H:%M:%S') if len(row) > 12 and row[12] else None,
                            updated_at=datetime.strptime(row[13], '%Y-%m-%d %H:%M:%S') if len(row) > 13 and row[13] else None
                        )
                        self._orders[order_id] = order
                        return order
        except Exception as e:
            logger.error(f"Error getting order from Google Sheets: {e}")
        
        return None
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            order.status = status
            order.updated_at = datetime.now()
            
            # Обновляем в памяти
            self._orders[order_id] = order
            
            # Обновляем в Google Sheets
            if self.sheet:
                try:
                    ws = self.sheet.worksheet('orders')
                    data = ws.get_all_values()
                    for i, row in enumerate(data):
                        if row and row[0] == order_id:
                            ws.update_cell(i+1, 12, status.value)
                            ws.update_cell(i+1, 14, order.updated_at.strftime('%Y-%m-%d %H:%M:%S'))
                            logger.info(f"Order {order_id} status updated in Google Sheets")
                            return True
                except Exception as e:
                    logger.error(f"Error updating order in Google Sheets: {e}")
                    # Заказ уже обновлён в памяти
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False

db = Database()
