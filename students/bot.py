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


def last_update(request):
    response = requests.get(request + "getUpdates")
    response = response.json()
    print(response)
    results = response["result"]
    if not results:
        return None
    return results[-1]


def get_chat_id(update):
    chat_id = update["message"]["chat"]["id"]
    return chat_id


def get_message_text(update):
    message_text = update["message"]["text"]
    return message_text


def send_message(chat, text):
    params = {"chat_id": chat, "text": text}
    response = requests.post(url + "sendMessage", data=params)
    return response


def main():
    try:
        update_id = None
        while True:
            time.sleep(1)
            update = last_update(url)
            if update is None:
                continue
            if update_id is None:
                update_id = update["update_id"]
            if update_id == update["update_id"]:
                text = get_message_text(update).lower()
                if text in ("hi", "hello", "hey"):
                    send_message(
                        get_chat_id(update),
                        'Greetings! Type "Dice" to roll the dice!',
                    )
                elif text == "csc31":
                    send_message(get_chat_id(update), "Python")
                elif text == "gin":
                    send_message(get_chat_id(update), "Finish")
                    break
                elif text == "python":
                    send_message(get_chat_id(update), "version 3.14")
                elif text == "name":
                    send_message(get_chat_id(update), "CSC31")
                elif "weather" in text:
                    city = text.replace("weather ", "")
                    weather = get_weather(city)
                    send_message(get_chat_id(update), weather)
                elif text == "dice":
                    _1 = random.randint(1, 6)
                    _2 = random.randint(1, 6)
                    send_message(
                        get_chat_id(update),
                        "You have "
                        + str(_1)
                        + " and "
                        + str(_2)
                        + "!\nYour result is "
                        + str(_1 + _2)
                        + "!",
                    )
                else:
                    result = calculate_expression(get_message_text(update))
                    if result is not None:
                        send_message(get_chat_id(update), result)
                    else:
                        send_message(
                            get_chat_id(update),
                            "Sorry, I don't understand you :(",
                        )

                update_id += 1
    except KeyboardInterrupt:
        print("\nБот зупинено")
