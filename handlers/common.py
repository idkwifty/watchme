

from telebot import types

from services.inter import t

GENRE_KEYS = [
    "action", "comedy", "drama", "horror", "romance",
    "scifi", "thriller", "fantasy", "animation", "mystery",
]


def language_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Українська", callback_data="lang:uk"),
        types.InlineKeyboardButton("Русский", callback_data="lang:ru"),
    )
    markup.add(types.InlineKeyboardButton("English", callback_data="lang:en"))
    return markup


def type_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t(lang, "type_movie"), callback_data="type:movie"),
        types.InlineKeyboardButton(t(lang, "type_series"), callback_data="type:series"),
    )
    markup.row(
        types.InlineKeyboardButton(t(lang, "type_anime"), callback_data="type:anime"),
        types.InlineKeyboardButton(t(lang, "type_dorama"), callback_data="type:dorama"),
    )
    markup.add(types.InlineKeyboardButton(t(lang, "menu_favorites"), callback_data="show_favorites"))
    markup.add(types.InlineKeyboardButton(t(lang, "menu_watched"), callback_data="show_watched"))
    markup.add(types.InlineKeyboardButton(t(lang, "change_language"), callback_data="change_lang"))
    return markup


def card_keyboard(lang: str, item_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t(lang, "like"), callback_data=f"like:{item_id}"),
        types.InlineKeyboardButton(t(lang, "next"), callback_data=f"next:{item_id}"),
    )
    markup.add(types.InlineKeyboardButton(t(lang, "watched"), callback_data=f"watched:{item_id}"))
    markup.add(types.InlineKeyboardButton(t(lang, "go_home"), callback_data="home"))
    return markup

def genre_keyboard(lang: str, selected: list[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    row: list[types.InlineKeyboardButton] = []
    for key in GENRE_KEYS:
        label = t(lang, f"genre_{key}")
        if key in selected:
            label = f"✓ {label}"
        row.append(types.InlineKeyboardButton(label, callback_data=f"genre:{key}"))
        if len(row) == 2:
            markup.row(*row)
            row = []
    if row:
        markup.row(*row)
    markup.add(types.InlineKeyboardButton(t(lang, "genre_done"), callback_data="genre:done"))
    return markup


def mood_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(lang, "mood_light"), callback_data="mood:light"))
    markup.add(types.InlineKeyboardButton(t(lang, "mood_sad"), callback_data="mood:sad"))
    markup.add(types.InlineKeyboardButton(t(lang, "mood_intense"), callback_data="mood:intense"))
    markup.add(types.InlineKeyboardButton(t(lang, "mood_any"), callback_data="mood:any"))
    return markup


def skip_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(lang, "skip"), callback_data="actor:skip"))
    return markup


def results_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t(lang, "show_more"), callback_data="more"),
        types.InlineKeyboardButton(t(lang, "restart"), callback_data="restart"),
    )
    return markup


def format_recommendation(item: dict, lang: str) -> str:
    lines = [
        f"<b>{item['title']}</b>",
        f"{t(lang, 'rating')}: {item['rating']}/10",
    ]
    if item.get("year"):
        lines.append(f" {t(lang, 'year')}: {item['year']}")
    if item.get("overview"):
        lines.append(f"\n{item['overview']}")
    return "\n".join(lines)

