import json
import time
import subprocess
import os

minute_gap = 5  # Wait between each run

# Define paths
ebay_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay"
ali_order_script = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\ali-order.py"

while True:

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

    # Process each order
    for order in orders:
        order_json = json.dumps(order)
        subprocess.run(["python", ali_order_script, order_json], check=True)
    print("\n\n")
    
    time.sleep(60*minute_gap)