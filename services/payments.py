import stripe  # Stripe SDK for payment processing
import os  # For accessing environment variables
from dotenv import load_dotenv  # To load environment variables
from services.telegram_api import send_message  # Import for sending Telegram messages

load_dotenv()  # Load environment variables

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # Initialize Stripe with our secret key

def create_checkout_session(user_id):
    """Creates a Stripe checkout session with proper metadata."""

    # ✅ Ensure user_id is not None
    if not user_id:
        return None  # Prevents sending invalid data to Stripe

    session = stripe.checkout.Session.create(
        metadata={"user_id": str(user_id)},  # ✅ Ensure metadata is passed
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1QwmugHosnZdZMx3vXdnmger',
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'https://t.me/FoodPropaganda_bot?start=welcome_back',
        cancel_url=f'https://t.me/FoodPropaganda_bot?start=subscription_cancelled',
    )


    return session.url
  # Return the checkout URL

def handle_payment(chat_id):
    """Sends the payment link to the user only after they click "Subscribe"."""
    checkout_url = create_checkout_session(chat_id)
    send_message(chat_id, f"💳 Чтобы оформить подписку, перейдите по ссылке: {checkout_url}")