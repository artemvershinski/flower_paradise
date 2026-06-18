from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from models import OrderStatus

# ==================== ЯЗЫКИ ====================

def language_keyboard():
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== ГЛАВНОЕ МЕНЮ ====================

def main_menu(lang="ru"):
    if lang == "en":
        text_buttons = [
            ("Catalog", "catalog"),
            ("Make Order", "order_flower"),
            ("My Orders", "my_orders"),
            ("Order Status", "order_status"),
            ("Contacts", "contacts"),
            ("Change Language", "change_lang"),
        ]
    else:
        text_buttons = [
            ("🌸 Каталог", "catalog"),
            ("🛒 Сделать заказ", "order_flower"),
            ("📋 Мои заказы", "my_orders"),
            ("📦 Статус заказа", "order_status"),
            ("📞 Контакты", "contacts"),
            ("🌐 Сменить язык", "change_lang"),
        ]
    
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in text_buttons]
    return InlineKeyboardMarkup(keyboard)

def main_menu_manager(lang="ru", is_manager=False):
    keyboard = main_menu(lang).keyboard
    if is_manager:
        if lang == "en":
            keyboard.insert(0, [InlineKeyboardButton("👔 Manager Panel", callback_data="manager_panel")])
        else:
            keyboard.insert(0, [InlineKeyboardButton("👔 Панель менеджера", callback_data="manager_panel")])
    return InlineKeyboardMarkup(keyboard)

# ==================== МЕНЮ МЕНЕДЖЕРА ====================

def manager_menu(lang="ru"):
    if lang == "en":
        buttons = [
            ("All Orders", "manager_all_orders"),
            ("New Orders", "manager_new_orders"),
            ("Statistics", "manager_stats"),
            ("Main Menu", "back_main"),
        ]
    else:
        buttons = [
            ("📋 Все заказы", "manager_all_orders"),
            ("🆕 Новые заказы", "manager_new_orders"),
            ("📊 Статистика", "manager_stats"),
            ("🏠 Главное меню", "back_main"),
        ]
    
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons]
    return InlineKeyboardMarkup(keyboard)

# ==================== КАТАЛОГ ====================

def categories_menu(lang="ru"):
    if lang == "en":
        buttons = [
            ("Roses", "cat_roses"),
            ("Exotic", "cat_exotic"),
            ("Field", "cat_field"),
            ("Wedding", "cat_wedding"),
            ("Holiday", "cat_holiday"),
            ("Back", "back_main"),
        ]
    else:
        buttons = [
            ("🌹 Розы", "cat_roses"),
            ("🌺 Экзотические", "cat_exotic"),
            ("🌻 Полевые", "cat_field"),
            ("💐 Свадебные", "cat_wedding"),
            ("🎄 Праздничные", "cat_holiday"),
            ("🔙 Назад", "back_main"),
        ]
    
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons]
    return InlineKeyboardMarkup(keyboard)

def flowers_list(flowers, page=0, per_page=5, lang="ru"):
    total = len(flowers)
    start = page * per_page
    end = min(start + per_page, total)
    
    keyboard = []
    for flower in flowers[start:end]:
        status_text = "✅ в наличии" if flower.in_stock else "❌ нет в наличии"
        if lang == "en":
            status_text = "✅ in stock" if flower.in_stock else "❌ out of stock"
        keyboard.append([
            InlineKeyboardButton(
                f"{flower.name} - {flower.price}₽ ({status_text})",
                callback_data=f"flower_{flower.id}"
            )
        ])
    
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"page_{page-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"page_{page+1}"))
    if nav:
        keyboard.append(nav)
    
    back_text = "🔙 Назад" if lang == "ru" else "🔙 Back"
    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_catalog")])
    return InlineKeyboardMarkup(keyboard)

