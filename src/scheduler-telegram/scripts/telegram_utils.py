import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession


async def send_telegram_message(api_id, api_hash, bot_token, chat_id, text):
    """Send a Telegram message with bounded connection and retry behavior."""
    client = TelegramClient(
        StringSession(),
        int(api_id),
        api_hash,
        timeout=10,
        request_retries=1,
        connection_retries=1,
        retry_delay=1,
        auto_reconnect=False,
    )

    try:
        # Keep the whole Telegram handshake bounded so reconnects cannot hang forever.
        await asyncio.wait_for(client.start(bot_token=bot_token), timeout=30)
        await asyncio.wait_for(
            client.send_message(int(chat_id), text, parse_mode="md"),
            timeout=30,
        )
    finally:
        await client.disconnect()
