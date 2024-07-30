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


sh = gc.open("Payment Automation Test")
sh_wks = sh.worksheet('Shares')


def get_user_input():
    month = input("Enter Month: ").strip()
    epochs = input("Enter Epochs (comma-separated, e.g., 09-13,14,15): ").split(',')
    participants = input("Enter Participants (comma-separated): ").split(',')
    return month, [epoch.strip() for epoch in epochs], [participant.strip() for participant in participants]


def process_data(sh_wks, participant, epochs):
    data = sh_wks.get_all_values()
    headers = data[0]

    try:
        participant_col_idx = headers.index("Participant")
    except ValueError:
        print("Participant column not found")
        return 0

    epoch_indices = {}
    for epoch in epochs:
        try:
            epoch_indices[f'Epoch {epoch}'] = headers.index(f'Epoch {epoch}')
        except ValueError:
            print(f'Epoch {epoch} column not found')

    total_value = 0
    for row in data[1:]:
        if row[participant_col_idx].strip() == participant:
            for epoch, idx in epoch_indices.items():
                try:
                    value = row[idx].replace(',', '').strip()
                    if value == "-" or not value:
                        value = "0"
                    total_value += float(value)
                except ValueError:
                    print(f"ValueError for row {row}, epoch {epoch}")

    return total_value

# Function to update the Transactions worksheet
def update_transactions_worksheet(sh, month, participants, epochs, results, transaction_link):
    try:
        trans_wks = sh.worksheet("Transactions")
    except gspread.exceptions.WorksheetNotFound:
        trans_wks = sh.add_worksheet(title="Transactions", rows="100", cols="20")

    existing_data = trans_wks.get_all_values()
    if not existing_data or existing_data[0] != ['Month', 'Participant', 'Epochs', 'Total Value', 'Transaction Link']:
        trans_wks.update('A1', [['Month', 'Participant', 'Epochs', 'Total Value', 'Transaction Link']])

    for participant, total_value in results.items():
        trans_wks.append_row([month, participant, ', '.join(epochs), total_value, transaction_link])

if __name__ == "__main__":
    month, epochs, participants = get_user_input()
    results = {participant: process_data(sh_wks, participant, epochs) for participant in participants}
    print("Calculated totals for each participant: ", results)
    
    transaction_link = input("Enter Transaction Link: ").strip()
    update_transactions_worksheet(sh, month, participants, epochs, results, transaction_link)
    print("Transactions worksheet updated with combined epoch data for each participant.")
