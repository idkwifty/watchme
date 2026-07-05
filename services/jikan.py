from html import unescape
from typing import Any

from config import JIKAN_BASE_URL
from services.http_utils import get_json

GENRE_NAMES = {
    "action": "Action",
    "comedy": "Comedy",
    "drama": "Drama",
    "horror": "Horror",
    "romance": "Romance",
    "scifi": "Sci-Fi",
    "thriller": "Thriller",
    "fantasy": "Fantasy",
    "animation": "Slice of Life",
    "mystery": "Mystery",
}

MOOD_GENRES = {
    "light": ["Comedy", "Slice of Life"],
    "sad": ["Drama", "Romance"],
    "intense": ["Action", "Thriller", "Horror"],
    "any": [],
}


def discover_anime(
    genres: list[str],
    mood: str,
    exclude_ids: list,
    page: int = 1,
) -> list[dict[str, Any]]:
    genre_list = [GENRE_NAMES[g] for g in genres if g in GENRE_NAMES]
    genre_list.extend(MOOD_GENRES.get(mood, []))
    genre_list = list(dict.fromkeys(genre_list))

    params: dict[str, Any] = {
        "order_by": "score",
        "sort": "desc",
        "page": page,
        "min_score": 7,
    }
    if genre_list:
        params["genres"] = ",".join(genre_list)

    try:
        data = get_json(f"{JIKAN_BASE_URL}/anime", params)
    except Exception:
        return []

    results = []
    for item in data.get("data", []):
        item_id = f"jikan_{item.get('mal_id')}"
        if item_id in exclude_ids:
            continue

        synopsis = item.get("synopsis") or ""
        synopsis = unescape(synopsis)
        if len(synopsis) > 300:
            synopsis = synopsis[:297] + "..."

        images = item.get("images", {}).get("jpg", {})
        score = item.get("score") or 0

        results.append({
            "id": item_id,
            "title": item.get("title_english") or item.get("title") or "?",
            "overview": synopsis,
            "rating": round(score, 1),
            "year": str(item.get("year") or ""),
            "poster_url": images.get("large_image_url") or images.get("image_url"),
            "media_type": "anime",
        })
        if len(results) >= 5:
            break
    return results