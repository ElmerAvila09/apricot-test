import os

# Configuration settings
CHROME_DRIVER_PATH = "chromedriver.exe"
MILENIO_SEARCH_URL = "https://www.milenio.com/buscador"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "output.csv")