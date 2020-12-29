import os
from dotenv import load_dotenv

load_dotenv("../config/.env")

class alpaca: 
    APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
    APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
    APCA_API_PAPER_BASE_URL = os.getenv('APCA_API_PAPER_BASE_URL')
    APCA_API_STREAM_BASE_URL = os.getenv('APCA_API_STREAM_BASE_URL')

class rating: 
    STRONG_BUY = 'STRONG_BUY'
    BUY = 'BUY'
    NEUTRAL = 'NEUTRAL'
    SELL = 'SELL'
    STRONG_SELL = 'STRONG_SELL'