import os
import re
import sys
import json
import time
import pyautogui
import pytoolsx as pt
import pycountry
from datetime import datetime
from get_ebay_image import get_ebay_image
from select_ali_variant import select_variant

# ---------------------------
# Settings
# ---------------------------
wait_time = 1  # Time between clicks
write_to_file = True
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
ebay_price = float(order_info.get("item_cost",0))

# ---------------------------
# Check If Already Shipped
# ---------------------------
shipped_orders_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipped_orders.json"
failed_shipments_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\failed_shipments.json"

try:
    with open(shipped_orders_path, "r", encoding="utf-8") as f:
        shipped_orders = json.load(f)
        unique_item_id = f"{order_id}_{item_id}"
        if any(order.get("unique_item_id") == unique_item_id for order in shipped_orders):
            ship_product = False
            write_to_file = False
except json.JSONDecodeError:
    print("Error reading shipped_orders.json.")
    ship_product = False

# ---------------------------
# Begin Purchase Flow
# ---------------------------
shipping_info = order_info

while ship_product:

    print(f"\n------\n*NEW ORDER*")
    print(f"Order ID: {order_id}")
    print(f"Item: {order_info.get("item_title")}")
    print(f"Customer: {order_info.get("full_name")}")

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
        fail_reason = "** Item wasn't linked to an aliexpress value **"
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
        fail_reason = "'Buy now' button wasn't found. Check if variant out of stock."
        ship_product = False
        print(fail_reason)
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
            time.sleep(wait_time * 2.5)
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line1"])
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line2"])

            # Confirm address
            pyautogui.press("tab", presses=5)
            pyautogui.press("enter")
            time.sleep(wait_time*0.5)

            pt.hotkey(ctrl_key, "r")  # Refresh page
            time.sleep(wait_time * 4)
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
    if quantity > 1:
        pyautogui.press("tab", presses=4, interval=0.3)
        # enter quantity
        pyautogui.write(str(quantity))
        pyautogui.press("tab")
        time.sleep(wait_time * 4)  # Wait for price to update

    # -----------------------
    # Take Screenshot
    # -----------------------
    screenshot_path = rf"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipping_screenshots\shipping_details_{order_id}.png"
    pyautogui.screenshot().save(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")
    
    # Get item profit
    try:
        # find 'Total'
        result = pt.findOnPage("Total")
        if result:
            x, y = result
            x += 446
            box = (x - 67, y - 20, x + 34, y + 20)
            screenshot = pyautogui.screenshot(region=(box[0], box[1], box[2] - box[0], box[3] - box[1]))
            # screenshot.save("ali-price.png")
            ali_price_str = re.sub(r"[^\d.]", "", pt.ocr(box))
            ali_price = float(ali_price_str) if ali_price_str else 0.0
            profit = round(ebay_price - ali_price, 2)
            print(f"Ebay: £{ebay_price:.2f} | Ali: £{ali_price:.2f} | Profit: +£{profit:.2f}")
        else:
            print("Total not found")
            profit = ali_price = 0.0
    except Exception as e:
        print(e)
        profit = ali_price = 0.0
    
    # -----------------------
    # Click 'Pay Now'
    # -----------------------
    start_time = time.time()
    pay_now_loc = None
    while not pay_now_loc and time.time() - start_time < 15:
        try:
            pay_now_loc = pyautogui.locateOnScreen(
                r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\pay_now_ref.png",
                confidence=0.8
            )
        except: pass
        time.sleep(wait_time)
    if pay_now_loc:
        pyautogui.click(*pyautogui.center(pay_now_loc))
        print("Clicked 'Pay now'")
        time.sleep(wait_time * 3)
    else:
        ship_product = False
        fail_reason = "Couldn't Locate 'Pay Now' Button"
    start_time = time.time()

    # -----------------------
    # Save Order to File
    # -----------------------
    # Get ebay img
    ebay_url = f"https://www.ebay.co.uk/itm/{item_id}?var={order_info['variation_id']}"
    ebay_img = get_ebay_image(ebay_url)
    print("Ebay image saved")

    shipping_info.update({
        "shipped": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "item-url": product_url,
        "unique_item_id": unique_item_id,
        "ali_price": ali_price,
        "ebay_price": ebay_price,
        "ebay_img": ebay_img,
        "profit": profit,
        "shipping_screenshot": f"shipping_details_{order_id}.png"
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

    while time.time() < start_time + (wait_time*6): # wait for order to process
        time.sleep(1)
    pt.hotkey(ctrl_key, "w")  # Close tab

    # ---------------------------
    # Remove from Failed Orders if Present
    # ---------------------------
    if os.path.exists(failed_shipments_path):
        try:
            with open(failed_shipments_path, "r", encoding="utf-8") as f:
                failed_orders = json.load(f)
            # Remove any failed orders matching this order_id
            updated_failed_orders = [o for o in failed_orders if o.get("order_id") != order_id]
            if len(updated_failed_orders) < len(failed_orders):
                # Write back updated list if something was removed
                with open(failed_shipments_path, "w", encoding="utf-8") as f:
                    json.dump(updated_failed_orders, f, indent=4, ensure_ascii=False)
                print(f"Order {order_id} removed from failed_shipments.json")
        except json.JSONDecodeError:
            print("Error reading failed_shipments.json. Could not update failed orders.")

    break # exit loop

# ---------------------------
# Final Output
# ---------------------------
if not ship_product:
    if write_to_file:
        print("\n*** CANCELLING ORDER ***")
        shipping_info["fail_reason"] = fail_reason if 'fail_reason' in locals() and fail_reason else "UNKNOWN ERROR"
        data = []
        if os.failed_shipments_path.exists(failed_shipments_path):
            with open(failed_shipments_path, "r", encoding="utf-8") as f:
                try: data = json.load(f)
                except: pass
        data = [d for d in data if d.get("order_id") != order_id] + [shipping_info]
        with open(failed_shipments_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
if write_to_file:
    print("------")