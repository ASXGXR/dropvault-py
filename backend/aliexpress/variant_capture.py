import sys
import time
import pyautogui
from PIL import ImageOps
from pytesseract import image_to_data, Output
import pytoolsx as pt
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def get_ebay_image(ebay_url):
    """Opens a headless browser and retrieves image URL from eBay listing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(ebay_url)
    try:
        first_image = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ux-image-carousel-item.image-treatment.active.image img"))
        )
        image_url = first_image.get_attribute("data-zoom-src") or first_image.get_attribute("src")
    except Exception as e:
        print("Error retrieving image:", e)
        image_url = None
    driver.quit()
    return image_url

def variant_capture(ali_url):

    # Get comparison image from ebay
    # ebay_url = f"https://www.ebay.co.uk/itm/{order_info['item_id']}?var={order_info['variation_id']}"
    # ebay_image_url = get_ebay_image(ebay_url)
    # if ebay_image_url:
    #     print(f"Found ebay image URL: {ebay_image_url}")

    debug = True
    wait_time = 1.1  # Time between clicks
    d = 110  # Distance between variant boxes

    # Area to screenshot item image
    variant_area = (179, 325, 774, 920)

    def ocr(region, invert=False):
        """Performs OCR on a region, returns text as a string."""
        screenshot = pyautogui.screenshot().convert("RGB")
        if region:
            x1, y1, x2, y2 = region
            screenshot = screenshot.crop((x1, y1, x2, y2))
        if invert:
            screenshot = ImageOps.invert(screenshot)
        data = image_to_data(screenshot, output_type=Output.DICT)
        extracted_text = " ".join(data['text'][i].strip() for i in range(len(data['text'])) if data['text'][i].strip())
        if debug:
            print(f"OCR Result: {extracted_text}")
        return extracted_text

    def capture_variant(current_x, current_y, wait_time, vname_area, screenshot_index, prev_ocr):
        """Clicks, waits, captures OCR, saves screenshots if OCR is new, and returns OCR text."""
        pyautogui.click(current_x, current_y)
        if screenshot_index == 14:
            time.sleep(wait_time)
            pyautogui.click(current_x, current_y)
        time.sleep(wait_time)

        # Take OCR of name
        ocr_text = ocr(vname_area)

        # If OCR is new, save screenshots
        if ocr_text != prev_ocr:
            # Screenshot of whole variant area
            variant_screenshot = pyautogui.screenshot().crop(variant_area)
            variant_screenshot.save(f"{folder_dir}/variant-{screenshot_index}-image.png")
            # Screenshot of OCR area
            ocr_screenshot = pyautogui.screenshot().crop(vname_area)
            ocr_screenshot.save(f"{folder_dir}/variant-{screenshot_index}-ocr.png")
            print(f"Saved screenshots for variant-{screenshot_index} with OCR: {ocr_text}")
        return ocr_text
    
    # Make folder from aliexpress link
    item_id_match = re.search(r'/item/(\d+)\.html', ali_url)
    item_id = item_id_match.group(1) if item_id_match else "unknown_item"
    folder_dir = rf"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\variant_images\{item_id}"
    os.makedirs(folder_dir, exist_ok=True)  # Ensures folder exists

    # search web
    search_web_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\search-web.py"
    sys.argv = [search_web_file, ali_url]
    with open(search_web_file, "r") as script:
        exec(script.read(), globals())

    # Find "Color:" label on the page
    ali_ref = pt.findOnPage(["Color:", "Name:"], loop=True)
    v = [ali_ref[0] - 20, ali_ref[1] + 60]  # First variant position
    vnamex, vnamey = ali_ref
    vname_area = (vnamex - 50, vnamey - 25, vnamex + 300, vnamey + 25)

    start_x, start_y = v[0], v[1]
    current_y = start_y
    screenshot_index = 1
    found_variant = False

    ocr_results = []
    prev_extracted = ""

    while not found_variant:
        current_x = start_x
        extracted_info = capture_variant(current_x, current_y, wait_time, vname_area, screenshot_index, prev_extracted)
        ocr_results.append(extracted_info)
        prev_extracted = extracted_info

        # Scan horizontally
        while True:
            current_x += d
            extracted_info = capture_variant(current_x, current_y, wait_time, vname_area, screenshot_index, prev_extracted)
            if debug:
                print(f"OCR at ({current_x}, {current_y}): '{extracted_info}'")
            if extracted_info == prev_extracted:  # End horizontal scan if no change
                break
            ocr_results.append(extracted_info)
            prev_extracted = extracted_info
            screenshot_index += 1
            print(screenshot_index)

        # Move down one row
        current_y += d
        new_row_ocr = capture_variant(start_x, current_y, wait_time, vname_area, screenshot_index, prev_extracted)
        if new_row_ocr == prev_extracted:
            print("No new variants found in new row. Ending search.")
            break
        ocr_results.append(new_row_ocr)
        prev_extracted = new_row_ocr
        screenshot_index += 1

    if not found_variant:
        print("**ERROR** Variant not found via OCR")

    return ocr_results



variant_capture("https://www.aliexpress.com/item/1005007050993901.html?sourceType=1&spm=a2g0o.wish-manage-home.0.0",
                "MCLAREN")