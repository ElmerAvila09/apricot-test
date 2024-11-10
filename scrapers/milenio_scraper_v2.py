from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from utils.webdriver_utils import get_driver
from config import MILENIO_SEARCH_URL
import time
import json
import os
from datetime import datetime
import re
class MilenioScraperV2:


    def __init__(self):
        self.driver = get_driver()
        self.actions = ActionChains(self.driver)

    def get_article_urls(self):
        """Get all article URLs from the search results page"""
        article_urls = []
        try:
            # Wait for articles to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "lr-list-row-row-news"))
            )
            
            # Find all article links
            articles = self.driver.find_elements(By.CSS_SELECTOR, ".lr-list-row-row-news__title a")
            for article in articles:
                try:
                    url = article.get_attribute('href')
                    if url:
                        article_urls.append(url)
                except Exception as e:
                    print(f"Error getting URL: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error finding articles: {str(e)}")
            
        return article_urls

    def extract_article_content(self, url):
        """Extract all available content from an article URL"""
        try:
            print(f"\nProcessing article: {url}")
            self.driver.get(url)
            time.sleep(2)
            
            # Handle popups if needed
            #self.handle_consent_popup()
            #self.handle_notifications_popup()
            
            # Get article data from schema
            page_source = self.driver.page_source
            schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page_source, re.DOTALL)
            
            if schema_match:
                schema_data = json.loads(schema_match.group(1))
                
                article_data = {
                    "url": url,
                    "extracted_at": datetime.now().isoformat(),
                    "title": schema_data.get('headline', ''),
                    "abstract": schema_data.get('description', ''),
                    "content": schema_data.get('articleBody', ''),
                    "author": schema_data.get('author', [{}])[0].get('name', ''),
                    "date_published": schema_data.get('datePublished', ''),
                    "date_modified": schema_data.get('dateModified', ''),
                    "keywords": schema_data.get('keywords', ''),
                    "location": schema_data.get('contentLocation', ''),
                }
                
                # Try to get image data if available
                if 'image' in schema_data:
                    article_data['image_url'] = schema_data['image'].get('url', '')
                    
                return article_data
                
        except Exception as e:
            print(f"Error processing article {url}: {str(e)}")
        
        return None

    def run_scraper(self, search_terms, max_pages=1):
        self.open_milenio_search()
        
        for term in search_terms:
            all_articles = []
            
            if self.perform_search(term):
                print(f"\nSearch completed for term: {term}")
                time.sleep(3)  # Wait for results to load
                
                # Get all article URLs from search results
                article_urls = self.get_article_urls()
                print(f"Found {len(article_urls)} articles")
                
                # Process each URL
                for url in article_urls:
                    article_data = self.extract_article_content(url)
                    if article_data:
                        all_articles.append(article_data)
                    time.sleep(1)  # Small delay between articles
                
                # Save articles
                if all_articles:
                    self.save_articles(all_articles, term)
                    print(f"Extracted and saved {len(all_articles)} articles for search term: {term}")
                
                self.wait_for_user_input()
            else:
                print(f"Failed to search for term: {term}")
                self.wait_for_user_input()
        
        self.close_browser()
        print("Milenio search process complete.")

    def save_articles(self, articles, search_term, output_dir="data"):
        """Save articles to JSON files"""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create search term specific directory
        search_dir = os.path.join(output_dir, search_term)
        os.makedirs(search_dir, exist_ok=True)
        
        for i, article in enumerate(articles, 1):
            try:
                # Create filename using timestamp if available
                if article.get("date_published"):
                    date_part = article["date_published"].split('T')[0].replace('-', '')
                    filename = f"article_{date_part}_{i}.json"
                else:
                    filename = f"article_{i}.json"
                    
                filepath = os.path.join(search_dir, filename)
                
                # Save article to JSON file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(article, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                print(f"Error saving article {i}: {str(e)}")
                continue








    def open_milenio_search(self):
        self.driver.get(MILENIO_SEARCH_URL)
        print(f"Opened {MILENIO_SEARCH_URL}")
        # Wait for 10 seconds to allow pop-ups to appear
        # Wait for initial page load
        time.sleep(5)
        
        # Move mouse to trigger consent popup
        #self.trigger_consent_popup()
        
        # Try to handle the consent pop-up
        self.handle_consent_popup()

        # Try to handle the notifications pop-up
        self.handle_notifications_popup()

    def close_browser(self):
        self.driver.quit()

    def wait_for_user_input(self):
        input("Press Enter to continue...")

    def handle_consent_popup(self):
        methods = [
            self.click_no_consent_button,
            self.click_no_consent_button_by_class,
            self.click_no_consent_button_by_javascript
        ]
        
        for method in methods:
            if method():
                print("Consent pop-up handled successfully.")
                return
        
        print("Failed to handle consent pop-up using all available methods.")

    def click_no_consent_button(self):
        try:
            no_consent_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'No consentir')]"))
            )
            no_consent_button.click()
            return True
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            print("Could not find or click 'No consentir' button by text.")
            return False

    def click_no_consent_button_by_class(self):
        try:
            no_consent_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".fc-cta-do-not-consent"))
            )
            no_consent_button.click()
            return True
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            print("Could not find or click 'No consentir' button by class.")
            return False

    def click_no_consent_button_by_javascript(self):
        try:
            self.driver.execute_script("""
                var buttons = document.getElementsByTagName('button');
                for(var i = 0; i < buttons.length; i++) {
                    if(buttons[i].textContent.includes('No consentir')) {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            """)
            return True
        except Exception as e:
            print(f"Error clicking 'No consentir' button by JavaScript: {str(e)}")
            return False

    def handle_notifications_popup(self):
        try:
            no_thanks_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btnSecondary') and contains(text(), 'No, gracias')]"))
            )
            no_thanks_button.click()
            print("Notifications pop-up handled successfully.")
            return True
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            print("Error handling pop-up trying to find NO, gracias button.")
            #print(f"Failed to handle notifications pop-up: {str(e)}")
            return False

    def perform_search(self, search_term):
        try:
            print("\n=== Starting search process ===")
            
            # Find all search inputs
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name='text']")
            
            # Find the visible one
            search_input = None
            for input_elem in search_inputs:
                if input_elem.is_displayed():
                    search_input = input_elem
                    print("Found visible search input")
                    break
            
            if not search_input:
                print("No visible search input found")
                return False
                
            # Verify we found the right one
            print(f"\nSelected input details:")
            print(f"Is displayed: {search_input.is_displayed()}")
            print(f"Location: {search_input.location}")
            print(f"Size: {search_input.size}")
            
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
            time.sleep(1)
            
            # Move to and click the element
            self.actions.move_to_element(search_input).perform()
            time.sleep(1)
            
            # Click and interact
            search_input.click()
            time.sleep(1)
            
            # Clear and enter search term
            self.driver.execute_script("arguments[0].value = '';", search_input)
            search_input.send_keys(search_term)
            time.sleep(1)
            
            # Try multiple submit approaches
            try:
                # First try Enter key
                search_input.send_keys(Keys.RETURN)
                time.sleep(2)
                
                # If that didn't work, try finding and clicking a search button
                if "buscador?" not in self.driver.current_url:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    search_button.click()
                    
                time.sleep(3)
                print(f"Current URL after search: {self.driver.current_url}")
                return True
                
            except Exception as e:
                print(f"Error during search submission: {str(e)}")
                return False
                
        except Exception as e:
            print(f"\nFailed to perform search: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            return False

    def trigger_consent_popup(self):
        print("Triggering consent popup with mouse movement...")
        
        # Get viewport size
        viewport_height = self.driver.execute_script("return window.innerHeight")
        viewport_width = self.driver.execute_script("return window.innerWidth")
        
        # Move mouse in a pattern across the page
        try:
            # Move to center
            self.actions.move_by_offset(viewport_width//2, viewport_height//2).perform()
            time.sleep(1)
            
            # Move to top left
            self.actions.move_by_offset(-viewport_width//4, -viewport_height//4).perform()
            time.sleep(1)
            
            # Move to bottom right
            self.actions.move_by_offset(viewport_width//2, viewport_height//2).perform()
            time.sleep(1)
            
            print("Mouse movement completed")
            
        except Exception as e:
            print(f"Error during mouse movement: {str(e)}")
        
        # Reset mouse position
        self.actions.move_to_element(self.driver.find_element(By.TAG_NAME, "body")).perform()
        
        # Wait for popup to appear
        time.sleep(3)

def main():
    scraper = MilenioScraperV2()
    scraper.open_milenio_search()
    scraper.wait_for_user_input()
    scraper.close_browser()

if __name__ == "__main__":
    main()
