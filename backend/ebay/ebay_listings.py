import os
import json
from ebaysdk.trading import Connection as Trading

base_path = r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay"

####################
##  GET LISTINGS  ##
####################

def getListings(EBAY_ACCESS_TOKEN,debug):
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
        return parseListings(all_listings,debug)

    except Exception as e:
        print(f"[ERROR] Unable to retrieve eBay listings: {e}")
        return []  # Return empty list if error


######################
##  PARSE LISTINGS  ##
######################

def parseListings(all_listings,debug):
    listings_json_path = os.path.join(base_path, "listings.json")
    existing_aliexpress = {item.get("item_id", ""): item for item in all_listings}  # Index by item_id

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

        # Handle variations
        variations = listing.get("Variations", {}).get("Variation", [])
        variations = [variations] if isinstance(variations, dict) else variations
        if variations:
            for var in variations:
                specifics = var.get("VariationSpecifics", {}).get("NameValueList", [])
                specifics = [specifics] if isinstance(specifics, dict) else specifics
                for s in specifics:
                    name, value = s.get("Name"), s.get("Value")
                    if name and value:
                        # Link existing ali-value if exists
                        existing_var_ali = next((v.get("ali-value", "") for v in existing_variations.get(name, []) if v.get("value") == value), "")
                        filtered["variations"].setdefault(name, []).append({"value": value, "ali-value": existing_var_ali})
        else:
            filtered["ali-value"] = existing_ali_value  # No variations case

        filtered_listings.append(filtered)  # Add to final list

    # Save parsed listings
    with open(listings_json_path, 'w') as outfile:
        json.dump(filtered_listings, outfile, indent=4)

    if debug:
        print(f"{len(filtered_listings)} listings parsed and saved.")