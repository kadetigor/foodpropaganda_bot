from services.openai_service import get_openai_response
from services.telegram_api import send_message, send_photo_with_buttons, delete_message
from database import save_visitor, get_user_status
from config import WELCOME_IMAGE_URL, COMPANY_WEBSITE
from utils.logger import setup_logger
from utils.message_tracker import track_message, delete_bot_messages
import re

# Set up logger
logger = setup_logger(__name__)

def is_valid_email(email):
    """Validate email format using regex."""
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email)

def handle_message(update):
    """
    Handles regular messages, tracks user interaction and deletes previous bot messages.
    Preserves AI responses.
    """
    chat_id = update["message"]["chat"]["id"]
    username = update["message"]["from"].get("username", None)  # Extracts Telegram @nickname
    user_message = update["message"]["text"]

    # First, delete previous bot messages when user sends a new message
    delete_bot_messages(chat_id)

    user_status = get_user_status(chat_id)  # ✅ Check if user exists

    if user_status is None:
        # ✅ User is new → Expect an email
        if is_valid_email(user_message):
            save_visitor(chat_id, user_message, username)  # ✅ Save email NOW

            # ✅ Show menu after saving email
            buttons = [
                [{"text": "Поговорить с моим ИИ клоном", "callback_data": "start_chat"}],
                [{"text": "Открыть сайт", "callback_data": "open_website"}],  # ✅ Intercept URL
                [{"text": "Что умеет этот бот?", "callback_data": "about_project"}],
                [{"text": "Подписаться", "callback_data": "open_stripe"}]  # ✅ Intercept URL
            ]
            msg_id = send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "✅ Ваш email сохранен! Выберите действие:", buttons)
            if msg_id:
                track_message(chat_id, msg_id)  # Track this message
            return  # ✅ STOP further processing (Prevents AI from responding)
        else:
            msg_id = send_message(chat_id, "⚠️ Похоже вы ввели недействительный email. Пожалуйста, отправьте реальный email, чтобы продолжить. Например: example@example.com")
            if msg_id:
                track_message(chat_id, msg_id)  # Track this message
            return  # ✅ Prevent AI from processing invalid messages

    # ✅ If the user exists, send their message to AI normally
    ai_response = get_openai_response(user_message, chat_id)
    send_message(chat_id, ai_response)
