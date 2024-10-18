from utils.menu import run_menu


def main():

    # List of search terms
    search_terms = ["IMSS"]
    
    # Maximum number of pages to scrape per search term
    max_pages = 2  # You can adjust this number
    
    all_articles = []

    run_menu(search_terms, max_pages)


    

if __name__ == "__main__":
    main()