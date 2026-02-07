import os
import logging
import schedule
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
def send_message():

    # Load secrets from .env
    load_dotenv()

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id']]):
        logging.error("Missing required environment variables")
        exit(1)

    # print(get_stock_performance("muthootfin.NS"))
    # print(process())

    timeperiod = '15d'    
    message = process(timeperiod)
    # print(message)

    try:
        with TelegramClient(StringSession(), env['api_id'], env['api_hash']).start(bot_token=env['bot_token']) as client:

            logging.info("Sending message...")
            # Message
            now = datetime.now()
            client.send_message(int(env['group_id']), now.strftime("%d-%m-%Y") + " " + timeperiod)
            client.send_message(int(env['group_id']), message, parse_mode="md")

            logging.info("Message sent successfully!")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    # logging.info("Scheduler started")
    # send_message()

    # Schedule job
    tz = pytz.timezone('Asia/Kolkata')

    # schedule.every().day.at("16:00").do(send_message)
    times = ["11:00", "14:30", "18:00"]
    for scheduled_time in times:
        schedule.every().day.at(scheduled_time).do(send_message)

    while True:
        schedule.run_pending()
        time.sleep(1)