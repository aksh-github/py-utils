import asyncio
import os
import logging
# import schedule
from dotenv import load_dotenv
from datetime import datetime
import pytz
from stock_perfom import process
import sys
from telegram_utils import send_telegram_message

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Get env variables
def get_environment_variables():
    return {
        'api_id': os.getenv('API_ID'),
        'api_hash': os.getenv('API_HASH'),
        'bot_token': os.getenv('BOT_TOKEN'),
        'group_id': os.getenv('GROUP_ID')
    }


# this is dummy func
def dummy_send_message():
    # Load secrets from .env
    load_dotenv()

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id']]):
        logging.error("Missing required environment variables")
        exit(1)

    now = datetime.now()
    asyncio.run(
        send_telegram_message(
            env['api_id'],
            env['api_hash'],
            env['bot_token'],
            env['group_id'],
            now.strftime("%d-%m-%Y") + "\n\n**this text will be bold** is it bold?",
        )
    )
    logging.info("Message sent successfully!")


# this is actual func
def send_update(msg):

    # Load secrets from .env
    load_dotenv()

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id']]):
        logging.error("Missing required environment variables")
        exit(1)

    # print(get_stock_performance("muthootfin.NS"))
    # print(process())

    timeperiod = '1y'    
    message = process(timeperiod, msg)
    # print(message)


    # if not blank
    if message:
        try:
            logging.info("Sending message...")
            now = datetime.now()
            asyncio.run(
                send_telegram_message(
                    env['api_id'],
                    env['api_hash'],
                    env['bot_token'],
                    env['group_id'],
                    now.strftime("%d-%m-%Y") + " " + timeperiod + "\n\n" + message,
                )
            )
            logging.info("Message sent successfully!")
        except Exception as e:
            logging.error(f"Error: {e}")
    else:
        logging.info("Stocks are performing good")


message = sys.argv[1] if len(sys.argv) > 1 else ""
send_update(message)
