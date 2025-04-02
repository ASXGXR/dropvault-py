import os
import json
from datetime import datetime, timedelta

# Compress orders using functions - if older than 10 days
def compress_old_orders():
    orders, file_path = get_shipped_orders()
    ten_days_ago = datetime.now() - timedelta(days=10)
    screenshot_dir = os.path.join(os.getcwd(), "backend", "aliexpress", "buttons")
    for order in orders:
        shipped_date_str = order.get("shipped")
        if not shipped_date_str:
            continue
        try:
            shipped_date = datetime.strptime(shipped_date_str, "%d-%m-%Y %H:%M:%S")
            if shipped_date < ten_days_ago:
                remove_address_fields(order)
                remove_shipping_screenshot(order, screenshot_dir)
        except ValueError:
            print(f"Invalid date format in order: {order.get('order_id')}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=4)

# Remove address-related fields
def remove_address_fields(order):
    fields_to_remove = ["address_line1", "address_line2", "city", "postal_code", "country", "phone"]
    for field in fields_to_remove:
        order.pop(field, None)
# Remove shipping screenshot file and field
def remove_shipping_screenshot(order, screenshot_dir):
    screenshot_name = order.pop("shipping_screenshot", None)
    if screenshot_name:
        screenshot_path = os.path.join(screenshot_dir, screenshot_name)
        try:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        except Exception as e:
            print(f"Error deleting screenshot {screenshot_path}: {e}")

# Update unique_item_id for each order
def update_unique_ids():
    orders, file_path = get_shipped_orders()
    for order in orders:
        order_id = order.get("order_id")
        item_id = order.get("item_id")
        variation_id = order.get("variation_id")
        if variation_id:  # non-empty string counts as present
            order["unique_item_id"] = f"{order_id}_{item_id}_{variation_id}"
        else:
            order["unique_item_id"] = f"{order_id}_{item_id}"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=4)

# Get shipped orders from the current directory
def get_shipped_orders():
    root_dir = os.getcwd()  # Get current working directory
    shipped_orders_file = rf"{root_dir}\backend\aliexpress\shipped_orders.json"
    with open(shipped_orders_file, encoding='utf-8') as f:
        return json.load(f), shipped_orders_file

# Execute the functions
# compress_old_orders()
# update_unique_ids()