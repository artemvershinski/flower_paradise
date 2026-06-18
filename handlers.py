import logging
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import MANAGER_CHAT_ID
from states import States
from keyboards import *
from database import db
from models import Flower, Order, OrderStatus

logger = logging.getLogger(__name__)

user_data_store = {}

def get_user_data(user_id):
    if user_id not in user_data_store:
        user_data_store[user_id] = {}
    return user_data_store[user_id]

def get_user_role(user_id: int) -> bool:
    if user_id == MANAGER_CHAT_ID:
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    is_manager = get_user_role(user_id)
    data = get_user_data(user_id)
    data['is_manager'] = is_manager
    
    welcome_text = (
        f"Hello, {user.first_name}!\n\n"
        "Welcome to Flower Paradise flower shop!\n"
        "We have the most beautiful and fresh flowers.\n\n"
        "Choose an action:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu(is_manager)
    )
    return States.MAIN_MENU

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)
    
    callback_data = query.data
    
    # Back to main menu
    if callback_data == "back_main":
        is_manager = get_user_role(user_id)
        await query.edit_message_text(
            "Main menu:\n\nChoose an action:",
            reply_markup=main_menu(is_manager)
        )
        return States.MAIN_MENU
    
    # Contacts
    if callback_data == "contacts":
        await query.edit_message_text(
            "Contacts\n\n"
            "Address: Tsvetochnaya str., 15\n"
            "Phone: +7 (999) 123-45-67\n"
            "Working hours: 9:00 - 21:00\n"
            "Website: flowerparadise.ru\n\n"
            "We work every day and are always glad to see you!",
            reply_markup=contacts_keyboard()
        )
        return States.MAIN_MENU
    
    # Catalog
    if callback_data == "catalog":
        await query.edit_message_text(
            "Select category:",
            reply_markup=categories_menu()
        )
        return States.SELECT_CATEGORY
    
    if callback_data == "back_catalog":
        await query.edit_message_text(
            "Select category:",
            reply_markup=categories_menu()
        )
        return States.SELECT_CATEGORY
    
    # Category selection
    if callback_data.startswith("cat_"):
        category = callback_data.replace("cat_", "")
        data['category'] = category
        
        flowers = db.get_flowers(category)
        if not flowers:
            await query.edit_message_text(
                "No flowers in this category yet.\n"
                "Check back later!",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        data['flowers'] = flowers
        data['page'] = 0
        
        await query.edit_message_text(
            f"Flowers in category:\n\n"
            f"Total: {len(flowers)} bouquets",
            reply_markup=flowers_list(flowers, 0)
        )
        return States.SELECT_FLOWER
    
    if callback_data == "back_flowers":
        flowers = data.get('flowers', [])
        await query.edit_message_text(
            f"Flowers in category:\n\n"
            f"Total: {len(flowers)} bouquets",
            reply_markup=flowers_list(flowers, data.get('page', 0))
        )
        return States.SELECT_FLOWER
    
    # Pagination
    if callback_data.startswith("page_"):
        page = int(callback_data.split("_")[1])
        data['page'] = page
        flowers = data.get('flowers', [])
        
        await query.edit_message_text(
            f"Flowers in category:\n\n"
            f"Total: {len(flowers)} bouquets",
            reply_markup=flowers_list(flowers, page)
        )
        return States.SELECT_FLOWER
    
    # View flower
    if callback_data.startswith("flower_"):
        flower_id = int(callback_data.split("_")[1])
        flower = db.get_flower(flower_id)
        if not flower:
            await query.edit_message_text(
                "Flower not found",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        data['selected_flower'] = flower
        
        text = (
            f"{flower.name}\n\n"
            f"Price: {flower.price} \n"
            f"{flower.description}\n\n"
            f"{'In stock' if flower.in_stock else 'Out of stock'}"
        )
        
        await query.edit_message_text(
            text,
            reply_markup=flower_detail(flower)
        )
        return States.VIEW_FLOWER
    
    # Order flower
    if callback_data.startswith("order_"):
        if "order_flower" in callback_data:
            await query.edit_message_text(
                "Select category first:",
                reply_markup=categories_menu()
            )
            return States.SELECT_CATEGORY
        
        flower_id = int(callback_data.split("_")[1])
        flower = db.get_flower(flower_id)
        if not flower:
            await query.edit_message_text(
                "Flower not found",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        data['selected_flower'] = flower
        data['order'] = {}
        
        await query.edit_message_text(
            f"Ordering: {flower.name}\n\n"
            "Please enter your delivery address:",
            reply_markup=None
        )
        return States.ASK_ADDRESS
    
    # Order from main menu
    if callback_data == "order_flower":
        await query.edit_message_text(
            "Select category:",
            reply_markup=categories_menu()
        )
        return States.SELECT_CATEGORY
    
    # Delivery date
    if callback_data.startswith("delivery_date_"):
        date = callback_data.replace("delivery_date_", "")
        data['delivery_date'] = date
        
        await query.edit_message_text(
            f"Delivery date: {date}\n\n"
            "Select delivery time:",
            reply_markup=delivery_time_keyboard()
        )
        return States.ASK_DELIVERY_TIME
    
    # Delivery time
    if callback_data.startswith("time_"):
        time = callback_data.replace("time_", "").replace("-", ":")
        data['delivery_time'] = time
        
        await query.edit_message_text(
            f"Delivery time: {time}\n\n"
            "Please enter your phone number:",
            reply_markup=None
        )
        return States.ASK_PHONE
    
    # Confirm order
    if callback_data == "confirm_order":
        order_data = data.get('order', {})
        flower = data.get('selected_flower')
        
        if not flower:
            await query.edit_message_text(
                "Error: no flower selected",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        order = Order(
            id="",
            user_id=user_id,
            user_name=order_data.get('name', ''),
            user_phone=order_data.get('phone', ''),
            flower=flower,
            address=order_data.get('address', ''),
            delivery_date=order_data.get('delivery_date', ''),
            delivery_time=order_data.get('delivery_time', ''),
            comment=order_data.get('comment', '')
        )
        
        order_id = db.create_order(order)
        
        # Notify manager
        await context.bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=f"New order!n\n"
                 f"Order ID: {order_id}\n"
                 f"Flower: {flower.name}\n"
                 f"Price: {flower.price}\n"
                 f"Customer: {order.user_name}\n"
                 f"Phone: {order.user_phone}\n"
                 f"Address: {order.address}\n"
                 f"Delivery: {order.delivery_date} at {order.delivery_time}"
        )
        
        await query.edit_message_text(
            f"Order confirmed!\n\n"
            f"Order ID: {order_id}\n"
            f"Flower: {flower.name}\n"
            f"Price: {flower.price}\n\n"
            "We will contact you shortly.",
            reply_markup=back_to_main()
        )
        
        data.pop('order', None)
        return ConversationHandler.END
    
    # Cancel order
    if callback_data == "cancel_order":
        data.pop('order', None)
        await query.edit_message_text(
            "Order cancelled.",
            reply_markup=back_to_main()
        )
        return States.MAIN_MENU
    
    # My orders
    if callback_data == "my_orders":
        orders = db.get_orders(user_id)
        if not orders:
            await query.edit_message_text(
                "You have no orders yet.",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        text = "Your orders:\n\n"
        for order in orders[:10]:
            text += (
                f"ID: {order.id}\n"
                f"Flower: {order.flower.name}\n"
                f"Status: {order.status.value}\n"
                f"Date: {order.delivery_date}\n"
                f"---\n"
            )
        
        await query.edit_message_text(
            text,
            reply_markup=back_to_main()
        )
        return States.ORDER_HISTORY
    
    # Order status
    if callback_data == "order_status":
        await query.edit_message_text(
            "Enter your order ID:",
            reply_markup=None
        )
        return States.ORDER_STATUS
    
    # Manager panel
    if callback_data == "manager_panel":
        if not get_user_role(user_id):
            await query.edit_message_text(
                "Access denied.",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        await query.edit_message_text(
            "Manager Panel:\n\n"
            "Select action:",
            reply_markup=manager_menu()
        )
        return States.MANAGER_MENU
    
    # Manager all orders
    if callback_data == "manager_all_orders":
        if not get_user_role(user_id):
            await query.edit_message_text(
                "Access denied.",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        orders = db.get_orders()
        if not orders:
            await query.edit_message_text(
                "No orders found.",
                reply_markup=manager_menu()
            )
            return States.MANAGER_MENU
        
        text = "All orders:\n\n"
        for order in orders[:20]:
            text += (
                f"ID: {order.id}\n"
                f"Flower: {order.flower.name}\n"
                f"Customer: {order.user_name}\n"
                f"Status: {order.status.value}\n"
                f"---\n"
            )
        
        keyboard = []
        for order in orders[:10]:
            keyboard.append([
                InlineKeyboardButton(
                    f"Order {order.id}",
                    callback_data=f"view_order_{order.id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("Back", callback_data="manager_panel")])
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return States.MANAGER_VIEW_ORDERS
    
    # View specific order
    if callback_data.startswith("view_order_"):
        order_id = callback_data.replace("view_order_", "")
        order = db.get_order(order_id)
        if not order:
            await query.edit_message_text(
                "Order not found.",
                reply_markup=manager_menu()
            )
            return States.MANAGER_MENU
        
        data['viewing_order'] = order_id
        
        text = (
            f"Order Details\n\n"
            f"ID: {order.id}\n"
            f"Flower: {order.flower.name}\n"
            f"Price: {order.flower.price}\n"
            f"Customer: {order.user_name}\n"
            f"Phone: {order.user_phone}\n"
            f"Address: {order.address}\n"
            f"Delivery: {order.delivery_date} at {order.delivery_time}\n"
            f"Status: {order.status.value}\n"
            f"Comment: {order.comment or 'None'}"
        )
        
        await query.edit_message_text(
            text,
            reply_markup=status_change_keyboard(order_id, order.status.value)
        )
        return States.MANAGER_CHANGE_STATUS
    
    # Change status
    if callback_data.startswith("change_status_"):
        parts = callback_data.split("_")
        order_id = parts[2]
        new_status = "_".join(parts[3:])
        
        order = db.get_order(order_id)
        if not order:
            await query.edit_message_text(
                "Order not found.",
                reply_markup=manager_menu()
            )
            return States.MANAGER_MENU
        
        status_map = {
            "New": OrderStatus.NEW,
            "Confirmed": OrderStatus.CONFIRMED,
            "Preparing": OrderStatus.PREPARING,
            "Delivery": OrderStatus.DELIVERY,
            "Delivered": OrderStatus.DELIVERED,
            "Cancelled": OrderStatus.CANCELLED,
        }
        
        status = status_map.get(new_status)
        if not status:
            await query.edit_message_text(
                "Invalid status.",
                reply_markup=manager_menu()
            )
            return States.MANAGER_MENU
        
        db.update_order_status(order_id, status)
        
        # Notify customer
        await context.bot.send_message(
            chat_id=order.user_id,
            text=f"Order {order_id} status updated to: {status.value}"
        )
        
        await query.edit_message_text(
            f"Order {order_id} status updated to: {status.value}",
            reply_markup=manager_menu()
        )
        return States.MANAGER_MENU
    
    if callback_data == "back_orders":
        await query.edit_message_text(
            "Manager Panel:",
            reply_markup=manager_menu()
        )
        return States.MANAGER_MENU
    
    if callback_data == "back_order":
        await query.edit_message_text(
            "Select category:",
            reply_markup=categories_menu()
        )
        return States.SELECT_CATEGORY
    
    return States.MAIN_MENU

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    text = update.message.text
    
    # Order status check
    if data.get('state') == States.ORDER_STATUS:
        order = db.get_order(text.strip())
        if not order:
            await update.message.reply_text(
                "Order not found. Please check your order ID.",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        if order.user_id != user_id:
            await update.message.reply_text(
                "Access denied.",
                reply_markup=back_to_main()
            )
            return States.MAIN_MENU
        
        status_text = (
            f"Order {order.id}\n\n"
            f"Flower: {order.flower.name}\n"
            f"Status: {order.status.value}\n"
            f"Delivery: {order.delivery_date} at {order.delivery_time}\n"
        )
        
        await update.message.reply_text(
            status_text,
            reply_markup=back_to_main()
        )
        return States.MAIN_MENU
    
    # Address input
    if data.get('state') == States.ASK_ADDRESS:
        data['address'] = text
        data['state'] = States.ASK_DELIVERY_DATE
        
        await update.message.reply_text(
            "Select delivery date:",
            reply_markup=delivery_date_keyboard()
        )
        return States.ASK_DELIVERY_DATE
    
    # Phone input
    if data.get('state') == States.ASK_PHONE:
        data['phone'] = text
        data['state'] = States.ASK_COMMENT
        
        await update.message.reply_text(
            "Any comments for your order? (or type 'no')",
            reply_markup=None
        )
        return States.ASK_COMMENT
    
    # Comment input
    if data.get('state') == States.ASK_COMMENT:
        comment = text if text.lower() != 'no' else ''
        
        flower = data.get('selected_flower')
        order = {
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'delivery_date': data.get('delivery_date', ''),
            'delivery_time': data.get('delivery_time', ''),
            'comment': comment
        }
        data['order'] = order
        
        confirmation_text = (
            f"Order confirmation:\n\n"
            f"Flower: {flower.name
