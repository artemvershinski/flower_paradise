from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class OrderStatus(str, Enum):
    NEW = "Новый"
    CONFIRMED = "Подтвержден"
    PREPARING = "Готовится"
    DELIVERY = "В доставке"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"

@dataclass
class Flower:
    id: int
    name: str
    price: int
    description: str
    image: str
    category: str
    in_stock: bool = True

@dataclass
class Order:
    id: str
    user_id: int
    user_name: str
    user_phone: str
    flower: Flower
    address: str
    delivery_date: str
    delivery_time: str
    comment: Optional[str] = None
    status: OrderStatus = OrderStatus.NEW
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    phone: Optional[str] = None
    address: Optional[str] = None
    is_manager: bool = False
