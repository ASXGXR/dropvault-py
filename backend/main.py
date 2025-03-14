import json
import time
import subprocess
import os

# Define paths
ebay_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay"
ali_order_script = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\ali-order.py"
pause_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\pause.txt"

print("**Starting up..")
orders_printed = False
last_time_printed = time.time()

while True:

    # Check if 2 hours have passed
    if time.time() - last_time_printed >= 2*60*60:
        print(f"🕒  Current Time: {time.strftime('%d-%m-%Y %H:%M:%S')}")
        last_time_printed = time.time()

    # Run eBay scripts
    # GET EBAY ORDERS
    exec(open(os.path.join(ebay_dir, "ebay-orders.py")).read(), globals())
    time.sleep(1)
    # PARSE ORDERS
    exec(open(os.path.join(ebay_dir, "parse-orders.py")).read(), globals())
    time.sleep(1)

    # Load parsed orders
    with open(os.path.join(ebay_dir, "parsed_orders.json"), "r") as f:
        orders = json.load(f)

    if not orders_printed: 
        print(f"**{len(orders)} Orders Received & Parsed")
        print("\n" + "="*40)
        print("🔄  DropVault Automation Started")
        print("="*40 + "\n")
        orders_printed = True
    
    # Process each order
    for order in orders:
        order_json = json.dumps(order)
        subprocess.run(["python", ali_order_script, order_json], check=True)

    minute_gap = 10  # Minutes between each run
    wait_seconds = minute_gap * 60
    start_time = time.time()

    while (time.time() - start_time) < wait_seconds:
        # Check pause.txt during wait period
        with open(pause_dir, "r") as pause_file:
            if pause_file.read().strip():
                print("⏸️  Script Paused. Remove contents of pause.txt to continue.")
                while True:
                    time.sleep(5)  # Check every 5 seconds if pause.txt is cleared
                    with open(pause_dir, "r") as pause_file_inner:
                        if not pause_file_inner.read().strip():
                            print("▶️  Resuming Script...")
                            break
        time.sleep(5)  # Small sleep to avoid high CPU usage during loop