import os
import logging
# import schedule
import time
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from datetime import datetime
import pytz
from stock_perfom import process

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

    with TelegramClient(StringSession(), env['api_id'], env['api_hash']).start(bot_token=env['bot_token']) as client:

        logging.info("Sending message...")
        # Message
        now = datetime.now()
        client.send_message(int(env['group_id']), now.strftime("%d-%m-%Y"))
        client.send_message(int(env['group_id']), "**this text will be bold** is it bold?", parse_mode="md")

        logging.info("Message sent successfully!")


# this is actual func
def send_update():

    # Load secrets from .env
    load_dotenv()

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id']]):
        logging.error("Missing required environment variables")
        exit(1)

    # print(get_stock_performance("muthootfin.NS"))
    # print(process())

    timeperiod = '1y'    
    message = process(timeperiod)
    # print(message)

    try:
        with TelegramClient(StringSession(), env['api_id'], env['api_hash'], timeout=5, request_retries=3, connection_retries=3 ).start(bot_token=env['bot_token']) as client:

            logging.info("Sending message...")
            # Message
            now = datetime.now()
            # client.send_message(int(env['group_id']), now.strftime("%d-%m-%Y") + " " + timeperiod)
            client.send_message(int(env['group_id']), now.strftime("%d-%m-%Y") + " " + timeperiod + "\n\n" + message, parse_mode="md")

            logging.info("Message sent successfully!")
    except Exception as e:
        logging.error(f"Error: {e}")


message = sys.argv[1]
main(message)

send_update()