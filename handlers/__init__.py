

from telebot import TeleBot

from handlers import quiz, start
from telebot import TeleBot

from handlers import quiz, start, favorites


def register_all(bot: TeleBot) -> None:
    start.register(bot)
    quiz.register(bot)
    favorites.register(bot)