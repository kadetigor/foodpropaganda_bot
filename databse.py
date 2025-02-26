from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase connection
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_user_subscription(user_id, status):
    """Save subscription status for a user."""
    data = {"user_id": user_id, "subscription_status": status}
    response = supabase.table("subscriptions").insert(data).execute()
    return response

def check_user_subscription(user_id):
    """Check if a user has an active subscription."""
    response = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
    return response.data if response.data else None