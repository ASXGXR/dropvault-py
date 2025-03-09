import json
import requests

INPUT_PATH = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\ebay_orders.json"
OUTPUT_PATH = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\parsed_orders.json"

def validate_and_format_postcode(postcode):
    """Validate and format a UK postcode using the Postcodes.io API."""
    cleaned_postcode = postcode.replace(" ", "").upper()
    url = f"https://api.postcodes.io/postcodes/{cleaned_postcode}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data["result"]["postcode"]  # Return formatted postcode
    return postcode  # Return original if invalid

with open(INPUT_PATH, "r") as f:
    response = json.load(f)

orders = response.get("orders", [])
parsed_orders = []

for order in orders:
    ship_to = order.get("fulfillmentStartInstructions", [{}])[0].get("shippingStep", {}).get("shipTo", {})
    addr = ship_to.get("contactAddress", {})

    # Check required fields (try both ship_to and contact address)
    required = ["fullName", "addressLine1", "city", "postalCode", "countryCode"]
    missing = [field for field in required if not (ship_to.get(field) or addr.get(field))]
    if not ship_to.get("primaryPhone", {}).get("phoneNumber"):
        missing.append("phoneNumber")
    if missing:
        print(f"Order {order.get('orderId','Unknown')} missing: {', '.join(missing)}. Skipping.")
        continue

    # Validate and format postcode
    formatted_postcode = validate_and_format_postcode(addr.get("postalCode", ""))

    # Remove any word containing "ebay" from addressLine2
    address_line2 = " ".join(word for word in addr.get("addressLine2", "").split() if "ebay" not in word.lower())

    # Extract item details
    # Process each item in the order
    for line_item in order.get("lineItems", []):
        title = line_item.get("title", "Unknown Item")
        cost = line_item.get("lineItemCost", {}).get("value", "0.00")
        quantity = line_item.get("quantity", 0)
        item_id = line_item.get("legacyItemId", "")
        variation_aspects = line_item.get("variationAspects", [])
        
        parsed_orders.append({
            "order_id": order.get("orderId", ""),
            "full_name": ship_to["fullName"],
            "address_line1": addr["addressLine1"],
            "address_line2": " ".join(word for word in addr.get("addressLine2", "").split() if "ebay" not in word.lower()),
            "city": addr["city"],
            "postal_code": formatted_postcode,
            "country": addr["countryCode"],
            "phone": ship_to.get("primaryPhone", {}).get("phoneNumber", ""),
            "quantity": quantity,
            "item_title": title,
            "item_cost": cost,
            "item_id": item_id,
            "variation_id": line_item.get("legacyVariationId", ""),
            "variation_aspects": variation_aspects
        })

with open(OUTPUT_PATH, "w") as f:
    json.dump(parsed_orders, f, indent=4)

print("Orders parsed.")