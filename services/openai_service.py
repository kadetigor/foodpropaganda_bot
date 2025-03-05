import requests
import time
from config import OPENAI_API_KEY, ASSISTANT_ID
from utils.logger import setup_logger

logger = setup_logger(__name__)

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2"
}

user_threads = {}

def get_openai_response(user_message, user_id):
    """
    Processes the user message and returns AI-generated response.
    Maintains conversation context by reusing the same thread for each user.
    """
    try:
        # Get or create a conversation thread for this user
        if user_id not in user_threads:
            logger.info(f"Creating new OpenAI thread for user {user_id}")
            thread_response = requests.post("https://api.openai.com/v1/threads", headers=HEADERS).json()
            
            if "id" not in thread_response:
                logger.error(f"Failed to create thread: {thread_response}")
                return "⚠️ Error: Could not create a conversation thread."
                
            user_threads[user_id] = thread_response["id"]
            logger.info(f"Thread created with ID: {user_threads[user_id]}")
        
        thread_id = user_threads[user_id]
        logger.info(f"Using thread {thread_id} for user {user_id}")

        # Add user message to the thread
        message_response = requests.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=HEADERS, 
            json={"role": "user", "content": user_message}
        ).json()
        
        if "id" not in message_response:
            logger.error(f"Failed to add message: {message_response}")
            return "⚠️ Error: Could not add your message to the conversation."

        # Run the Assistant on the thread
        run_response = requests.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=HEADERS, 
            json={"assistant_id": ASSISTANT_ID}
        ).json()
        
        if "id" not in run_response:
            logger.error(f"Failed to run assistant: {run_response}")
            return "⚠️ Error: Could not process your message."
            
        run_id = run_response["id"]
        
        # Poll until completion with timeout
        start_time = time.time()
        max_wait_time = 60  # 60 seconds max wait
        
        while time.time() - start_time < max_wait_time:
            run_status = requests.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}", 
                headers=HEADERS
            ).json()
            
            if "status" not in run_status:
                logger.error(f"Failed to get run status: {run_status}")
                return "⚠️ Error: Could not check the status of your request."
                
            if run_status["status"] == "completed":
                break
                
            elif run_status["status"] in ["failed", "cancelled", "expired"]:
                logger.error(f"Run failed with status: {run_status['status']}")
                return f"⚠️ Error: Your request {run_status['status']}. Please try again."
                
            time.sleep(2)
        
        # Check if we timed out
        if time.time() - start_time >= max_wait_time:
            logger.warning(f"Run timed out for user {user_id}")
            return "⚠️ Request is taking too long. Please try a shorter message or try again later."

        # Retrieve the response
        messages_response = requests.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages", 
            headers=HEADERS
        ).json()
        
        if "data" not in messages_response or not messages_response["data"]:
            logger.error(f"Failed to get messages: {messages_response}")
            return "⚠️ Error: Could not retrieve the response."
            
        # Return the assistant's response
        return messages_response["data"][0]["content"][0]["text"]["value"]
        
    except Exception as e:
        logger.error(f"Error in get_openai_response: {e}")
        return "⚠️ Произошла ошибка при обработке вашего сообщения. Пожалуйста, попробуйте еще раз позже."

def reset_user_thread(user_id):
    """Reset a user's conversation thread to start fresh."""
    if user_id in user_threads:
        logger.info(f"Resetting thread for user {user_id}")
        del user_threads[user_id]
        return True
    return False
