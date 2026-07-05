
import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent.parent / "locales"

# Завантажуємо всі мови в пам'ять при старті бота
_LOCALES: dict[str, dict[str, str]] = {}


def load_locales() -> None:
    """Прочитати JSON-файли з папки locales/."""
    for path in LOCALES_DIR.glob("*.json"):
        lang = path.stem  # "uk" з "uk.json"
        with open(path, encoding="utf-8") as f:
            _LOCALES[lang] = json.load(f)


def t(lang: str, key: str, **kwargs: str) -> str:
   
    texts = _LOCALES.get(lang) or _LOCALES.get("en", {})
    text = texts.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