def flower_detail(flower, lang="ru"):
    keyboard = []
    
    if flower.in_stock:
        order_text = "🛒 Заказать" if lang == "ru" else "🛒 Order"
        keyboard.append([InlineKeyboardButton(order_text, callback_data=f"order_{flower.id}")])
    
    back_text = "🔙 Назад к списку" if lang == "ru" else "🔙 Back to list"
    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_flowers")])
    return InlineKeyboardMarkup(keyboard)

# ==================== ДОСТАВКА ====================

def delivery_date_keyboard(lang="ru"):
    from datetime import datetime, timedelta
    keyboard = []
    
    today = datetime.now()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"] if lang == "ru" else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(7):
        date = today + timedelta(days=i)
        day_name = days[date.weekday()]
        date_str = date.strftime("%d.%m.%Y")
        keyboard.append([
            InlineKeyboardButton(
                f"{day_name} {date_str}",
                callback_data=f"delivery_date_{date_str}"
            )
        ])
    
    back_text = "🔙 Назад" if lang == "ru" else "🔙 Back"
    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_order")])
    return InlineKeyboardMarkup(keyboard)

def delivery_time_keyboard(lang="ru"):
    times = [
        ("09:00 - 11:00", "time_09-11"),
        ("11:00 - 13:00", "time_11-13"),
        ("13:00 - 15:00", "time_13-15"),
        ("15:00 - 17:00", "time_15-17"),
        ("17:00 - 19:00", "time_17-19"),
        ("19:00 - 21:00", "time_19-21"),
    ]
    
    keyboard = [[InlineKeyboardButton(t[0], callback_data=t[1])] for t in times]
    back_text = "🔙 Назад" if lang == "ru" else "🔙 Back"
    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_order")])
    return InlineKeyboardMarkup(keyboard)

def order_confirmation(lang="ru"):
    if lang == "en":
        buttons = [
            ("✅ Confirm order", "confirm_order"),
            ("✏️ Edit", "edit_order"),
            ("❌ Cancel", "cancel_order"),
        ]
    else:
        buttons = [
            ("✅ Подтвердить заказ", "confirm_order"),
            ("✏️ Изменить", "edit_order"),
            ("❌ Отменить", "cancel_order"),
        ]
    
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons]
    return InlineKeyboardMarkup(keyboard)

def status_change_keyboard(order_id, current_status, lang="ru"):
    statuses = [
        OrderStatus.NEW,
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.DELIVERY,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
    ]
    
    status_names_ru = {
        "New": "🆕 Новый",
        "Confirmed": "✅ Подтверждён",
        "Preparing": "👨‍🍳 Готовится",
        "Delivery": "🚚 В доставке",
        "Delivered": "📦 Доставлен",
        "Cancelled": "❌ Отменён",
    }
    
    keyboard = []
    for status in statuses:
        if status.value != current_status:
            label = status.value if lang == "en" else status_names_ru.get(status.value, status.value)
            keyboard.append([
                InlineKeyboardButton(
                    f"➡️ {label}",
                    callback_data=f"change_status_{order_id}_{status.value}"
                )
            ])
    
    back_text = "🔙 Назад" if lang == "ru" else "🔙 Back"
    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_orders")])
    return InlineKeyboardMarkup(keyboard)

def back_to_main(lang="ru"):
    text = "🏠 Главное меню" if lang == "ru" else "🏠 Main Menu"
    keyboard = [[InlineKeyboardButton(text, callback_data="back_main")]]
    return InlineKeyboardMarkup(keyboard)

def contacts_keyboard(lang="ru"):
    keyboard = [
        [InlineKeyboardButton("📞 Позвонить", url="tel:+79991234567")],
        [InlineKeyboardButton("📍 Открыть карту", url="https://maps.google.com/?q=Flower+Paradise")],
    ]
    if lang == "en":
        keyboard = [
            [InlineKeyboardButton("📞 Call", url="tel:+79991234567")],
            [InlineKeyboardButton("📍 Open map", url="https://maps.google.com/?q=Flower+Paradise")],
        ]
    keyboard.append([InlineKeyboardButton("🏠 Главное меню" if lang == "ru" else "🏠 Main Menu", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)
