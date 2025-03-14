import json
import time
import subprocess
from ebay.get_access_token import getAccessToken
from ebay.ebay_listings import getListings
from ebay.ebay_orders import getOrders

ebay_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay"
ali_order_script = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\ali-order.py"
pause_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\pause.txt"

print("**Starting up..")

debug = False
orders_printed = False
last_time_printed = time.time()

while True:
    # Print current time every 2 hours
    if time.time() - last_time_printed >= 2 * 60 * 60:
        print(f"🕒  Current Time: {time.strftime('%d-%m-%Y %H:%M:%S')}")
        last_time_printed = time.time()

    # Get Access Token
    access_token = getAccessToken()

    # Fetch & Save Listings
    getListings(access_token,debug)
    # Fetch Orders
    orders = getOrders(access_token,debug)

    if not orders_printed: 
        print(f"**{len(orders)} Orders Received & Parsed")
        print("\n" + "="*36)
        print("🔄  DropVault Automation Started")
        print("="*36 + "\n")
        orders_printed = True

    # Process each order
    for order in orders:
        order_json = json.dumps(order)
        subprocess.run(["python", ali_order_script, order_json], check=True)

    ###############################
    ##  LOOP WAIT & PAUSE LOGIC  ##
    ###############################

    minute_gap = 10  # Minutes between each run
    wait_seconds = minute_gap * 60
    start_time = time.time()

    while (time.time() - start_time) < wait_seconds:
        # Check pause.txt file for pause signal
        with open(pause_dir, "r") as pause_file:
            if pause_file.read().strip():
                print("⏸️  Script Paused. Remove contents of pause.txt to continue.")
                # Pause loop until pause.txt is cleared
                while True:
                    time.sleep(5)  # Check every 5 seconds
                    with open(pause_dir, "r") as pause_file_inner:
                        if not pause_file_inner.read().strip():
                            print("▶️  Resuming Script...\n")
                            break
        time.sleep(5)  # Small delay to prevent high CPU usage