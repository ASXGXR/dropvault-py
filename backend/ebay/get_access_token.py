import os
import requests
from datetime import datetime, timedelta

#######################
##  EBAY API ACCESS  ##
#######################

debug = False
CLIENT_ID = "AlexSaga-DropVaul-PRD-5deb947bc-5f49e26a"
CLIENT_SECRET = "PRD-deb947bc0570-5952-4a60-963f-ef77"
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

root_dir = os.getcwd()  # Get current working directory
base_path = rf"{root_dir}\backend\ebay"

def getAccessToken():
    token_file = os.path.join(base_path, "a_token_refresh_time.txt")
    access_token_file = os.path.join(base_path, "a_token.txt")

    current_time = datetime.now()
    with open(token_file, "r") as file:
        last_refresh_time = datetime.strptime(file.read().strip(), "%Y-%m-%d %H:%M:%S")
    # Refresh if 1 hour passed
    if current_time > last_refresh_time + timedelta(hours=1):
        if debug:
            print("Refreshing access token...")
        return refreshAccessToken()  # Return new token directly

    # Load and return existing access token
    with open(access_token_file, "r") as f:
        return f.read().strip()


def refreshAccessToken():
    refresh_token_file = os.path.join(base_path, "r_token.txt")
    access_token_file = os.path.join(base_path, "a_token.txt")
    refresh_time_file = os.path.join(base_path, "a_token_refresh_time.txt")

    # Load refresh token
    with open(refresh_token_file, "r") as f:
        REFRESH_TOKEN = f.read().strip()

    # Request new access token
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    # Save new token if successful
    if response.status_code == 200:
        new_access_token = response.json()["access_token"]
        with open(access_token_file, "w") as f:
            f.write(new_access_token)
        if debug:
            print("New access token saved to file.")
        # Log refresh time
        with open(refresh_time_file, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return new_access_token  # Return token directly
    else:
        print(f"Error: {response.status_code}, {response.text}")


def getRefreshToken(AUTH_CODE):
    # Example:
    # AUTH_CODE = "v^1.1#i^1#f^0#r^1#p^3#I^3#t^Ul41XzY6OTc5REM5QTRCNzc5Q0E5NkVFNUQ1NTFCMUM4RDgzODdfMF8xI0VeMjYw"

    refresh_token_file = os.path.join(base_path, "r_token.txt")
    REDIRECT_URI = "Alex_Sagar-AlexSaga-DropVa-zoofzng"

    # Request refresh token
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "authorization_code", "code": AUTH_CODE, "redirect_uri": REDIRECT_URI},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    # Save refresh token if successful
    if response.status_code == 200:
        refresh_token = response.json().get("refresh_token")
        if refresh_token:
            with open(refresh_token_file, "w") as f:
                f.write(refresh_token)
            print(f"New Refresh Token: {refresh_token}")
        else:
            print("Error: No refresh token in response.")
    else:
        print(f"Error: {response.status_code}, {response.text}")