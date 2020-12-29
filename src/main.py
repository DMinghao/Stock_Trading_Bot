import os
from dotenv import load_dotenv

load_dotenv("../config/.env")

APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
APCA_API_PAPER_BASE_URL = os.getenv('APCA_API_PAPER_BASE_URL')
APCA_API_STREAM_BASE_URL = os.getenv('APCA_API_STREAM_BASE_URL')

class algo: 
    pass

class util: 
    pass