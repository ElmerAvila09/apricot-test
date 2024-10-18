from scrapers.milenio_scraper import MilenioScraper
from scrapers.milenio_scraper_v2 import MilenioScraperV2

def display_menu():
    print("\nMilenio Scraper Menu:")
    print("1. Run original Milenio Scraper")
    print("2. Run Milenio Scraper V2 (Observation Mode)")
    print("3. Exit")
    return input("Enter your choice (1-3): ")

def run_menu(search_terms, max_pages):
    while True:
        choice = display_menu()
        if choice == '1':
            scraper = MilenioScraper()
            scraper.run_scraper(search_terms, max_pages)
        elif choice == '2':
            scraper = MilenioScraperV2()
            scraper.run_scraper(search_terms, max_pages)
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")