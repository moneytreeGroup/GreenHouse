from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

url = 'https://www.houseplantresource.com/?v=1923594eeec381139a09000cf8ab6186'

# Set up headless Firefox
firefox_options = Options()
firefox_options.add_argument('--headless')

try:
    driver = webdriver.Firefox(options=firefox_options)
    print("Using Firefox driver")
    
    driver.get(url)
    
    # Wait for JavaScript to render
    time.sleep(5)
    
    print("Successfully loaded the page!")
    print("Page title:", driver.title)
    print("Page URL:", driver.current_url)
    print("\n--- PAGE SOURCE ---")
    print(driver.page_source[:2000])  # Print first 2000 characters
    print("...")
    
    driver.quit()
    
except Exception as e:
    print(f"Firefox failed: {e}")
    print("Make sure Firefox and geckodriver are installed")
