from telebot import TeleBot

from database import db
from handlers.common import (
    card_keyboard,
    format_recommendation,
    genre_keyboard,
    mood_keyboard,
    results_keyboard,
    skip_keyboard,
    sort_keyboard,
    type_keyboard,  
)

from services import jikan, tmdb
from services.inter import t


def _fetch_recommendations(user: dict) -> list[dict]:
    quiz = user["quiz_data"]
    lang = user["language"]
    content_type = quiz.get("type", "movie")
    genres = quiz.get("genres", [])
    mood = quiz.get("mood", "any")
    sort_by = quiz.get("sort", "rating")
    actor_id = quiz.get("actor_id")
    exclude_ids = user.get("shown_ids", []) + db.get_watched_ids(user["user_id"])
    page = quiz.get("page", 1)

    if content_type == "movie":
        return tmdb.discover_movies(lang, genres, mood, actor_id, exclude_ids, page, sort_by)
    if content_type == "series":
        return tmdb.discover_series(lang, genres, mood, actor_id, exclude_ids, page, sort_by)
    if content_type == "dorama":
        return tmdb.discover_dorama(lang, genres, mood, actor_id, exclude_ids, page, sort_by)
    if content_type == "anime":
        return jikan.discover_anime(genres, mood, exclude_ids, page, sort_by)
    return []


