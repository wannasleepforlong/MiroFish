import requests
import json
from typing import List, Dict, Any, Optional
from ..utils.logger import get_logger

import time

logger = get_logger('mirofish.gdelt')

class GDELTFetcher:
    """
    Fetcher for GDELT news data.
    """
    
    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
    _cache = {} # {(countries_tuple): (timestamp, articles)}
    _CACHE_TTL = 60 # 60 seconds
    
    @classmethod
    def fetch_war_news(cls, countries: List[str], max_rows: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch war-related news for specific countries.
        """
        if not countries:
            return []
        
        # Simple cache check
        cache_key = tuple(sorted(countries))
        if cache_key in cls._cache:
            ts, data = cls._cache[cache_key]
            if time.time() - ts < cls._CACHE_TTL:
                logger.info(f"Returning cached news for {countries}")
                return data
            
        # Build query: war AND (Country1 OR Country2)
        countries_query = " OR ".join([f'"{c}"' for c in countries])
        if len(countries) > 1:
            query = f'war AND ({countries_query})'
        else:
            query = f'war AND {countries_query}'
        
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrows": max_rows
        }
        
        try:
            logger.info(f"Fetching GDELT news with query: {query}")
            response = requests.get(cls.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'json' not in content_type.lower():
                logger.warning(f"GDELT returned non-JSON response: {content_type}. Content: {response.text[:200]}...")
                return []

            try:
                data = response.json()
            except json.JSONDecodeError as jde:
                logger.error(f"GDELT JSON decode error: {str(jde)}. Content: {response.text[:200]}...")
                return []

            articles = data.get('articles', [])
            
            processed_articles = []
            for art in articles:
                processed_articles.append({
                    "title": art.get('title', 'No Title'),
                    "url": art.get('url', ''),
                    "source": art.get('domain', art.get('source', 'Unknown')),
                    "published_at": art.get('seendate', ''),
                    "description": art.get('title', 'No Description') # DOC API doesn't have description in artlist mode usually
                })
                
            logger.info(f"Successfully fetched {len(processed_articles)} articles from GDELT")
            # Update cache
            cls._cache[cache_key] = (time.time(), processed_articles)
            return processed_articles
            
        except Exception as e:
            logger.error(f"Failed to fetch news from GDELT: {str(e)}")
            return []

    @classmethod
    def fetch_live_ticker(cls, countries: List[str], count: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch latest news for a live ticker.
        """
        return cls.fetch_war_news(countries, max_rows=count)