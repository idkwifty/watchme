

from telebot import TeleBot

from handlers import quiz, start


def register_all(bot: TeleBot) -> None:
    start.register(bot)
    quiz.register(bot)
