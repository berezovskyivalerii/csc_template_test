import random
import sys
import time
from pathlib import Path

import requests

from config import get_token, require_token

_STUDENTS = Path(__file__).resolve().parent
if str(_STUDENTS) not in sys.path:
    sys.path.insert(0, str(_STUDENTS))

from commands._calculator import calculate_expression
from commands._weather import get_weather

bot_key = require_token("TELEGRAM_BOT_TOKEN")
URL = get_token("TELEGRAM_API_URL", "https://api.telegram.org/bot")
url = f"{URL}{bot_key}/"

session = requests.Session()


def _api(method, **params):
    for attempt in range(5):
        try:
            if params:
                return session.post(url + method, data=params, timeout=35)
            return session.get(url + method, timeout=35)
        except requests.RequestException as exc:
            wait = min(2 ** attempt, 30)
            print(f"Telegram API помилка ({exc}), повтор через {wait}s...")
            time.sleep(wait)
    return None


def get_updates(offset=None):
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset
    response = _api("getUpdates", **params)
    if response is None or not response.ok:
        return []
    data = response.json()
    if not data.get("ok"):
        return []
    return data.get("result", [])


def get_chat_id(update):
    return update["message"]["chat"]["id"]


def get_message_text(update):
    return update["message"]["text"]


def send_message(chat, text):
    _api("sendMessage", chat_id=chat, text=text)


def handle_message(update):
    text = get_message_text(update).lower()
    chat_id = get_chat_id(update)

    if text in ("hi", "hello", "hey", "/start"):
        send_message(chat_id, 'Greetings, I'm Valerii! Type "Dice" to roll the dice!')
    elif text == "csc31":
        send_message(chat_id, "Python")
    elif text == "gin":
        send_message(chat_id, "Finish")
        return False
    elif text == "python":
        send_message(chat_id, "version 3.14")
    elif text == "name":
        send_message(chat_id, "CSC31")
    elif "weather" in text:
        city = text.replace("weather ", "")
        send_message(chat_id, get_weather(city))
    elif text == "dice":
        _1 = random.randint(1, 6)
        _2 = random.randint(1, 6)
        send_message(
            chat_id,
            f"You have {_1} and {_2}!\nYour result is {_1 + _2}!",
        )
    else:
        result = calculate_expression(get_message_text(update))
        if result is not None:
            send_message(chat_id, result)
        else:
            send_message(chat_id, "Sorry, I don't understand you :(")
    return True


def main():
    print("Бот запущено...")
    # пропускаємо старі повідомлення в черзі
    offset = None
    pending = get_updates()
    if pending:
        offset = pending[-1]["update_id"] + 1
        print(f"Пропущено {len(pending)} старих повідомлень")

    try:
        while True:
            try:
                updates = get_updates(offset)
                if not updates:
                    time.sleep(2)
                    continue
                for update in updates:
                    offset = update["update_id"] + 1
                    if "message" not in update or "text" not in update["message"]:
                        continue
                    if not handle_message(update):
                        print("Бот зупинено (gin)")
                        return
            except Exception as exc:
                print(f"Помилка циклу ({exc}), продовжую через 5s...")
                time.sleep(5)
    except KeyboardInterrupt:
        print("\nБот зупинено")
