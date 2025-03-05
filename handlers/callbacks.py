from services.telegram_api import send_message, delete_message
from services.payments import handle_payment  # Import the handle_payment function
from services.payments import create_checkout_session  # Import the create_checkout_session function

def handle_callback(update):
    """Handles inline button interactions."""
    callback_query = update["callback_query"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    callback_data = callback_query["data"]

    try:
        print(f"📌 DEBUG: Received callback with data: {callback_data}")  # ✅ Debugging

        if callback_data == "open_fractalbio":
            url = "https://www.fractalbio.ai"  # ✅ Safe URL inside the function
            safe_url = url.replace(".", "\\.")  # ✅ Escape dots for MarkdownV2
            send_message(chat_id, f"🔗 [Нажмите здесь, чтобы открыть сайт]({safe_url})", parse_mode="MarkdownV2")
            delete_message(chat_id, message_id)  # ✅ Ensure callback messages are deleted

        elif callback_data == "open_stripe":
            url = create_checkout_session(chat_id)  # ✅ Stripe URL
            safe_url = url.replace(".", "\\.")  # ✅ Escape dots for MarkdownV2
            send_message(chat_id, f"💳 [Оформить подписку]({safe_url})", parse_mode="MarkdownV2")
            delete_message(chat_id, message_id)  # ✅ Ensure callback messages are deleted

        elif callback_data == "start_chat":
            send_message(chat_id, "Привет! Я digital-Даша, твой тренер. Чем могу помочь?")
            delete_message(chat_id, message_id)  # ✅ Ensure callback messages are deleted

        elif callback_data == "about_project":
            send_message(chat_id, "📌 Это мой Telegram бот, который помогает с фитнесом и ИИ-советами!")
            delete_message(chat_id, message_id)  # ✅ Ensure callback messages are deleted

        delete_message(chat_id, message_id)  # ✅ Ensure callback messages are deleted

    except Exception as e:
        print(f"🚨 ERROR in handle_callback: {e}")  # ✅ Catch errors
        send_message(chat_id, "⚠️ Ошибка обработки запроса. Попробуйте позже.")
