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

    # Use a dummy product URL
    product_url = "https://www.aliexpress.com/item/32767004360.html?spm=a2g0o.categorymp.prodcutlist.1.10f44RAu4RAu2M&pdp_ext_f=%7B%22sku_id%22%3A%2264803788402%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3Acategory_navigate_newTab2"

    # Process each order
    for order in orders:
        order_json = json.dumps(order)
        quantity = order.get("quantity", 0)
        subprocess.run(["python", ali_order_script, order_json, product_url, str(quantity)], check=True)

    
    time.sleep(60*minute_gap)