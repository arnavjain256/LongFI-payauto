import os
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


api_key = 'truK64nJ2-Te-G04wZCf7mqtr4N5HmTon5VYL633jik'
data_api_url = 'https://api.heliumgeek.com/v0/gateways/{}/mobile/data/sum?min_time=2024-07-01T00%3A00%3A00.000Z&max_time=2024-07-30T00%3A00%3A00.000Z&bucket=day'
details_api_url = 'https://api.heliumgeek.com/v0/gateways/{}'

# Set up headers
headers = {
    'x-api-key': api_key
}

# Set up retries with exponential backoff
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

try:
    sheet = client.open("Hotspot").sheet1
    print("Successfully opened the 'Hotspot' sheet")
except gspread.SpreadsheetNotFound:
    print("Spreadsheet 'Hotspot' not found. Please check the name and share permissions.")
    exit()

csv_file = 'rewards.csv'
if not os.path.isfile(csv_file):
    print(f"CSV file '{csv_file}' not found. Please check the file name and path.")
    exit()

# Check if the CSV file is empty
if os.path.getsize(csv_file) == 0:
    print(f"CSV file '{csv_file}' is empty. Please check the file content.")
    exit()


try:
    hotspot_addresses = pd.read_csv(csv_file, skiprows=4)
    if hotspot_addresses.empty:
        print(f"CSV file '{csv_file}' is empty. Please check the file content.")
        exit()
except pd.errors.EmptyDataError:
    print(f"CSV file '{csv_file}' has no columns to parse. Please check the file content.")
    exit()


print("DataFrame columns:", hotspot_addresses.columns.tolist())
print("DataFrame head:\n", hotspot_addresses.head())


collected_data = []

# Prepare the header row and data
header = ['ID', 'Address', 'Name', 'Epoch Number', 'Start Timestamp', 'End Timestamp', 'DC Sum', 'Upload Bytes Sum', 'Download Bytes Sum', 'Rewardable Bytes Sum', 'Latitude', 'Longitude']
collected_data.append(header)

def get_gateway_details(gateway_address):
    try:
        response = session.get(details_api_url.format(gateway_address), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch details for {gateway_address}. Error: {e}")
        return None


webpage_url = 'https://explorer.moken.io/wallets/Fz85mw5jedQnzF4nDq8PfwqzXtsRETTcLHFjHNKSH9Xq?lat=17.063447747849768&lng=-96.72745154992164&zoom=12&layer=active-hotspots&filter=total'
response = requests.get(webpage_url)
if response.status_code != 200:
    print(f"Failed to fetch the webpage. Status code: {response.status_code}")
    exit()
soup = BeautifulSoup(response.content, 'html.parser')

# Define the selectors to extract addresses and names
address_selector = 'h2'
name_selector = 'h1'

# Dictionary to store address-name mapping
address_name_map = {}
addresses = soup.select(address_selector)

for address_elem in addresses:
    address = address_elem.get_text(strip=True)
    name_elem = address_elem.find_previous(name_selector)
    name = name_elem.get_text(strip=True) if name_elem else 'No Name'
    address_name_map[address] = name

# Define the starting epoch date
epoch_start_date = datetime(2024, 7, 1)

row_id = 1
for index, row in hotspot_addresses.iterrows():
    try:
        address = row['Address']
    except KeyError:
        print("Column 'Address' not found in the CSV file. Please check the column names.")
        exit()

    # Get gateway details
    gateway_details = get_gateway_details(address)
    if not gateway_details:
        continue
    
    lat = gateway_details.get('location', {}).get('lat', 'No Latitude')
    lng = gateway_details.get('location', {}).get('lng', 'No Longitude')


    api_url = data_api_url.format(address)
    try:
        response = session.get(api_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {address}. Error: {e}")
        continue

    data = response.json()
    print(f"Successfully fetched data for {address}")  # Summarize the success message
    
    # Print the API response for each address
    print(f"API response for {address}: {data}")
    
    # Assuming the API returns a list of dictionaries, each representing a day
    for entry in data:
        start_timestamp = entry.get('startTimestamp', 0)
        dc_sum = entry.get('dcSum', 0)
        upload_bytes_sum = entry.get('uploadBytesSum', 0)
        download_bytes_sum = entry.get('downloadBytesSum', 0)
        rewardable_bytes_sum = entry.get('rewardableBytesSum', 0)

        # Calculate the end timestamp as one day from the start timestamp
        start_datetime = datetime.fromtimestamp(start_timestamp)
        end_datetime = start_datetime + timedelta(days=1)  # 1 day

        # Calculate the epoch number
        epoch_number = (end_datetime - epoch_start_date).days + 1

        start_datetime_iso = start_datetime.isoformat() if start_timestamp else None
        end_datetime_iso = end_datetime.isoformat() if start_timestamp else None

        name = address_name_map.get(address, 'No Name')
        collected_data.append([row_id, address, name, epoch_number, start_datetime_iso, end_datetime_iso, dc_sum, upload_bytes_sum, download_bytes_sum, rewardable_bytes_sum, lat, lng])
        row_id += 1

sheet.clear()

sheet.update('A1', collected_data)

print("Data collection complete. The results have been saved to your Google Sheet.")
