from telebot import TeleBot, types

from database import db
from handlers.common import format_recommendation
from services.inter import t


def _favorite_keyboard(lang: str, item_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(lang, "remove_favorite"), callback_data=f"unfav:{item_id}"))
    return markup


def _send_favorites(bot: TeleBot, chat_id: int, user_id: int) -> None:
    user = db.get_user(user_id)
    lang = user["language"]
    items = db.get_favorites(user_id)

    if not items:
        bot.send_message(chat_id, t(lang, "no_favorites"))
        return

    for item in items:
        text = format_recommendation(item, lang)
        markup = _favorite_keyboard(lang, item["id"])
        if item.get("poster_url"):
            bot.send_photo(chat_id, item["poster_url"], caption=text, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


def register(bot: TeleBot) -> None:

    @bot.message_handler(commands=["favorites"])
    def on_favorites(message):
        _send_favorites(bot, message.chat.id, message.from_user.id)

    @bot.callback_query_handler(func=lambda c: c.data == "show_favorites")
    def on_favorites_button(call):
        _send_favorites(bot, call.message.chat.id, call.from_user.id)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("unfav:"))
    def on_remove_favorite(call):
        _, item_id = call.data.split(":", 1)
        user_id = call.from_user.id
        db.remove_favorite(user_id, item_id)
        bot.answer_callback_query(call.id, "")
        bot.delete_message(call.message.chat.id, call.message.message_id)