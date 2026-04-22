import asyncio
import logging
import datetime
import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from telegram_utils import send_telegram_message

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


def main(message):
    # message = "Timesheet"
    
    # Load secrets from .env (parent directory)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['id']]):
        logging.error("Missing required environment variables")
        exit(1)

    try:
        logging.info("Sending message...")
        asyncio.run(
            send_telegram_message(
                env['api_id'],
                env['api_hash'],
                env['bot_token'],
                env['id'],
                message,
            )
        )
        logging.info("Message sent successfully!")
    except Exception as e:
        logging.error(f"Error: {e}")

# Check if arguments are provided
if len(sys.argv) != 2:
    logging.error("Usage: python timesheet.py <message>")
    sys.exit(1)

message = sys.argv[1]
main(message)
