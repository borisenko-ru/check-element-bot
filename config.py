from enum import Enum

token = '1441927561:AAHMO0-tMDIaAht_7tWVUk5k6KfP_mGLF24'
db_file = 'database.vdb'


class States(Enum):
    S_START = "1"
    S_ENTER_ELEMENT = "2"
    S_ENTER_FEATURES_LIST = "3"