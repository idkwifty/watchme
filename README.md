# Watch Bot — Telegram-бот «Що подивитись?»

Бот задає питання і підбирає рекомендації. 3 мови: 🇺🇦 🇷🇺 🇬🇧

**Усі API безкоштовні** — TMDB не використовується.

---

## Які API використовує бот

| Тип контенту | API | Ключ потрібен? | Ціна |
|---|---|---|---|
| 🎬 Фільми | [OMDb](https://www.omdbapi.com) | Так (безкоштовний) | 1000 запитів/день |
| 📺 Серіали | [TVmaze](https://www.tvmaze.com/api) | **Ні** | Безкоштовно |
| 🌸 Дорами | [TVmaze](https://www.tvmaze.com/api) | **Ні** | Безкоштовно |
| ⛩ Аніме | [Jikan](https://jikan.moe) | **Ні** | Безкоштовно |

### Про TMDB і $149/місяць

TMDB **безкоштовний** для особистих і навчальних проєктів.

$149/місяць — це **комерційна** ліцензія, якщо бот:
- з рекламою або підпискою
- приносить гроші
- є «основним продуктом» (не хобі)

Для свого бота без монетизації TMDB теж можна безкоштовно. Але ми перейшли на інші API — вони простіші і не вимагають комерційної ліцензії.

---

## Крок 1. Створити Telegram-бота

1. Відкрийте **@BotFather** у Telegram
2. `/newbot` → введіть ім'я та username
3. Скопіюйте **токен** → він піде в `.env` як `BOT_TOKEN`

---

## Крок 2. Отримати ключ OMDb (тільки для фільмів)

1. Відкрийте https://www.omdbapi.com/apikey.aspx
2. Введіть email → оберіть **FREE** (1000 запитів/день)
3. Підтвердіть email → скопіюйте ключ
4. Вставте в `.env` як `OMDB_API_KEY`

**TVmaze і Jikan — ключі не потрібні.**

---

## Крок 3. Налаштування (Python 3.14 підтримується)

```powershell
cd C:\Users\maksym\Projects\watch-bot
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Встановлюється лише **2 пакети**: `pyTelegramBotAPI` + `python-dotenv`.
Решта (SQLite, HTTP) — вбудовано в Python.

Створіть файл `.env`:

```env
BOT_TOKEN=ваш_токен_від_BotFather
OMDB_API_KEY=ваш_ключ_від_OMDb
```

---

## Крок 4. Запуск

```powershell
venv\Scripts\activate
python bot.py
```

У Telegram: знайдіть бота → `/start`

---

## Структура проєкту

```
watch-bot/
├── bot.py                 ← ЗАПУСКАТИ ЦЕЙ ФАЙЛ
├── config.py              ← Налаштування
├── .env                   ← Токени (не в git!)
│
├── locales/               ← Тексти uk / ru / en
├── handlers/
│   ├── start.py           ← /start, мова
│   └── quiz.py            ← Опитування + результати
│
├── services/
│   ├── omdb.py            ← Фільми
│   ├── tvmaze.py          ← Серіали + дорами
│   ├── jikan.py           ← Аніме
│   └── i18n.py            ← Переклади
│
└── database/
    └── db.py              ← Збереження відповідей
```

---

## Як працює кожен API

### OMDb (фільми)

```
GET https://www.omdbapi.com/?apikey=КЛЮЧ&s=action+comedy&type=movie&page=1
```

Повертає список фільмів → бот додає опис і рейтинг.

### TVmaze (серіали, дорами)

```
GET https://api.tvmaze.com/search/shows?q=drama
GET https://api.tvmaze.com/search/people?q=actor_name
```

Ключ не потрібен. Дорами — серіали з Кореї, Японії, Китаю.

### Jikan (аніме)

```
GET https://api.jikan.moe/v4/anime?genres=Action,Comedy&order_by=score&sort=desc
```

Ключ не потрібен. Ліміт: ~3 запити/сек.

---

## Обмеження безкоштовних API

| API | Обмеження |
|-----|-----------|
| OMDb | 1000 запитів/день (на фільм ~2 запити) |
| TVmaze | ~20 запитів / 10 сек |
| Jikan | ~3 запити/сек, 60/хв |

Для особистого бота цього більш ніж достатньо.

---

## Команди бота

| Команда | Дія |
|---------|-----|
| `/start` | Почати, обрати мову |
| `/language` | Змінити мову |
| `/help` | Довідка |

---

## Проблеми?

| Проблема | Рішення |
|----------|---------|
| Немає фільмів | Перевірте `OMDB_API_KEY` у `.env` |
| Немає серіалів/дорам | TVmaze працює без ключа — перевірте інтернет |
| Немає аніме | Зачекайте 1–2 сек (ліміт Jikan) і спробуйте знову |
| Бот не відповідає | Термінал відкритий? `python bot.py` запущено? |
