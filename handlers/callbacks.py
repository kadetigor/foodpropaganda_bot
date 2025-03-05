from services.telegram_api import send_message, delete_message, send_photo_with_buttons
from services.payments import create_checkout_session, cancel_subscription  # Import the cancel_subscription function
from utils.logger import setup_logger
from utils.message_tracker import track_message, delete_bot_messages
from config import WELCOME_IMAGE_URL
from database import get_user_status  # To check if user is a subscriber

# Set up logger
logger = setup_logger(__name__)

def handle_callback(update):
    """Handles inline button interactions."""
    callback_query = update["callback_query"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    callback_data = callback_query["data"]

    try:
        logger.info(f"Received callback with data: {callback_data}")

        # Delete previous bot messages when user clicks a button
        delete_bot_messages(chat_id)

        # Always try to delete the message that contained the clicked button
        try:
            delete_message(chat_id, message_id)
        except Exception as e:
            logger.error(f"Error deleting message with button: {e}")

        # Check if user is subscriber for subscriber-only features
        user_status = get_user_status(chat_id)

        if callback_data == "open_fractalbio" or callback_data == "open_website":
            url = "https://www.fractalbio.ai"
            safe_url = url.replace(".", "\\.")
            msg_id = send_message(chat_id, f"🔗 [Нажмите здесь, чтобы открыть сайт]({safe_url})", parse_mode="MarkdownV2")
            if msg_id:
                track_message(chat_id, msg_id)

        elif callback_data == "open_stripe":
            url = create_checkout_session(chat_id)
            if url:
                safe_url = url.replace(".", "\\.")
                msg_id = send_message(chat_id, f"💳 [Оформить подписку]({safe_url})", parse_mode="MarkdownV2")
                if msg_id:
                    track_message(chat_id, msg_id)
            else:
                msg_id = send_message(chat_id, "⚠️ Не удалось создать ссылку для оплаты. Пожалуйста, попробуйте позже.")
                if msg_id:
                    track_message(chat_id, msg_id)
            

        elif callback_data == "start_chat":
            msg_id = send_message(chat_id, "Привет! Я digital-Даша, твой тренер. Чем могу помочь?")
            # This is an AI response, so we don't track it
            # Don't track_message here as it's an AI response

        elif callback_data == "about_project":
            msg_id = send_message(chat_id, "📌 Это мой Telegram бот, который помогает с фитнесом и ИИ-советами!")
            if msg_id:
                track_message(chat_id, msg_id)

        # New subscriber-specific buttons
        elif callback_data == "submit_report":
            if user_status == "subscriber":
                msg_id = send_message(chat_id, "📝 Пожалуйста, отправьте свой отчет по тренировке/питанию за сегодня.")
                if msg_id:
                    track_message(chat_id, msg_id)
            else:
                msg_id = send_message(chat_id, "⚠️ Эта функция доступна только для подписчиков.")
                if msg_id:
                    track_message(chat_id, msg_id)
        
        elif callback_data == "settings":
            if user_status == "subscriber":
                buttons = [
                    [{"text": "Отменить подписку", "callback_data": "cancel_subscription"}],
                    [{"text": "Подключить FatSecret", "callback_data": "connect_fatsecret"}],
                    [{"text": "Отключить напоминания", "callback_data": "disable_reminders"}],
                    [{"text": "Назад", "callback_data": "back_to_subscriber_menu"}]
                ]
                msg_id = send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "⚙️ Настройки", buttons)
                if msg_id:
                    track_message(chat_id, msg_id)
            else:
                msg_id = send_message(chat_id, "⚠️ Настройки доступны только для подписчиков.")
                if msg_id:
                    track_message(chat_id, msg_id)
        
        elif callback_data == "back_to_subscriber_menu":
            show_subscriber_menu(chat_id)
        
        elif callback_data == "cancel_subscription":
            if user_status == "subscriber":
                # Get subscription ID from database and cancel it
                success = cancel_subscription(chat_id)
                
                if success:
                    msg_id = send_message(chat_id, "✅ Ваш запрос на отмену подписки принят. Подписка будет отменена в конце текущего периода.")
                    if msg_id:
                        track_message(chat_id, msg_id)
                    
                    # Return to settings menu
                    buttons = [
                        [{"text": "Назад к настройкам", "callback_data": "settings"}]
                    ]
                    msg_id = send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "Подписка отменена", buttons)
                    if msg_id:
                        track_message(chat_id, msg_id)
                else:
                    msg_id = send_message(chat_id, "⚠️ Не удалось отменить подписку. Пожалуйста, попробуйте позже или обратитесь в поддержку.")
                    if msg_id:
                        track_message(chat_id, msg_id)
            else:
                msg_id = send_message(chat_id, "⚠️ У вас нет активной подписки для отмены.")
                if msg_id:
                    track_message(chat_id, msg_id)
        
        elif callback_data == "connect_fatsecret":
            if user_status == "subscriber":
                msg_id = send_message(chat_id, "🔄 Функция подключения к FatSecret находится в разработке.")
                if msg_id:
                    track_message(chat_id, msg_id)
            else:
                msg_id = send_message(chat_id, "⚠️ Эта функция доступна только для подписчиков.")
                if msg_id:
                    track_message(chat_id, msg_id)
        
        elif callback_data == "disable_reminders":
            if user_status == "subscriber":
                msg_id = send_message(chat_id, "🔄 Напоминания отключены.")
                if msg_id:
                    track_message(chat_id, msg_id)
            else:
                msg_id = send_message(chat_id, "⚠️ Эта функция доступна только для подписчиков.")
                if msg_id:
                    track_message(chat_id, msg_id)

    except Exception as e:
        logger.error(f"ERROR in handle_callback: {e}")
        try:
            msg_id = send_message(chat_id, "⚠️ Ошибка обработки запроса. Попробуйте позже.")
            if msg_id:
                track_message(chat_id, msg_id)
        except Exception as err:
            logger.error(f"Failed to send error message: {err}")

def show_subscriber_menu(chat_id):
    """Show the subscriber menu with subscriber-specific buttons."""
    buttons = [
        [{"text": "Спросить ИИ", "callback_data": "start_chat"}],
        [{"text": "Сдать Отчет", "callback_data": "submit_report"}],
        [{"text": "Настройки", "callback_data": "settings"}]
    ]
    
    msg_id = send_photo_with_buttons(
        chat_id, 
        WELCOME_IMAGE_URL, 
        "👋 Добро пожаловать! Выберите действие:", 
        buttons
    )
    if msg_id:
        track_message(chat_id, msg_id)