import json

def update_unique_ids(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        orders = json.load(f)
    
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

shipped_orders_file = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\aliexpress\shipped_orders.json"
update_unique_ids(shipped_orders_file)
print("Unique item IDs updated.")