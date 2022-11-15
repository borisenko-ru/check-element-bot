from enum import Enum
from os import environ
from dotenv import load_dotenv

db_file = 'database.vdb'
#load .env
load_dotenv()

TOKEN = environ.get('YOUR_TOKEN')
PORT = int(environ.get('PORT', 5000))

class States(Enum):
    S_START = "1"
    S_ENTER_ELEMENT = "2"
    S_ENTER_FEATURES_LIST = "3"
