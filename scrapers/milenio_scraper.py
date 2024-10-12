import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from utils.webdriver_utils import get_driver
from config import MILENIO_SEARCH_URL
import time

class MilenioScraper:
    def __init__(self):
        self.driver = get_driver()

    def handle_consent_modal(self):
        try:
            no_consent_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'No consentir')]"))
            )
            no_consent_button.click()
            logging.info("Consent modal handled.")
        except TimeoutException:
            logging.info("Consent modal not found or already handled.")

    def handle_notification_prompt(self):
        try:
            no_thanks_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'No, gracias')]"))
            )
            try:
                no_thanks_button.click()
            except ElementClickInterceptedException:
                logging.info("Click intercepted, trying JavaScript click.")
                self.driver.execute_script("arguments[0].click();", no_thanks_button)
            logging.info("Notification prompt handled.")
        except TimeoutException:
            logging.info("Notification prompt not found or already handled.")
        except Exception as e:
            logging.error(f"Error handling notification prompt: {str(e)}")

    def close_overlays(self):
        overlays = self.driver.find_elements(By.CSS_SELECTOR, ".modal, .overlay, .dialog")
        for overlay in overlays:
            try:
                self.driver.execute_script("arguments[0].style.display='none';", overlay)
            except Exception as e:
                logging.error(f"Error closing overlay: {str(e)}")

    def handle_keep_reading_popup(self):
        try:
            close_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'close') or contains(@class, 'cerrar')]"))
            )
            close_button.click()
            logging.info("Keep reading popup handled.")
        except TimeoutException:
            logging.info("Keep reading popup not found or already handled.")

    def search_and_scrape(self, query, max_pages=3):
        self.driver.get(MILENIO_SEARCH_URL)
        logging.info(f"Navigated to {MILENIO_SEARCH_URL}")

        time.sleep(5)
        
        # Handle potential interruptions
        self.handle_consent_modal()
        self.handle_notification_prompt()
        self.close_overlays()
        self.handle_keep_reading_popup()

        try:
            # Wait for the search input to be clickable
            search_input = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='text']"))
            )
            logging.info("Search input found")
            
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
            logging.info("Scrolled to search input")
            
            # Wait a bit for any animations to complete
            time.sleep(2)
            
            # Try to click the element first
            self.driver.execute_script("arguments[0].click();", search_input)
            logging.info("Clicked on search input")
            
            # Now send the keys
            search_input.send_keys(query)
            logging.info(f"Entered search query: {query}")
            search_input.submit()
            logging.info("Submitted search query")

        except Exception as e:
            logging.error(f"An error occurred while trying to search: {str(e)}")
            self.driver.quit()
            return []

        # Wait for results to load
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".lr-list-row-row-news__title"))
            )
        except Exception as e:
            logging.error(f"No results found or page didn't load properly: {str(e)}")
            self.driver.quit()
            return []

        articles = []
        page = 1
        while page <= max_pages:
            logging.info(f"Scraping page {page} for query: {query}")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            for article in soup.select(".lr-list-row-row-news__title"):
                title = article.text.strip()
                link = article.get('href')
                date, content = self.scrape_article(link)
                articles.append({
                    "title": title,
                    "date": date,
                    "content": content,
                    "link": link
                })

            # Check if there's a next page
            next_page = soup.select_one('.board-module__a[rel="next"]')
            if not next_page:
                break

            # Go to next page
            page += 1
            if page > max_pages:
                break
            self.driver.get(f"{MILENIO_SEARCH_URL}?page={page}&text={query}")
            time.sleep(2)  # Wait for page to load

        self.driver.quit()
        return articles

    def scrape_article(self, url):
        self.driver.get(url)
        
        # Handle potential interruptions on article page
        self.handle_consent_modal()
        self.handle_notification_prompt()
        self.close_overlays()
        self.handle_keep_reading_popup()

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".nd-content-body"))
            )
        except Exception as e:
            logging.error(f"Error loading article {url}: {str(e)}")
            return "", ""
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        date = soup.select_one('.content-date')
        date = date.text.strip() if date else "Date not found"
        
        content_paragraphs = soup.select('.nd-content-body p')
        content = ' '.join([p.text.strip() for p in content_paragraphs]) if content_paragraphs else "Content not found"
        
        return date, content
