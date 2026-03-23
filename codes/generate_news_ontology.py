import os
import sys
import json
import argparse
from typing import List, Optional

# Path adjustment to allow imports from MiroFish backend
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

from app.config import Config
from app.services.ontology_generator import OntologyGenerator
from app.services.live_news_fetcher import LiveDataFetcher

def generate_news_based_ontology(topic: str, output_path: str = None, fetch_news: bool = True):
    print(f"\n🔍 Topic: {topic}")
    
    news_text = ""
    if fetch_news:
        if not Config.NEWS_API_KEY:
            print("⚠️ Warning: NEWS_API_KEY not found in .env. Skipping news fetch.")
        else:
            print(f"📡 Fetching latest news for '{topic}'...")
            fetcher = LiveDataFetcher(api_key=Config.NEWS_API_KEY)
            try:
                # Fetch recent 48h news
                results = fetcher.fetch_recent_news(topic, hours=48, page_size=10)
                articles = results.get("articles", [])
                
                if not articles:
                    print("📭 No recent news found for this topic.")
                else:
                    print(f"✅ Found {len(articles)} articles.")
                    for i, art in enumerate(articles, 1):
                        title = art.get('title', 'N/A')
                        desc = art.get('description', 'N/A')
                        source = art.get('source', {}).get('name', 'N/A')
                        news_text += f"\n[Article {i}] {title}\nSource: {source}\nSummary: {desc}\n"
            except Exception as e:
                print(f"❌ Error fetching news: {e}")

    # Combine topic and news for the generator
    context_for_ontology = [f"Topic: {topic}\n\nRelated News context:\n{news_text}"]
    
    print(f"🧠 Generating MiroFish Ontology (Schema)...")
    generator = OntologyGenerator(language=Config.LANGUAGE)
    
    try:
        ontology = generator.generate(
            document_texts=context_for_ontology,
            simulation_requirement=f"Simulate a social media public opinion event about: {topic}"
        )
        
        # Save results
        if not output_path:
            safe_name = "".join([c if c.isalnum() else "_" for c in topic]).lower()
            output_path = os.path.join(os.path.dirname(__file__), f"ontology_{safe_name}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ontology, f, indent=4, ensure_ascii=False)
            
        print(f"\n✨ Ontology successfully generated and saved to:")
        print(f"👉 {output_path}")
        
        # Summary stats
        entities = ontology.get("entity_types", [])
        edges = ontology.get("edge_types", [])
        print(f"\n📊 Extraction Results:")
        print(f" - Entities: {len(entities)}")
        print(f" - Relationships: {len(edges)}")
        print(f" - Summary: {ontology.get('analysis_summary', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Ontology generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MiroFish News-to-Ontology Generator")
    parser.add_argument("--topic", required=True, help="Topic to search news for and define social entities")
    parser.add_argument("--output", help="Optional output filename")
    parser.add_argument("--no-news", action="store_true", help="Don't fetch live news; use topic only")
    
    args = parser.parse_args()
    
    generate_news_based_ontology(args.topic, args.output, not args.no_news)
