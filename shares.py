import gspread
from collections import defaultdict

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


mini_automation_sh = gc.open("mini automation test")

shares_wks = mini_automation_sh.add_worksheet(title="SharesLongFi", rows="1000", cols="26")


longfi_db_sh = gc.open("LongFi Xnet Rev Shares Database")

longfi_shares_wks = longfi_db_sh.worksheet("Shares")


longfi_shares_data = longfi_shares_wks.get_all_values()

shares_header = longfi_shares_data[0]
shares_data = longfi_shares_data[1:]


print("Shares Header from LongFi Database:", shares_header)

equipment_identifier_idx = shares_header.index('Equipment Identifier')
rev_share_idx = shares_header.index('Rev Share')

rev_share_dict = {}
for row in shares_data:
    try:
        equipment_identifier = row[equipment_identifier_idx]
        rev_share = float(row[rev_share_idx].strip('%')) / 100
        rev_share_dict[equipment_identifier] = rev_share
    except ValueError:
        print(f"Non-numeric value in 'Rev Share' column: {row[rev_share_idx]} for row: {row}")

gateway_earnings_wks = mini_automation_sh.worksheet("Gateway Earnings")

gateway_earnings_data = gateway_earnings_wks.get_all_values()

gateway_header_row = gateway_earnings_data[0]
gateway_earnings = gateway_earnings_data[1:]


gateway_idx = gateway_header_row.index('Gateway')
epoch_columns = {header: idx for idx, header in enumerate(gateway_header_row) if 'Epoch' in header}

earnings_per_gateway = []

for row in gateway_earnings:
    gateway = row[gateway_idx]
    rev_share = rev_share_dict.get(gateway, 0)
    total_earnings = sum(float(row[epoch_columns[epoch]].replace(',', '')) for epoch in epoch_columns if row[epoch_columns[epoch]])
    earnings = total_earnings * rev_share
    earnings_per_gateway.append([gateway, rev_share, earnings])


new_shares_header = ['Gateway', 'Rev Share', 'Earnings']
new_shares_data = [new_shares_header] + earnings_per_gateway


shares_wks.update('A1', new_shares_data)
print("Updated new Shares worksheet in 'mini automation test' with earnings per gateway")

