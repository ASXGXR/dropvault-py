from datetime import datetime
import requests
import os

# python backend/ebay/refresh-access-token.py

# eBay OAuth token endpoint
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

# Credentials
CLIENT_ID = "AlexSaga-DropVaul-PRD-5deb947bc-5f49e26a"
CLIENT_SECRET = "PRD-deb947bc0570-5952-4a60-963f-ef77"
REFRESH_TOKEN = open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\r_token.txt").read().strip()

# Request headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Request body
data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}

# Make request to get a new access token
response = requests.post(TOKEN_URL, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))

# Handle response
if response.status_code == 200:
    new_access_token = response.json()["access_token"]
    print(f"New access token saved to file.")
    os.chdir(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay")
    with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\a_token.txt", 'w') as f:
      f.write(new_access_token)
else:
    print(f"Error: {response.status_code}, {response.text}")

# Write current time to the file
current_time = datetime.now()
with open(r"C:\Users\44755\3507 Dropbox\Alex Sagar\WEBSITES\dropvault-py\backend\ebay\a_token_refresh_time.txt", "w") as file:
    file.write(current_time.strftime("%Y-%m-%d %H:%M:%S"))