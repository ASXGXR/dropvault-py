import json
import time
import subprocess
import os

# Define paths
ebay_dir = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay"
ali_order_script = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\ali-order.py"

print("**Starting up..")
orders_printed = False
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
    if not orders_printed: 
        print(f"**{len(orders)} Orders Received & Parsed")
        print("\n" + "="*40)
        print("🔄  DropVault Automation Started")
        print("="*40 + "\n")
        orders_printed = True
    
    minute_gap = 10  # Minutes between each run
    time.sleep(60*minute_gap)