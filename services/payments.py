import stripe  # Stripe SDK for payment processing
from services.telegram_api import send_message  # Import for sending Telegram messages
from config import STRIPE_SECRET_KEY, STRIPE_PRICE_ID  # Import Stripe price ID
from utils.logger import setup_logger
from utils.message_tracker import track_message
from database import supabase  # Import Supabase for database operations

# Set up logger
logger = setup_logger(__name__)

# Initialize Stripe with our secret key
stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(user_id):
    """Creates a Stripe checkout session with proper metadata."""

    # ✅ Ensure user_id is not None
    if not user_id:
        logger.error("Attempted to create checkout session with None user_id")
        return None  # Prevents sending invalid data to Stripe

    try:
        logger.info(f"Creating Stripe checkout session for user {user_id}")

        session = stripe.checkout.Session.create(
            metadata={"user_id": str(user_id)},  # ✅ Ensure metadata is passed
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'https://t.me/FoodPropaganda_bot?start=welcome_back',
            cancel_url=f'https://t.me/FoodPropaganda_bot?start=subscription_cancelled',
        )

        logger.info(f"Checkout session created: {session.id}")
        return session.url
    except stripe.error.StripeError as e:
        # Handle specific Stripe errors
        logger.error(f"Stripe error: {str(e)}")
        return None
        
    except Exception as e:
        # Handle other unexpected errors
        logger.error(f"Error creating checkout session: {str(e)}")
        return None


def handle_payment(chat_id, username=None):
    """Sends the payment link to the user only after they click "Subscribe"."""

    logger.info(f"Payment handling initiated for user {chat_id}")

    checkout_url = create_checkout_session(chat_id)

    if checkout_url:
        logger.info(f"Sending payment link to user {chat_id}")
        msg_id = send_message(
            chat_id, 
            f"💳 Чтобы оформить подписку, перейдите по ссылке: {checkout_url}"
        )
        if msg_id:
            track_message(chat_id, msg_id)  # Track this message
    else:
        logger.error(f"Failed to create checkout URL for user {chat_id}")
        msg_id = send_message(
            chat_id, 
            "⚠️ Произошла ошибка при создании ссылки для оплаты. Пожалуйста, попробуйте позже."
        )
        if msg_id:
            track_message(chat_id, msg_id)  # Track this message


def get_user_subscription_id(user_id):
    """Retrieves a user's Stripe subscription ID from the database."""
    try:
        logger.info(f"Fetching subscription ID for user {user_id}")
        
        # Query the subscriptions table for this user
        response = supabase.table("subscriptions").select("stripe_sub_id").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            subscription_id = response.data[0].get("stripe_sub_id")
            logger.info(f"Found subscription ID: {subscription_id}")
            return subscription_id
        else:
            logger.warning(f"No subscription found for user {user_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching subscription for user {user_id}: {str(e)}")
        return None

def cancel_subscription(user_id):
    """Cancels a user's subscription."""
    
    subscription_id = get_user_subscription_id(user_id)
    
    if not subscription_id:
        logger.error(f"Cannot cancel: No subscription ID found for user {user_id}")
        return False
    
    try:
        logger.info(f"Attempting to cancel subscription {subscription_id} for user {user_id}")
        
        # Cancel at period end to avoid immediate cancellation
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        # Update the status in the database
        supabase.table("subscriptions").update(
            {"status": "cancelling"}
        ).eq("user_id", user_id).execute()
        
        logger.info(f"Subscription {subscription_id} marked for cancellation at period end")
        return True
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error cancelling subscription {subscription_id}: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"Error cancelling subscription {subscription_id}: {str(e)}")
        return False

def check_subscription_status(subscription_id):
    """Check the current status of a subscription."""
    
    try:
        logger.info(f"Checking status of subscription {subscription_id}")
        
        subscription = stripe.Subscription.retrieve(subscription_id)
        logger.info(f"Subscription {subscription_id} status: {subscription.status}")
        
        return {
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error checking subscription {subscription_id}: {str(e)}")
        return None
        
    except Exception as e:
        logger.error(f"Error checking subscription {subscription_id}: {str(e)}")
        return None