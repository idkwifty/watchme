
from telebot import TeleBot

from database import db
from handlers.common import language_keyboard, type_keyboard
from services.inter import t


def register(bot: TeleBot) -> None:

    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        db.reset_quiz(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "Оберіть мову / Выберите язык / Choose language:",
            reply_markup=language_keyboard(),
        )

    @bot.message_handler(commands=["language"])
    def cmd_language(message):
        db.reset_quiz(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "Оберіть мову / Выберите язык / Choose language:",
            reply_markup=language_keyboard(),
        )

    @bot.message_handler(commands=["help"])
    def cmd_help(message):
        user = db.get_user(message.from_user.id)
        bot.send_message(message.chat.id, t(user["language"], "help"))

    @bot.callback_query_handler(func=lambda c: c.data.startswith("lang:"))
    def on_language_chosen(call):
        lang = call.data.split(":")[1]
        user_id = call.from_user.id

        db.set_language(user_id, lang)
        db.reset_quiz(user_id)

        bot.edit_message_text(
            t(lang, "welcome"),
            call.message.chat.id,
            call.message.message_id,
        )
        bot.send_message(
            call.message.chat.id,
            t(lang, "choose_type"),
            reply_markup=type_keyboard(lang),
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data == "change_lang")
    def on_change_language(call):
        bot.edit_message_text(
            "Оберіть мову / Выберите язык / Choose language:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=language_keyboard(),
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data == "restart")
    def on_restart(call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        lang = user["language"]

        db.reset_quiz(user_id)
        bot.send_message(
            call.message.chat.id,
            t(lang, "choose_type"),
            reply_markup=type_keyboard(lang),
        )
        bot.answer_callback_query(call.id)
