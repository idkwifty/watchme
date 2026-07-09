from telebot import TeleBot

from database import db
from handlers.common import format_recommendation
from services.inter import t


def _send_watched(bot: TeleBot, chat_id: int, user_id: int) -> None:
    user = db.get_user(user_id)
    lang = user["language"]
    items = db.get_watched(user_id)

    if not items:
        bot.send_message(chat_id, t(lang, "no_watched"))
        return

    for item in items:
        text = format_recommendation(item, lang)
        if item.get("poster_url"):
            bot.send_photo(chat_id, item["poster_url"], caption=text, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, parse_mode="HTML")


def register(bot: TeleBot) -> None:

    @bot.message_handler(commands=["watched"])
    def on_watched(message):
        _send_watched(bot, message.chat.id, message.from_user.id)

    @bot.callback_query_handler(func=lambda c: c.data == "show_watched")
    def on_watched_button(call):
        _send_watched(bot, call.message.chat.id, call.from_user.id)
        bot.answer_callback_query(call.id)