def _send_next_card(bot: TeleBot, chat_id: int, user_id: int, lang: str) -> None:
    user = db.get_user(user_id)
    quiz = user["quiz_data"]
    queue = quiz.get("queue", [])

    if not queue:
        quiz["page"] = quiz.get("page", 1) + 1
        db.update_quiz_data(user_id, quiz)

        results = _fetch_recommendations(user)
        if not results:
            bot.send_message(chat_id, t(lang, "no_results"), reply_markup=results_keyboard(lang))
            return

        quiz["queue"] = results
        db.update_quiz_data(user_id, quiz)
        queue = results

    item = queue[0]
    text = format_recommendation(item, lang)
    markup = card_keyboard(lang, item["id"])

    if item.get("poster_url"):
        bot.send_photo(chat_id, item["poster_url"], caption=text, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


def register(bot: TeleBot) -> None:

    @bot.callback_query_handler(func=lambda c: c.data == "home")
    def on_go_home(call):
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

    @bot.callback_query_handler(func=lambda c: c.data.startswith("type:"))
    def on_type_chosen(call):
        content_type = call.data.split(":")[1]
        user_id = call.from_user.id
        user = db.get_user(user_id)
        lang = user["language"]
        quiz_data = {
            "type": content_type,
            "genres": [],
            "mood": "any",
            "actor_id": None,
            "actor_name": None,
            "page": 1,
            "queue": [],
        }
        db.update_quiz_data(user_id, quiz_data)
        db.set_quiz_step(user_id, "choosing_genre")
        bot.edit_message_text(
            t(lang, "choose_genre"),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=genre_keyboard(lang, []),
        )
        bot.answer_callback_query(call.id)
        
        
    @bot.callback_query_handler(func=lambda c: c.data.startswith("genre:"))
    def on_genre_chosen(call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        if user["quiz_step"] != "choosing_genre":
            bot.answer_callback_query(call.id)
            return

        lang = user["language"]
        action = call.data.split(":")[1]
        quiz_data = user["quiz_data"]
        selected: list[str] = quiz_data.get("genres", [])

        if action == "done":
            if not selected:
                bot.answer_callback_query(call.id, "⚠️")
                return

            quiz_data["genres"] = selected
            db.update_quiz_data(user_id, quiz_data)
            db.set_quiz_step(user_id, "choosing_mood")

            bot.edit_message_text(
                t(lang, "ask_mood"),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=mood_keyboard(lang),
            )
            bot.answer_callback_query(call.id)
            return

        if action in selected:
            selected.remove(action)
        else:
            selected.append(action)

        quiz_data["genres"] = selected
        db.update_quiz_data(user_id, quiz_data)
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=genre_keyboard(lang, selected),
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("mood:"))
    def on_mood_chosen(call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        if user["quiz_step"] != "choosing_mood":
            bot.answer_callback_query(call.id)
            return

        lang = user["language"]
        mood = call.data.split(":")[1]
        quiz_data = user["quiz_data"]
        quiz_data["mood"] = mood
        db.update_quiz_data(user_id, quiz_data)
        db.set_quiz_step(user_id, "choosing_sort")

        bot.edit_message_text(
            t(lang, "ask_sort"),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=sort_keyboard(lang),
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("sort:"))
    def on_sort_chosen(call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        if user["quiz_step"] != "choosing_sort":
            bot.answer_callback_query(call.id)
            return

        lang = user["language"]
        sort_value = call.data.split(":")[1]
        quiz_data = user["quiz_data"]
        quiz_data["sort"] = sort_value
        db.update_quiz_data(user_id, quiz_data)

        if quiz_data.get("type") == "anime":
            bot.edit_message_text(t(lang, "searching"), call.message.chat.id, call.message.message_id)
            _send_next_card(bot, call.message.chat.id, user_id, lang)
            db.set_quiz_step(user_id, "")
            bot.answer_callback_query(call.id)
            return

        db.set_quiz_step(user_id, "entering_actor")
        bot.edit_message_text(
            t(lang, "ask_actors"),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=skip_keyboard(lang),
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data == "actor:skip")
    def on_actor_skip(call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        lang = user["language"]

        bot.edit_message_text(t(lang, "searching"), call.message.chat.id, call.message.message_id)
        _send_next_card(bot, call.message.chat.id, user_id, lang)
        db.set_quiz_step(user_id, "")
        bot.answer_callback_query(call.id)

    @bot.message_handler(func=lambda m: db.get_user(m.from_user.id)["quiz_step"] == "entering_actor")
    def on_actor_name(message):
        user_id = message.from_user.id
        user = db.get_user(user_id)
        lang = user["language"]
        name = message.text.strip()
        quiz_data = user["quiz_data"]

        actor_id = tmdb.search_person(name)
        if actor_id is None:
            bot.send_message(
                message.chat.id,
                t(lang, "actor_not_found"),
                reply_markup=skip_keyboard(lang),
            )
            return
        quiz_data["actor_id"] = actor_id
        quiz_data["actor_name"] = name

        db.update_quiz_data(user_id, quiz_data)
        bot.send_message(message.chat.id, t(lang, "searching"))
        _send_next_card(bot, message.chat.id, user_id, lang)
        db.set_quiz_step(user_id, "")

    @bot.callback_query_handler(func=lambda c: c.data.startswith(("like:", "next:", "watched:")))
    def on_card_action(call):
        action, item_id = call.data.split(":", 1)
        user_id = call.from_user.id
        user = db.get_user(user_id)
        lang = user["language"]
        quiz_data = user["quiz_data"]
        queue = quiz_data.get("queue", [])

        if action == "like":
            liked_item = None
            for it in queue:
                if str(it["id"]) == item_id:
                    liked_item = it
                    break
            if liked_item:
                db.add_favorite(user_id, liked_item)

        if action == "watched":
            watched_item = None
            for it in queue:
                if str(it["id"]) == item_id:
                    watched_item = it
                    break
            if watched_item:
                db.add_watched(user_id, watched_item)

        if queue and str(queue[0]["id"]) == item_id:
            queue.pop(0)
        quiz_data["queue"] = queue
        db.update_quiz_data(user_id, quiz_data)
        db.add_shown_ids(user_id, [item_id])

        bot.answer_callback_query(call.id)
        _send_next_card(bot, call.message.chat.id, user_id, lang)

    @bot.callback_query_handler(func=lambda c: c.data == "more")
    def on_show_more(call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        lang = user["language"]
        bot.answer_callback_query(call.id)
        _send_next_card(bot, call.message.chat.id, user_id, lang)