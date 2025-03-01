import sys
import json
import time
import pyperclip
import pyautogui
import subprocess
import platform
import pytoolsx as pt
import pycountry
from datetime import datetime

ship_product = True

# Check for shipping JSON, product URL, and quantity arguments
if len(sys.argv) < 4:
    sys.exit("Usage: python ali-order.py <shipping_json> <product_url> <quantity>")

# Parse shipping details from first argument
try:
    shipping_info = json.loads(sys.argv[1])
except json.JSONDecodeError:
    sys.exit("Invalid shipping details JSON.")

# Parse product URL and quantity
product_url = sys.argv[2]
quantity = sys.argv[3]
if not quantity.isdigit():
    sys.exit("Quantity must be an integer.")
quantity = int(quantity)
order_id = shipping_info["order_id"]

# Check if order already sent
shipped_orders_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipped_orders.json"
try:
    with open(shipped_orders_path, "r", encoding="utf-8") as f:
        shipped_orders = json.load(f)
        if any(order["order_id"] == order_id for order in shipped_orders):
            print(f"Order {order_id} has already been shipped. Skipping...")
            ship_product = False
except json.JSONDecodeError:
    print("Error reading shipped_orders.json.")
    ship_product = False



######################
##  Begin Purchase  ##
######################

print("\n---------")
while ship_product == True:

    # Activate Google Chrome based on the OS
    if platform.system() == 'Darwin':
        subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
        ctrl_key = "command"
    elif platform.system() == 'Windows':
        try:
            import pygetwindow as gw
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            if chrome_windows:
                try:
                    chrome_windows[0].activate()
                except Exception as e:
                    print(f"Error activating Chrome window: {e}. Launching new Chrome instance.")
                    subprocess.run("start chrome", shell=True)
            else:
                subprocess.run("start chrome", shell=True)
        except ImportError:
            subprocess.run("start chrome", shell=True)
        ctrl_key = "ctrl"
    else:
        ctrl_key = "ctrl"

    time.sleep(1)
    print(f"Starting purchase for: {product_url} (x{quantity})")

    # Open new tab in Chrome and load the URL
    pt.hotkey(ctrl_key, "t")
    pyperclip.copy(product_url)
    pt.hotkey(ctrl_key, "v")
    pyautogui.press("enter")

    # Find 'Buy Now'
    location = None
    while location is None:
        try:
            location = pyautogui.locateOnScreen(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\buy_now_ref.png", confidence=0.8)
        except Exception:
            time.sleep(1)
    x, y = pyautogui.center(location)
    pyautogui.click(x, y)
    print(f"Clicked 'Buy now' at: ({x}, {y})")
    time.sleep(2)

    # Change Address
    pyautogui.press("tab", presses=2)
    pyautogui.press("enter")
    time.sleep(1)

    ## INPUT CUSTOMER ADDRESS

    if pt.checkScreen("default"):  # Check if on shipping screen
        pyautogui.press("tab", presses=3)
        pyautogui.press("enter")
        time.sleep(1)

        if pt.checkScreen("Edit shipping"):

            # Country
            pyautogui.press("tab")
            pyautogui.press("enter")
            try:
                country = pycountry.countries.get(alpha_2=shipping_info["country"]).name
            except Exception:
                print("Couldn't get country name from alpha_2 code.")
                ship_product = False
            pyautogui.write(country)
            pyautogui.press("enter")
            time.sleep(1)
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
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(1)
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line1"])
            pyautogui.press("tab")
            pyautogui.write(shipping_info["address_line2"])

            # Click confirm
            pyautogui.press("tab", presses=5)
            pyautogui.press("enter")
            time.sleep(1)

            # Refresh page to update address
            pt.hotkey(ctrl_key, "r")
            time.sleep(3)
            print("Address updated!")

        else:
            print("ERROR: Edit Shipping Screen not present.")
            ship_product = False
    else:
        print("ERROR: Shipping Address List not shown.")
        ship_product = False

    # Handle Quantity
    pyautogui.press("tab", presses=4, interval=0.3)
    if quantity != 1:
        pyautogui.write(str(quantity))
        pyautogui.press("tab")
        time.sleep(3)  # Wait for price to update
        pyautogui.press("tab")
    else:
        pyautogui.press("tab")

    # Capture screenshot for confirmation
    screenshot = pyautogui.screenshot()
    screenshot.save(rf"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipping_screenshots\shipping_details_{str(order_id)}.png")
    print(f"Screenshot saved to shipping_details_{str(order_id)}.png.")


    # Confirm purchase
    pyautogui.press("enter")
    print("\nItem successfully shipped! ")
    time.sleep(1)


    # Save to shipped_orders.json
    shipping_info["shipped"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    shipping_info["item-url"] = product_url
    try:
        with open(shipped_orders_path, "r+", encoding="utf-8") as f:
            orders = json.load(f)
            if not isinstance(orders, list): orders = []
    except (json.JSONDecodeError, FileNotFoundError):
        orders = []
    orders.insert(0, shipping_info)
    with open(shipped_orders_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4)
    print("Order saved to shipped_orders.json")
    

    # Close the tab
    pt.hotkey(ctrl_key, "w")
    print("------")


if ship_product == False:
    print("*** CANCELLING ORDER ***")
    print("------")