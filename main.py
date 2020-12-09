import config
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import telebot
import dbworker
from random import randint
import re
from tabulate import tabulate
from os import environ
from dotenv import load_dotenv
from flask import Flask, request

#load .env
load_dotenv()
TOKEN = environ.get('TOKEN')
PORT = int(environ.get('PORT', 5000))  # second value by default if first value not found

# create bot
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)

pict = [
    'https://besthqwallpapers.com/Uploads/13-11-2020/144318/thumb-chemistry-periodic-table-chemical-elements-chemistry-background-chemistry-concepts.jpg',
    'https://365psd.com/images/istock/previews/1024/102459903-chemical-elements-from-periodic-table-white-icons-on-blurred-background.jpg'
    'https://ak.picdn.net/shutterstock/videos/14759659/thumb/1.jpg',
    'https://www.wits.ac.za/media/wits-university/course-finder-images/periodic-table.png',
    'https://www.science.edu/acellus/wp-content/uploads/2016/12/Acellus-General-Chemistry.jpg'
    ]

"""Collect data from a website

Create function for website parsing of chemical elements basic information.
"""


def elements_data():
    url = 'https://images-of-elements.com/element-properties.php'
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    table = soup.find_all('table')[1]
    rows = table.find_all('tr')
    field_list = []

    for i in range(12):
        col = []
        # add header
        col.append(rows[0].find_all('th')[i].get_text().strip())
        # start with second row as first one was taken earlier
        for row in rows[1:]:
            try:
                # find all tags td in a row
                r = row.find_all('td')
                # save data to a list
                col.append(r[i].get_text().strip())
            except:
                pass
        field_list.append(col)
    d = dict()
    for i in range(12):
        d[field_list[i][0]] = field_list[i][1:]
    df = pd.DataFrame(d)
    df = df.rename(columns={'Valence el.': 'Valence',
                            'Stable isotopes': 'StableIsotopes',
                            'Melting point': 'MeltingPoint',
                            'Boiling point': 'BoilingPoint'})
    df = df.replace('', np.nan)

    radius_note = 'Unknown'
    valence_note = 'Unknown'
    melting_point_note = 'Unknown'
    stable_isotopes_note = 'Unknown'
    boiling_point_note = 'Unknown'
    density_note = 'Unknown'
    df['Radius'].fillna(radius_note, inplace=True)
    df['Valence'].fillna(valence_note, inplace=True)
    df['MeltingPoint'].fillna(melting_point_note, inplace=True)
    df['StableIsotopes'].fillna(stable_isotopes_note, inplace=True)
    df['BoilingPoint'].fillna(boiling_point_note, inplace=True)
    df['Density'].fillna(density_note, inplace=True)

    return df

@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, "Info method is used to show you what I am capable of.\n"
                                      "I could provide you with some basic information on periodic table elements.\n"
                                      "I have info for all discovered elements.\n"
                                      "First you gotta select the symbol of an element:\n"
                                      "for example  Fe or Ca.\n"
                                      "You can also get list of all elements using /listelements.\n"
                                      "Type /reset to start anew.")
    bot.send_message(message.chat.id, "The next step is to specify what specific features you are interested in.\n"
                                      "You should enter comma-delimited list of features or just a single feature\n"
                                      "For example  Mass, Valence.\n"
                                      "You can get list of available features using /listfeatures\n"
                                      "Type /reset to start anew.")
    bot.send_message(message.chat.id, "There's a number of commands you can use here.\n"
                                      "Type /commands to get the list of available functions.\n"
                                      "Type /reset to start anew.")

@bot.message_handler(commands=["listelements"])
def cmd_listelements(message):
    x = elements_data()['Symbol']
    bot.send_message(message.chat.id, ', '.join(i for i in list(x) if i != ''))

@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/reset - is used to discard previous selections and start anew.\n"
                                      "/start - is used to start a new dialogue from the very beginning.\n"
                                      "/info - is used to know what i can do for you (there's a tree of commands)\n"
                                      "/commands - If you got here, you know what it is used for.\n"
                                      "/listelements - is used to list elements of periodic table.\n"
                                      "/listfeatures - is used to list fields available in element features")

@bot.message_handler(commands=["listfeatures"])
def cmd_listfields(message):
    x = ['Number', 'Period', 'Group', 'Name',
         'Mass', 'Radius', 'Valence', 'StableIsotopes',
         'MeltingPoint', 'BoilingPoint', 'Density']
    bot.send_message(message.chat.id, ", ".join(x))

# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Let's start anew.\n"
                                      "Which element`s information You want to get:\n"
                                      "Enter a symbol of an element:\n"
                                      "just type - Fe, Ca or any other.\n"
                                      "Type /listelements to get the list of all 118 currently discovered elements.\n"
                                      "Use /info or /commands to rewind what I am and what can I do.")
    bot.send_photo(message.chat.id, pict[randint(0, 5)])
    dbworker.set_state(message.chat.id, config.States.S_ENTER_ELEMENT_SYMBOL.value)
    #TODO:
    # Удалить состояние пользователя

@bot.message_handler(commands=["start"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    state = dbworker.get_current_state(message.chat.id)
    # Под "остальным" понимаем состояние "0" - начало диалога
    bot.send_message(message.chat.id, "Greetings again! I'm CheckElementBot :) \n"
                                      "You gotta specify which element`s information You want to get.\n"
                                      "Enter a symbol of an element:\n"
                                      "just type - Fe, Ca or any other.\n"
                                      "Type /info to know what I am and what I can do for you.\n"
                                      "Tye /commands to list the available commands.\n"
                                      "Type /reset to discard previous selections and start anew.")
    bot.send_photo(message.chat.id, pict[randint(0, 5)])
    dbworker.set_state(message.chat.id, config.States.S_ENTER_ELEMENT.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_ELEMENT.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listelements', '/listfeatures'))
def enter_element(message):
    # global elements, element
    dbworker.del_state(str(message.chat.id) + 'elements')  # Если в базе когда-то был выбор списка элементов, удалим (мы же новый пишем)
    elements = [x.strip() for x in re.split(',', message.text)]
    element = dbworker.get_current_state(str(message.chat.id)+'element')

    bot.send_message(message.chat.id, 'Thank you, I\'m checkin\' your info.')
    x = elements_data()['Symbol']
    lst = [i for i in list(x) if i != '']

    # bot.send_message(message.chat.id,', '.join(lst))
    errors = [i for i in elements if i not in lst]

    if errors == []:
        if elements != []:
            bot.send_message(message.chat.id, "Ok, Now you gotta specify the information you need. \n"
                                              "Enter the list of features\n"
                                              "Type /listfeatures to get the list of available fields.\n"
                                              "You could type /info to recollect what we are doing now.\n"
                                              "Type /reset to start anew.")
            dbworker.set_state(str(message.chat.id)+'elements', ', '.join(elements))
            dbworker.set_state(message.chat.id, config.States.S_ENTER_FEATURES_LIST.value)
        else:
            bot.send_message(message.chat.id, "Something has gone wrong! Enter the list of countries/regions properly")
    else:
        bot.send_message(message.chat.id, "There\'s a number of elements with typos or something that\'s not in our list.\n"
                                          "Here they are:" + ", ".join(errors)+"\n"
                                          "To get lists of available elements use /listelements")

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_FEATURES_LIST.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start', '/commands',
                                                              '/listelements', '/listfeatures'))
def enter_features_list(message):
    features = re.findall(r'\w+', message.text)

    lst = ['Number', 'Period', 'Group', 'Name',
           'Mass', 'Radius', 'Valence', 'StableIsotopes',
           'MeltingPoint', 'BoilingPoint', 'Density']

    bot.send_message(message.chat.id, 'Thank you, I\'m checkin\' your info.')

    elements = dbworker.get_current_state(str(message.chat.id) + 'elements').split(', ')

    errors = [i for i in features if i not in lst]

    if errors == []:
        if features != []:
            dbworker.set_state(message.chat.id, config.States.S_START.value)
            df = elements_data()
            for_sending = df[df.Symbol.isin(elements)][['Symbol', *features]]
            for_sending_tr = for_sending.transpose()
            dbworker.del_state(str(message.chat.id) + 'element')
            dbworker.del_state(str(message.chat.id) + 'elements')
            bot.send_message(message.chat.id, tabulate(for_sending_tr, tablefmt="pipe"))
        else:
            bot.send_message(message.chat.id, "Something has gone wrong! Enter the list of features properly")

    else:
        bot.send_message(message.chat.id,
                         "There\'s a number of features with typos or something that\'s not in our list.\n"
                         "Here they are:" + ", ".join(errors) + "\n"
                         "To get lists of available features use /listfeatures")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://check-element-bot.herokuapp.com/' + TOKEN)
    return "!", 200

# main function with Web Hook
# our bot is waiting a message from Telegram
def main():
    server.run(host="0.0.0.0", port=PORT)
        
if __name__ == '__main__':
    main()
