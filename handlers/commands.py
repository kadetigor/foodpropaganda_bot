from services.telegram_api import send_message, send_photo_with_buttons
from services.payments import handle_payment, create_checkout_session  # Import payment handling
from config import WELCOME_IMAGE_URL, STRIPE_CHECKOUT_URL
from database import save_visitor, get_user_status   # Function to save users in Supabase
from utils.logger import setup_logger
from utils.message_tracker import track_message, delete_bot_messages

# Set up logger
logger = setup_logger(__name__)

def handle_start(update):
    """Handles the /start command by asking for an email."""
    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")
    username = update["message"]["from"].get("username", None)  # Extracts Telegram @nickname

    # Delete previous bot messages when user sends a command
    delete_bot_messages(chat_id)

    logger.info(f"Received /start command from chat_id: {chat_id}, text: {text}")

    if not username:
        username = f"user_{chat_id}"  # Fallback if the user has no Telegram username
    
    # Check if the user already exists in visitors or subscriptions
    user_status = get_user_status(chat_id)  # ✅ Now checks both tables
    logger.info(f"User status from database: {user_status}")

    if user_status is None:
        msg_id = send_message(chat_id, "👋 Добро пожаловать! Пожалуйста отправьте следующим сообщением свой email чтобы продолжить.")
        if msg_id:
            track_message(chat_id, msg_id)  # Track this message
        return

    if "subscription_success_" in text:
        msg_id = send_message(chat_id, "🎉 Спасибо за подписку! Ваша подписка активирована.")
        if msg_id:
            track_message(chat_id, msg_id)  # Track this message
    elif "subscription_cancelled" in text:
        msg_id = send_message(chat_id, "❌ Подписка была отменена. Если у вас есть вопросы, напишите поддержку.")
        if msg_id:
            track_message(chat_id, msg_id)  # Track this message
    
    # Show different menus based on user status
    if user_status == "subscriber":
        # User is a subscriber, show subscriber menu
        buttons = [
            [{"text": "Спросить ИИ", "callback_data": "start_chat"}],
            [{"text": "Сдать Отчет", "callback_data": "submit_report"}],
            [{"text": "Настройки", "callback_data": "settings"}]
        ]
        logger.info("Sending subscriber menu with buttons...")
    else:
        # User is a visitor, show visitor menu
        buttons = [
            [{"text": "Поговорить с моим ИИ клоном", "callback_data": "start_chat"}],
            [{"text": "Открыть сайт", "callback_data": "open_website"}],  # ✅ Intercept URL
            [{"text": "Что умеет этот бот?", "callback_data": "about_project"}],
            [{"text": "Подписаться", "callback_data": "open_stripe"}]  # ✅ Intercept URL
        ]
        logger.info("Sending visitor menu with buttons...")
    
    msg_id = send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "👋 Добро пожаловать в мой ТГ чат-бот!", buttons)
    if msg_id:
        track_message(chat_id, msg_id)  # Track this message


def handle_subscribe(update):  # Updated to accept full update object
    """Handles the /subscribe command."""
    chat_id = update["message"]["chat"]["id"]  # Extract chat ID
    username = update["message"]["from"].get("username", "user")  # Get username with fallback

    # Delete previous bot messages when user sends a command
    delete_bot_messages(chat_id)

    handle_payment(chat_id, username)  # Create and send payment link

def handle_daily_tip(update):
    """Handles the /daily_tip command."""
    chat_id = update["message"]["chat"]["id"]

    # Delete previous bot messages when user sends a command
    delete_bot_messages(chat_id)

    msg_id = send_message(chat_id, "You've subscribed to daily fitness tips!")
    if msg_id:
            track_message(chat_id, msg_id)  # Track this message