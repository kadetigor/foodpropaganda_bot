from flask import Flask, request  # Flask to handle incoming HTTP requests
import stripe  # Stripe library to interact with Stripe API
from datetime import datetime, timedelta  # To handle expiration dates and time calculations
from supabase import create_client  # Supabase client to interact with the database
import os  # For accessing environment variables
from dotenv import load_dotenv  # To load environment variables from .env file
from services.telegram_api import send_message  # Import your function to send Telegram messages

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

# Define the route that Stripe will use to send webhook events
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """
    Handles Stripe webhook events and updates the user's subscription in Supabase.
    """
    payload = request.get_data(as_text=True)  # Get the raw POST data from Stripe
    sig_header = request.headers.get("Stripe-Signature")  # Get the Stripe-Signature header for validation

    # ✅ Log Incoming Webhook Requests
    print(f"🔹 Received Webhook: {payload}")  # Debugging line
    print(f"🔹 Signature Header: {sig_header}")  # Debugging line

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        print(f"🚨 Invalid JSON: {e}")  # Debugging line
        return f"Invalid JSON: {e}", 400
    except stripe.error.SignatureVerificationError as e:
        print(f"🚨 Invalid Signature: {e}")  # Debugging line
        return f"Invalid signature: {e}", 400
    except Exception as e:
        print(f"🚨 Other Error: {e}")  # Debugging line
        return f"Error: {e}", 403  # <== This should return error details

    # ✅ If successful, print Stripe event type
    print(f"✅ Successful Stripe Event: {event['type']}")  # Debugging line

    def process_subscription(user_id, telegram_nickname):
        expires_at = datetime.utcnow() + timedelta(days=30)
        try:
            supabase.table("subscriptions").upsert({
                "user_id": user_id,
                "username": telegram_nickname,
                "provider": "stripe",
                "expires_at": expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                "last_active": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "return_frequency": 0
            }).execute()
            print(f"✅ Subscription saved for user: {user_id}")
            
            message = f"🎉 Спасибо за подписку, @{telegram_nickname}! Ваша подписка активирована до {expires_at.strftime('%Y-%m-%d')}."
            send_message(user_id, message)
            return True
        except Exception as db_error:
            print(f"🚨 Database Error: {db_error}")
            return False

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        customer = stripe.Customer.retrieve(customer_id)
        
        print(f"📝 Customer data: {customer}")
        metadata = session.get("metadata", {})
        
        user_id = metadata.get("user_id")
        telegram_nickname = metadata.get("telegram_nickname")
        
        if user_id and telegram_nickname:
            if not process_subscription(user_id, telegram_nickname):
                return "Database Error", 500
        else:
            print("🚨 Required metadata missing from checkout session")
            return "Metadata missing!", 400

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        customer = stripe.Customer.retrieve(customer_id)
        
        print(f"📝 Customer data: {customer}")
        metadata = customer.metadata
        
        user_id = metadata.get("user_id")
        telegram_nickname = metadata.get("telegram_nickname")
        
        if user_id and telegram_nickname:
            if not process_subscription(user_id, telegram_nickname):
                return "Database Error", 500
        else:
            print("🚨 Required metadata missing from customer")
            return "Metadata missing!", 400

    return "", 200