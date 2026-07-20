import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def _request_with_retry(
    request: urllib.request.Request,
    timeout: int = 8,
    retries: int = 3,
    delay: float = 1.5,
) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                pass
            print(
                f"[http_utils] HTTPError {e.code} on attempt {attempt}/{retries} "
                f"for {request.full_url}: {body[:300]}",
                flush=True,
            )
            last_error = e
            if e.code == 429:
                # Rate limited — wait longer before retrying
                wait = delay * attempt * 2
                if attempt < retries:
                    time.sleep(wait)
                    continue
            elif attempt < retries:
                time.sleep(delay)
                continue
            raise last_error
        except (urllib.error.URLError, TimeoutError) as e:
            print(
                f"[http_utils] {type(e).__name__} on attempt {attempt}/{retries} "
                f"for {request.full_url}: {e}",
                flush=True,
            )
            last_error = e
            if attempt < retries:
                time.sleep(delay)
                continue
            raise last_error


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "WatchBot/1.0",
            "Accept": "application/json",
        },
    )
    return _request_with_retry(request, timeout=8, retries=3, delay=1.5)


def post_json(url: str, body: dict[str, Any]) -> Any:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "WatchBot/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )
    return _request_with_retry(request, timeout=8, retries=3, delay=1.5)