import logging
import json
import os
import prettytable as pt

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

import Telegram.keyboard
import sql.sqlite
import Twitter.twitter

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
SENT_INTERVAL = settings["telegram"]["SENT_INTERVAL"]

if BOT_TOKEN == "" and ALLOWED_USERS == [] and BINDED_GROUP == "":
    BOT_TOKEN = os.environ['BOT_TOKEN']
    ALLOWED_USERS = os.environ['ALLOWED_USERS'].split(',')
    BINDED_GROUP = os.environ['BINDED_GROUP']
    SENT_INTERVAL = int(os.environ['SENT_INTERVAL'])

if BOT_TOKEN == "" and ALLOWED_USERS == [] and BINDED_GROUP == "" and SENT_INTERVAL == 0:
    print("Please set BOT_TOKEN, ALLOWED_USERS and BINDED_GROUP")
    exit(1)


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename="error.log",
                    level=logging.ERROR, format=LOG_FORMAT)

FUNCTION_SELECT, ADD_SOURCE, REMOVE_SOURCE, ADD_TWITTER, ADD_PIXIV, REMOVE_TWITTER, REMOVE_PIXIV, SETTINGS, SETTINGS_LIST_SOURCE = range(
    9)


def start(update: Update, context: CallbackContext) -> int:
    context.job_queue.run_once(get_twitter_update, when=0)
    context.job_queue.run_repeating(
        get_twitter_update, interval=int(SENT_INTERVAL), first=0)
    user = update.message.from_user['username']
    if user not in ALLOWED_USERS:
        update.message.reply_text(
            'You are not allowed to use this bot.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Hi! This is Your-Waifu-Is-Mine bot and thank you for choosing me!'
        )
        reply_keyboard = k.main_menu
        update.message.reply_text(
            'Choose the function below.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
            ),
        )
        return FUNCTION_SELECT


def function_select(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message == 'Add Source':
        reply_keyboard = k.add_source_menu
        update.message.reply_text(
            'Please choose the platform you want to add: (Twitter or Pixiv)',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
        return ADD_SOURCE
    if message == 'Remove Source':
        reply_keyboard = k.add_source_menu
        update.message.reply_text(
            'Please choose the platform you want to remove: (Twitter or Pixiv)',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
        return REMOVE_SOURCE
    if message == 'Settings':
        reply_keyboard = k.settings_menu
        update.message.reply_text(
            'Here are the settings.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
            ),
        )
        return SETTINGS


def add_source(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message == 'Twitter':
        update.message.reply_text(
            "Please send me the url of a twitter user. Link format:'https://twitter.com/TWITTER_USERNAME' Send /cancel to cancel.",
        )
        return ADD_TWITTER
    if message == 'Pixiv':
        update.message.reply_text(
            'Under construction.',
        )
    # OR Go Back
    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def add_twitter(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message != '/cancel':
        username = message.split('/')[-1]
        twitter_id = twi.url_to_id(username)
        if db.add_twitter_user(twitter_id, username):
            update.message.reply_text(
                "Twitter user " + username + " add successfully.")
        else:
            update.message.reply_text(
                "Twitter user " + username + " add failed or already exists.")

    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def add_pixiv(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Under construction.",
    )
    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def remove_source(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message == 'Twitter':
        update.message.reply_text(
            "Please send me the url of a twitter user. Link format:'https://twitter.com/TWITTER_USERNAME' Send /cancel to cancel.",
        )
        return REMOVE_TWITTER
    if message == 'Pixiv':
        update.message.reply_text(
            'Under construction.',
        )
    # OR Go Back
    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def remove_twitter(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message != '/cancel':
        message = update.message.text
        username = message.split('/')[-1]
        twitter_id = twi.url_to_id(username)
        if db.del_twitter_user(twitter_id):
            update.message.reply_text(
                "Delete Successfully.")
        else:
            update.message.reply_text(
                "Delete Failed. Please check the log file.")

    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def remove_pixiv(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Under construction.',
    )

    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def settings(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message == 'List Source':
        reply_keyboard = k.list_source_menu
        update.message.reply_text(
            'Choose the platform you want to list.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
            ),
        )
        return SETTINGS_LIST_SOURCE

    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def list_source(update: Update, context: CallbackContext) -> int:
    message = update.message.text
    if message == 'Twitter':
        infos = db.get_all_twitter_user_info()
        table = pt.PrettyTable(['Username', 'Twitter ID'])
        table.align['Username'] = 'l'
        table.align['Twitter ID'] = 'l'
        for info in infos:
            table.add_row([info[0], info[1]])
        
        update.message.reply_text(
            f'<pre>{table}</pre>', parse_mode=ParseMode.HTML
        )
    if message == 'Pixiv':
        update.message.reply_text(
            'Under construction.',
        )

    reply_keyboard = k.main_menu
    update.message.reply_text(
        'Choose the function below.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
        ),
    )
    return FUNCTION_SELECT


def get_twitter_update(context: CallbackContext) -> None:
    twitter_infos = db.get_all_twitter_user_info()
    for info in twitter_infos:
        name = info[0]
        id = info[1]
        return_data = twi.get_new_tweets_of_user(id)
        tweets_with_media = return_data[0]
        true_urls = []
        if tweets_with_media != []:
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
                context.bot.sendMessage(BINDED_GROUP, true_url)
            else:
                break
        db.shorten_twitter_db(name)


def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FUNCTION_SELECT: [MessageHandler(Filters.regex('^(Add Source|Remove Source|Settings)$'), function_select)],
            ADD_SOURCE: [MessageHandler(Filters.regex('^(Twitter|Pixiv|Go Back)$'), add_source)],
            ADD_TWITTER: [MessageHandler(Filters.text, add_twitter)],
            ADD_PIXIV: [MessageHandler(Filters.text, add_pixiv)],
            REMOVE_SOURCE: [MessageHandler(Filters.regex('^(Twitter|Pixiv|Go Back)$'), remove_source)],
            REMOVE_TWITTER: [MessageHandler(Filters.text, remove_twitter)],
            REMOVE_PIXIV: [MessageHandler(Filters.text, remove_pixiv)],
            SETTINGS: [MessageHandler(Filters.regex('^(List Source|Go Back)$'), settings)],
            SETTINGS_LIST_SOURCE: [MessageHandler(Filters.regex('^(Twitter|Pixiv|Go Back)$'), list_source)],
        },
        fallbacks=[CommandHandler('cancel', function_select)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
