from flask import Flask, request  # Flask to handle incoming HTTP requests
import stripe  # Stripe library to interact with Stripe API
from datetime import datetime, timedelta  # To handle expiration dates and time calculations
from supabase import create_client  # Supabase client to interact with the database
import os  # For accessing environment variables
from dotenv import load_dotenv  # To load environment variables from .env file
from services.telegram_api import send_message, send_photo_with_buttons  # Import your function to send Telegram messages
from database import get_visitor, transfer_user_to_subscriptions  # Import your database functions
from utils.logger import setup_logger
from utils.message_tracker import track_message
from config import WELCOME_IMAGE_URL

# Set up logger
logger = setup_logger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set Stripe secret key for API communication and webhook secret for verifying requests
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # Stripe secret key for authenticating API calls
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')  # Webhook secret for validating Stripe events

# Supabase connection setup (initialize the Supabase client to interact with the database)
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Supabase URL from the .env file
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Supabase API key from the .env file
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)  # Create a Supabase client instance

# Initialize the Flask app (Flask will handle incoming requests to your webhook endpoint)
app = Flask(__name__)

def show_subscriber_menu(chat_id, nickname):
    """Show the subscriber menu with subscriber-specific buttons."""
    buttons = [
        [{"text": "Спросить ИИ", "callback_data": "start_chat"}],
        [{"text": "Сдать Отчет", "callback_data": "submit_report"}],
        [{"text": "Настройки", "callback_data": "settings"}]
    ]
    
    msg_id = send_photo_with_buttons(
        chat_id, 
        WELCOME_IMAGE_URL, 
        f"🎉 Спасибо за подписку, {nickname}! Ваша подписка активирована.", 
        buttons
    )
    if msg_id:
        track_message(chat_id, msg_id)

# Define the route that Stripe will use to send webhook events
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """Handles Stripe webhooks and transfers users from visitors to subscriptions."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        logger.error(f"Error parsing webhook event: {e}")
        return f"Error: {e}", 400

    logger.info(f"Successful Stripe Event: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")  # Ensure metadata exists

        # Check if user_id is missing
        if not user_id:
            logger.error("Missing user_id in metadata! Stripe session data:")
            return "", 200  # Prevents further errors

        try:
            user_id = int(user_id)  # Ensure it's an integer
        except ValueError:
            logger.error(f"Invalid user_id format: {user_id}")
            return "", 200  # Prevents errors

        stripe_sub_id = session.get("subscription")
        stripe_cust_id = session.get("customer")
        next_payment = session.get("current_period_end")

        visitor = get_visitor(user_id)  # Fetch user safely
        if visitor:
            transfer_user_to_subscriptions(
                user_id=user_id,
                email=visitor["email"],
                nickname=visitor["nickname"],
                stripe_sub_id=stripe_sub_id,
                stripe_cust_id=stripe_cust_id,
                provider="stripe",
                status="active",
                next_payment=next_payment
            )
            send_message(user_id, f"🎉 Спасибо за подписку, @{visitor['nickname']}! Ваша подписка активирована.")
            show_subscriber_menu(user_id, visitor['nickname'])
            # This is not an AI response, but it's an important subscription message that we should keep
            # We don't track it to avoid deletion
        else:
            logger.error("User not found in Supabase visitors table!")

    return "", 200