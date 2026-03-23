import requests
import json
import time
from typing import List, Dict, Any

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
_cache = {}
_CACHE_TTL = 300

def build_query(countries: List[str]) -> str:
    """Build a valid GDELT query string."""
    if len(countries) == 1:
        return f"war {countries[0]}"
    else:
        countries_part = " OR ".join(countries)
        return f"war ({countries_part})"

def fetch_war_news(countries: List[str], max_rows: int = 10) -> List[Dict[str, Any]]:
    if not countries:
        return []

    cache_key = tuple(sorted(countries))
    if cache_key in _cache:
        ts, data = _cache[cache_key]
        if time.time() - ts < _CACHE_TTL:
            print(f"[CACHE HIT] Returning cached news for {countries}")
            return data

    query = build_query(countries)
    print(f"[GDELT] Query: {query}")

    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrows": min(max_rows, 10),
        "timespan": "7d",
        "sort": "social",        # rank by social media popularity
        # "sourcelang": "english", # english only
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; research/1.0)"
    }

    for attempt in range(3):
        try:
            if attempt > 0:
                wait = 2 ** attempt
                print(f"[RETRY] Attempt {attempt + 1}, waiting {wait}s...")
                time.sleep(wait)
            else:
                time.sleep(1)  # Always wait 1s before first request

            response = requests.get(BASE_URL, params=params, headers=headers, timeout=20)

            # response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "json" not in content_type.lower():
                # Print full error message from GDELT (it's always short)
                print(f"[GDELT ERROR] {response.text.strip()}")
                return []

            data = response.json()
            articles = data.get("articles", [])

            processed = [
                {
                    "title":        art.get("title", "No Title"),
                    "url":          art.get("url", ""),
                    "source":       art.get("domain", art.get("source", "Unknown")),
                    "published_at": art.get("seendate", ""),
                    "description":  art.get("title", ""),
                }
                for art in articles
            ]

            print(f"[GDELT] Fetched {len(processed)} articles.")
            _cache[cache_key] = (time.time(), processed)
            return processed

        except requests.HTTPError as e:
            print(f"[HTTP ERROR] {e}")
        except json.JSONDecodeError as e:
            print(f"[JSON ERROR] {e} — raw: {response.text[:200]}")
        except requests.RequestException as e:
            print(f"[REQUEST ERROR] {e}")

    print("[FAILED] All retries exhausted.")
    return []


if __name__ == "__main__":
    countries = ["Iran", "USA"]

    print("Fetching news...")
    articles = fetch_war_news(countries, max_rows=10)

    if not articles:
        print("No articles returned.")
    else:
        for i, a in enumerate(articles, 1):
            print(f"\n[{i}] {a['title']}")
            print(f"    Source : {a['source']}")
            print(f"    Date   : {a['published_at']}")
            print(f"    URL    : {a['url']}")