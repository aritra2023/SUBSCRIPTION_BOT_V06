import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
ADMIN_ID: int = int(os.environ["ADMIN_ID"])
MONGO_URI: str = os.environ["MONGO_URI"]

DB_NAME: str = "flixverse_bot"
