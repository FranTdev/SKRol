import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    COSMOS_URI = os.getenv("COSMOS_URI")
    COSMOS_KEY = os.getenv("COSMOS_KEY")
    COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "rpg.db")
    COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER_NAME", "users")
    SECRET_KEY = os.getenv("SECRET_KEY", "secreto_default")

settings = Settings()