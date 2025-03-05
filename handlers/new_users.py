from services.telegram_api import send_photo_with_buttons
from config import WELCOME_IMAGE_URL
from utils.message_tracker import track_message
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

def handle_new_user(update):
    """Detects new users joining the chat and sends a welcome message."""
    if "message" in update and "new_chat_members" in update["message"]:
        chat_id = update["message"]["chat"]["id"]

        for user in update["message"]["new_chat_members"]:
            if not user["is_bot"]:  # Ensure it's a human
                logger.info(f"New user joined: {user.get('username', 'Unknown')}")
                msg_id = send_photo_with_buttons(
                    chat_id,
                    WELCOME_IMAGE_URL,
                    "👋 Добро пожаловать в мой ТГ чат-бот!",
                    [[{"text": "Что умеет этот бот?", "callback_data": "about_project"}]]
                )
                if msg_id:
                    track_message(chat_id, msg_id)  # Track this message
