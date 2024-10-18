from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from utils.webdriver_utils import get_driver
from config import MILENIO_SEARCH_URL
import time
from selenium.webdriver.common.keys import Keys

class MilenioScraperV2:
    def __init__(self):
        self.driver =  get_driver()

    def run_scraper(self, search_terms, max_pages):
        self.open_milenio_search()
        
        for term in search_terms:
            if self.perform_search(term):
                # Here you can add code to scrape and process the search results
                print(f"Search completed for term: {term}")
                # For now, we'll just wait for user input after each search
                self.wait_for_user_input()
            else:
                print(f"Failed to search for term: {term}")
                self.wait_for_user_input()
        
        self.close_browser()
        print("Milenio search process complete.")

    def open_milenio_search(self):
        self.driver.get(MILENIO_SEARCH_URL)
        print(f"Opened {MILENIO_SEARCH_URL}")
        # Wait for 10 seconds to allow pop-ups to appear
        # time.sleep(10)
        
        # Try to handle the consent pop-up
        self.handle_consent_popup()

        # Try to handle the notifications pop-up
        self.handle_notifications_popup()


    def close_browser(self):
        self.driver.quit()

    def wait_for_user_input(self):
        input("Press Enter to close the browser...")

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
            print(f"Failed to handle notifications pop-up: {str(e)}")
            return False

    def perform_search(self, search_term):
        try:
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[title='search']"))
            )

            print(str(search_input))


            self.wait_for_user_input()

            search_input.clear()

            self.wait_for_user_input()

            search_input.send_keys(search_term)
            search_input.send_keys(Keys.RETURN)
            print(f"Performed search for: {search_term}")
            time.sleep(5)  # Wait for search results to load
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Failed to perform search: {str(e)}")
            return False


def main():
    scraper = MilenioScraperV2()
    scraper.open_milenio_search()
    scraper.wait_for_user_input()
    scraper.close_browser()

if __name__ == "__main__":
    main()
