
import json
import urllib.parse
import urllib.request
from typing import Any


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
   
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    request = urllib.request.Request(url, headers={"User-Agent": "WatchBot/1.0"})
    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))

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
    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))
