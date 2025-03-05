import sys
import os
import time
from dotenv import load_dotenv
from utils.logger import setup_logger

# Ensure proper imports regardless of run location
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Set up logger
logger = setup_logger("test_bot")

def test_config():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    from config import TELEGRAM_BOT_TOKEN, STRIPE_SECRET_KEY, OPENAI_API_KEY
    
    # Check essential config variables
    missing_configs = []
    if not TELEGRAM_BOT_TOKEN:
        missing_configs.append("TELEGRAM_BOT_TOKEN")
    if not STRIPE_SECRET_KEY:
        missing_configs.append("STRIPE_SECRET_KEY")
    if not OPENAI_API_KEY:
        missing_configs.append("OPENAI_API_KEY")
    
    if missing_configs:
        logger.error(f"Missing configuration: {', '.join(missing_configs)}")
        return False
    
    logger.info("✅ Configuration loaded successfully")
    return True

def test_telegram_api():
    """Test Telegram API connection"""
    logger.info("Testing Telegram API connection...")
    from services.telegram_api import get_updates
    
    try:
        response = get_updates()
        if "ok" in response and response["ok"]:
            logger.info("✅ Telegram API connection successful")
            return True
        else:
            logger.error(f"Telegram API error: {response}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Telegram API: {e}")
        return False

def test_database():
    """Test database connection"""
    logger.info("Testing database connection...")
    from database import supabase
    
    try:
        # Try a simple query
        response = supabase.table("visitors").select("count", count="exact").execute()
        if hasattr(response, "count"):
            logger.info(f"✅ Database connection successful. Found {response.count} visitors.")
            return True
        else:
            logger.error(f"Database connection issue: {response}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return False

def test_openai():
    """Test OpenAI connection"""
    logger.info("Testing OpenAI connection...")
    from services.openai_service import get_openai_response
    
    try:
        response = get_openai_response("Hello, this is a test message", "test_user_1")
        if response and not response.startswith("⚠️ Error"):
            logger.info("✅ OpenAI connection successful")
            return True
        else:
            logger.error(f"OpenAI API error: {response}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to OpenAI API: {e}")
        return False

def test_stripe():
    """Test Stripe connection"""
    logger.info("Testing Stripe connection...")
    import stripe
    from config import STRIPE_SECRET_KEY
    
    stripe.api_key = STRIPE_SECRET_KEY
    
    try:
        # Try to retrieve the product associated with the price ID
        from config import STRIPE_PRICE_ID
        price = stripe.Price.retrieve(STRIPE_PRICE_ID)
        
        if price and hasattr(price, "id"):
            logger.info(f"✅ Stripe connection successful. Found price: {price.id}")
            return True
        else:
            logger.error(f"Stripe API error: Could not retrieve price")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Stripe API: {e}")
        return False

def run_tests():
    """Run all tests and report results"""
    logger.info("Starting bot diagnostic tests...")
    
    tests = [
        ("Configuration", test_config),
        ("Telegram API", test_telegram_api),
        ("Database", test_database),
        ("OpenAI", test_openai),
        ("Stripe", test_stripe)
    ]
    
    results = {}
    all_passed = True
    
    for name, test_func in tests:
        logger.info(f"\n{'='*50}\nTesting {name}...\n{'='*50}")
        try:
            result = test_func()
            results[name] = result
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"Error during {name} test: {e}")
            results[name] = False
            all_passed = False
    
    # Print summary
    logger.info("\n\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{name}: {status}")
    
    if all_passed:
        logger.info("\n✅ All tests passed! Bot should be operational.")
    else:
        logger.info("\n⚠️ Some tests failed. Please check the logs and fix the issues before deployment.")

if __name__ == "__main__":
    run_tests()