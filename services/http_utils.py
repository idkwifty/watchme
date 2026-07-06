import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def _request_with_retry(request: urllib.request.Request, timeout: int = 20, retries: int = 3, delay: float = 1.5) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            last_error = e
            # На останній спробі не чекаємо, а одразу пробрасуємо помилку
            if attempt < retries:
                time.sleep(delay)
                continue
            raise last_error


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    request = urllib.request.Request(url, headers={"User-Agent": "WatchBot/1.0"})
    return _request_with_retry(request, timeout=20, retries=3, delay=1.5)


def post_json(url: str, body: dict[str, Any]) -> Any:
    
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "WatchBot/1.0",
        },
        method="POST",
    )
    return _request_with_retry(request, timeout=20, retries=3, delay=1.5)