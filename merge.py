import requests
import pandas as pd
import json
from datetime import datetime
from bs4 import BeautifulSoup

# File paths
file_path = 'MokenData.xlsx'
output_file_path = 'JulyData_with_titles.csv'
webpage_url = 'https://explorer.moken.io/wallets/Fz85mw5jedQnzF4nDq8PfwqzXtsRETTcLHFjHNKSH9Xq?lat=17.063447747849768&lng=-96.72745154992164&zoom=12&layer=active-hotspots&filter=total'

# Read the existing Excel file
df = pd.read_excel(file_path)

# API base URL and parameters
base_url = 'https://api.heliumgeek.com/v0/gateways/'
address_column = 'Address'
params = {
    "min_time": "2024-07-01T00:00:00.000Z",
    "max_time": "2024-07-18T00:00:00.000Z",
    "bucket": "month"
}
headers = {
    "x-api-key": "truK64nJ2-Te-G04wZCf7mqtr4N5HmTon5VYL633jik"
}

# Fetch and parse the webpage content
response = requests.get(webpage_url)
if response.status_code != 200:
    print(f"Failed to fetch the webpage. Status code: {response.status_code}")
    exit()
soup = BeautifulSoup(response.content, 'html.parser')

# Define the selectors to extract addresses and titles
address_selector = 'h2'
title_selector = 'h1'

# Dictionary to store address-title mapping
address_title_map = {}
addresses = soup.select(address_selector)

for address_elem in addresses:
    address = address_elem.get_text(strip=True)
    title_elem = address_elem.find_previous(title_selector)
    title = title_elem.get_text(strip=True) if title_elem else 'No Title'
    address_title_map[address] = title

# Prepare data list
data = []

# Iterate over each address and fetch data from the API
for index, row in df.iterrows():
    address = row[address_column]
    url = f"{base_url}{address}/mobile/data/sum"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response_data = response.json()
        for item in response_data:
            start_timestamp = item.get("startTimestamp")
            start_datetime = datetime.fromtimestamp(start_timestamp).isoformat() if start_timestamp else None

            data.append({
                "Title": address_title_map.get(address, 'No Title'),
                "Address": address,
                "startTimestamp": start_datetime,
                "dcSum": item.get("dcSum"),
                "uploadBytesSum": item.get("uploadBytesSum"),
                "downloadBytesSum": item.get("downloadBytesSum"),
                "rewardableBytesSum": item.get("rewardableBytesSum")
            })
    else:
        data.append({
            "Title": address_title_map.get(address, 'No Title'),
            "Address": address,
            "startTimestamp": None,
            "dcSum": None,
            "uploadBytesSum": None,
            "downloadBytesSum": None,
            "rewardableBytesSum": None,
            "error": response.status_code,
            "message": response.text
        })

# Create DataFrame and write to CSV
output_df = pd.DataFrame(data)

numeric_columns = ["dcSum", "uploadBytesSum", "downloadBytesSum", "rewardableBytesSum"]
output_df[numeric_columns] = output_df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)

output_df.to_csv(output_file_path, index=False)

print(f"Data has been written to {output_file_path}")
