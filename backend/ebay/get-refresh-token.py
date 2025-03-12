import requests

# eBay OAuth token endpoint
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

# eBay API Credentials (Replace these with actual values)
CLIENT_ID = "AlexSaga-DropVaul-PRD-5deb947bc-5f49e26a"  # eBay App ID
CLIENT_SECRET = "PRD-deb947bc0570-5952-4a60-963f-ef77"  # eBay Cert ID
REDIRECT_URI = "Alex_Sagar-AlexSaga-DropVa-zoofzng"  # Your redirect URI

# Extracted Authorization Code from eBay redirect URL
AUTH_CODE = "v^1.1#i^1#f^0#r^1#p^3#I^3#t^Ul41XzY6OTc5REM5QTRCNzc5Q0E5NkVFNUQ1NTFCMUM4RDgzODdfMF8xI0VeMjYw"  # Replace with your actual auth code

# Headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Request body
data = {
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "redirect_uri": REDIRECT_URI
}

# Make request
response = requests.post(TOKEN_URL, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))

# Handle response
if response.status_code == 200:
    response_json = response.json()
    refresh_token = response_json.get("refresh_token")

    if refresh_token:
        print(f"New Refresh Token: {refresh_token}")
        
        # Save the refresh token for later use
        with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\r_token.txt", "w") as f:
            f.write(refresh_token)
    else:
        print("Error: Refresh token not found in the response.")
else:
    print(f"Error: {response.status_code}, {response.text}")