from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config import CHROME_DRIVER_PATH

def get_driver():
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    return webdriver.Chrome(service=service, options=options)