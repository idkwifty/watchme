import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

TVMAZE_BASE_URL = "https://api.tvmaze.com"
JIKAN_BASE_URL = "https://api.jikan.moe/v4/"

DATABASE_PATH = Path(__file__).parent / "bot_data.db"
SUPPORTED_LANGUAGES = ("uk", "ru", "en")

TMDB_LANGUAGE = {
    "uk": "uk-UA",
    "ru": "ru-RU",
    "en": "en-US",
}
