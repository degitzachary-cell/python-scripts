"""
CSV Data Cleaner
----------------
Reads a CSV file, cleans common data issues, and outputs a clean version.

Demonstrates:
- File I/O with csv module
- Data validation and transformation
- Command-line arguments with argparse
- Error handling

Usage:
    python csv_cleaner.py input.csv output.csv

Author: Zac
"""

import csv
import argparse
import os
from datetime import datetime


def clean_row(row: dict) -> dict:
    """
    Clean a single row of data:
    - Strip whitespace from all string fields
    - Normalize email addresses to lowercase
    - Convert empty strings to None
    """
    cleaned = {}
    for key, value in row.items():
        key = key.strip()
        if isinstance(value, str):
            value = value.strip()
            if key.lower() in ("email", "email_address"):
                value = value.lower()
            if value == "":
                value = None
        cleaned[key] = value
    return cleaned


def clean_csv(input_path: str, output_path: str) -> dict:
    """Read, clean, and write a CSV file. Returns a summary dict."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows_read = 0
    rows_written = 0
    rows_skipped = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("CSV file has no headers.")
        all_rows = []
        for row in reader:
            rows_read += 1
            cleaned = clean_row(row)
            if all(v is None for v in cleaned.values()):
                rows_skipped += 1
                continue
            all_rows.append(cleaned)
            rows_written += 1

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    return {
        "input_file": input_path,
        "output_file": output_path,
        "rows_read": rows_read,
        "rows_written": rows_written,
        "rows_skipped": rows_skipped,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Clean a CSV file: strip whitespace, normalise emails, remove empty rows."
    )
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument("output", help="Path to write the cleaned CSV file")
    args = parser.parse_args()

    try:
        summary = clean_csv(args.input, args.output)
        print(f"Done! {summary['rows_written']} rows written, {summary['rows_skipped']} skipped.")
        print(f"Clean file saved to: {summary['output_file']}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
