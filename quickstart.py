import gspread

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

# Open the target spreadsheet
sh = gc.open("mini automation test")
sh_wks = sh.sheet1

# Open the source spreadsheet by URL
sh1 = gc.open_by_url('https://docs.google.com/spreadsheets/d/12bxgz1snvoaxDfy0Lg8002YhaWWtQKOyfQWo33lVDUA/edit?gid=0#gid=0')

# Get data from the source sheets
cvs_data = sh1.sheet1.get("A1:BF812")
sh1_wks2 = sh1.worksheet("Bonus Rewards - Dispersal")
bonus_data = sh1_wks2.get("A1:BF812")
sh1_wks3 = sh1.worksheet("Data Rewards - Dispersal")
data_data = sh1_wks3.get("A1:BF812")

# Update the target spreadsheet with the retrieved data
sh_wks.update(range_name="A1", values=cvs_data)
sh_wks2 = sh.worksheet("Bonus Rewards")
sh_wks2.update(range_name="A1", values=bonus_data)
sh_wks3 = sh.worksheet("Data Rewards")
sh_wks3.update(range_name="A1", values=data_data)

print("Updated the main sheet, Bonus Rewards, and Data Rewards with source data.")

# Open the LongFi Xnet Rev Shares Database spreadsheet
sh2 = gc.open("LongFi Xnet Rev Shares Database")

# Get data from the "XNET CVS Ledger" sheet
xnet_cvs_ledger_data = sh2.worksheet('XNET CVS Ledger').get_all_values()
print("Retrieved XNET CVS Ledger data from LongFi Xnet Rev Shares Database")

# Convert the data to a dictionary for fast lookup
lookup_dict = {}
for row in xnet_cvs_ledger_data[1:]:
    lookup_dict[row[2]] = row  # Assuming the Radio ID is in the third column (C)

# Function to perform VLOOKUP manually in Python
def vlookup(lookup_value, lookup_dict, col_index):
    if lookup_value in lookup_dict:
        return lookup_dict[lookup_value][col_index - 1]
    return None

# Determine the indices of the columns to update
header_row = sh_wks.row_values(1)
epoch_columns = {
    'Epoch 14': header_row.index('Epoch 14') + 1,
    'Epoch 15': header_row.index('Epoch 15') + 1,
    'Epoch 16': header_row.index('Epoch 16') + 1
}

# Update the target sheet with VLOOKUP results
for row_idx in range(3, len(sh_wks.get_all_values()) + 1):
    radio_id = sh_wks.cell(row_idx, 1).value  # Column A (Radio ID)
    for epoch_name, col_idx in epoch_columns.items():
        epoch_index = header_row.index(epoch_name) + 1
        result = vlookup(radio_id, lookup_dict, epoch_index)
        if result is not None:
            sh_wks.update_cell(row_idx, col_idx, result)
            print(f"Updated cell ({row_idx}, {col_idx}) with value {result}")

print("Completed updating the target sheet with VLOOKUP results")
