from services.telegram_api import send_message, send_photo_with_buttons
from services.payments import handle_payment  # Import payment handling
from config import WELCOME_IMAGE_URL, STRIPE_CHECKOUT_URL

def handle_start(chat_id):
    """Handles the /start command."""
    buttons = [
        [{"text": "Поговорить с моим ИИ клоном", "callback_data": "start_chat"}],
        [{"text": "Мой сайт", "url": "https://www.fractalbio.ai/"}],
        [{"text": "Что умеет этот бот?", "callback_data": "about_project"}],
        [{"text": "Подписаться", "url": STRIPE_CHECKOUT_URL}]
    ]

    send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "👋 Добро пожаловать в мой ТГ чат-бот!", buttons)

def handle_subscribe(update):  # Updated to accept full update object
    """Handles the /subscribe command."""
    chat_id = update["message"]["chat"]["id"]  # Extract chat ID
    username = update["message"]["from"].get("username", "user")  # Get username with fallback
    handle_payment(chat_id, username)  # Create and send payment link

def handle_daily_tip(chat_id):
    """Handles the /daily_tip command."""
    send_message(chat_id, "You've subscribed to daily fitness tips!")