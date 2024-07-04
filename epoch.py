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

# Authorize the client
gc, authorized_user = gspread.oauth_from_dict(credentials)

# Open the source spreadsheet by URL or name
source_spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1EghS37A_8Nyw7hpWgzZS795-vK6ZAJEozCyapvaEml8/edit?gid=1421353283#gid=1421353283'
source_sh = gc.open_by_url(source_spreadsheet_url)

# Specify the sheet within the spreadsheet
source_sheet_name = 'Epoch Earnings'  # Replace with your actual sheet name
source_sh_wks = source_sh.worksheet(source_sheet_name)

# Print and debug the header row from the source spreadsheet
header_row = [header.strip() for header in source_sh_wks.row_values(2)]  # Adjusted to row 2
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
