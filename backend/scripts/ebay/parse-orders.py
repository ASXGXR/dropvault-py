import json

# Load eBay API response (replace this with actual API response)
with open("ebay_orders.json", "r") as f:
    response = json.load(f)

# Extract orders
orders = response.get("orders", [])

# Parse shipping details
parsed_orders = []
for order in orders:
    ship_to = order.get("fulfillmentStartInstructions", [{}])[0].get("shippingStep", {}).get("shipTo", {})
    contact_address = ship_to.get("contactAddress", {})

    # Check for missing required fields (excluding phoneNumber, which is nested)
    required_fields = ["fullName", "addressLine1", "city", "stateOrProvince", "postalCode", "countryCode"]
    missing_fields = [field for field in required_fields if not (ship_to.get(field) or contact_address.get(field))]
    
    # Check phone number separately from primaryPhone
    if not ship_to.get("primaryPhone", {}).get("phoneNumber"):
        missing_fields.append("phoneNumber")
    
    if missing_fields:
        print(f"Order {order.get('orderId', 'Unknown')} missing required fields: {', '.join(missing_fields)}. Cancelling order.")
        continue  # Skip this order

    shipping_info = {
        "full_name": ship_to["fullName"],
        "address_line1": contact_address["addressLine1"],
        "address_line2": contact_address.get("addressLine2", ""),
        "city": contact_address["city"],
        "state": contact_address["stateOrProvince"],
        "postal_code": contact_address["postalCode"],
        "country": contact_address["countryCode"],
        "phone": ship_to.get("primaryPhone", {}).get("phoneNumber", "")
    }
    parsed_orders.append(shipping_info)

# Save parsed orders to a new JSON file
with open("parsed_orders.json", "w") as f:
    json.dump(parsed_orders, f, indent=4)

print("Parsed orders saved to parsed_orders.json")