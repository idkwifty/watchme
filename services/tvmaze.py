
import re
from html import unescape
from typing import Any
from urllib.parse import quote

from config import TVMAZE_BASE_URL
from services.http_utils import get_json

GENRE_NAMES = {
    "action": "Action",
    "comedy": "Comedy",
    "drama": "Drama",
    "horror": "Horror",
    "romance": "Romance",
    "scifi": "Science-Fiction",
    "thriller": "Thriller",
    "fantasy": "Fantasy",
    "animation": "Animation",
    "mystery": "Mystery",
}

MOOD_GENRES = {
    "light": ["Comedy", "Family"],
    "sad": ["Drama", "Romance"],
    "intense": ["Thriller", "Action", "Horror"],
    "any": [],
}

DORAMA_COUNTRIES = {"KR", "JP", "CN", "TW", "TH"}


def _get(path: str) -> Any:
    try:
        return get_json(f"{TVMAZE_BASE_URL}{path}")
    except Exception:
        return None


def _parse_show(show: dict, media_type: str = "series") -> dict[str, Any]:
    summary = show.get("summary") or ""
    summary = re.sub(r"<[^>]+>", "", summary)
    summary = unescape(summary)
    if len(summary) > 300:
        summary = summary[:297] + "..."

    image = show.get("image") or {}
    rating_obj = show.get("rating") or {}

    return {
        "id": f"tvmaze_{show.get('id')}",
        "title": show.get("name", "?"),
        "overview": summary,
        "rating": round(rating_obj.get("average") or 0, 1),
        "year": (show.get("premiered") or "")[:4],
        "poster_url": image.get("medium") or image.get("original"),
        "media_type": media_type,
    }


def _show_matches_genres(show: dict, genres: list[str], mood: str) -> bool:
    show_genres = set(show.get("genres") or [])
    wanted = {GENRE_NAMES[g] for g in genres if g in GENRE_NAMES}
    wanted |= set(MOOD_GENRES.get(mood, []))
    if not wanted:
        return True
    return bool(show_genres & wanted)


def _is_dorama(show: dict) -> bool:
    network = show.get("network") or show.get("webChannel") or {}
    country = (network.get("country") or {}).get("code", "")
    if country in DORAMA_COUNTRIES:
        return True
    name = (show.get("name") or "").lower()
    return any(w in name for w in ("korean", "kdrama", "dorama"))


def search_person(name: str) -> int | None:
    data = _get(f"/search/people?q={quote(name)}")
    if not data:
        return None
    for entry in data:
        person = entry.get("person", {})
        if person.get("id"):
            return person["id"]
    return None


def _shows_by_actor(
    person_id: int,
    genres: list[str],
    mood: str,
    exclude_ids: list,
    dorama_only: bool,
) -> list[dict[str, Any]]:
    credits = _get(f"/people/{person_id}/castcredits")
    if not credits:
        return []

    results = []
    for credit in credits:
        show = credit.get("_embedded", {}).get("show") or credit.get("show")
        if not show:
            continue
        show_id = f"tvmaze_{show.get('id')}"
        if show_id in exclude_ids:
            continue
        if dorama_only and not _is_dorama(show):
            continue
        if not dorama_only and _is_dorama(show):
            continue
        if not _show_matches_genres(show, genres, mood):
            continue
        media = "dorama" if _is_dorama(show) else "series"
        results.append(_parse_show(show, media))
        if len(results) >= 5:
            break
    return results


def discover_series(
    genres: list[str],
    mood: str,
    actor_name: str | None,
    actor_id: int | None,
    exclude_ids: list,
    page: int = 1,
) -> list[dict[str, Any]]:
    if actor_id:
        return _shows_by_actor(actor_id, genres, mood, exclude_ids, dorama_only=False)

    query = " ".join(GENRE_NAMES.get(g, g) for g in genres[:2]) or "drama"
    data = _get(f"/search/shows?q={quote(query)}")
    if not data:
        return []

    results = []
    for entry in data:
        show = entry.get("show", {})
        show_id = f"tvmaze_{show.get('id')}"
        if show_id in exclude_ids or _is_dorama(show):
            continue
        if not _show_matches_genres(show, genres, mood):
            continue
        results.append(_parse_show(show, "series"))
        if len(results) >= 5:
            break
    return results


def discover_dorama(
    genres: list[str],
    mood: str,
    actor_name: str | None,
    actor_id: int | None,
    exclude_ids: list,
    page: int = 1,
) -> list[dict[str, Any]]:
    if actor_id:
        shows = _shows_by_actor(actor_id, genres, mood, exclude_ids, dorama_only=True)
        if shows:
            return shows

    queries = ["korean drama", "japanese drama", "dorama"]
    query = queries[(page - 1) % len(queries)]
    if genres:
        query = f"{GENRE_NAMES.get(genres[0], 'drama')} {query}"

    data = _get(f"/search/shows?q={quote(query)}")
    if not data:
        return []

    results = []
    for entry in data:
        show = entry.get("show", {})
        show_id = f"tvmaze_{show.get('id')}"
        if show_id in exclude_ids or not _is_dorama(show):
            continue
        if not _show_matches_genres(show, genres, mood):
            continue
        results.append(_parse_show(show, "dorama"))
        if len(results) >= 5:
            break
    return results
