import requests
from config import TELEGRAM_API_URL

def get_updates(offset=None):
    """Get updates (new messages and button clicks) from Telegram."""
    url = f"{TELEGRAM_API_URL}getUpdates"
    params = {"offset": offset, "timeout": 30}  # Long polling
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    """Send a message to a Telegram user."""
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def delete_message(chat_id, message_id):
    """Delete a specific message by message_id."""
    url = f"{TELEGRAM_API_URL}deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, json=payload)

def send_photo_with_buttons(chat_id, photo_url, caption, buttons):
    """Send a photo with inline buttons."""
    url = f"{TELEGRAM_API_URL}sendPhoto"
    keyboard = {"inline_keyboard": buttons}
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "reply_markup": keyboard
    }

    requests.post(url, json=payload)
