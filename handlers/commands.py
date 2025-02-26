from services.telegram_api import send_message, send_photo_with_buttons
from config import WELCOME_IMAGE_URL, STRIPE_CHECKOUT_URL

def handle_start(chat_id):
    """Handles the /start command."""
    buttons = [
        [{"text": "Поговорить с моим ИИ клоном", "callback_data": "start_chat"}],
        [{"text": "Мой сайт", "url": "https://www.fractalbio.ai/"}],
        [{"text": "Что умеет этот бот?", "callback_data": "about_project"}]
    ]

    send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "👋 Добро пожаловать в мой ТГ чат-бот!", buttons)

def handle_subscribe(chat_id):
    """Handles the /subscribe command."""
    send_message(chat_id, f"Subscribe here: {STRIPE_CHECKOUT_URL}")

def handle_daily_tip(chat_id):
    """Handles the /daily_tip command."""
    send_message(chat_id, "You've subscribed to daily fitness tips!")