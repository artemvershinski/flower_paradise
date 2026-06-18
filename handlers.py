import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import MANAGER_CHAT_ID, DEFAULT_LANGUAGE
from states import States
from keyboards import *
from database import db
from models import Flower, Order, OrderStatus

logger = logging.getLogger(__name__)

user_data_store = {}

def get_user_data(user_id):
    if user_id not in user_data_store:
        user_data_store[user_id] = {"lang": DEFAULT_LANGUAGE}
    return user_data_store[user_id]

def get_lang(user_id):
    return get_user_data(user_id).get("lang", DEFAULT_LANGUAGE)

def get_user_role(user_id: int) -> bool:
    return user_id == MANAGER_CHAT_ID

def get_text(key, lang="ru"):
    texts = {
        "welcome": {
            "ru": "🌸 Привет, {name}!\n\nДобро пожаловать в цветочный магазин «Цветочный рай»!\nУ нас самые красивые и свежие цветы.\n\nВыберите действие:",
            "en": "🌸 Hello, {name}!\n\nWelcome to Flower Paradise flower shop!\nWe have the most beautiful and fresh flowers.\n\nChoose an action:"
        },
        "contacts": {
            "ru": "📞 *Контакты*\n\n📍 *Адрес:* ул. Цветочная, 15\n📱 *Телефон:* +7 (999) 123-45-67\n🕐 *Режим работы:* 9:00 - 21:00\n🌐 *Сайт:* flowerparadise.ru\n\n✨ Мы работаем ежедневно и всегда рады вам!",
            "en": "📞 *Contacts*\n\n📍 *Address:* Tsvetochnaya str., 15\n📱 *Phone:* +7 (999) 123-45-67\n🕐 *Working hours:* 9:00 - 21:00\n🌐 *Website:* flowerparadise.ru\n\n✨ We work every day and are always glad to see you!"
        },
        "select_category": {
            "ru": "🌸 Выберите категорию букетов:",
            "en": "🌸 Select category:"
        },
        "no_flowers": {
            "ru": "😔 В этой категории пока нет букетов.\nЗагляните позже!",
            "en": "😔 No flowers in this category yet.\nCheck back later!"
        },
        "flowers_in_category": {
            "ru": "🌸 *Букеты в категории:*\n\nВсего: {total} букетов",
            "en": "🌸 *Flowers in category:*\n\nTotal: {total} bouquets"
        },
        "flower_not_found": {
            "ru": "😔 Букет не найден",
            "en": "😔 Flower not found"
        },
        "flower_detail": {
            "ru": "{name}\n\n💰 *Цена:* {price} ₽\n📝 {description}\n\n{stock}",
            "en": "{name}\n\n💰 *Price:* {price} ₽\n📝 {description}\n\n{stock}"
        },
        "in_stock": {"ru": "✅ В наличии", "en": "✅ In stock"},
        "out_of_stock": {"ru": "❌ Нет в наличии", "en": "❌ Out of stock"},
        "ask_name": {
            "ru": "Заказ: {name}\n\nПожалуйста, введите ваше полное имя:",
            "en": "Ordering: {name}\n\nPlease enter your full name:"
        },
        "ask_address": {
            "ru": "Спасибо, {name}!\n\nВведите адрес доставки:",
            "en": "Thank you, {name}!\n\nPlease enter your delivery address:"
        },
        "ask_delivery_date": {
            "ru": "Выберите дату доставки:",
            "en": "Select delivery date:"
        },
        "ask_delivery_time": {
            "ru": "Дата доставки: {date}\n\nВыберите время доставки:",
            "en": "Delivery date: {date}\n\nSelect delivery time:"
        },
        "ask_phone": {
            "ru": "Время доставки: {time}\n\nВведите ваш номер телефона:",
            "en": "Delivery time: {time}\n\nPlease enter your phone number:"
        },
        "ask_comment": {
            "ru": "Комментарий к заказу? (отправьте 'нет' если без комментария)",
            "en": "Any comments for your order? (type 'no' for none)"
        },
        "confirm_order": {
            "ru": "✅ *Подтверждение заказа*\n\n🌸 {flower}\n💰 {price} ₽\n📍 {address}\n📅 {date} в {time}\n📱 {phone}\n📝 Комментарий: {comment}",
            "en": "✅ *Order confirmation*\n\n🌸 {flower}\n💰 {price} ₽\n📍 {address}\n📅 {date} at {time}\n📱 {phone}\n📝 Comment: {comment}"
        },
        "order_confirmed": {
            "ru": "✅ *Заказ подтверждён!*\n\n🆔 {order_id}\n🌸 {flower}\n💰 {price} ₽\n\nМы свяжемся с вами в ближайшее время.",
            "en": "✅ *Order confirmed!*\n\n🆔 {order_id}\n🌸 {flower}\n💰 {price} ₽\n\nWe will contact you shortly."
        },
        "order_cancelled": {
            "ru": "❌ Заказ отменён.",
            "en": "❌ Order cancelled."
        },
        "no_orders": {
            "ru": "У вас пока нет заказов.",
            "en": "You have no orders yet."
        },
        "my_orders": {
            "ru": "📋 *Ваши заказы:*\n\n",
            "en": "📋 *Your orders:*\n\n"
        },
        "order_status_input": {
            "ru": "Введите ID заказа:",
            "en": "Enter your order ID:"
        },
        "order_status_not_found": {
            "ru": "Заказ не найден. Проверьте ID.",
            "en": "Order not found. Please check your order ID."
        },
        "order_status_text": {
            "ru": "📦 *Заказ {id}*\n\n🌸 {flower}\n📊 Статус: {status}\n📅 Доставка: {date} в {time}",
            "en": "📦 *Order {id}*\n\n🌸 {flower}\n📊 Status: {status}\n📅 Delivery: {date} at {time}"
        },
        "manager_access_denied": {
            "ru": "⛔ Доступ запрещён.",
            "en": "⛔ Access denied."
        },
        "manager_panel": {
            "ru": "👔 *Панель менеджера*\n\nВыберите действие:",
            "en": "👔 *Manager Panel*\n\nSelect action:"
        },
        "manager_no_orders": {
            "ru": "Заказов нет.",
            "en": "No orders found."
        },
        "manager_all_orders": {
            "ru": "📋 *Все заказы:*\n\n",
            "en": "📋 *All orders:*\n\n"
        },
        "manager_new_orders": {
            "ru": "🆕 *Новые заказы:* {count}\n\n",
            "en": "🆕 *New orders:* {count}\n\n"
        },
        "manager_stats": {
            "ru": "📊 *Статистика*\n\nВсего заказов: {total}\n🆕 Новых: {new}\n📦 Доставлено: {delivered}\n❌ Отменено: {cancelled}",
            "en": "📊 *Statistics*\n\nTotal orders: {total}\n🆕 New: {new}\n📦 Delivered: {delivered}\n❌ Cancelled: {cancelled}"
        },
        "manager_order_detail": {
            "ru": "📋 *Детали заказа*\n\n🆔 {id}\n🌸 {flower}\n💰 {price} ₽\n👤 {customer}\n📱 {phone}\n📍 {address}\n📅 {date} в {time}\n📊 Статус: {status}\n📝 Комментарий: {comment}",
            "en": "📋 *Order Details*\n\n🆔 {id}\n🌸 {flower}\n💰 {price} ₽\n👤 {customer}\n📱 {phone}\n📍 {address}\n📅 {date} at {time}\n📊 Status: {status}\n📝 Comment: {comment}"
        },
        "manager_status_updated": {
            "ru": "✅ Статус заказа {id} обновлён на: {status}",
            "en": "✅ Order {id} status updated to: {status}"
        },
        "customer_status_update": {
            "ru": "📦 Статус вашего заказа {id} обновлён: {status}",
            "en": "📦 Your order {id} status updated: {status}"
        },
        "language_changed": {
            "ru": "🌐 Язык изменён на русский.",
            "en": "🌐 Language changed to English."
        },
        "select_language": {
            "ru": "🌐 Выберите язык:",
            "en": "🌐 Select language:"
        },
        "call_phone": {
            "ru": "📞 *Телефон для связи:* +7 (999) 123-45-67\n\nРежим работы: 9:00 - 21:00",
            "en": "📞 *Phone:* +7 (999) 123-45-67\n\nWorking hours: 9:00 - 21:00"
        }
    }
    return texts.get(key, {}).get(lang, texts.get(key, {}).get("ru", ""))

