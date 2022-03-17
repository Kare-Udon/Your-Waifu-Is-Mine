from time import sleep
import os
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup
from keyboard import _keyboard

TOKEN = os.getenv('TG_BOT_TOKEN')

k = _keyboard()

bot = telepot.Bot(token=TOKEN)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg['text'] == '/start':
        reply_makeup = ReplyKeyboardMarkup(keyboard=k.main_menu, resize_keyboard=True)
        bot.sendMessage(chat_id, text="Welcome! Choose the function below.", reply_markup=reply_makeup)
    if msg['text'] == 'Add Source':
        reply_makeup = ReplyKeyboardMarkup(keyboard=k.add_source_menu, resize_keyboard=True)
        bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
    if msg['text'] == 'Remove Source':
        reply_makeup = ReplyKeyboardMarkup(keyboard=k.remove_source_menu, resize_keyboard=True)
        bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
    if msg['text'] == 'Settings':
        reply_makeup = ReplyKeyboardMarkup(keyboard=k.settings_menu, resize_keyboard=True)
        bot.sendMessage(chat_id, text="1", reply_markup=reply_makeup)
    
MessageLoop(bot, on_chat_message).run_as_thread()
while(1):
    sleep(10)

