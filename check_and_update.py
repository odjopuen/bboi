import os
import subprocess
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

# Ensure script is running in the correct directory
os.chdir("/home/dakboard/myenv/bboi")

# Path to your credentials file
CREDENTIALS_FILE = "/home/dakboard/myenv/credentials/credentials.json"

# Google Sheets API setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)

SPREADSHEET_ID = "1htUrHqALLhLm_OYdL04Zik2BtC9jSWKuGp1lC6wrcYc"  # Replace with your ID
RANGE_NAME = "Sheet1!A1:Z1000"

# Log file path
LOG_FILE = "/home/dakboard/myenv/check_log.txt"

# Path to index.html
INDEX_FILE = "/home/dakboard/myenv/bboi/index.html"

def log_message(message):
    """Log messages to a file for debugging."""
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def fetch_last_ten_rows():
    """Fetch the last 10 rows from Google Sheets."""
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        rows = result.get("values", [])
        return rows[-10:] if len(rows) > 10 else rows[1:]  # Exclude header
    except Exception as e:
        log_message(f"Error fetching data from Google Sheets: {e}")
        return []

def load_existing_content():
    """Load existing entries from index.html."""
    try:
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r") as file:
                return [line.strip() for line in file if line.strip().startswith("<p>")]
    except Exception as e:
        log_message(f"Error loading existing content: {e}")
    return []

def update_html(latest_rows):
    """Update index.html with the last 10 rows."""
    header = [
        "<!DOCTYPE html>\n",
        "<html>\n",
        "<head>\n",
        "    <title>Latest Inputs</title>\n",
        "</head>\n",
        "<body>\n",
        "    <h1>Inputs Log</h1>\n"
    ]
    footer = ["</body>\n", "</html>\n"]
    content = [f"<p>{' | '.join(row)}</p>" for row in latest_rows]

    try:
        with open(INDEX_FILE, "w") as file:
            file.writelines(header + content + footer)
        log_message("Updated index.html with the latest data.")
    except Exception as e:
        log_message(f"Error updating index.html: {e}")

def main():
    """Main function to check for updates and trigger GitHub push."""
    log_message("Checking for updates...")

    # Fetch new data and compare with existing content
    latest_rows = fetch_last_ten_rows()
    existing_content = load_existing_content()
    formatted_latest = [f"<p>{' | '.join(row)}</p>" for row in latest_rows]

    # Check if there are changes
    if formatted_latest != existing_content:
        log_message("Changes detected. Updating index.html and triggering GitHub update.")
        update_html(latest_rows)

        # Trigger the GitHub update script
        try:
            subprocess.run(
                ["/home/dakboard/myenv/bin/python", "/home/dakboard/myenv/bboi/update_github.py"],
                check=True
            )
            log_message("GitHub update triggered successfully.")
        except subprocess.CalledProcessError as e:
            log_message(f"Error triggering GitHub update: {e}")
    else:
        log_message("No changes detected. Skipping update.")

if __name__ == "__main__":
    main()
