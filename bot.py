from handlers.commands import handle_start, handle_subscribe, handle_daily_tip
from handlers.messages import handle_message
from handlers.callbacks import handle_callback
from services.telegram_api import get_updates

def main():
    """Main loop to fetch and process Telegram updates."""
    last_update_id = None

    while True:
        updates = get_updates(offset=last_update_id)
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1

            if "message" in update and update["message"].get("text"):
                text = update["message"]["text"]
                chat_id = update["message"]["chat"]["id"]

                if text == "/start":
                    handle_start(chat_id)
                elif text == "/subscribe":
                    handle_subscribe(chat_id)
                elif text == "/daily_tip":
                    handle_daily_tip(chat_id)
                else:
                    handle_message(update)

            elif "callback_query" in update:
                handle_callback(update)

if __name__ == "__main__":
    main()
