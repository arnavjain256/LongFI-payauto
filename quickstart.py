import gspread
from collections import defaultdict


credentials = {
    "installed":{
        "client_id":"897141788662-2u9ion3pugjoqj5tichb6qpene5g8bot.apps.googleusercontent.com",
        "project_id":"payment-automation-428216",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"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",
        "redirect_uris":["http://localhost"]
        }
}

gc, authorized_user = gspread.oauth_from_dict(credentials)


sh = gc.open("Payment Automation Test")

sh_wks = sh.sheet1

sh1 = gc.open_by_url('https://docs.google.com/spreadsheets/d/12bxgz1snvoaxDfy0Lg8002YhaWWtQKOyfQWo33lVDUA/edit?gid=0#gid=0')

sh1_wks1 = sh1.sheet1

cvs_data = sh1_wks1.get("A1:BF812")

sh1_wks2 = sh1.worksheet("Bonus Rewards - Dispersal")

bonus_data = sh1_wks2.get("A1:BF812")

sh1_wks3 = sh1.worksheet("Data Rewards - Dispersal")

data_data = sh1_wks3.get("A1:BF812")

sh_wks.update(cvs_data, "A1")

sh_wks2 = sh.worksheet("Bonus Rewards")

sh_wks2.update(bonus_data, "A1")

sh_wks3 = sh.worksheet("Data Rewards")

sh_wks3.update(data_data, "A1")

sh_wks4 = sh.worksheet("Epoch Earnings")

start_cell = 'E3'

end_cell = 'BF812'

cell_range = sh_wks.range(f'{start_cell}:{end_cell}')

for cell in cell_range:
    if cell.value.__contains__("-"):
        cell.value = "0"

sh_wks.update_cells(cell_range)

cell_range2 = sh_wks2.range(f'{start_cell}:{end_cell}')

for cell in cell_range2:
    if cell.value.__contains__("-"):
        cell.value = "0"

sh_wks2.update_cells(cell_range2)

cell_range3 = sh_wks3.range(f'{start_cell}:{end_cell}')

for cell in cell_range3:
    if cell.value.__contains__("-"):
        cell.value = "0"

sh_wks3.update_cells(cell_range3)

gateway_list = sh_wks4.col_values(3)

for row, value in enumerate(gateway_list):
    clean = value.strip()
    if clean != value:
        sh_wks4.update_cell(row + 1, 3, clean)



sh_wks5 = sh.worksheet("Gateway Earnings")

source_spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1EghS37A_8Nyw7hpWgzZS795-vK6ZAJEozCyapvaEml8/edit?gid=1421353283#gid=1421353283'
source_sh = gc.open_by_url(source_spreadsheet_url)

# Specify the sheet within the spreadsheet
source_sheet_name = 'Epoch Earnings'  # Replace with your actual sheet name
source_sh_wks = source_sh.worksheet(source_sheet_name)

header_row = [header.strip() for header in source_sh_wks.row_values(2)]  # Adjusted to row 2


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

# Update the "Gateway Earnings" sheet with the prepared data
sh_wks5.update("A2", gateway_earnings_data)
print("Updated Gateway Earnings sheet with aggregated results")

val = list(range(2, 42))

list_range = 'B1:AO1'

sh_wks5.update(list_range, [val])

shares = gc.open_by_url('https://docs.google.com/spreadsheets/d/1EghS37A_8Nyw7hpWgzZS795-vK6ZAJEozCyapvaEml8/edit?gid=0#gid=0')

shares_longfiwks = shares.worksheet('Shares')

#shares_protocol = shares_longfiwks.get("A1:K123")

sh_shares = sh.worksheet("Shares")

#sh_shares.update(shares_protocol, "A1")

shares_epoch = shares_longfiwks.get("N1:BB1")

sh_shares.update(shares_epoch, "N1")



