#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
import logging
import json
import jsonpickle
import re
import threading
import schedule
import time
from os import path

USERDATA_FILE = "userdata.json"
GENERAL_LOL_REGEX = re.compile(r"(.*lol.*)|(.*almao.*)|(.*arofl.*)")
LOL_SCORES = {
    "\s*lol\s*": 1,
    "\s*rwalol\s*": 2,
    "\s*walol\s*": 3,
    "\s*alol\s*": 4,
    "\s*rwalmao\s*": 5,
    "\s*walmao\s*": 6,
    "\s*almao\s*": 7,
    "\s*rwarofl\s*": 8,
    "\s*warofl\s*": 9,
    "\s*arofl\s*": 10,
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class UserData(object):
    def __init__(self, current_score: int, full_name: str, banned: bool):
        self.current_score = current_score
        self.full_name = full_name
        self.banned = banned


dump_thread_stop = threading.Event()


def run_schedule():
    while not dump_thread_stop.is_set():
        schedule.run_pending()
        time.sleep(1)


def dump_dictionary(dictionary: dict, file_name: str):
    with open(file_name, "w") as fp:
        fp.write(jsonpickle.encode(dictionary))


def update_dictionary(dictionary: dict, file_name: str) -> dict:
    if path.exists(file_name):
        with open(file_name, "r") as fp:
            return jsonpickle.decode(fp.read())
            # print(dictionary["1234"].current_score)
    else:
        dump_dictionary(dictionary, file_name)
        return dictionary


id_to_userdata = {"1234": UserData(4, "cameron reikes", False)}

schedule.every(5).minutes.do(dump_dictionary, id_to_userdata, USERDATA_FILE)
dump_thread = threading.Thread(target=run_schedule)
dump_thread.start()


id_to_userdata = update_dictionary(id_to_userdata, USERDATA_FILE)


with open(".token", "r") as tokenfile:
    updater = Updater(token=tokenfile.read().replace("\n", ""), use_context=True)

dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id, text="If I see one illegal alol... 👀"
    )


def on_lol_message(update, context):
    logging.info("lol detected")
    # update.message.reply_text("This is a lol")
    if update.message.from_user == update.message.reply_to_message.from_user:
        update.message.reply_text(
            "You really thought 🤦‍♂️🤦‍♂️🤦‍♂️ bruhhhh..... bitchass meatbody. You want a ban?"
        )
        return
    lol_score = None
    message_text = update.message.text.lower()
    for lol_regex in LOL_SCORES.keys():
        if re.match(lol_regex, message_text):
            lol_score = LOL_SCORES[lol_regex]
            break
    if lol_score == None:
        logging.error(f"No lol regex matched for: {update.message.text}!")
        return
    user = update.message.reply_to_message.from_user
    user_id = str(user.id)
    if user_id in id_to_userdata:
        id_to_userdata[user_id].current_score += lol_score
    else:
        id_to_userdata[user_id] = UserData(lol_score, user.full_name, False)
    logging.info(f"User {user.full_name} gained {lol_score} points!")


def get_key(key):
    return int(key)


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
lol_handler = MessageHandler(
    filters=(Filters.regex(GENERAL_LOL_REGEX)), callback=on_lol_message
)
dispatcher.add_handler(lol_handler)


updater.start_polling()
logging.info("Polling...")
updater.idle()

dump_thread_stop.set()
dump_thread.join()
dump_dictionary(id_to_userdata, USERDATA_FILE)
