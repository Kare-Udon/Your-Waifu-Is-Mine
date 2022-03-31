from time import sleep
import os
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup

import Telegram.keyboard
import sql.sqlite
import Twitter.twitter

twi = Twitter.twitter.Twitter()
db = sql.sqlite.database()


TOKEN = os.getenv('TG_BOT_TOKEN')

k = Telegram.keyboard.keyboard()

class GoldenArches(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(GoldenArches, self).__init__(*args, **kwargs)
        self.indicator = 'start'

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(msg['text'])
        
        # Add Source #
        if self.indicator == 'add_source_twitter':
            if msg['text'] == '/cancel':
                bot.sendMessage(
                    chat_id, text="Cancelled. Please choose the function below.")
                self.indicator = 'start'
            else:
                username = msg['text'].split('/')[-1]
                
                twitter_id = twi.url_to_id(username)
                db.add_twitter_user(twitter_id, username)
                
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
            if msg['text'] == 'Back to Main Menu':
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.main_menu, resize_keyboard=True)
                bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
                self.indicator = 'start'
        
        # Remove Source #
        if self.indicator == 'remove_source_pixiv':
            pass
        
        if self.indicator == 'remove_source_twitter':
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
            if msg['text'] == 'Back to Main Menu':
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.main_menu, resize_keyboard=True)
                bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
                self.indicator = 'start'
                
        # Start #
        if self.indicator == 'start':
            if msg['text'] == '/start':
                self.indicator = 'start'
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.main_menu, resize_keyboard=True)
                bot.sendMessage(
                    chat_id, text="Welcome! Choose the function below.", reply_markup=reply_makeup)
            if msg['text'] == 'Add Source':
                self.indicator = 'add_source'
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.add_source_menu, resize_keyboard=True)
                bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
            if msg['text'] == 'Remove Source':
                self.indicator = 'remove_source'
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.remove_source_menu, resize_keyboard=True)
                bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
            if msg['text'] == 'Settings':
                self.indicator = 'settings'
                reply_makeup = ReplyKeyboardMarkup(
                    keyboard=k.settings_menu, resize_keyboard=True)
                bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)    

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, GoldenArches, timeout=10),
])

MessageLoop(bot).run_as_thread()

while(1):
    sleep(10)
