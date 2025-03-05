from handlers.commands import handle_start, handle_subscribe, handle_daily_tip
from handlers.messages import handle_message
from handlers.callbacks import handle_callback
from services.telegram_api import get_updates
from services.webhook import app  # Import the webhook Flask app
from threading import Thread
import time

def main():
    """Main loop to fetch and process Telegram updates."""
    last_update_id = None

    while True:
        try:
            updates = get_updates(offset=last_update_id)
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1

                if "message" in update and update["message"].get("text"):
                    text = update["message"]["text"]
                    chat_id = update["message"]["chat"]["id"]

                    if text == "/start":
                        handle_start(update)
                    elif text == "/subscribe":
                        handle_subscribe(update)
                    elif text == "/daily_tip":
                        handle_daily_tip(update)
                    else:
                        handle_message(update)
                elif "callback_query" in update:
                    handle_callback(update)
            time.sleep(1)  # Prevents excessive API calls
        except Exception as e:
            print(f"Error fetching updates: {e}")
            continue  # Prevents crash and continues fetching updates

if __name__ == "__main__":
    Thread(target=lambda: app.run(port=5050)).start()
    main()
