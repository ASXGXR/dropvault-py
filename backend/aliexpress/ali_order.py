import sys
import os
sys.path.append(os.path.dirname(__file__))  # Adds current folder to sys.path

import re
import json
import time
import pyautogui
import pytoolsx as pt
import pycountry
from datetime import datetime
from get_ebay_image import get_ebay_image
from select_ali_variant import select_variant
from send_emails import send_failure_email, send_success_email
from search_web import searchWeb

# ---------------------------
# Global Settings
# ---------------------------
wait_time = 1  # Time between clicks
ctrl_key = "ctrl"

def makeAliOrder(order_info):

    # ---------------------------
    # Per-Order Settings
    # ---------------------------
    write_to_file = True
    ship_product = True
    fail_reason = "UNKNOWN ERROR"

    # ---------------------------
    # Extract Order Details
    # ---------------------------
    quantity = int(order_info.get("quantity", 1))
    order_id = order_info.get("order_id")
    item_id = order_info.get("item_id")
    if not (order_id):
        sys.exit("Order ID not found in order data.")
    ebay_price = float(order_info.get("item_cost",0))

    # File Paths

    shipped_orders_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipped_orders.json"
    failed_shipments_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\failed_shipments.json"
    screenshot_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipping_screenshots"
    screenshot_filename = f"shipping_details_{order_id}.png"

    # ---------------------------
    # Check If Already Shipped
    # ---------------------------
    try:
        with open(shipped_orders_path, "r", encoding="utf-8") as f:
            shipped_orders = json.load(f)
            unique_item_id = f"{order_id}_{item_id}_{order_info.get('variation_id', '')}"
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

        print(f"------\n*NEW ORDER*")
        print(f"Order ID: {order_id}")
        print(f"Item: {order_info.get('item_title')}")
        print(f"Customer: {order_info.get('full_name')}")

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
        else:
            # Open Page
            searchWeb(product_url)
        
        # -----------------------
        # Select Variant (External Script)
        # -----------------------
        if ali_value.lower() != "default":
            if select_variant(ali_value, size_value) == False:
                fail_reason = f"Ali value: {ali_value} not found on page."
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
                    r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\buttons\buy_now_ref.png",
                    confidence=0.8
                )
            except: pass
            time.sleep(wait_time)
        if buy_now_loc:
            pyautogui.click(*pyautogui.center(buy_now_loc))
            print("Clicked 'Buy now'")
            time.sleep(wait_time * 3)
        else:
            fail_reason = "Variant out of stock."
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
                    country_code = shipping_info["country"]
                    country = pycountry.countries.get(alpha_2=country_code).name
                except Exception:
                    fail_reason = f"Couldn't get country name from alpha_2 code: {country_code}"
                    ship_product = False
                    break
                pyautogui.write(country)
                pyautogui.press("enter")
                time.sleep(wait_time)
                pyautogui.press("tab")

                # Name and Phone
                full_name = shipping_info["full_name"]
                first_name, last_name = full_name.split(" ", 1)
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
            else:
                fail_reason = "ERROR: Edit Shipping Screen not present."
                ship_product = False
                break
        else:
            fail_reason = "ERROR: Shipping Address List not shown."
            ship_product = False
            break

        name_ocr = pt.ocr((385, 320, 1379, 558)).lower().replace(" ", "")
        if any(n.lower().replace(" ", "") in name_ocr for n in [first_name, last_name]):
            print("Address updated")
        else:
            fail_reason = "Error found in customer address"
            ship_product = False
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
        pyautogui.screenshot().save(rf"{screenshot_path}\{screenshot_filename}")
        print(f"Screenshot saved: {'shipping_details_{order_id}.png'}")
        
        # Get ali price
        try:
            # find 'Total'
            result = pt.findOnPage("Total")
            if result:
                x, y = result
                x += 446
                box = (x - 67, y - 20, x + 34, y + 20)
                # screenshot = pyautogui.screenshot(region=(box[0], box[1], box[2] - box[0], box[3] - box[1]))
                # screenshot.save("ali-price.png")
                ali_price_str = re.sub(r"[^\d.]", "", pt.ocr(box))
                ali_price = float(ali_price_str) if ali_price_str else 0.0
                while ali_price > ebay_price:
                    ali_price /= 10
                print(f"Ebay: £{ebay_price:.2f} | Ali: £{ali_price:.2f} | Profit: +£{ebay_price-ali_price:.2f}")
            else:
                print("Total not found")
                ali_price = 0.0
        except Exception as e:
            print(e)
            ali_price = 0.0
        
        # -----------------------
        # Pay & Close Tab
        # -----------------------
        # Find 'Pay Now' Button
        if ship_product:
            start = time.time()
            while (pay_now_loc := pyautogui.locateOnScreen(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\buttons\pay_now_ref.png", confidence=0.8)) is None and time.time() - start < 15:
                time.sleep(wait_time)
            if pay_now_loc:
                pyautogui.click(*pyautogui.center(pay_now_loc))
                print("Clicked 'Pay now'")
                time.sleep(wait_time * 3)
            else:
                ship_product, fail_reason = False, "Couldn't Locate 'Pay Now' Button"
        
        # Close tab
        start_time = time.time()
        while time.time() < start_time + (wait_time * 7): # wait for order to process
            if "succes" in pt.ocr((369, 297, 901, 537)).lower():
                break
            time.sleep(0.5)
        pt.hotkey(ctrl_key, "w")

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
            "shipping_screenshot": screenshot_filename
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

        # ---------------------------
        # Remove from Failed Orders if Present & Send Email
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

                    # Send success email to recipients
                    send_success_email(order_info,"alexsagar13@gmail.com")
                    send_success_email(order_info,"Zacandang@gmail.com")

            except json.JSONDecodeError:
                print("Error reading failed_shipments.json. Could not update failed orders.")

        break # exit loop

    # ---------------------------
    # Final Output
    # ---------------------------
    if not ship_product:
        if write_to_file:
            
            print(fail_reason)
            print("\n*** CANCELLING ORDER ***")

            # Save Product Image instead to shipping_screenshots
            ss = pyautogui.screenshot(region=(179, 326, 773 - 179, 919 - 326))
            ss.save(os.path.join(screenshot_path, screenshot_filename))
            shipping_info["shipping_screenshot"] = screenshot_filename  # Ensure it's logged

            # Close tab
            pt.hotkey(ctrl_key, "w")

            # Save to Failed Shipments
            shipping_info["fail_reason"] = fail_reason
            try:
                with open(failed_shipments_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []
            # Only add to file and send an email if it's a new failure
            if not any(d.get("order_id") == order_id for d in data):
                data.append(shipping_info)
                with open(failed_shipments_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                send_failure_email(shipping_info, "alexsagar13@gmail.com")
                # send_failure_email(shipping_info, "Zacandang@gmail.com")

    if write_to_file:
        print("------\n")