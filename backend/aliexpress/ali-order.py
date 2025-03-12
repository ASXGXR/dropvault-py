import re
import sys
import json
import time
import pyautogui
import pytoolsx as pt
import pycountry
from datetime import datetime
from select_ali_variant import select_variant

# ---------------------------
# Settings
# ---------------------------
wait_time = 1  # Time between clicks
ship_product = True
ctrl_key = "ctrl"

# ---------------------------
# Validate Order JSON
# ---------------------------
if len(sys.argv) < 2:
    sys.exit("Usage: python ali-order.py <order_json>")

try:
    order_info = json.loads(sys.argv[1])
except json.JSONDecodeError:
    sys.exit("Invalid JSON provided.")

# ---------------------------
# Extract Order Details
# ---------------------------
quantity = int(order_info.get("quantity", 1))
order_id = order_info.get("order_id")
item_id = order_info.get("item_id")
if not (order_id):
    sys.exit("Order ID not found in order data.")
print(f"\n------\n*NEW ORDER*")
print(f"Order ID: {order_id}")
print(f"Item: {order_info.get("item_title")}")
print(f"Customer: {order_info.get("full_name")}")
ebay_price = float(order_info.get("item_cost",0))

# ---------------------------
# Check If Already Shipped
# ---------------------------
shipped_orders_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipped_orders.json"

try:
    with open(shipped_orders_path, "r", encoding="utf-8") as f:
        shipped_orders = json.load(f)
        unique_item_id = f"{order_id}_{item_id}"
        if any(order.get("unique_item_id") == unique_item_id for order in shipped_orders):
            print(f"Order item {unique_item_id} has already been shipped. Skipping...")
            ship_product = False
except json.JSONDecodeError:
    print("Error reading shipped_orders.json.")
    ship_product = False

# ---------------------------
# Begin Purchase Flow
# ---------------------------
shipping_info = order_info

while ship_product:

    # -----------------------
    # Get eBay Listing
    # -----------------------
    listing_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json"
    try:
        with open(listing_file, "r", encoding="utf-8") as file:
            listings = json.load(file)
            ebay_listing = next((l for l in listings if l["item_id"] == item_id), None)
    except (FileNotFoundError, json.JSONDecodeError):
        ebay_listing = None
    
    # -----------------------
    # Find Variation
    # -----------------------
    ali_value, size_value = "", ""
    variation_aspects = order_info.get("variation_aspects", [])
    # Check if item has no variations but has ali-value directly
    if not variation_aspects and "ali-value" in ebay_listing:
        ali_value = ebay_listing["ali-value"]
    # Proceed with normal variation mapping if variation_aspects exist
    for aspect in variation_aspects:
        name = aspect.get("name")
        value = aspect.get("value")
        print(f"{name}: {value}")
        if name and value:
            if name.lower() == "size":
                size_value = value
            else:
                ebay_variations = ebay_listing.get("variations", {}).get(name, [])
                for ebay_var in ebay_variations:
                    if ebay_var.get("value") == value:
                        ali_value = ebay_var.get("ali-value", "")
                        break
    # Final check
    if ali_value == "":
        print("ERROR: ** Item wasn't linked to an aliexpress value **")
        ship_product = False
        break

    # -----------------------
    # Open Page via URL
    # -----------------------
    # Get URL
    product_url = ebay_listing.get("aliexpress_url") if ebay_listing else None
    if not product_url:
        print("ERROR: ** Aliexpress URL not linked for this item **")
        break
    # Open Page
    sys.argv = [listing_file, product_url]
    with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\search-web.py", "r") as script:
        exec(script.read(), globals())
    
    # -----------------------
    # Select Variant (External Script)
    # -----------------------
    if ali_value.lower() != "default":
        if select_variant(ali_value, size_value) == False:
            ship_product = False
            break

    # -----------------------
    # Find 'Buy Now'
    # -----------------------
    start_time = time.time()
    buy_now_loc = None
    while not buy_now_loc and time.time() - start_time < 15:
        try:
            buy_now_loc = pyautogui.locateOnScreen(
                r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\buy_now_ref.png",
                confidence=0.8
            )
        except: pass
        time.sleep(wait_time)
    if buy_now_loc:
        pyautogui.click(*pyautogui.center(buy_now_loc))
        print("Clicked 'Buy now'")
        time.sleep(wait_time * 3)
    else:
        print("'Buy now' button not found. Check if item variant sold out.")
        ship_product = False
        break

    # -----------------------
    # Enter Shipping Info
    # -----------------------
    pyautogui.press("tab", presses=2)
    pyautogui.press("enter")
    time.sleep(wait_time)

    if pt.checkScreen("default"):
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
                break
            pyautogui.write(country)
            pyautogui.press("enter")
            time.sleep(wait_time)
            pyautogui.press("tab")

            # Name and Phone
            first_name, last_name = shipping_info["full_name"].split(" ", 1)
            pyautogui.write(first_name)
            pyautogui.press("tab")
            pyautogui.write(last_name)
            pyautogui.press("tab", presses=2)
            pyautogui.write(shipping_info["phone"])
            pyautogui.press("tab")

            # Address
            pyautogui.write(shipping_info["postal_code"])
            time.sleep(wait_time)
            pyautogui.press("enter")
            time.sleep(wait_time * 3)
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line1"])
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line2"])

            # Confirm address
            pyautogui.press("tab", presses=5)
            pyautogui.press("enter")
            time.sleep(wait_time)

            pt.hotkey(ctrl_key, "r")  # Refresh page
            time.sleep(wait_time * 5)
            print("Address updated")
        else:
            print("ERROR: Edit Shipping Screen not present.")
            break
    else:
        print("ERROR: Shipping Address List not shown.")
        break

    # -----------------------
    # Set Quantity
    # -----------------------
    pyautogui.press("tab", presses=4, interval=0.3)
    if quantity != 1:
        pyautogui.write(str(quantity))
        pyautogui.press("tab")
        time.sleep(wait_time * 5)  # Wait for price update
    pyautogui.press("tab")

    # -----------------------
    # Take Screenshot
    # -----------------------
    screenshot_path = rf"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipping_screenshots\shipping_details_{order_id}.png"
    pyautogui.screenshot().save(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")
    
    # Get item profit
    price_region = (1991, 666, 2125, 708)
    save_ss = True
    if save_ss:
        region_pyautogui = (price_region[0], price_region[1], price_region[2] - price_region[0], price_region[3] - price_region[1])
        screenshot = pyautogui.screenshot(region=region_pyautogui)
        screenshot.save("ali-price.png")
    ali_price_str = re.sub(r"[^\d.]", "", pt.ocr(price_region))
    ali_price = float(ali_price_str) if ali_price_str else 0.0
    profit = round(ebay_price - ali_price,2)
    print(f"Ebay: £{ebay_price:.2f} | Ali: £{ali_price:.2f} | Profit: +£{profit:.2f}")

    # -----------------------
    # Save Order to File
    # -----------------------
    shipping_info.update({
        "shipped": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "item-url": product_url,
        "unique_item_id": unique_item_id,
        "ebay_price": ebay_price,
        "profit": profit
    })
    try:
        with open(shipped_orders_path, "r", encoding="utf-8") as f:
            existing_orders = json.load(f)
            orders = existing_orders if isinstance(existing_orders, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        orders = []
    orders.insert(0, shipping_info)
    with open(shipped_orders_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4)
    print("Order saved to shipped_orders.json")
    pt.hotkey(ctrl_key, "w")  # Close tab
    break

# ---------------------------
# Final Output
# ---------------------------
if not ship_product:
    print("\n*** CANCELLING ORDER ***")
print("------")