import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Telegram API credentials

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

# Stripe API credentials
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_9AQ9Dz9iucT8aHK6oo"
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")

# Welcome image
WELCOME_IMAGE_URL = "https://drive.google.com/uc?export=view&id=1w4a3_IpWnq4gB-Xz759Aug_l4DEEZ536"


# URLs and resources
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE")
WELCOME_IMAGE_URL = os.getenv("WELCOME_IMAGE_URL")