
import logging
import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Get env variables
def get_environment_variables():
    return {
        'api_id': os.getenv('API_ID'),
        'api_hash': os.getenv('API_HASH'),
        'bot_token': os.getenv('BOT_TOKEN'),
        'id': os.getenv('ID')
    }

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    message = "Pay ELECTRICITY BILL, WATER BILL, PROPERTY TAX"
    logging.info("main executed")

    # Load secrets from .env (parent directory)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['id']]):
        logging.error("Missing required environment variables")
        exit(1)

    try:
        with TelegramClient(StringSession(), env['api_id'], env['api_hash']).start(bot_token=env['bot_token']) as client:

            logging.info("Sending message...")
            
            # client.send_message(int(env['id']), now.strftime("%d-%m-%Y") + " " + timeperiod)
            client.send_message(int(env['id']), message, parse_mode="md")

            logging.info("Message sent successfully!")
    except Exception as e:
        logging.error(f"Error: {e}")

main()