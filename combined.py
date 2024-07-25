import gspread
from collections import defaultdict

# Define credentials
credentials = {
  "installed": {
    "client_id": "757406773741-rnk2g858gtqig4iqa1bgkdgcqafr0dfm.apps.googleusercontent.com",
    "project_id": "paymenttool",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "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",
    "redirect_uris": ["http://localhost"]
  }
}

gc, authorized_user = gspread.oauth_from_dict(credentials)
print(type(gc))

# Open the source and destination spreadsheets
mini_automation_sh = gc.open("mini automation test")
longfi_db_sh = gc.open("LongFi Xnet Rev Shares Database")

# Get or create the "sharesMini" worksheet in the destination spreadsheet
try:
    shares_wks = mini_automation_sh.worksheet("sharesMini")
except gspread.exceptions.WorksheetNotFound:
    shares_wks = mini_automation_sh.add_worksheet(title="sharesMini", rows="1000", cols="26")

# Get the source worksheet
longfi_shares_wks = longfi_db_sh.worksheet("Shares")
longfi_shares_data = longfi_shares_wks.get_all_values()

# Define the columns to copy
columns_to_copy = [
    'Protocol', 'Equipment Identifier', 'Equipment Owner', 'Status',
    'Participant', 'Participant Type', 'RevShareType', 'Rev Share',
    'Cash Lease', 'Address', 'City', 'Token', 'Date Installed'
]

# Define the columns for epoch earnings
epoch_columns_to_sum = ['Epoch 09-13'] + [f'Epoch {i}' for i in range(14, 41)]

# Extract the headers and data
shares_header = longfi_shares_data[0]
shares_data = longfi_shares_data[1:]

# Find the indices of the columns to copy
indices_to_copy = [shares_header.index(col) for col in columns_to_copy]
epoch_indices_to_sum = [shares_header.index(col) for col in epoch_columns_to_sum]

# Create the new header and data based on the selected columns
new_shares_header = [shares_header[idx] for idx in indices_to_copy]
new_shares_header.append('Total Sum')

new_shares_data = []

for row in shares_data:
    new_row = [row[idx] for idx in indices_to_copy]
    total_sum = sum(
        float(row[idx].replace(',', '')) 
        for idx in epoch_indices_to_sum 
        if row[idx] and row[idx] not in ['-', '#N/A']
    )
    new_row.append(total_sum)
    new_shares_data.append(new_row)

# Insert the new header at the beginning of the data
new_shares_data.insert(0, new_shares_header)

# Clear the existing content in the "sharesMini" worksheet
shares_wks.clear()

# Update the "sharesMini" worksheet with the selected columns and total sum
shares_wks.update('A1', new_shares_data)
print("Updated 'sharesMini' worksheet in 'mini automation test' with selected columns and total sum from 'LongFi Xnet Rev Shares Database'")

# Open the source spreadsheet by URL or name
source_spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1EghS37A_8Nyw7hpWgzZS795-vK6ZAJEozCyapvaEml8/edit?gid=1421353283#gid=1421353283'
source_sh = gc.open_by_url(source_spreadsheet_url)

# Specify the sheet within the spreadsheet
source_sheet_name = 'Epoch Earnings'
source_sh_wks = source_sh.worksheet(source_sheet_name)

# Print and debug the header row from the source spreadsheet
header_row = [header.strip() for header in source_sh_wks.row_values(2)]
print("Trimmed Header row:", header_row)

# Ensure that the header row contains the expected columns
required_columns = ['Gateway', 'Radio ID']
missing_columns = [col for col in required_columns if col not in header_row]

if missing_columns:
    raise ValueError(f"Missing columns in header row: {missing_columns}")

# Get all data from the source sheet
all_values = source_sh_wks.get_all_values()

# Create a dictionary to hold the aggregated data
gateway_earnings = defaultdict(lambda: defaultdict(int))

# Identify the columns
gateway_idx = header_row.index('Gateway')
epoch_columns = {header: idx for idx, header in enumerate(header_row) if 'Epoch' in header}

# Aggregate earnings per gateway
for row in all_values[2:]:  # Skip header row and row before
    gateway = row[gateway_idx]
    for epoch, idx in epoch_columns.items():
        try:
            earnings = int(row[idx].replace(',', ''))
        except ValueError:
            earnings = 0
        gateway_earnings[gateway][epoch] += earnings

# Prepare data for "Gateway Earnings" sheet
gateway_earnings_data = [['Gateway'] + list(epoch_columns.keys())]
for gateway, earnings in gateway_earnings.items():
    row = [gateway] + [earnings[epoch] for epoch in epoch_columns.keys()]
    gateway_earnings_data.append(row)

# Open the target spreadsheet where the "Gateway Earnings" sheet will be created/updated
target_spreadsheet = gc.open("mini automation test")

# Create a new sheet for "Gateway Earnings" if it doesn't exist
try:
    gateway_earnings_sheet = target_spreadsheet.worksheet("Gateway Earnings")
    target_spreadsheet.del_worksheet(gateway_earnings_sheet)
    gateway_earnings_sheet = target_spreadsheet.add_worksheet(title="Gateway Earnings", rows="1000", cols="26")
except gspread.exceptions.WorksheetNotFound:
    gateway_earnings_sheet = target_spreadsheet.add_worksheet(title="Gateway Earnings", rows="1000", cols="26")

# Update the "Gateway Earnings" sheet with the prepared data
gateway_earnings_sheet.update("A1", gateway_earnings_data)
print("Updated Gateway Earnings sheet with aggregated results")

# Open the source spreadsheet containing the additional data sheets
additional_source_sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/12bxgz1snvoaxDfy0Lg8002YhaWWtQKOyfQWo33lVDUA/edit?gid=0#gid=0')

# Get the source worksheets and data
sh1_wks1 = additional_source_sh.sheet1
cvs_data = sh1_wks1.get("A1:BF812")

sh1_wks2 = additional_source_sh.worksheet("Bonus Rewards - Dispersal")
bonus_data = sh1_wks2.get("A1:BF812")

sh1_wks3 = additional_source_sh.worksheet("Data Rewards - Dispersal")
data_data = sh1_wks3.get("A1:BF812")

# Update the "cvs_data", "Bonus Rewards", and "Data Rewards" sheets in the destination spreadsheet
sh_wks = mini_automation_sh.sheet1
sh_wks.update("A1", cvs_data)

sh_wks2 = mini_automation_sh.worksheet("Bonus Rewards")
sh_wks2.update("A1", bonus_data)

sh_wks3 = mini_automation_sh.worksheet("Data Rewards")
sh_wks3.update("A1", data_data)

print("Updated 'cvs_data', 'Bonus Rewards', and 'Data Rewards' sheets in 'mini automation test' with data from the source spreadsheet")
