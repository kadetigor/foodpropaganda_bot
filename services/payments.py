from services.telegram_api import send_message
from config import STRIPE_CHECKOUT_URL

def handle_payment(chat_id):
    """Sends the payment link to the user."""
    send_message(chat_id, f"Чтобы оформить подписку, перейдите по ссылке: {STRIPE_CHECKOUT_URL}")