import os
import json
from ebaysdk.trading import Connection as Trading

root_dir = os.getcwd()  # Get current working directory
base_path = rf"{root_dir}\backend\ebay"

####################
##  GET LISTINGS  ##
####################

def getListings(EBAY_ACCESS_TOKEN, debug):
    try:
        # eBay API credentials
        EBAY_APP_ID = 'AlexSaga-DropVaul-PRD-5deb947bc-5f49e26a'
        EBAY_CERT_ID = 'PRD-deb947bc0570-5952-4a60-963f-ef77'
        EBAY_DEV_ID = 'f08e4a91-97f3-4c8f-a921-88b2b20b6610'

        # Trading API connection
        api = Trading(
            appid=EBAY_APP_ID,
            certid=EBAY_CERT_ID,
            devid=EBAY_DEV_ID,
            token=EBAY_ACCESS_TOKEN,
            config_file=None
        )

        # Loop through pages of active listings
        page = 1
        all_listings = []
        while True:
            response = api.execute('GetMyeBaySelling', {
                'ActiveList': {
                    'Include': True,
                    'Pagination': {
                        'EntriesPerPage': 100,
                        'PageNumber': page
                    }
                }
            })
            data = response.dict()
            items = data.get('ActiveList', {}).get('ItemArray', {}).get('Item', [])

            # Normalize single dict to list
            if isinstance(items, dict):
                items = [items]
            all_listings.extend(items)

            # Stop if last page
            total_pages = int(data.get('ActiveList', {}).get('PaginationResult', {}).get('TotalNumberOfPages', 1))
            if page >= total_pages:
                break
            page += 1

        # Save raw listings to file
        raw_listings_path = os.path.join(base_path, "raw_listings.json")
        with open(raw_listings_path, 'w') as outfile:
            json.dump(all_listings, outfile, indent=4)

        if debug:
            print(f"✅ {len(all_listings)} listings retrieved and saved to raw_listings.json.")

        # Return Parsed Listings
        return parseListings(all_listings, debug)

    except Exception as e:
        print(f"[ERROR] Unable to retrieve eBay listings: {e}")
        return []  # Return empty list if error


######################
##  PARSE LISTINGS  ##
######################

def parseListings(all_listings, debug):
    listings_json_path = os.path.join(base_path, "listings.json")

    # ✅ Loads listings.json to retain ali-values
    if os.path.exists(listings_json_path):
        with open(listings_json_path, encoding='utf-8') as f:
            existing_data = json.load(f)
        existing_aliexpress = {item.get("item_id", ""): item for item in existing_data}
    else:
        existing_aliexpress = {}

    filtered_listings = []

    for listing in reversed(all_listings):  # Reverse to maintain order
        item_id = listing.get("ItemID", "")
        existing_item = existing_aliexpress.get(item_id, {})
        existing_variations = existing_item.get("variations", {})
        existing_ali_value = existing_item.get("ali-value", "")

        # Base listing structure
        filtered = {
            "item_id": item_id,
            "title": listing.get("Title", ""),
            "item_url": listing.get("ListingDetails", {}).get("ViewItemURL", ""),
            "price": listing.get("BuyItNowPrice", {}).get("value", ""),
            "image_url": listing.get("PictureDetails", {}).get("GalleryURL", ""),
            "aliexpress_url": existing_item.get("aliexpress_url", ""),
            "variations": {}
        }

        # Handle variations, collecting unique options
        variations = listing.get("Variations", {}).get("Variation", [])
        variations = [variations] if isinstance(variations, dict) else variations

        variation_options = {}  # To collect unique values per variation name

        if variations:
            for var in variations:
                specifics = var.get("VariationSpecifics", {}).get("NameValueList", [])
                specifics = [specifics] if isinstance(specifics, dict) else specifics
                for s in specifics:
                    name, value = s.get("Name"), s.get("Value")
                    if name and value:
                        # Initialise set for each variation name
                        variation_options.setdefault(name, set()).add(value)

            # Build final variation structure and link existing ali-values
            for name, values in variation_options.items():
                filtered["variations"][name] = []
                for value in sorted(values):  # Sorted to keep consistent order
                    existing_var_ali = next(
                        (v.get("ali-value", "") for v in existing_variations.get(name, []) if v.get("value") == value),
                        ""
                    )
                    filtered["variations"][name].append({"value": value, "ali-value": existing_var_ali})
        else:
            # If no variations, keep existing ali-value if any
            filtered["ali-value"] = existing_ali_value

        filtered_listings.append(filtered)  # Add to final list

    # Save parsed listings
    with open(listings_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(filtered_listings, outfile, indent=4, ensure_ascii=False)

    if debug:
        print(f"✅ {len(filtered_listings)} listings parsed and saved to listings.json.")

    return filtered_listings