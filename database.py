from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import datetime  # Ensuring correct import
from dateutil.relativedelta import relativedelta  # For handling month variations

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_status(user_id):
    """Check if the user exists in either visitors or subscriptions table."""
    visitor = supabase.table("visitors").select("*").eq("user_id", user_id).execute()
    subscription = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()

    if subscription.data:
        return "subscriber"
    elif visitor.data:
        return "visitor"
    else:
        return None  # User does not exist


def save_visitor(user_id, email=None, nickname=None):
    """Save visitor info in Supabase, ensuring nickname is preserved when updating email."""

    # Retrieve existing record
    existing_record = supabase.table("visitors").select("email, nickname").eq("user_id", user_id).execute()

    if existing_record.data:
        # If user exists, update only missing fields
        existing_data = existing_record.data[0]
        if not email:
            email = existing_data.get("email")  # Preserve existing email
        if not nickname:
            nickname = existing_data.get("nickname")  # Preserve existing nickname

    else:
        # If new user, set default nickname if not provided
        if not nickname:
            nickname = f"user_{user_id}"

    # Upsert (insert or update) the record, preserving nickname
    data = {"user_id": user_id, "email": email, "nickname": nickname}

    response = supabase.table("visitors").upsert(data).execute()

    if response.data:
        print(f"✅ Visitor {user_id} stored with email: {email}, nickname: {nickname}")
    else:
        print(f"🚨 Failed to store visitor {user_id}")

    return response


def get_visitor(user_id):
    """Retrieve visitor details from Supabase by user_id."""
    response = supabase.table("visitors").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

def transfer_user_to_subscriptions(user_id, email, nickname, stripe_sub_id, stripe_cust_id, provider, status, next_payment):
    """Move user from visitors table to subscriptions table."""
    try:
        # Ensure next_payment is converted properly and handles missing values correctly
        if next_payment:
            next_payment_dt = datetime.datetime.fromtimestamp(next_payment, datetime.timezone.utc)
        else:
            next_payment_dt = datetime.datetime.now(datetime.timezone.utc) + relativedelta(months=1)


        # Insert user into subscriptions
        supabase.table("subscriptions").insert({
            "user_id": user_id,
            "email": email,
            "nickname": nickname,
            "provider": provider,
            "stripe_sub_id": stripe_sub_id,
            "stripe_cust_id": stripe_cust_id,
            "status": status,
            "next_payment": next_payment_dt.strftime('%Y-%m-%d %H:%M:%S'),
            "created_at": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            "return_frequency": 0,  # Default value
            "last_active": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }).execute()

        # Delete user from visitors
        supabase.table("visitors").delete().eq("user_id", user_id).execute()

        print(f"✅ User {user_id} moved from visitors to subscriptions")
        return True
    except Exception as e:
        print(f"🚨 Database Error: {e}")
        return False


# def save_user_subscription(user_id, status):
#     """Save subscription status for a user."""
#     data = {"user_id": user_id, "subscription_status": status}
#     response = supabase.table("subscriptions").insert(data).execute()
#     return response

# def check_user_subscription(user_id):
#     """Check if a user has an active subscription."""
#     response = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
#     return response.data if response.data else None