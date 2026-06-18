from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from models import OrderStatus

def main_menu(is_manager: bool = False):
    keyboard = [
        [InlineKeyboardButton("Catalog", callback_data="catalog")],
        [InlineKeyboardButton("Make Order", callback_data="order_flower")],
        [InlineKeyboardButton("My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("Order Status", callback_data="order_status")],
        [InlineKeyboardButton("Contacts", callback_data="contacts")],
    ]
    
    if is_manager:
        keyboard.insert(0, [InlineKeyboardButton("Manager Panel", callback_data="manager_panel")])
    
    return InlineKeyboardMarkup(keyboard)

def manager_menu():
    keyboard = [
        [InlineKeyboardButton("All Orders", callback_data="manager_all_orders")],
        [InlineKeyboardButton("New Orders", callback_data="manager_new_orders")],
        [InlineKeyboardButton("Statistics", callback_data="manager_stats")],
        [InlineKeyboardButton("Main Menu", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def categories_menu():
    keyboard = [
        [InlineKeyboardButton("Roses", callback_data="cat_roses")],
        [InlineKeyboardButton("Exotic", callback_data="cat_exotic")],
        [InlineKeyboardButton("Field", callback_data="cat_field")],
        [InlineKeyboardButton("Wedding", callback_data="cat_wedding")],
        [InlineKeyboardButton("Holiday", callback_data="cat_holiday")],
        [InlineKeyboardButton("Back", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def flowers_list(flowers, page=0, per_page=5):
    total = len(flowers)
    start = page * per_page
    end = min(start + per_page, total)
    
    keyboard = []
    for flower in flowers[start:end]:
        status = "in stock" if flower.in_stock else "out of stock"
        keyboard.append([
            InlineKeyboardButton(
                f"{flower.name} - {flower.price} ( {status} )",
                callback_data=f"flower_{flower.id}"
            )
        ])
    
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("<", callback_data=f"page_{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton(">", callback_data=f"page_{page+1}"))
    if nav:
        keyboard.append(nav)
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_catalog")])
    return InlineKeyboardMarkup(keyboard)

def flower_detail(flower):
    keyboard = []
    
    if flower.in_stock:
        keyboard.append([InlineKeyboardButton("Order", callback_data=f"order_{flower.id}")])
    
    keyboard.append([InlineKeyboardButton("Back to list", callback_data="back_flowers")])
    return InlineKeyboardMarkup(keyboard)

def delivery_date_keyboard():
    from datetime import datetime, timedelta
    keyboard = []
    
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date.weekday()]
        date_str = date.strftime("%d.%m.%Y")
        keyboard.append([
            InlineKeyboardButton(
                f"{day_name} {date_str}",
                callback_data=f"delivery_date_{date_str}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_order")])
    return InlineKeyboardMarkup(keyboard)

def delivery_time_keyboard():
    keyboard = [
        [InlineKeyboardButton("09:00 - 11:00", callback_data="time_09-11")],
        [InlineKeyboardButton("11:00 - 13:00", callback_data="time_11-13")],
        [InlineKeyboardButton("13:00 - 15:00", callback_data="time_13-15")],
        [InlineKeyboardButton("15:00 - 17:00", callback_data="time_15-17")],
        [InlineKeyboardButton("17:00 - 19:00", callback_data="time_17-19")],
        [InlineKeyboardButton("19:00 - 21:00", callback_data="time_19-21")],
        [InlineKeyboardButton("Back", callback_data="back_order")],
    ]
    return InlineKeyboardMarkup(keyboard)

def order_confirmation():
    keyboard = [
        [InlineKeyboardButton("Confirm order", callback_data="confirm_order")],
        [InlineKeyboardButton("Edit", callback_data="edit_order")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_order")],
    ]
    return InlineKeyboardMarkup(keyboard)

def status_change_keyboard(order_id, current_status):
    statuses = [
        OrderStatus.NEW,
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.DELIVERY,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
    ]
    
    keyboard = []
    for status in statuses:
        if status.value != current_status:
            keyboard.append([
                InlineKeyboardButton(
                    f"Set {status.value}",
                    callback_data=f"change_status_{order_id}_{status.value}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_orders")])
    return InlineKeyboardMarkup(keyboard)

def back_to_main():
    keyboard = [
        [InlineKeyboardButton("Main Menu", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

def contacts_keyboard():
    keyboard = [
        [InlineKeyboardButton("Call", url="tel:+79991234567")],
        [InlineKeyboardButton("Map", url="https://maps.google.com/?q=Flower+Paradise")],
        [InlineKeyboardButton("Main Menu", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
