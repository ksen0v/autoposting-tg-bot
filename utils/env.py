from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
CRYPTO_BOT_TOKEN = str(os.getenv('CRYPTO_BOT_TOKEN'))
ADMIN_SECRET_KEY = str(os.getenv('ADMIN_SECRET_KEY'))