#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler
import logging
import json
from os import path

SCORES_FILE = "scores.json"
IDS_FILE = "ids.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

id_to_score = {1234: 27}
id_to_fullname = {1234: "Cameron Reikes"}


def dump_dictionary(file_name, dictionary):
    with open(file_name, "w") as fp:
        json.dump(dictionary, fp, sort_keys=True, indent=4)


def update_dictionary(file_name, dictionary):
    if path.exists(file_name):
        with open(file_name, "r") as fp:
            dictionary = json.load(fp)
    else:
        dump_dictionary(file_name, dictionary)


update_dictionary(SCORES_FILE, id_to_score)
update_dictionary(IDS_FILE, id_to_fullname)


with open(".token", "r") as tokenfile:
    updater = Updater(token=tokenfile.read().replace("\n", ""), use_context=True)

dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text="If I see one illegal alol... 👀"
    )


def get_scores(update, context):
    full_message = f"-- Current lol scores --\n"
    sorted_ids = sorted(id_to_score.keys())
    for current_id in sorted_ids:
        full_message += f"{id_to_fullname[current_id]}: {id_to_score[current_id]}\n"
    context.bot.send_message(chat_id=update.message.chat_id, text=full_message)


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("getscores", get_scores))

updater.start_polling()
updater.idle()

dump_dictionary(SCORES_FILE, id_to_score)
dump_dictionary(IDS_FILE, id_to_fullname)
