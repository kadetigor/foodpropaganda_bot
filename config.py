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

# Payment links
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_checkout_link"

# Welcome image
WELCOME_IMAGE_URL = "https://drive.google.com/uc?export=view&id=1w4a3_IpWnq4gB-Xz759Aug_l4DEEZ536"
