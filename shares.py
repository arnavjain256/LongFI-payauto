import gspread
from collections import defaultdict

# Credentials for OAuth
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
print(type(gc))

# Open the "mini automation test" spreadsheet
mini_automation_sh = gc.open("mini automation test")
# Create a new "Shares" worksheet within the same spreadsheet
shares_wks = mini_automation_sh.add_worksheet(title="SharesLongFi", rows="1000", cols="26")

# Open the "LongFi Xnet Rev Shares Database" spreadsheet
longfi_db_sh = gc.open("LongFi Xnet Rev Shares Database")
# Open the "Shares" worksheet from "LongFi Xnet Rev Shares Database"
longfi_shares_wks = longfi_db_sh.worksheet("Shares")

# Get all data from the "Shares" worksheet in the LongFi database
longfi_shares_data = longfi_shares_wks.get_all_values()

# Convert data to dictionaries for easier processing
shares_header = longfi_shares_data[0]
shares_data = longfi_shares_data[1:]

# Debugging prints to ensure correct headers
print("Shares Header from LongFi Database:", shares_header)

# Find the indexes of relevant columns in the Shares sheet
equipment_identifier_idx = shares_header.index('Equipment Identifier')
rev_share_idx = shares_header.index('Rev Share')

# Create a dictionary for rev share lookup using Equipment Identifier
rev_share_dict = {}
for row in shares_data:
    try:
        equipment_identifier = row[equipment_identifier_idx]
        rev_share = float(row[rev_share_idx].strip('%')) / 100
        rev_share_dict[equipment_identifier] = rev_share
    except ValueError:
        print(f"Non-numeric value in 'Rev Share' column: {row[rev_share_idx]} for row: {row}")

# Open the "Gateway Earnings" worksheet from "mini automation test"
gateway_earnings_wks = mini_automation_sh.worksheet("Gateway Earnings")
# Get all data from the "Gateway Earnings" worksheet
gateway_earnings_data = gateway_earnings_wks.get_all_values()

# Convert data to dictionaries for easier processing
gateway_header_row = gateway_earnings_data[0]
gateway_earnings = gateway_earnings_data[1:]

# Find the indexes of relevant columns in the Gateway Earnings sheet
gateway_idx = gateway_header_row.index('Gateway')
epoch_columns = {header: idx for idx, header in enumerate(gateway_header_row) if 'Epoch' in header}

# Calculate earnings for each gateway
earnings_per_gateway = []

for row in gateway_earnings:
    gateway = row[gateway_idx]
    rev_share = rev_share_dict.get(gateway, 0)
    total_earnings = sum(float(row[epoch_columns[epoch]].replace(',', '')) for epoch in epoch_columns if row[epoch_columns[epoch]])
    earnings = total_earnings * rev_share
    earnings_per_gateway.append([gateway, rev_share, earnings])

# Prepare data to update the new "Shares" worksheet
new_shares_header = ['Gateway', 'Rev Share', 'Earnings']
new_shares_data = [new_shares_header] + earnings_per_gateway

# Update the new "Shares" worksheet with the calculated data
shares_wks.update('A1', new_shares_data)
print("Updated new Shares worksheet in 'mini automation test' with earnings per gateway")