# ==================== ОСНОВНЫЕ ОБРАБОТЧИКИ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    data = get_user_data(user_id)
    lang = data.get("lang", DEFAULT_LANGUAGE)
    is_manager = get_user_role(user_id)
    data["is_manager"] = is_manager
    
    welcome = get_text("welcome", lang).format(name=user.first_name)
    
    await update.message.reply_text(
        welcome,
        reply_markup=main_menu_manager(lang, is_manager)
    )
    return States.MAIN_MENU

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)
    lang = data.get("lang", DEFAULT_LANGUAGE)
    is_manager = data.get("is_manager", False)
    
    callback_data = query.data
    
    # ========== ИЗМЕНЕНИЕ ЯЗЫКА ==========
    if callback_data == "change_lang":
        await query.edit_message_text(
            get_text("select_language", lang),
            reply_markup=language_keyboard()
        )
        return States.LANGUAGE_SELECT
    
    if callback_data.startswith("lang_"):
        new_lang = callback_data.replace("lang_", "")
        data["lang"] = new_lang
        lang = new_lang
        
        await query.edit_message_text(
            get_text("welcome", lang).format(name=query.from_user.first_name),
            reply_markup=main_menu_manager(lang, is_manager)
        )
        return States.MAIN_MENU
    
    # ========== ГЛАВНОЕ МЕНЮ ==========
    if callback_data == "back_main":
        await query.edit_message_text(
            get_text("welcome", lang).format(name=query.from_user.first_name),
            reply_markup=main_menu_manager(lang, is_manager)
        )
        return States.MAIN_MENU
    
    if callback_data == "contacts":
        await query.edit_message_text(
            get_text("contacts", lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=contacts_keyboard(lang)
        )
        return States.MAIN_MENU
    
    # ===== ДОБАВЛЕННЫЙ ОБРАБОТЧИК ДЛЯ ЗВОНКА =====
    if callback_data == "call_phone":
        await query.edit_message_text(
            get_text("call_phone", lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_main(lang)
        )
        return States.MAIN_MENU
    # =============================================
    
    # ========== КАТАЛОГ ==========
    if callback_data == "catalog":
        await query.edit_message_text(
            get_text("select_category", lang),
            reply_markup=categories_menu(lang)
        )
        return States.SELECT_CATEGORY
    
    if callback_data == "back_catalog":
        await query.edit_message_text(
            get_text("select_category", lang),
            reply_markup=categories_menu(lang)
        )
        return States.SELECT_CATEGORY
    
    if callback_data.startswith("cat_"):
        category = callback_data.replace("cat_", "")
        data["category"] = category
        
        flowers = db.get_flowers(category)
        if not flowers:
            await query.edit_message_text(
                get_text("no_flowers", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        data["flowers"] = flowers
        data["page"] = 0
        
        await query.edit_message_text(
            get_text("flowers_in_category", lang).format(total=len(flowers)),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=flowers_list(flowers, 0, lang=lang)
        )
        return States.SELECT_FLOWER
    
    if callback_data == "back_flowers":
        flowers = data.get("flowers", [])
        await query.edit_message_text(
            get_text("flowers_in_category", lang).format(total=len(flowers)),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=flowers_list(flowers, data.get("page", 0), lang=lang)
        )
        return States.SELECT_FLOWER
    
    if callback_data.startswith("page_"):
        page = int(callback_data.split("_")[1])
        data["page"] = page
        flowers = data.get("flowers", [])
        
        await query.edit_message_text(
            get_text("flowers_in_category", lang).format(total=len(flowers)),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=flowers_list(flowers, page, lang=lang)
        )
        return States.SELECT_FLOWER
    
    if callback_data.startswith("flower_"):
        flower_id = int(callback_data.split("_")[1])
        flower = db.get_flower(flower_id)
        if not flower:
            await query.edit_message_text(
                get_text("flower_not_found", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        data["selected_flower"] = flower
        
        stock_text = get_text("in_stock", lang) if flower.in_stock else get_text("out_of_stock", lang)
        text = get_text("flower_detail", lang).format(
            name=flower.name,
            price=flower.price,
            description=flower.description,
            stock=stock_text
        )
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=flower_detail(flower, lang)
        )
        return States.VIEW_FLOWER
    
    # ========== ОФОРМЛЕНИЕ ЗАКАЗА ==========
    if callback_data.startswith("order_") and callback_data != "order_flower":
        flower_id = int(callback_data.split("_")[1])
        flower = db.get_flower(flower_id)
        if not flower:
            await query.edit_message_text(
                get_text("flower_not_found", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        data["selected_flower"] = flower
        data["order"] = {}
        
        await query.edit_message_text(
            get_text("ask_name", lang).format(name=flower.name),
            reply_markup=None
        )
        return States.ASK_NAME
    
    if callback_data == "order_flower":
        await query.edit_message_text(
            get_text("select_category", lang),
            reply_markup=categories_menu(lang)
        )
        return States.SELECT_CATEGORY
    
    # ========== ДОСТАВКА ==========
    if callback_data.startswith("delivery_date_"):
        date = callback_data.replace("delivery_date_", "")
        data["delivery_date"] = date
        
        await query.edit_message_text(
            get_text("ask_delivery_time", lang).format(date=date),
            reply_markup=delivery_time_keyboard(lang)
        )
        return States.ASK_DELIVERY_TIME
    
    if callback_data.startswith("time_"):
        time = callback_data.replace("time_", "").replace("-", ":")
        data["delivery_time"] = time
        
        await query.edit_message_text(
            get_text("ask_phone", lang).format(time=time),
            reply_markup=None
        )
        return States.ASK_PHONE
    
    if callback_data == "back_order":
        await query.edit_message_text(
            get_text("select_category", lang),
            reply_markup=categories_menu(lang)
        )
        return States.SELECT_CATEGORY
    
    # ========== ПОДТВЕРЖДЕНИЕ ЗАКАЗА ==========
    if callback_data == "confirm_order":
        order_data = data.get("order", {})
        flower = data.get("selected_flower")
        
        if not flower:
            await query.edit_message_text(
                get_text("flower_not_found", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        order = Order(
            id="",
            user_id=user_id,
            user_name=order_data.get("name", ""),
            user_phone=order_data.get("phone", ""),
            flower=flower,
            address=order_data.get("address", ""),
            delivery_date=order_data.get("delivery_date", ""),
            delivery_time=order_data.get("delivery_time", ""),
            comment=order_data.get("comment", "")
        )
        
        order_id = db.create_order(order)
        
        await context.bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=f"🆕 *Новый заказ!*\n\n"
                 f"🆔 {order_id}\n"
                 f"🌸 {flower.name}\n"
                 f"💰 {flower.price} ₽\n"
                 f"👤 {order.user_name}\n"
                 f"📱 {order.user_phone}\n"
                 f"📍 {order.address}\n"
                 f"📅 {order.delivery_date} в {order.delivery_time}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        await query.edit_message_text(
            get_text("order_confirmed", lang).format(
                order_id=order_id,
                flower=flower.name,
                price=flower.price
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_main(lang)
        )
        
        data.pop("order", None)
        data.pop("selected_flower", None)
        return ConversationHandler.END
    
    if callback_data == "edit_order":
        await query.edit_message_text(
            get_text("ask_address", lang).format(name=data.get("order", {}).get("name", "")),
            reply_markup=None
        )
        return States.ASK_ADDRESS
    
    if callback_data == "cancel_order":
        data.pop("order", None)
        data.pop("selected_flower", None)
        await query.edit_message_text(
            get_text("order_cancelled", lang),
            reply_markup=back_to_main(lang)
        )
        return States.MAIN_MENU
    
    # ========== МОИ ЗАКАЗЫ ==========
    if callback_data == "my_orders":
        orders = db.get_orders(user_id)
        if not orders:
            await query.edit_message_text(
                get_text("no_orders", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        text = get_text("my_orders", lang)
        for order in orders[:10]:
            status_ru = {
                "New": "🆕 Новый",
                "Confirmed": "✅ Подтверждён",
                "Preparing": "👨‍🍳 Готовится",
                "Delivery": "🚚 В доставке",
                "Delivered": "📦 Доставлен",
                "Cancelled": "❌ Отменён",
            }.get(order.status.value, order.status.value)
            
            text += f"🆔 {order.id}\n🌸 {order.flower.name}\n📊 {status_ru if lang == 'ru' else order.status.value}\n📅 {order.delivery_date}\n---\n"
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_main(lang)
        )
        return States.ORDER_HISTORY
    
    # ========== СТАТУС ЗАКАЗА ==========
    if callback_data == "order_status":
        await query.edit_message_text(
            get_text("order_status_input", lang),
            reply_markup=None
        )
        data["state"] = States.ORDER_STATUS_INPUT
        return States.ORDER_STATUS_INPUT
    
    # ========== ПАНЕЛЬ МЕНЕДЖЕРА ==========
    if callback_data == "manager_panel":
        if not is_manager:
            await query.edit_message_text(
                get_text("manager_access_denied", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        await query.edit_message_text(
            get_text("manager_panel", lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=manager_menu(lang)
        )
        return States.MANAGER_MENU
    
    if callback_data == "manager_all_orders":
        if not is_manager:
            await query.edit_message_text(
                get_text("manager_access_denied", lang),
                reply_markup=back_to_main(lang)
            )
            return States.MAIN_MENU
        
        orders = db.get_orders()
        if not orders:
            await query.edit_message_text(
                get_text("manager_no_orders", lang),
                reply_markup=manager_menu(lang)
            )
            return States.MANAGER_MENU
        
        text = get_text("manager_all_orders", lang)
        keyboard = []
        for order in orders[:10]:
            status_ru = {
                "New": "🆕",
                "Confirmed": "✅",
                "Preparing": "👨‍🍳",
                "Delivery": "🚚",
                "Delivered": "📦",
                "Cancelled": "❌",
            }.get(order.status.value, "")
            
            status_display = status_ru if lang == "ru" else order.status.value
            text += f"🆔 {order.id} | {order.flower.name} | {status_display}\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 {order.id} - {order.flower.name}",
                    callback_data=f"view_order_{order.id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад" if lang == "ru" else "🔙 Back", callback_data="manager_panel")])
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return States.MANAGER_VIEW_ORDERS
