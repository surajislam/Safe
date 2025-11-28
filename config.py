import re
import os
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get your token from @BotFather on Telegram.
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "8578397940:AAHj6zglBBc6DJtSzH4kLQfv0uu-KtbyK1A")
