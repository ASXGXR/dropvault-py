from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def get_ebay_image(ebay_url):
    """Opens a headless Chrome browser to retrieve the main image URL from an eBay listing."""
    # Setup headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--log-level=3")  # Suppress console warnings
    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(ebay_url)
    try:
        # Wait for image element to load
        first_image = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ux-image-carousel-item.image-treatment.active.image img")
            )
        )
        # Extract image URL from attribute
        image_url = first_image.get_attribute("data-zoom-src") or first_image.get_attribute("src")
    except Exception as e:
        print("Error retrieving image:", e)
        image_url = None  # Return None on failure
    finally:
        driver.quit()  # Close browser
    return image_url