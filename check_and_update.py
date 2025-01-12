import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import subprocess

# Paths
CREDENTIALS_FILE = "/home/dakboard/myenv/credentials/credentials.json"
LAST_DATA_FILE = "/home/dakboard/myenv/last_google_data.txt"
INDEX_FILE = "/home/dakboard/myenv/bboi/index.html"
UPDATE_SCRIPT = "/home/dakboard/myenv/bboi/update_github.py"

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1htUrHqALLhLm_OYdL04Zik2BtC9jSWKuGp1lC6wrcYc"
RANGE_NAME = "Sheet1!A1:Z1000"

# Initialize Google Sheets API
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)

def fetch_latest_data():
    """Fetch the latest rows from Google Sheets."""
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get("values", [])
    return rows[-10:] if len(rows) > 10 else rows[1:]

def load_last_data():
    """Load the last fetched data from a file."""
    if os.path.exists(LAST_DATA_FILE):
        with open(LAST_DATA_FILE, "r") as file:
            return file.read()
    return ""

def save_last_data(data):
    """Save the latest fetched data to a file."""
    with open(LAST_DATA_FILE, "w") as file:
        file.write(data)

def update_html(latest_rows):
    """Update the HTML content."""
    print("Updating index.html...")
    content_lines = [f"<p>{' | '.join(row)}</p>" for row in latest_rows]

    header_lines = [
        "<!DOCTYPE html>\n",
        "<html>\n",
        "<head>\n",
        "    <title>Latest Inputs</title>\n",
        "</head>\n",
        "<body>\n",
        "    <h1>Inputs Log</h1>\n"
    ]
    footer_lines = ["</body>\n", "</html>\n"]

    with open(INDEX_FILE, "w") as file:
        file.writelines(header_lines + content_lines + footer_lines)

    print("index.html updated.")

def main():
    try:
        print("Fetching the latest data from Google Sheets...")
        latest_rows = fetch_latest_data()
        latest_data_str = "\n".join([" | ".join(row) for row in latest_rows])

        # Compare with the last saved data
        last_data = load_last_data()
        if latest_data_str != last_data:
            print("New data found! Updating index.html...")
            save_last_data(latest_data_str)
            update_html(latest_rows)

            # Trigger the GitHub update script
            print("Triggering GitHub update...")
            subprocess.run(["python", UPDATE_SCRIPT], check=True)
        else:
            print("No new data found. Exiting.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
