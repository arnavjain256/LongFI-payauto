import os
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Define the API key and base endpoint
api_key = 'truK64nJ2-Te-G04wZCf7mqtr4N5HmTon5VYL633jik'
base_api_url = 'https://api.heliumgeek.com/v0/gateways/{}/mobile/data/sum?min_time=2024-07-01T00%3A00%3A00.000Z&max_time=2024-07-16T00%3A00%3A00.000Z&bucket=day'

# Set up headers
headers = {
    'x-api-key': api_key
}

# Set up retries with exponential --- makes sure we try multipme times
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://", adapter)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(creds)


print("Available sheets:")
for sheet in client.openall():
    print(f"'{sheet.title}' (length: {len(sheet.title)})")

# Open the Google Sheets document
try:
    sheet = client.open("Hotspot").sheet1
    print("Successfully opened the 'Hotspot' sheet")
except gspread.SpreadsheetNotFound:
    print("Spreadsheet 'Hotspot' not found. Please check the name and share permissions.")
    exit()

# Check if the CSV file exists
csv_file = 'rewards.csv'
if not os.path.isfile(csv_file):
    print(f"CSV file '{csv_file}' not found. Please check the file name and path.")
    exit()

# Check if the CSV file is empty
if os.path.getsize(csv_file) == 0:
    print(f"CSV file '{csv_file}' is empty. Please check the file content.")
    exit()

# Read the CSV file containing the list of hotspot addresses, we made sure to skip the first 4 rows
try:
    hotspot_addresses = pd.read_csv(csv_file, skiprows=4)
    if hotspot_addresses.empty:
        print(f"CSV file '{csv_file}' is empty. Please check the file content.")
        exit()
except pd.errors.EmptyDataError:
    print(f"CSV file '{csv_file}' has no columns to parse. Please check the file content.")
    exit()

# Debug: Print the first few rows and column names of the DataFrame
print("DataFrame columns:", hotspot_addresses.columns.tolist())
print("DataFrame head:\n", hotspot_addresses.head())

# Create a list to store the collected data
collected_data = []

# Prepare the header row and data
header = ['ID', 'Address', 'Start Timestamp', 'DC Sum', 'Upload Bytes Sum', 'Download Bytes Sum', 'Rewardable Bytes Sum']
collected_data.append(header)

# Iterate through each address and make the API request
for index, row in hotspot_addresses.iterrows():
    try:
        address = row['Address']
    except KeyError:
        print("Column 'Address' not found in the CSV file. Please check the column names.")
        exit()

    api_url = base_api_url.format(address)
    try:
        response = session.get(api_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {address}. Error: {e}")
        continue
    
    data = response.json()
    print(f"Successfully fetched data for {address}")  # Summarize the success message
    # Assuming the API returns a list of dictionaries, each representing a day
    for entry in data:
        start_timestamp = entry.get('startTimestamp', 0)
        dc_sum = entry.get('dcSum', 0)
        upload_bytes_sum = entry.get('uploadBytesSum', 0)
        download_bytes_sum = entry.get('downloadBytesSum', 0)
        rewardable_bytes_sum = entry.get('rewardableBytesSum', 0)
        collected_data.append([index + 1, address, start_timestamp, dc_sum, upload_bytes_sum, download_bytes_sum, rewardable_bytes_sum])


sheet.clear()


sheet.update('A1', collected_data)

print("Data collection complete. The results have been saved to your Google Sheet.")
