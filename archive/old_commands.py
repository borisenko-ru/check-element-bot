@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, 'Hi!')

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, 'Howdy, how are You doing!')

@bot.message_handler(func=lambda message:message.text.strip().lower() not in ('/start', '/help'))
def echo(message):
    bot.send_message(message.chat.id, message.text)