import re
import json
import requests

# =========================
# Paths
# =========================
INPUT_PATH = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\ebay_orders.json"
OUTPUT_PATH = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\parsed_orders.json"


# =========================
# Helper Functions
# =========================
def format_words(text):
    """Capitalize each word and remove commas, full stops, and extra spaces."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[.,]", "", text)  # Remove commas and full stops
    return " ".join(word.capitalize() for word in text.strip().split())

def validate_and_format_postcode(postcode):
    """Validate and format a UK postcode using Postcodes.io API."""
    cleaned_postcode = postcode.replace(" ", "").upper()
    url = f"https://api.postcodes.io/postcodes/{cleaned_postcode}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["result"]["postcode"]
    except requests.RequestException as e:
        print(f"[Postcode API Error] {e}")
        return postcode  # Return original if API fails


# =========================
# Main Parsing Logic
# =========================
with open(INPUT_PATH, "r") as f:
    response = json.load(f)

orders = response.get("orders", [])
parsed_orders = []

for order in orders:
    ship_to = order.get("fulfillmentStartInstructions", [{}])[0].get("shippingStep", {}).get("shipTo", {})
    addr = ship_to.get("contactAddress", {})

    # Check for required fields
    required_fields = ["fullName", "addressLine1", "city", "postalCode", "countryCode"]
    missing = [field for field in required_fields if not (ship_to.get(field) or addr.get(field))]
    if not ship_to.get("primaryPhone", {}).get("phoneNumber"):
        missing.append("phoneNumber")
    if missing:
        print(f"[Skipped] Order {order.get('orderId', 'Unknown')} missing: {', '.join(missing)}")
        continue

    # Format postcode and clean addressLine2
    formatted_postcode = validate_and_format_postcode(addr.get("postalCode", ""))
    address_line2 = " ".join(word for word in addr.get("addressLine2", "").split() if "ebay" not in word.lower())

    # Parse each line item in the order
    for item in order.get("lineItems", []):
        parsed_orders.append({
            "order_id": order.get("orderId", ""),
            "full_name": format_words(ship_to["fullName"]),
            "address_line1": format_words(addr["addressLine1"]),
            "address_line2": format_words(address_line2),
            "city": format_words(addr["city"]),
            "postal_code": formatted_postcode,
            "country": addr["countryCode"],
            "phone": ship_to.get("primaryPhone", {}).get("phoneNumber", ""),
            "quantity": item.get("quantity", 0),
            "item_title": item.get("title", "Unknown Item"),
            "item_cost": item.get("lineItemCost", {}).get("value", "0.00"),
            "item_id": item.get("legacyItemId", ""),
            "variation_id": item.get("legacyVariationId", ""),
            "variation_aspects": item.get("variationAspects", [])
        })


# =========================
# Save Result
# =========================
with open(OUTPUT_PATH, "w") as f:
    json.dump(parsed_orders, f, indent=4)

print("Orders parsed.")