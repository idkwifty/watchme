

import logging
import sys

import telebot

from config import BOT_TOKEN
from database.db import init_db
from handlers import register_all
from services.inter import load_locales

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN.startswith("123456789"):
        logger.error(
            "Вставте справжній BOT_TOKEN у файл .env\n"
            "   Отримати: Telegram → @BotFather → /newbot"
        )
        return

    load_locales()
    init_db()

    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
    register_all(bot)

    logger.info("Бот запущено на Python %s! Ctrl+C — зупинка.", sys.version.split()[0])
    bot.infinity_polling()


if __name__ == "__main__":
    main()
