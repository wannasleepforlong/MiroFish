from flask import request, jsonify
from . import news_bp
from ..services.gdel import GDELTFetcher
from ..utils.logger import get_logger

logger = get_logger('mirofish.api.news')

@news_bp.route('/live', methods=['GET'])
def get_live_news():
    """
    Fetch live news for requested countries.
    Usage: /api/news/live?countries=Ukraine,Russia
    """
    countries_str = request.args.get('countries', '')
    if not countries_str:
        return jsonify({
            "success": False,
            "error": "No countries provided"
        }), 400
        
    countries = [c.strip() for c in countries_str.split(',') if c.strip()]
    
    try:
        articles = GDELTFetcher.fetch_live_ticker(countries, count=15)
        return jsonify({
            "success": True,
            "data": articles
        })
    except Exception as e:
        logger.error(f"Error fetching live news: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
