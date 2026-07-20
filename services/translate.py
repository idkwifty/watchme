from typing import Any

from services.http_utils import get_json

MYMEMORY_URL = "https://api.mymemory.translated.net/get"


LANG_CODE_MAP = {
    "ua": "uk",
    "uk": "uk",
    "en": "en",
    "ru": "ru",
    "pl": "pl",
    "de": "de",
    "es": "es",
}


def translate_text(text: str, target_lang: str, source_lang: str = "en") -> str:
    """Translate text via MyMemory (free, no API key). Falls back to the
    original text if translation fails or isn't needed."""
    if not text:
        return text

    iso_target = LANG_CODE_MAP.get(target_lang, target_lang)
    if iso_target == source_lang:
        return text

    try:
        data: dict[str, Any] = get_json(
            MYMEMORY_URL,
            {"q": text, "langpair": f"{source_lang}|{iso_target}"},
        )
        translated = (data.get("responseData") or {}).get("translatedText")
        if translated and "MYMEMORY WARNING" not in translated:
            return translated
    except Exception:
        import traceback
        traceback.print_exc()

    return text