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


sh = gc.open("mini automation test")

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