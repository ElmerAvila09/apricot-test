from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import CHROME_DRIVER_PATH

def test_chrome_driver():
    print("Testing ChromeDriver...")
    
    try:
        # Set up the ChromeDriver service
        service = Service(CHROME_DRIVER_PATH)
        
        # Create a new Chrome driver instance
        driver = webdriver.Chrome(service=service)
        
        # Navigate to a website
        driver.get("https://www.python.org")
        
        # Wait for the title to be present (timeout after 10 seconds)
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.site-headline"))
        ).text
        
        # Print the title of the page
        print(f"Successfully loaded page. Title: {title}")
        
        # Close the browser
        driver.quit()
        
        print("ChromeDriver test completed successfully!")
        return True
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_chrome_driver()