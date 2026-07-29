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
from arattai_utils import send_arattai_message

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Get env variables
def get_environment_variables():
    return {
        'api_id': os.getenv('API_ID'),
        'api_hash': os.getenv('API_HASH'),
        'bot_token': os.getenv('BOT_TOKEN'),
        'group_id': os.getenv('GROUP_ID'),
        'zohoflow_url': os.getenv('ZOHOFLOW_URL'),
    }


def write_stock_update_file(content):
    try:
        if content is None:
            raise ValueError("Content cannot be None")

        output_path = os.path.join(os.path.dirname(__file__), 'stock-update.txt')   # need to be same as serve_stock_file.py
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(str(content))
        logging.info("Stock update file written successfully: %s", output_path)
        return True
    except FileNotFoundError as exc:
        logging.error("Directory not found while writing stock update file: %s", exc)
        return False
    except PermissionError as exc:
        logging.error("Permission denied while writing stock update file: %s", exc)
        return False
    except ValueError as exc:
        logging.error("Invalid content provided: %s", exc)
        return False
    except Exception as exc:
        logging.error("Unexpected error while writing stock update file: %s", exc)
        return False


# this is dummy func
def dummy_send_message():
    # Load secrets from .env
    load_dotenv()

    env = get_environment_variables()

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id'], env['zohoflow_url']]):
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

    if not all([env['api_id'], env['api_hash'], env['bot_token'], env['group_id'], env['zohoflow_url']]):
        logging.error("Missing required environment variables")
        exit(1)

    # print(get_stock_performance("muthootfin.NS"))
    # print(process())

    timeperiod = '1y'    
    message = process(timeperiod, msg)
    # print(message)


    # if not blank
    if message:

        # if its perfom check, send telegram message
        if msg:    
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
                logging.info("Trying with Arattai...")

                send_arattai_message(env['zohoflow_url'], message)


        else:
        # write to text file, and just send link over telegram
            try:
                logging.info("Writing message to file...")

                issuccess = write_stock_update_file(message)

                if issuccess==False:
                    logging.error(f"Something wrong while writing to file...")

                now = datetime.now()
                asyncio.run(
                    send_telegram_message(
                        env['api_id'],
                        env['api_hash'],
                        env['bot_token'],
                        env['group_id'],
                        now.strftime("%d-%m-%Y") + " " + timeperiod + "\n\n" + "Click this link to access latest report: [Stock report](http://bharatvidya.duckdns.org/stock-perfor)",
                    )
                )
                logging.info("Message sent successfully!")
                logging.info("File content written successfully!")
            except Exception as e:
                logging.error(f"Error: {e}")
            
    else:
        logging.info("Stocks are performing good")

# Don't run on weekends
if datetime.now().weekday() in (5, 6):
    logging.info("It's Weekend!!")
else:
    message = sys.argv[1] if len(sys.argv) > 1 else ""
    send_update(message)
    # dummy_send_message()


# message = sys.argv[1] if len(sys.argv) > 1 else ""
# send_update(message)