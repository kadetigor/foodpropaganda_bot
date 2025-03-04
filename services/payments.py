import stripe  # Stripe SDK for payment processing
import os  # For accessing environment variables
from dotenv import load_dotenv  # To load environment variables
from services.telegram_api import send_message  # Import for sending Telegram messages

load_dotenv()  # Load environment variables

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # Initialize Stripe with our secret key

def create_checkout_session(user_id, telegram_nickname):
    """Creates Stripe checkout session with user metadata."""
    # First create a customer with metadata
    customer = stripe.Customer.create(
        metadata={
            'user_id': str(user_id),
            'telegram_nickname': telegram_nickname
        }
    )

    # Then create session with this customer
    session = stripe.checkout.Session.create(
        customer=customer.id,  # Use our pre-created customer
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1QwmugHosnZdZMx3vXdnmger',
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://t.me/your_bot_username',
        cancel_url='https://t.me/your_bot_username',
        subscription_data={
            'metadata': {
                'user_id': str(user_id),
                'telegram_nickname': telegram_nickname
            }
        }
    )
    return session.url
  # Return the checkout URL

def handle_payment(chat_id, telegram_nickname):  # Updated to include username
    """Sends the payment link to the user."""
    checkout_url = create_checkout_session(chat_id, telegram_nickname)  # Generate unique checkout URL
    send_message(chat_id, f"Чтобы оформить подписку, перейдите по ссылке: {checkout_url}")  # Send to user