#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
import logging
import json
import jsonpickle
import re
from os import path

USERDATA_FILE = "userdata.json"
GENERAL_LOL_REGEX = ".*lol.*|.*almao.*|.*arofl.*"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class UserData(object):
    def __init__(self, current_score: int, full_name: str, banned: bool):
        self.current_score = current_score
        self.full_name = full_name
        self.banned = banned


id_to_userdata = {"1234": UserData(4, "cameron reikes", False)}


def dump_dictionary(dictionary: dict, file_name: str):
    with open(file_name, "w") as fp:
        fp.write(jsonpickle.encode(dictionary))


def update_dictionary(dictionary: dict, file_name: str):
    if path.exists(file_name):
        with open(file_name, "r") as fp:
            dictionary = jsonpickle.decode(fp.read())
            # print(dictionary["1234"].current_score)
    else:
        dump_dictionary(dictionary, file_name)


update_dictionary(id_to_userdata, USERDATA_FILE)


with open(".token", "r") as tokenfile:
    updater = Updater(token=tokenfile.read().replace("\n", ""), use_context=True)

dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text="If I see one illegal alol... 👀"
    )


def on_lol_message(update, context):
    logging.info("Lol detected!")


def get_key(key):
    try:
        return int(key)
    except ValueError:
        return key


def get_scores(update, context):
    global id_to_userdata
    full_message = f"-- Current lol scores --\n"
    sorted_ids = sorted(id_to_userdata.keys(), key=lambda t: get_key(t[0]))
    for current_id in sorted_ids:
        user: UserData = id_to_userdata[current_id]
        banned_str = "banned" if user.banned else "not banned"
        full_message += f"{user.full_name}: {user.current_score}, {banned_str}\n"
    context.bot.send_message(chat_id=update.message.chat_id, text=full_message)


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("getscores", get_scores))
dispatcher.add_handler(
    MessageHandler(
        filters=(Filters.reply & Filters.regex(GENERAL_LOL_REGEX)),
        callback=on_lol_message,
    )
)


updater.start_polling()
updater.idle()

dump_dictionary(id_to_userdata, USERDATA_FILE)
