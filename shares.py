import gspread

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

# Add new worksheet in the destination spreadsheet
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

# Update the new worksheet with the selected columns and total sum
shares_wks.update('A1', new_shares_data)
print("Updated new Shares worksheet in 'mini automation test' with selected columns and total sum from 'LongFi Xnet Rev Shares Database'")