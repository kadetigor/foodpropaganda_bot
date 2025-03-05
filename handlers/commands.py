from services.telegram_api import send_message, send_photo_with_buttons
from services.payments import handle_payment, create_checkout_session  # Import payment handling
from config import WELCOME_IMAGE_URL, STRIPE_CHECKOUT_URL
from database import save_visitor, get_user_status   # Function to save users in Supabase

def handle_start(update):
    """Handles the /start command by asking for an email."""
    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")
    username = update["message"]["from"].get("username", None)  # Extracts Telegram @nickname

    print(f"📌 DEBUG: Received /start command from chat_id: {chat_id}, text: {text}")  # ✅ Debugging

    if not username:
        username = f"user_{chat_id}"  # Fallback if the user has no Telegram username
    
    # Check if the user already exists in visitors or subscriptions
    user_status = get_user_status(chat_id)  # ✅ Now checks both tables
    print(f"📌 DEBUG: User status from database: {user_status}")  # ✅ Debugging

    if user_status is None:
        send_message(chat_id, "👋 Добро пожаловать! Пожалуйста отправьте следующим сообщением свой email чтобы продолжить.")
        return

    if "subscription_success_" in text:
        send_message(chat_id, "🎉 Спасибо за подписку! Ваша подписка активирована.")
    elif "subscription_cancelled" in text:
        send_message(chat_id, "❌ Подписка была отменена. Если у вас есть вопросы, напишите поддержку.")
    
    # User already exists, show the menu
    buttons = [
        [{"text": "Поговорить с моим ИИ клоном", "callback_data": "start_chat"}],
        [{"text": "Открыть сайт", "callback_data": "open_website"}],  # ✅ Intercept URL
        [{"text": "Что умеет этот бот?", "callback_data": "about_project"}],
        [{"text": "Подписаться", "callback_data": "open_stripe"}]  # ✅ Intercept URL
    ]
    print("📌 DEBUG: Sending menu with buttons...")  # ✅ Debugging
    send_photo_with_buttons(chat_id, WELCOME_IMAGE_URL, "👋 Добро пожаловать в мой ТГ чат-бот!", buttons)


def handle_subscribe(update):  # Updated to accept full update object
    """Handles the /subscribe command."""
    chat_id = update["message"]["chat"]["id"]  # Extract chat ID
    username = update["message"]["from"].get("username", "user")  # Get username with fallback
    handle_payment(chat_id, username)  # Create and send payment link

def handle_daily_tip(chat_id):
    """Handles the /daily_tip command."""
    send_message(chat_id, "You've subscribed to daily fitness tips!")