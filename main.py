import os
import json
import csv
from scrapers.milenio_scraper import MilenioScraper
from utils.file_utils import save_to_csv
from config import DATA_DIR, OUTPUT_CSV

def main():
    # Initialize the MilenioScraper
    milenio_scraper = MilenioScraper()
    
    # List of search terms
    search_terms = ["IMSS"]
    
    # Maximum number of pages to scrape per search term
    max_pages = 2  # You can adjust this number
    
    all_articles = []
    
    # Iterate through each search term
    for term in search_terms:
        # Scrape articles for the current term, limiting to max_pages
        articles = milenio_scraper.search_and_scrape(term, max_pages=max_pages)
        all_articles.extend(articles)
        
        # Save each article as a JSON file
        for i, article in enumerate(articles):
            filename = f"{term.lower()}_{i+1}.json"
            filepath = os.path.join(DATA_DIR, "articles", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article, f, ensure_ascii=False, indent=4)
    
    # Save all articles to CSV
    save_to_csv(all_articles, OUTPUT_CSV)
    
    print(f"Scraped {len(all_articles)} articles. Data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()