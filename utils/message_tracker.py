"""
Message tracker module for the Telegram bot.
Keeps track of sent messages and provides functionality to delete them.
"""
from services.telegram_api import delete_message
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Dictionary to store sent message IDs by chat_id
# Format: {chat_id: [message_id1, message_id2, ...]}
bot_messages = {}

def track_message(chat_id, message_id, is_ai_response=False):
    """
    Track a sent message.
    
    Args:
        chat_id: The chat ID where the message was sent
        message_id: The ID of the sent message
        is_ai_response: If True, message won't be deleted (AI responses)
    """
    if is_ai_response:
        return  # Don't track AI responses as they shouldn't be deleted
    
    if message_id is None:
        logger.warning(f"Attempted to track a None message_id for chat {chat_id}")
        return
        
    if chat_id not in bot_messages:
        bot_messages[chat_id] = []
    
    bot_messages[chat_id].append(message_id)
    logger.info(f"Tracked message {message_id} for chat {chat_id}")

def delete_bot_messages(chat_id):
    """
    Delete all tracked messages for a specific chat.
    
    Args:
        chat_id: The chat ID for which to delete messages
    """
    if chat_id not in bot_messages or not bot_messages[chat_id]:
        return
    
    # Get messages to delete and clear the list
    messages_to_delete = bot_messages[chat_id].copy()
    bot_messages[chat_id] = []
    
    # Delete each message
    for message_id in messages_to_delete:
        try:
            success = delete_message(chat_id, message_id)
            if success:
                logger.info(f"Deleted message {message_id} from chat {chat_id}")
            else:
                logger.warning(f"Failed to delete message {message_id} from chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")