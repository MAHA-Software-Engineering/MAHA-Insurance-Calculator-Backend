import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

async def findCarMSRP(make, model):
    # Construct the URL based on the car make and model
    base_url = "https://www.edmunds.com"
    selected_url = f"{base_url}/{make}/{model}/"

    loop = asyncio.get_event_loop()
    msrp_info = await loop.run_in_executor(None, lambda: scrapeMSRP(selected_url))
    return msrp_info

def scrapeMSRP(selected_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36")
  
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(selected_url)
    
    time.sleep(5)  # Wait for the page to load completely

    # Adapt the selector based on the actual structure of the Edmunds website for the MSRP
    try:
        msrp_element = driver.find_element(By.CSS_SELECTOR, 'div[data-tracking-parent="msrp_range"] span.font-weight-bold')
        msrp = msrp_element.text
    except Exception as e:
        msrp = "MSRP not found"
        print(f"Error while scraping MSRP: {e}")

    driver.quit()
    return msrp

# Example usage:
make = "lamborghini"
model = "urus"
msrp_info = asyncio.run(findCarMSRP(make, model))
print(msrp_info)
