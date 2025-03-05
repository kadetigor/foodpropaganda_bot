import requests
from config import TELEGRAM_API_URL
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

def get_updates(offset=None):
    """Get updates (new messages and button clicks) from Telegram."""
    url = f"{TELEGRAM_API_URL}getUpdates"
    params = {"offset": offset, "timeout": 30}  # Long polling
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text, parse_mode: str = None):
    """Send a message to a Telegram user."""
    url = f"{TELEGRAM_API_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if parse_mode:
        payload["parse_mode"] = parse_mode  # ✅ Add parse_mode only if provided

    response = requests.post(url, json=payload).json()

    # Return the message ID so we can track it
    if response.get("ok") and "result" in response:
        return response["result"].get("message_id")
    logger.error(f"Failed to send message: {response}")
    return None

def delete_message(chat_id, message_id):
    """Delete a specific message by message_id."""
    url = f"{TELEGRAM_API_URL}deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        response = requests.post(url, json=payload)
        response_json = response.json()
        return response_json.get("ok", False)
    except Exception as e:
        logger.error(f"Error deleting message {message_id}: {e}")
        return False

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

    response = requests.post(url, json=payload).json()
    logger.debug(f"Telegram API response (sendPhoto): {response}")

    # Return the message ID so we can track it
    if response.get("ok") and "result" in response:
        return response["result"].get("message_id")
    logger.error(f"Failed to send photo: {response}")
    return None