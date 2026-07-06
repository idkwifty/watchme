import json
from pathlib import Path
from functools import lru_cache

from config import SUPPORTED_LANGUAGES

LOCALES_DIR = Path(__file__).parent.parent / "locales"


@lru_cache(maxsize=None)
def _load_locale(lang: str) -> dict:
    path = LOCALES_DIR / f"{lang}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def t(lang: str, key: str) -> str:
    if lang not in SUPPORTED_LANGUAGES:
        lang = "uk"

    data = _load_locale(lang)
    return data.get(key, key)