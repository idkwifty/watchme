from html import unescape
from typing import Any

from services.http_utils import post_json

ANILIST_URL = "https://graphql.anilist.co"

# AniList genre names are used directly in the API — no ID mapping needed.
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

_QUERY = """
query ($page: Int, $perPage: Int, $genres: [String], $sort: [MediaSort]) {
  Page(page: $page, perPage: $perPage) {
    media(
      type: ANIME
      genre_in: $genres
      sort: $sort
      averageScore_greater: 69
      isAdult: false
    ) {
      id
      title {
        english
        romaji
      }
      description(asHtml: false)
      averageScore
      seasonYear
      coverImage {
        large
      }
    }
  }
}
"""


def discover_anime(
    genres: list[str],
    mood: str,
    exclude_ids: list,
    page: int = 1,
    sort_by: str = "rating",
) -> list[dict[str, Any]]:
    genre_list = [GENRE_NAMES[g] for g in genres if g in GENRE_NAMES]
    genre_list.extend(MOOD_GENRES.get(mood, []))
    genre_list = list(dict.fromkeys(genre_list))

    anilist_sort = ["START_DATE_DESC"] if sort_by == "year" else ["SCORE_DESC"]

    variables: dict[str, Any] = {
        "page": page,
        "perPage": 15,
        "sort": anilist_sort,
    }
    if genre_list:
        variables["genres"] = genre_list

    try:
        data = post_json(ANILIST_URL, {"query": _QUERY, "variables": variables})
    except Exception:
        import traceback
        traceback.print_exc()
        return []

    if "errors" in data:
        print(f"[anilist] GraphQL errors: {data['errors']}", flush=True)
        return []

    media_list = data.get("data", {}).get("Page", {}).get("media", []) or []

    results = []
    for item in media_list:
        item_id = f"anilist_{item.get('id')}"
        if item_id in exclude_ids:
            continue

        synopsis = item.get("description") or ""
        synopsis = unescape(synopsis)
        # AniList sometimes leaves <br> tags even with asHtml:false — strip stray markup.
        synopsis = synopsis.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
        if len(synopsis) > 300:
            synopsis = synopsis[:297] + "..."

        score = item.get("averageScore") or 0
        rating = round(score / 10, 1)  # AniList is 0-100, keep the app's existing 0-10 scale

        title = item.get("title") or {}

        results.append({
            "id": item_id,
            "title": title.get("english") or title.get("romaji") or "?",
            "overview": synopsis,
            "rating": rating,
            "year": str(item.get("seasonYear") or ""),
            "poster_url": (item.get("coverImage") or {}).get("large"),
            "media_type": "anime",
        })
        if len(results) >= 5:
            break
    return results