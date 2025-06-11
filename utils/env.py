from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
CRYPTO_BOT_TOKEN = str(os.getenv('CRYPTO_BOT_TOKEN'))