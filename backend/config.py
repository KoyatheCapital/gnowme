import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "Gnowme"
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/gnowme_db")
    USER_VOICE_REF = "data/voice/user_ref.wav"  # Record 5-10 seconds of your voice
