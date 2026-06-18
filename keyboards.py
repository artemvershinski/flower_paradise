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
                f"{flower.name} - {flower.price} ({status})",
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

def
