import sys
import json
import time
import pyautogui
import pytoolsx as pt
import pycountry
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from select_ali_variant import select_variant

wait_time = 1

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

ship_product = True
ctrl_key = "ctrl"

# Check for order JSON
if len(sys.argv) < 2:
    sys.exit("Usage: python ali-order.py <order_json>")
try:
    order_info = json.loads(sys.argv[1])
except json.JSONDecodeError:
    sys.exit("Invalid JSON provided.")

# Extract quantity and order ID
quantity = int(order_info.get("quantity", 1))
order_id = order_info.get("order_id")
item_id = order_info.get("item_id")
item_title = order_info.get("item_title")
if order_id and item_title:
    print(f"\n------\n*NEW ORDER*")
    print(f"Order ID: {order_id}")
    print(f"Item: {item_title}")
else:
    sys.exit("Order ID not found in order data.")

# Extract total price from order_info
pricing_summary = order_info.get("pricingSummary", {})
total_price = float(pricing_summary.get("total", {}).get("value", 0))

# Check if order already sent
shipped_orders_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipped_orders.json"
try:
    with open(shipped_orders_path, "r", encoding="utf-8") as f:
        shipped_orders = json.load(f)
        unique_item_id = f"{order_id}_{order_info.get('item_id', '')}"
        if any(order.get("unique_item_id") == unique_item_id for order in shipped_orders):
            print(f"Order item {unique_item_id} has already been shipped. Skipping...")
            ship_product = False
except json.JSONDecodeError:
    print("Error reading shipped_orders.json.")
    ship_product = False

######################
##  Begin Purchase  ##
######################

# Use order_info as shipping_info for the address details.
shipping_info = order_info

while ship_product == True:

    # Find Aliexpress URL
    listing_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json"
    try:
        with open(listing_file, "r", encoding="utf-8") as file:
            listings = json.load(file)
            product_url = next((l.get("aliexpress_url") for l in listings if l["item_id"] == item_id), None)
    except (FileNotFoundError, json.JSONDecodeError):
        product_url = None
    if not product_url:
        print("ERROR: ** Aliexpress URL not linked for this item**")
        ship_product = False
        break
    # input URL
    search_web_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\search-web.py"
    sys.argv = [search_web_file, product_url]
    with open(search_web_file, "r") as script:
        exec(script.read(), globals())

    # Variation Checker
    if order_info.get("variation_aspects"):
        # Extract variation
        variation_value = order_info["variation_aspects"][0]["value"]
        print(f"Variation: {variation_value}")
        # Get comparison image from ebay
        ebay_url = f"https://www.ebay.co.uk/itm/{order_info['item_id']}?var={order_info['variation_id']}"
        ebay_image_url = get_ebay_image(ebay_url)
        if ebay_image_url:
            print(f"Found ebay image URL: {ebay_image_url}")
        # Find variation on AliExpress
        if select_variant(variation_value) == False:
            ship_product = False
            break

    # Find 'Buy Now'
    location = None
    while location is None:
        try:
            location = pyautogui.locateOnScreen(
                r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\buy_now_ref.png", 
                confidence=0.8
            )
        except Exception:
            time.sleep(wait_time)
    x, y = pyautogui.center(location)
    pyautogui.click(x, y)
    print(f"Clicked 'Buy now' at: ({x}, {y})")
    time.sleep(wait_time*3)

    # Change Address
    pyautogui.press("tab", presses=2)
    pyautogui.press("enter")
    time.sleep(wait_time)

    ## INPUT CUSTOMER ADDRESS

    if pt.checkScreen("default"):  # Check if on shipping screen
        pyautogui.press("tab", presses=3)
        pyautogui.press("enter")
        time.sleep(wait_time)

        if pt.checkScreen("Edit shipping"):

            # Country
            pyautogui.press("tab")
            pyautogui.press("enter")
            try:
                country = pycountry.countries.get(alpha_2=shipping_info["country"]).name
            except Exception:
                print("Couldn't get country name from alpha_2 code.")
                ship_product = False
                break
            pyautogui.write(country)
            pyautogui.press("enter")
            time.sleep(wait_time)
            pyautogui.press("tab")

            # Split full name into first and last names
            first_name, last_name = shipping_info["full_name"].split(" ", 1)
            pyautogui.write(first_name)
            pyautogui.press("tab")
            pyautogui.write(last_name)
            pyautogui.press("tab", presses=2)

            # Phone number
            pyautogui.write(shipping_info["phone"])
            pyautogui.press("tab")

            # Address: Postcode, then Address line 1 and line 2
            pyautogui.write(shipping_info["postal_code"])
            time.sleep(wait_time)
            pyautogui.press("enter")
            time.sleep(wait_time*2)
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line1"])
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line2"])

            # Click confirm
            pyautogui.press("tab", presses=5)
            pyautogui.press("enter")
            time.sleep(wait_time)

            # Refresh page to update address
            pt.hotkey(ctrl_key, "r")
            time.sleep(wait_time*5)
            print("Address updated!")

        else:
            print("ERROR: Edit Shipping Screen not present.")
            ship_product = False
            break
    else:
        print("ERROR: Shipping Address List not shown.")
        ship_product = False
        break

    # Handle Quantity
    pyautogui.press("tab", presses=4, interval=0.3)
    if quantity != 1:
        pyautogui.write(str(quantity))
        pyautogui.press("tab")
        time.sleep(wait_time*5)  # Wait for price to update
        pyautogui.press("tab")
    else:
        pyautogui.press("tab")

    # Capture screenshot for confirmation
    screenshot = pyautogui.screenshot()
    screenshot.save(rf"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipping_screenshots\shipping_details_{str(order_id)}.png")
    print(f"Screenshot saved to shipping_details_{str(order_id)}.png.")

    # Confirm purchase
    # pyautogui.press("enter")
    print("\nItem successfully shipped! ")
    time.sleep(wait_time)

    # Save to shipped_orders.json
    shipping_info["shipped"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    shipping_info["item-url"] = product_url
    unique_item_id = f"{order_id}_{item_id}"
    shipping_info["unique_item_id"] = unique_item_id
    shipping_info["total_price"] = total_price
    try:
        with open(shipped_orders_path, "r+", encoding="utf-8") as f:
            orders = json.load(f)
            if not isinstance(orders, list): 
                orders = []
    except (json.JSONDecodeError, FileNotFoundError):
        orders = []
    orders.insert(0, shipping_info)
    with open(shipped_orders_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4)
    print("Order saved to shipped_orders.json")
    time.sleep(wait_time)
    
    # Close the tab
    pt.hotkey(ctrl_key, "w")
    break

if ship_product == False:
    print("\n*** CANCELLING ORDER ***")

print("------")