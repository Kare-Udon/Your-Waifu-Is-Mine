from time import sleep
import os
import logging
import telepot
import traceback
import json
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup

import Telegram.keyboard
import sql.sqlite
import Twitter.twitter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename="error.log",
                    level=logging.ERROR, format=LOG_FORMAT)

twi = Twitter.twitter.Twitter()
db = sql.sqlite.database()
k = Telegram.keyboard.keyboard()

try:
    f = open("./settings.json", "r")
except FileNotFoundError:
    print("Please create settings.json")

settings_json = f.read()
f.close()
settings = json.loads(settings_json)


BOT_TOKEN = settings["telegram"]["BOT_TOKEN"]
ALLOWED_USERS = settings["telegram"]["ALLOWED_USERS"]
BINDED_GROUP = settings["telegram"]["BINDED_GROUP"]

if BOT_TOKEN == "" and ALLOWED_USERS == [] and BINDED_GROUP == "":
    BOT_TOKEN = os.environ['BOT_TOKEN']
    ALLOWED_USERS = os.environ['ALLOWED_USERS'].split(',')
    BINDED_GROUP = os.environ['BINDED_GROUP']

if BOT_TOKEN == "" and ALLOWED_USERS == [] and BINDED_GROUP == "":
    print("Please set BOT_TOKEN, ALLOWED_USERS and BINDED_GROUP")
    exit(1)


class GoldenArches(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(GoldenArches, self).__init__(*args, **kwargs)
        self.indicator = 'start'

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        chat_info = bot.getChat(chat_id)
        if chat_info['username'] not in ALLOWED_USERS:
            bot.sendMessage(chat_id, 'You are not allowed to use this bot.')
            return

        # Add Source #
        if self.indicator == 'add_source_twitter':
            if msg['text'] == '/cancel':
                bot.sendMessage(
                    chat_id, text="Cancelled. Please choose the function below.")
                self.indicator = 'start'
            else:
                username = msg['text'].split('/')[-1]
                twitter_id = twi.url_to_id(username)
                if db.add_twitter_user(twitter_id, username):
                    bot.sendMessage(
                        chat_id, text="Twitter user " + username + " add successfully.")
                else:
                    bot.sendMessage(
                        chat_id, text="Twitter user " + username + " add failed or already exists.")
                self.indicator = 'start'

        if self.indicator == 'add_source_pixiv':
            pass

        if self.indicator == 'add_source':
            if msg['text'] == 'Twitter':
                bot.sendMessage(
                    chat_id, text="Please send me the url of a twitter user. Link format:'https://twitter.com/TWITTER_USERNAME' Send /cancel to cancel.")
                self.indicator = 'add_source_twitter'
            if msg['text'] == 'Pixiv':
                bot.sendMessage(
                    chat_id, text="Please send me the url of a pixiv user. Send /cancel to cancel.")
                self.indicator = 'add_source_pixiv'

        # Remove Source #
        if self.indicator == 'remove_source_twitter':
            if msg['text'] == '/cancel':
                bot.sendMessage(
                    chat_id, text="Cancelled. Please choose the function below.")
                self.indicator = 'start'
            else:
                username = msg['text'].split('/')[-1]
                twitter_id = twi.url_to_id(username)
                if db.del_twitter_user(twitter_id):
                    bot.sendMessage(
                        chat_id, text="Delete Successfully.")
                else:
                    bot.sendMessage(
                        chat_id, text="Delete Failed. Please check the log file.")
                self.indicator = 'start'

        if self.indicator == 'remove_source_pixiv':
            pass

        if self.indicator == 'remove_source':
            if msg['text'] == 'Twitter':
                bot.sendMessage(
                    chat_id, text="Please send me the url of a twitter user. Send /cancel to cancel.")
                self.indicator = 'remove_source_twitter'
            if msg['text'] == 'Pixiv':
                bot.sendMessage(
                    chat_id, text="Please send me the url of a pixiv user. Send /cancel to cancel.")
                self.indicator = 'remove_source_pixiv'

        # Start #
        if self.indicator == 'start':
            if msg['text'] == '/start':
                self.indicator = 'start'
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.main_menu, resize_keyboard=True)
                bot.sendMessage(
                    chat_id, text="Welcome! Choose the function below.", reply_markup=reply_makeup)
            else:
                if msg['text'] == 'Add Source':
                    self.indicator = 'add_source'
                    reply_makeup = ReplyKeyboardMarkup(
                        keyboard=k.add_source_menu, resize_keyboard=True)
                    bot.sendMessage(
                        chat_id, text="Please choose the platform you want to add: (Twitter or Pixiv)", reply_markup=reply_makeup)
                else:
                    if msg['text'] == 'Remove Source':
                        self.indicator = 'remove_source'
                        reply_makeup = ReplyKeyboardMarkup(
                            keyboard=k.remove_source_menu, resize_keyboard=True)
                        bot.sendMessage(chat_id, text="1",
                                        reply_markup=reply_makeup)
                    else:
                        if msg['text'] == 'Settings':
                            self.indicator = 'settings'
                            reply_makeup = ReplyKeyboardMarkup(
                                keyboard=k.settings_menu, resize_keyboard=True)
                            bot.sendMessage(chat_id, text="1",
                                            reply_markup=reply_makeup)
                        else:
                            reply_makeup = ReplyKeyboardMarkup(
                                keyboard=k.main_menu, resize_keyboard=True)
                            bot.sendMessage(
                                chat_id, text="Returning to main menu.", reply_markup=reply_makeup)

        if msg['text'] == 'Back to Main Menu':
            reply_makeup = ReplyKeyboardMarkup(
                keyboard=k.main_menu, resize_keyboard=True)
            bot.sendMessage(chat_id, text="Returning to main menu.",
                            reply_markup=reply_makeup)
            self.indicator = 'start'


bot = telepot.DelegatorBot(BOT_TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, GoldenArches, timeout=30),
])

MessageLoop(bot).run_as_thread()

while(1):
    # sleep(10000)

    # Twitter update #
    try:
        twitter_infos = db.get_all_twitter_user_info()
        for info in twitter_infos:
            name = info[0]
            id = info[1]
            return_data = twi.get_new_tweets_of_user(id)
            tweets_with_media = return_data[0]
            #medias = return_data[1]
            true_urls = return_data[2]
            for tweet, true_url in zip(tweets_with_media, true_urls):
                if db.add_new_tweet(name, tweet['id']):
                    #mediakeys = tweet['attachments']['media_keys']
                    #photo_urls = []
                    # for mediakey in mediakeys:
                    # for media in medias:
                    # if mediakey == media['media_key']:
                    # photo_urls.append(telepot.namedtuple.InputMediaPhoto(media=media['url']))
                    #text = tweet['text']
                    #bot.sendMediaGroup(BINDED_GROUP, photo_urls)
                    bot.sendMessage(BINDED_GROUP, text=true_url)
                else:
                    break
            db.shorten_twitter_db(name)
    except Exception as e:
        print("Twitter update failed, please check the log file.")
        logging.error(str(e))
        logging.error(traceback.format_exc())

    # Pixiv update #
    try:
        pass
    except Exception as e:
        print("Pixiv update failed, please check the log file.")
        logging.error(str(e))
        logging.error(traceback.format_exc())

    sleep(1200)
