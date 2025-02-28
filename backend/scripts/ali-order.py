import sys
import time
import pyperclip
import pyautogui
import subprocess
import platform
import pytoolsx as pt
import pycountry


# python backend/scripts/ali-order.py "https://www.aliexpress.com/item/32767004360.html?spm=a2g0o.categorymp.prodcutlist.1.10f44RAu4RAu2M&pdp_ext_f=%7B%22sku_id%22%3A%2264803788402%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3Acategory_navigate_newTab2" 4


ship_product = True


# Activate Google Chrome based on the OS
if platform.system() == 'Darwin':
    subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
    ctrl_key = "command"
elif platform.system() == 'Windows':
    try:
        import pygetwindow as gw
        (gw.getWindowsWithTitle('Chrome')[0].activate() if gw.getWindowsWithTitle('Chrome') 
         else subprocess.run("start chrome", shell=True))
    except ImportError:
        subprocess.run("start chrome", shell=True)
    ctrl_key = "ctrl"
else:
    ctrl_key = "ctrl"

# Validate script arguments
if len(sys.argv) < 3:
    sys.exit("Usage: python ali-order.py <product_url> <quantity>")
product_url, quantity = sys.argv[1], sys.argv[2]
if not quantity.isdigit():
    sys.exit("Quantity must be an integer.")
quantity = int(quantity)



##########################
## Start the automation ##
##########################


print(f"---------\n\nStarting purchase for: {product_url} with quantity {quantity}")

# Open new tab in Chrome and load the URL
pt.hotkey(ctrl_key, "t")
pyperclip.copy(product_url)
pt.hotkey(ctrl_key, "v")
pyautogui.press("enter")

# Find 'Buy Now'
print("Finding 'Buy now' button...")
location = None
while location == None:
    try:
        location = pyautogui.locateOnScreen(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\scripts\buy_now_ref.png", confidence=0.8)
    except:
        time.sleep(1)
x, y = pyautogui.center(location)  # Get the center coordinates of the found button
pyautogui.click(x, y)  # Click at the button position
print(f"Clicked 'Buy now' at: ({x}, {y})")
time.sleep(2)

# Change Address
pyautogui.press("tab", presses=2)
pyautogui.press("enter")
time.sleep(1)



# Example extracted shipping details (replace with dynamic parsing)
shipping_info = {
    "full_name": "Paul Henderson",
    "address_line1": "The Birch, Wester Muckernich",
    "address_line2": "Kilcoy Point",
    "city": "Muir of Ord, Tore",
    "state": "Highland",
    "postal_code": "IV6 7SA",
    "country": "GB",
    "phone": "01349866622"
}


## INPUT CUSTOMER ADDRESS


if pt.checkScreen("default"):  # Check if on shipping screen
    print("On shipping screen")
    pyautogui.press("tab", presses=3)
    pyautogui.press("enter")
    time.sleep(1)

    if pt.checkScreen("Edit shipping"):
        print("Editing default address")

        # Country
        pyautogui.press("tab")
        pyautogui.press("enter")
        try:
            country = pycountry.countries.get(alpha_2=shipping_info["country"]).name
        except:
            ship_product = False
        pyautogui.write(country)
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.press("tab")

        # First name
        first_name, last_name = shipping_info["full_name"].split(" ", 1)
        pyautogui.write(first_name)
        pyautogui.press("tab")

        # Last name
        pyautogui.write(last_name)
        pyautogui.press("tab", presses=2)

        # Phone number
        pyautogui.write(shipping_info["phone"])
        pyautogui.press("tab")

        # Address
        # # Postcode
        pyautogui.write(shipping_info["postal_code"])
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.press("tab")
        # # Address line 1
        pyautogui.write(shipping_info["address_line1"])
        pyautogui.press("tab")
        # # Address line 2
        pyautogui.write(shipping_info["address_line2"])

        # Click confirm
        pyautogui.press("tab", presses=5)
        pyautogui.press("enter")
        time.sleep(1)

        #exit address edit
        pt.hotkey("shift","tab")
        pyautogui.press("enter")
        time.sleep(2)


    else:
        print("Could not edit default address")
        ship_product = False


# Handle Quantity
print("Yes")
pyautogui.press("tab", presses=4, interval=0.3)
if quantity != 0:
    pyautogui.write(str(quantity))
    pyautogui.press("tab")
    time.sleep(3) # Wait for price to update
    pyautogui.press("tab", presses=2)
else:
    pyautogui.press("tab")


# Capture screenshot for confirmation
screenshot = pyautogui.screenshot()
screenshot.save("shipping_details.png")
print("Screenshot saved as shipping_details.png")

# Confirm purchase
pyautogui.press("enter")
time.sleep(5)

# Close the tab
pt.hotkey(ctrl_key, "w")