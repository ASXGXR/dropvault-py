import requests
import json
import re
import os

#########################
##  GETTING ORDERS     ##
#########################

with open(os.path.join(os.path.dirname(__file__), "..", "root_dir.txt")) as f:
    root_dir = f.read().strip()
base_path = rf"{root_dir}\backend\ebay"


def getOrders(EBAY_ACCESS_TOKEN,debug):
    """Fetch eBay orders & call parse function."""
    EBAY_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order"
    headers = {
        "Authorization": f"Bearer {EBAY_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    params = {
        "limit": 10,
        "filter": "orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS}"
    }

    response = requests.get(EBAY_ORDERS_URL, headers=headers, params=params)

    if response.status_code == 200:
        orders = response.json().get("orders", [])
        raw_orders_path = os.path.join(base_path, "raw_orders.json")
        with open(raw_orders_path, "w") as f:
            json.dump(orders, f, indent=4)
        if debug:
            print(f"✅ {len(orders)} orders received and saved.")
        return parseOrders(orders,debug)  # Return parsed orders for downstream use
    else:
        print(f"[ERROR] Failed to fetch orders: {response.status_code} - {response.text}")
        return []  # Return empty list if failed


def parseOrders(orders,debug):
    """Parse each order & save to file."""
    output_path = os.path.join(base_path, "orders.json")
    parsed_orders = []

    # ----------------------
    # Helper functions
    # ----------------------
    def format_words(text):
        # Removes periods and commas, then capitalizes each word
        if not isinstance(text, str):
            return ""
        text = re.sub(r"[.,]", "", text).strip()
        return " ".join(word.capitalize() for word in text.split())

    def english_only(text):
        # Keep only English letters, spaces, hyphens, apostrophes, periods, and capitalize words
        if not isinstance(text, str):
            return ""
        clean = re.sub(r"[^A-Za-z\s\-'.]", "", text).strip()
        return " ".join(word.capitalize() for word in clean.split())

    def validate_and_format_postcode(postcode):
        """Format UK postcode using API, fallback to original if error."""
        cleaned_postcode = postcode.replace(" ", "").upper()
        url = f"https://api.postcodes.io/postcodes/{cleaned_postcode}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()["result"]["postcode"]
        except requests.RequestException:
            return postcode

    # ----------------------
    # Parse each order
    # ----------------------
    for order in orders:
        ship_to = order.get("fulfillmentStartInstructions", [{}])[0].get("shippingStep", {}).get("shipTo", {})
        addr = ship_to.get("contactAddress", {})

        # Check required fields
        required_fields = ["fullName", "addressLine1", "city", "postalCode", "countryCode"]
        missing = [field for field in required_fields if not (ship_to.get(field) or addr.get(field))]
        phone_number = ship_to.get("primaryPhone", {}).get("phoneNumber") or order.get("buyer", {}).get("buyerRegistrationAddress", {}).get("primaryPhone", {}).get("phoneNumber")
        if not phone_number:
            missing.append("phoneNumber")

        if missing:
            print(f"[Skipped] Order {order.get('orderId', 'Unknown')} missing: {', '.join(missing)}")
            continue

        # Format name
        names = english_only(ship_to["fullName"]).split() or ["TT", "TT"]
        full_name = " ".join([n*2 if len(n) == 1 else n for n in names]) # If name len=1, duplicate letter

        # Format address
        formatted_postcode = validate_and_format_postcode(addr.get("postalCode", ""))
        address_line2 = " ".join(word for word in addr.get("addressLine2", "").split() if "ebay" not in word.lower())

        # Parse items
        for item in order.get("lineItems", []):
            parsed_orders.append({
                "order_id": order.get("orderId", ""),
                "full_name": full_name,
                "address_line1": format_words(addr["addressLine1"]),
                "address_line2": address_line2,
                "city": format_words(addr["city"]),
                "postal_code": formatted_postcode,
                "country": addr["countryCode"],
                "phone": phone_number,
                "quantity": item.get("quantity", 0),
                "item_title": item.get("title", "Unknown Item"),
                "item_cost": item.get("lineItemCost", {}).get("value", "0.00"),
                "item_id": item.get("legacyItemId", ""),
                "variation_id": item.get("legacyVariationId", ""),
                "variation_aspects": item.get("variationAspects", [])
            })

    # ----------------------
    # Save parsed orders
    # ----------------------
    with open(output_path, "w") as f:
        json.dump(parsed_orders, f, indent=4)

    if debug:
        print(f"✅ {len(parsed_orders)} orders parsed and saved.")
    return parsed_orders  # Return for use elsewhere