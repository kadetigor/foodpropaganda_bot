from services.telegram_api import send_message, delete_message

def handle_callback(update):
    """Handles inline button interactions."""
    callback_query = update["callback_query"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    callback_data = callback_query["data"]

    if callback_data == "start_chat":
        send_message(chat_id, "Привет! Я digital-Даша, твой тренер. Чем могу помочь?")
    elif callback_data == "about_project":
        send_message(chat_id, "📌 Это мой Telegram бот, который помогает с фитнесом и ИИ-советами!")
    
    delete_message(chat_id, message_id)
