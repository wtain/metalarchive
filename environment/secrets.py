import os

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
