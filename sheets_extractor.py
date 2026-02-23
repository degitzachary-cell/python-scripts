"""
Google Sheets Extractor
-----------------------
Exports a Google Sheet to a local CSV file.

Works with:
- Public sheets (no credentials needed)
- Private sheets via a Google Service Account JSON key

Demonstrates:
- Google API authentication (public vs service account)
- Writing CSV from API data
- Command-line arguments with argparse
- Error handling for missing credentials and API errors

Setup (private sheets):
    1. Create a Service Account in Google Cloud Console
    2. Share your Google Sheet with the service account email
    3. Download the JSON key and pass it with --credentials

Dependencies:
    pip install gspread google-auth

Usage:
    python sheets_extractor.py --sheet-id YOUR_SHEET_ID --output data.csv
    python sheets_extractor.py --sheet-id YOUR_SHEET_ID --credentials creds.json --output data.csv

Author: Zachary Degitz
"""

import argparse
import csv
import sys
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Error: Missing dependencies. Run: pip install gspread google-auth")
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_client(credentials_path: str | None = None) -> gspread.Client:
    """
    Return an authenticated gspread client.

    Uses anonymous access for public sheets, or a service account
    JSON key for private sheets.
    """
    if credentials_path:
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        return gspread.authorize(creds)
    else:
        return gspread.Client(auth=None)


def extract_sheet(
    sheet_id: str,
    output_path: str,
    credentials_path: str | None = None,
    worksheet_index: int = 0,
) -> dict:
    """
    Open a Google Sheet and write all rows to a CSV file.

    Returns a summary dict with row/column counts and metadata.
    """
    client = get_client(credentials_path)

    try:
        spreadsheet = client.open_by_key(sheet_id)
    except gspread.exceptions.APIError as e:
        raise RuntimeError(f"Could not open sheet '{sheet_id}': {e}") from e
    except gspread.exceptions.NoValidUrlKeyFound:
        raise ValueError(f"Invalid sheet ID: {sheet_id}")

    worksheet = spreadsheet.get_worksheet(worksheet_index)
    if worksheet is None:
        raise ValueError(f"Worksheet index {worksheet_index} not found in this spreadsheet.")

    rows = worksheet.get_all_values()
    if not rows:
        raise ValueError("The sheet appears to be empty.")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return {
        "sheet_id": sheet_id,
        "sheet_title": spreadsheet.title,
        "worksheet": worksheet.title,
        "rows_exported": len(rows) - 1,  # exclude header
        "columns": len(rows[0]) if rows else 0,
        "output_file": output_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Export a Google Sheet to a local CSV file."
    )
    parser.add_argument("--sheet-id", required=True, help="Google Sheet ID (from the URL)")
    parser.add_argument("--output", required=True, help="Path to write the output CSV")
    parser.add_argument(
        "--credentials",
        default=None,
        help="Path to a Service Account JSON key (required for private sheets)",
    )
    parser.add_argument(
        "--worksheet",
        type=int,
        default=0,
        metavar="INDEX",
        help="Worksheet index to export (0 = first sheet, default: 0)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args()

    print("=" * 50)
    print("  Google Sheets Extractor")
    print("=" * 50)

    mode = "Service Account" if args.credentials else "Public (anonymous)"
    print(f"  Auth mode  : {mode}")
    print(f"  Sheet ID   : {args.sheet_id}")
    print(f"  Worksheet  : index {args.worksheet}")
    print(f"  Output     : {args.output}")
    print()

    try:
        summary = extract_sheet(
            sheet_id=args.sheet_id,
            output_path=args.output,
            credentials_path=args.credentials,
            worksheet_index=args.worksheet,
        )
        print(f"  Sheet title : {summary['sheet_title']}")
        print(f"  Worksheet   : {summary['worksheet']}")
        print(f"  Rows        : {summary['rows_exported']}")
        print(f"  Columns     : {summary['columns']}")
        print()
        print(f"  Saved to: {summary['output_file']}")
    except (RuntimeError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
