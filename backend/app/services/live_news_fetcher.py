import requests
from datetime import datetime, timedelta
from typing import Optional
from ..config import Config


class LiveDataFetcher:
    """
    A class for fetching live and historical news data using the NewsAPI.

    Attributes:
        api_key (str): Your NewsAPI key.
        base_url (str): Base URL for the NewsAPI.
    """

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str):
        """
        Initialize the LiveDataFetcher with your NewsAPI key.

        Args:
            api_key (str): Your NewsAPI key from https://newsapi.org
        """
        self.api_key = api_key

        self.session = requests.Session()
        self.session.params = {"apiKey": self.api_key}
        print("API KEY:", self.api_key)
    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get(self, endpoint: str, params: dict) -> dict:
        """
        Send a GET request to the given NewsAPI endpoint.
        Returns:
            dict: Parsed JSON response from the API.
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("status") != "ok":
            raise ValueError(f"NewsAPI error: {data.get('message', 'Unknown error')}")

        return data

    # ------------------------------------------------------------------ #
    #  Public methods                                                      #
    # ------------------------------------------------------------------ #

    def fetch_top_headlines(
        self,
        country: Optional[str] = None,
        category: Optional[str] = None,
        sources: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 20,
        page: int = 1,
    ) -> dict:
        """
        Fetch the latest top headlines.

        Args:
            country (str, optional): 2-letter ISO 3166-1 country code
                (e.g. 'us', 'gb', 'in'). Cannot be combined with `sources`.
            category (str, optional): Category of news. One of:
                business, entertainment, general, health, science, sports, technology.
                Cannot be combined with `sources`.
            sources (str, optional): Comma-separated list of source identifiers
                (e.g. 'bbc-news,cnn'). Cannot be combined with `country`/`category`.
            query (str, optional): Keywords to search for in headlines.
            page_size (int): Number of results per page (max 100). Default 20.
            page (int): Page number for paginated results. Default 1.

        Returns:
            dict: {
                "status": "ok",
                "totalResults": int,
                "articles": list[dict]
            }

        Example:
            fetcher.fetch_top_headlines(country="us", category="technology")
        """
        params = {"pageSize": page_size, "page": page}

        if sources:
            params["sources"] = sources
        else:
            if country:
                params["country"] = country
            if category:
                params["category"] = category

        if query:
            params["q"] = query

        return self._get("/top-headlines", params)

    def fetch_everything(
        self,
        query: Optional[str] = None,
        sources: Optional[str] = None,
        domains: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20,
        page: int = 1,
    ) -> dict:
        """
        Search every article published by over 80,000 sources.

        Args:
            query (str, optional): Keywords or phrases to search for.
                Supports advanced search: exact phrases (""), AND/OR/NOT.
            sources (str, optional): Comma-separated list of source identifiers.
            domains (str, optional): Comma-separated list of domains to restrict
                results (e.g. 'bbc.co.uk,techcrunch.com').
            from_date (str, optional): Oldest article date in ISO 8601 format
                (e.g. '2026-03-01' or '2026-03-01T00:00:00').
            to_date (str, optional): Newest article date in ISO 8601 format.
            language (str): 2-letter ISO 639-1 language code. Default 'en'.
            sort_by (str): Sort order. One of: relevancy, popularity, publishedAt.
                Default 'publishedAt'.
            page_size (int): Number of results per page (max 100). Default 20.
            page (int): Page number for paginated results. Default 1.

        Returns:
            dict: {
                "status": "ok",
                "totalResults": int,
                "articles": list[dict]
            }

        Example:
            fetcher.fetch_everything(query="Apple M5", sort_by="popularity")
        """
        params = {
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page,
        }

        if query:
            params["q"] = query
        if sources:
            params["sources"] = sources
        if domains:
            params["domains"] = domains
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        return self._get("/everything", params)

    def fetch_sources(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        country: Optional[str] = None,
    ) -> dict:
        """
        Fetch the subset of news publishers that top-headlines supports.

        Args:
            category (str, optional): Category to filter sources by. One of:
                business, entertainment, general, health, science, sports, technology.
            language (str, optional): 2-letter ISO 639-1 language code (e.g. 'en').
            country (str, optional): 2-letter ISO 3166-1 country code (e.g. 'us').

        Returns:
            dict: {
                "status": "ok",
                "sources": list[dict]   # each dict has id, name, description, url, etc.
            }

        Example:
            fetcher.fetch_sources(category="technology", country="us")
        """
        params = {}
        if category:
            params["category"] = category
        if language:
            params["language"] = language
        if country:
            params["country"] = country

        return self._get("/top-headlines/sources", params)

    def fetch_recent_news(
        self,
        query: str,
        hours: int = 24,
        sort_by: str = "publishedAt",
        page_size: int = 20,
    ) -> dict:
        """
        Convenience method: fetch articles from the last N hours.

        Args:
            query (str): Keywords to search for.
            hours (int): How many hours back to look. Default 24.
            sort_by (str): Sort order (relevancy, popularity, publishedAt).
            page_size (int): Number of results to return (max 100).

        Returns:
            dict: Same structure as fetch_everything().

        Example:
            fetcher.fetch_recent_news("AI chips", hours=6)
        """
        from_date = (datetime.utcnow() - timedelta(hours=hours)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        return self.fetch_everything(
            query=query,
            from_date=from_date,
            sort_by=sort_by,
            page_size=page_size,
        )

    def fetch_by_source(self, source_id: str, page_size: int = 20) -> dict:
        """
        Convenience method: fetch top headlines from a specific source.

        Args:
            source_id (str): The source identifier (e.g. 'bbc-news', 'cnn').
                Use fetch_sources() to discover valid IDs.
            page_size (int): Number of results to return (max 100).

        Returns:
            dict: Same structure as fetch_top_headlines().

        Example:
            fetcher.fetch_by_source("bbc-news")
        """
        return self.fetch_top_headlines(sources=source_id, page_size=page_size)



if __name__ == "__main__":
    fetcher = LiveDataFetcher(api_key=Config.NEWS_API_KEY)

    # 1. Top US headlines
    print("=== Top US Headlines ===")
    result = fetcher.fetch_top_headlines(country="us", page_size=1)
    for article in result["articles"]:
        print(f"  [{article['source']['name']}] {article['title']}")

    print()

    # 2. Search everything about Apple
    print("=== Everything: Apple ===")
    result = fetcher.fetch_everything(query="Apple", sort_by="popularity", page_size=1)
    for article in result["articles"]:
        print(f"  [{article['publishedAt'][:10]}] {article['title']}")

    print()

    # 3. Recent news from the last 12 hours
    print("=== Recent News (last 12h): AI ===")
    result = fetcher.fetch_recent_news("artificial intelligence", hours=12, page_size=1)
    for article in result["articles"]:
        print(f"  {article['title']}")

    print()

    # 4. Headlines from BBC News
    print("=== BBC News Headlines ===")
    result = fetcher.fetch_by_source("bbc-news", page_size=1)
    for article in result["articles"]:
        print(f"  {article['title']}")

    print()

    # 5. Available technology sources in the US
    print("=== US Tech Sources ===")
    result = fetcher.fetch_sources(category="technology", country="us")
    for source in result["sources"][:5]:
        print(f"  {source['id']:30s} — {source['name']}")