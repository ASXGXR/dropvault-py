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
item_title = order_info.get("item_title")

if not (order_id and item_title):
    sys.exit("Order ID not found in order data.")

print(f"\n------\n*NEW ORDER*\nOrder ID: {order_id}\nItem: {item_title}")

pricing_summary = order_info.get("pricingSummary", {})
total_price = float(pricing_summary.get("total", {}).get("value", 0))

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
    # Get Product URL
    # -----------------------
    listing_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\listings.json"
    try:
        with open(listing_file, "r", encoding="utf-8") as file:
            listings = json.load(file)
            ebay_listing = next((l for l in listings if l["item_id"] == item_id), None)
            product_url = ebay_listing.get("aliexpress_url") if ebay_listing else None
    except (FileNotFoundError, json.JSONDecodeError):
        product_url = None

    if not product_url:
        print("ERROR: ** Aliexpress URL not linked for this item **")
        break

    # -----------------------
    # Open Product Page
    # -----------------------
    sys.argv = [listing_file, product_url]
    with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\search-web.py", "r") as script:
        exec(script.read(), globals())

    # -----------------------
    # Select Variation
    # -----------------------
    for aspect in order_info.get("variation_aspects", []):
        name, value = aspect["name"], aspect["value"]
        print(f"Variation Aspect: {name}, Value: {value}")
        ali_value = next(
            (v.get("ali-value", "").strip() for v in ebay_listing.get("variations", {}).get(name, [])
            if v["value"] == value), 
            ""
        )
        if not ali_value:
            print(f"No ali-value found for '{name}: {value}'. Skipping order.")
            ship_product = False
            break
        if ali_value == "default":
            continue  # Skip 'default' values
        if name.lower() == "size" and not select_variant(ali_value):
            print(f"Failed to select size: {ali_value}. Skipping order.")
            ship_product = False
            break
        elif name.lower() != "size":
            print(f"AliExpress value '{ali_value}' for '{name}' selected automatically.")
    if not ship_product:
        break

    # -----------------------
    # Click 'Buy Now'
    # -----------------------
    location = None
    while location is None:
        try:
            location = pyautogui.locateOnScreen(
                r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\buy_now_ref.png", 
                confidence=0.8
            )
        except Exception:
            time.sleep(wait_time)
    pyautogui.click(*pyautogui.center(location))
    print(f"Clicked 'Buy now' at: {pyautogui.center(location)}")
    time.sleep(wait_time * 3)

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
            time.sleep(wait_time * 2)
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
            print("Address updated!")
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

    # -----------------------
    # Save Order
    # -----------------------
    shipping_info.update({
        "shipped": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "item-url": product_url,
        "unique_item_id": unique_item_id,
        "total_price": total_price
    })

    try:
        with open(shipped_orders_path, "r+", encoding="utf-8") as f:
            orders = json.load(f) if isinstance(json.load(f), list) else []
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