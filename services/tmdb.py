from html import unescape
from typing import Any

from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_LANGUAGE
from services.http_utils import get_json


GENRE_IDS = {
    "action": 28,
    "comedy": 35,
    "drama": 18,
    "horror": 27,
    "romance": 10749,
    "scifi": 878,
    "thriller": 53,
    "fantasy": 14,
    "animation": 16,
    "mystery": 9648,
}

MOOD_GENRES = {
    "light": [35, 10751],
    "sad": [18, 10749],
    "intense": [53, 28, 27],
    "any": [],
}


TV_GENRE_IDS = {
    "action": 10759,
    "comedy": 35,
    "drama": 18,
    "scifi": 10765,
    "fantasy": 10765,
    "animation": 16,
    "mystery": 9648,
}

TV_MOOD_GENRES = {
    "light": [35, 10751],
    "sad": [18],
    "intense": [10759, 10765],
    "any": [],
}

DORAMA_COUNTRIES = "KR|JP|CN|TW|TH"


def _tmdb_get(endpoint: str, params: dict | None = None) -> dict | None:
    if not TMDB_API_KEY:
        print("TMDB_API_KEY порожній — перевір .env")
        return None
    try:
        data = get_json(
            f"{TMDB_BASE_URL}/{endpoint}",
            {"api_key": TMDB_API_KEY, **(params or {})},
        )
    except Exception as e:
        print(f"TMDB API error on {endpoint}: {e}")
        return None
    return data if isinstance(data, dict) else None


def search_person(name: str) -> int | None:
    data = _tmdb_get("search/person", {"query": name})
    if not data or not data.get("results"):
        return None
    return data["results"][0]["id"]


def _genre_ids(genres: list[str], mood: str) -> list[int]:
    ids = [GENRE_IDS[g] for g in genres if g in GENRE_IDS]
    ids.extend(MOOD_GENRES.get(mood, []))
    return list(dict.fromkeys(ids))


def _tv_genre_ids(genres: list[str], mood: str) -> list[int]:
    ids = [TV_GENRE_IDS[g] for g in genres if g in TV_GENRE_IDS]
    ids.extend(TV_MOOD_GENRES.get(mood, []))
    return list(dict.fromkeys(ids))


DORAMA_COUNTRY_SET = {"KR", "JP", "CN", "TW", "TH"}


def _format_results(
    data: dict | None,
    exclude_ids: list,
    media_type: str,
    exclude_countries: set[str] | None = None,
) -> list[dict[str, Any]]:
    if not data:
        return []

    results = []
    for item in data.get("results", []):
        item_id = item.get("id")
        if item_id in exclude_ids:
            continue

        if exclude_countries:
            origin = set(item.get("origin_country") or [])
            if origin & exclude_countries:
                continue

        title = item.get("title") or item.get("name") or "?"
        overview = item.get("overview") or ""
        if len(overview) > 300:
            overview = overview[:297] + "..."

        poster = item.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
        year = (item.get("release_date") or item.get("first_air_date") or "")[:4]

        results.append({
            "id": item_id,
            "title": title,
            "overview": unescape(overview),
            "rating": round(item.get("vote_average", 0), 1),
            "year": year,
            "poster_url": poster_url,
            "media_type": media_type,
        })
        if len(results) >= 5:
            break
    return results


def discover_movies(
    lang: str,
    genres: list[str],
    mood: str,
    actor_id: int | None,
    exclude_ids: list,
    page: int = 1,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "language": TMDB_LANGUAGE.get(lang, "en-US"),
        "sort_by": "vote_average.desc",
        "vote_count.gte": 100,
        "page": page,
    }
    genre_ids = _genre_ids(genres, mood)
    if genre_ids:
        params["with_genres"] = "|".join(str(g) for g in genre_ids)
    if actor_id:
        params["with_cast"] = actor_id

    return _format_results(_tmdb_get("discover/movie", params), exclude_ids, "movie")


def discover_series(
    lang: str,
    genres: list[str],
    mood: str,
    actor_id: int | None,
    exclude_ids: list,
    page: int = 1,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "language": TMDB_LANGUAGE.get(lang, "en-US"),
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "page": page,
    }
    genre_ids = _tv_genre_ids(genres, mood)
    if genre_ids:
        params["with_genres"] = "|".join(str(g) for g in genre_ids)
    if actor_id:
        params["with_cast"] = actor_id

    return _format_results(
        _tmdb_get("discover/tv", params),
        exclude_ids,
        "series",
        exclude_countries=DORAMA_COUNTRY_SET,   
    )


def discover_dorama(
    lang: str,
    genres: list[str],
    mood: str,
    actor_id: int | None,
    exclude_ids: list,
    page: int = 1,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "language": TMDB_LANGUAGE.get(lang, "en-US"),
        "sort_by": "vote_average.desc",
        "vote_count.gte": 20,
        "with_origin_country": DORAMA_COUNTRIES,
        "page": page,
    }
    genre_ids = _tv_genre_ids(genres, mood)
    if genre_ids:
        params["with_genres"] = "|".join(str(g) for g in genre_ids)
    if actor_id:
        params["with_cast"] = actor_id

    return _format_results(_tmdb_get("discover/tv", params), exclude_ids, "dorama")