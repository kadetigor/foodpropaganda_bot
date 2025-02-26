from services.openai_service import get_openai_response
from services.telegram_api import send_message

def handle_message(update):
    """Handles regular messages by sending them to OpenAI API."""
    chat_id = update["message"]["chat"]["id"]
    user_message = update["message"]["text"]
    ai_response = get_openai_response(user_message)
    send_message(chat_id, ai_response)
