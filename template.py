import gspread

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
sh_wks = sh.worksheet('Shares')

template = {
    "Equipment Identifier": "",
    "Equipment Owner": "",
    "Status": "",
    "Participant": "",
    "Participant Type": "",
    "RevShareType": "",
    "Rev Share": "",
    "Cash Lease": "",
    "Address": "",
    "City": "",
    "Date Installed": ""
}

def user_input(template):
    for key in template.keys():
        template[key] = input(f"Enter value for {key}: ")
    return template


def update_sheet(sh_wks, user_data):
    empty_row = len(sh_wks.get_all_values()) + 1
    values = [user_data[key] for key in template.keys()]
    sh_wks.append_row(values)

if __name__ == "__main__":
    user_data = user_input(template)
    update_sheet(sh_wks, user_data)
    print("Spreadsheet updated with user input.")
