import os
import logging
import schedule
import time
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from datetime import datetime
import pytz

# Read stocks file
def read_stocks():
    with open('stocks.txt', 'r') as f:
        stocks = []

        for line in f:
            line = line.strip()
            if line == '':
                break
            stocks.append(line)
            
    print(stocks)



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



def send_message():

    # Load secrets from .env
    load_dotenv()

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id']]):
        logging.error("Missing required environment variables")
        exit(1)

    try:
        with TelegramClient(StringSession(), env['api_id'], env['api_hash']).start(bot_token=env['bot_token']) as client:
            logging.info("Sending message...")
            # Message
            message = 'Good Afternoon! 😊'
            client.send_message(int(env['group_id']), message)
            logging.info("Message sent successfully!")
    except Exception as e:
        logging.error(f"Error: {e}")

# Schedule job
tz = pytz.timezone('Asia/Kolkata')
schedule.every().day.at("16:00").do(send_message)

if __name__ == '__main__':
    logging.info("Scheduler started")
    send_message()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)