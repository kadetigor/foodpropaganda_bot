from services.telegram_api import send_photo_with_buttons
from config import WELCOME_IMAGE_URL

def handle_new_user(update):
    """Detects new users joining the chat and sends a welcome message."""
    if "message" in update and "new_chat_members" in update["message"]:
        chat_id = update["message"]["chat"]["id"]

        for user in update["message"]["new_chat_members"]:
            if not user["is_bot"]:  # Ensure it's a human
                send_photo_with_buttons(
                    chat_id,
                    WELCOME_IMAGE_URL,
                    "👋 Добро пожаловать в мой ТГ чат-бот!",
                    [[{"text": "Что умеет этот бот?", "callback_data": "about_project"}]]
                )
