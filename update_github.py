import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import subprocess
from datetime import datetime

# File paths
CREDENTIALS_FILE = "/home/dakboard/myenv/credentials/credentials.json"
GITHUB_TOKEN_FILE = "/home/dakboard/myenv/credentials/.github_token"

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1htUrHqALLhLm_OYdL04Zik2BtC9jSWKuGp1lC6wrcYc"
RANGE_NAME = "Sheet1!A1:Z1000"

# Authenticate with Google Sheets
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)

def fetch_last_ten_rows():
    """Fetch the last 10 rows from the spreadsheet."""
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get("values", [])
    return rows[-10:] if len(rows) > 10 else rows[1:]  # Exclude the header

def update_html(rows):
    """Update the index.html file with the last 10 rows."""
    content_lines = [f"<p>{' | '.join(row)}</p>" for row in rows]
    header = "<!DOCTYPE html>\n<html>\n<head>\n<title>Latest Inputs</title>\n</head>\n<body>\n<h1>Inputs Log</h1>\n"
    footer = "</body>\n</html>\n"
    with open("index.html", "w") as file:
        file.write(header + "\n".join(content_lines) + footer)
    print("Updated index.html with the last 10 rows.")

def push_to_github():
    """Push the updated index.html to GitHub."""
    # Load GitHub token
    with open(GITHUB_TOKEN_FILE, "r") as token_file:
        github_token = token_file.read().strip()

    # Set up GitHub authentication
    os.environ["GIT_ASKPASS"] = "/bin/echo"
    os.environ["GIT_USERNAME"] = "odjopuen"
    os.environ["GIT_PASSWORD"] = github_token

    # Add, commit, and push changes
    subprocess.run(["git", "add", "index.html"])
    subprocess.run(["git", "commit", "-m", f"Auto-update index.html: {datetime.now().strftime('%c')}"])
    subprocess.run(["git", "push", "https://odjopuen@github.com/odjopuen/bboi.git", "main"])
    print("Pushed changes to GitHub.")

if __name__ == "__main__":
    print("Fetching the latest data from Google Sheets...")
    rows = fetch_last_ten_rows()
    print("Updating index.html...")
    update_html(rows)
    print("Pushing updates to GitHub...")
    push_to_github()
    print("Process complete!")
