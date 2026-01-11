import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Load secrets from .env
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
group_id = os.getenv('GROUP_ID')

# Message
message = 'Hello from Telethon Bot! 😊'

with TelegramClient(StringSession(), api_id, api_hash).start(bot_token=bot_token) as client:
    client.send_message(int(group_id), message)