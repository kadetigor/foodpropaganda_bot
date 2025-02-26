# This allows us to import handlers as a package
from .commands import handle_start, handle_subscribe, handle_daily_tip
from .messages import handle_message
from .callbacks import handle_callback
from .new_users import handle_new_user

# Function to register all handlers
def register_handlers(dp):
    """Registers all handlers to the bot's dispatcher."""
    dp.register_message_handler(handle_start, commands=["start"])
    dp.register_message_handler(handle_subscribe, commands=["subscribe"])
    dp.register_message_handler(handle_daily_tip, commands=["daily_tip"])
    dp.register_message_handler(handle_message)
    dp.register_callback_query_handler(handle_callback)
    dp.register_message_handler(handle_new_user, content_types=["new_chat_members"])