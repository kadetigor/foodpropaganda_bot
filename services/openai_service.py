import requests
import time
from config import OPENAI_API_KEY, ASSISTANT_ID

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2"
}

def get_openai_response(user_message):
    """Processes the user message and returns AI-generated response."""
    
    # Create a conversation thread
    thread_response = requests.post("https://api.openai.com/v1/threads", headers=HEADERS).json()

    if "id" not in thread_response:
        return "⚠️ Error: Could not create a conversation thread."

    thread_id = thread_response["id"]

    # Add user message
    requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages",
                  headers=HEADERS, json={"role": "user", "content": user_message})

    # Run the Assistant
    run_response = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/runs",
                                 headers=HEADERS, json={"assistant_id": ASSISTANT_ID}).json()
    
    run_id = run_response["id"]

    # Poll until completion
    while True:
        run_status = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}", headers=HEADERS).json()
        if run_status["status"] == "completed":
            break
        time.sleep(2)

    # Retrieve the response
    messages_response = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=HEADERS).json()
    return messages_response["data"][0]["content"][0]["text"]["value"]
