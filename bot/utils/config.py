import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")
BRAND_NAME = os.environ.get("brand_name", "Zyrox X")
NAME = BRAND_NAME
server = "https://discord.gg/codexdev"
ch = "https://discord.com/channels/699587669059174461/1271825678710476911"
OWNER_IDS = [767979794411028491]
BotName = BRAND_NAME
serverLink = "https://discord.gg/codexdev"
CMD_WEBHOOK_URL = os.getenv("CMD_WEBHOOK_URL")