# 🐍 Python Scripts

![CI](https://github.com/degitzachary-cell/python-scripts/actions/workflows/ci.yml/badge.svg)

A collection of clean, well-documented Python automation scripts built for real-world freelance use cases. Each script is production-ready, handles errors gracefully, and is easy to customise for specific client needs.

**Author:** Zachary Degitz
**Contact:** z.degit@gmail.com

---

## 📁 Scripts

| Script | Description | Key Libraries |
|--------|-------------|---------------|
| age_validator.py | CLI age input validator with classification | stdlib only |
| csv_cleaner.py | Cleans messy CSV files, strips whitespace, normalises emails, removes empty rows | stdlib only |
| file_organiser.py | Auto-sorts files into subfolders by type with dry-run preview | stdlib only |
| sheets_extractor.py | Exports Google Sheets data to CSV (public + private/service account) | gspread, google-auth |
| web_scraper.py | Scrapes links, headings, or metadata from any webpage to CSV/JSON | requests, beautifulsoup4 |
| email_sender.py | Sends personalised bulk emails from a CSV contact list via Gmail | smtplib, python-dotenv |
| pdf_extractor.py | Extracts text from single or batch PDF files to TXT or CSV | pymupdf |

---

## 🚀 Quick Start

Clone the repo and install dependencies for whichever script you need:

    pip install requests beautifulsoup4   # web_scraper.py
    pip install gspread google-auth       # sheets_extractor.py
    pip install pymupdf                   # pdf_extractor.py
    pip install python-dotenv             # email_sender.py

See `requirements.txt` for pinned versions.

---

## 📄 Script Details

### age_validator.py
CLI tool that asks for an age, validates input with try/except, and returns category and voting eligibility.
No dependencies required.

### csv_cleaner.py
Reads a CSV, strips whitespace, normalises emails to lowercase, removes empty rows, writes clean output.
Usage: python csv_cleaner.py input.csv output_clean.csv

Try it with the sample file:
Usage: python csv_cleaner.py samples/dirty.csv output_clean.csv

### file_organiser.py
Scans a folder and sorts files into subfolders by type. Supports --dry-run to preview first.
Usage: python file_organiser.py /path/to/folder --dry-run

### sheets_extractor.py
Exports a Google Sheet to CSV. Works with public sheets or private sheets via Service Account key.
Usage: python sheets_extractor.py --sheet-id YOUR_ID --output data.csv

Usage (private): python sheets_extractor.py --sheet-id YOUR_ID --credentials creds.json --output data.csv

### web_scraper.py
Scrapes links, headings, or page metadata from any public webpage and exports to CSV or JSON.
Usage: python web_scraper.py --url https://example.com --output links.csv --extract links

Usage: python web_scraper.py --url https://example.com --output headings.json --extract headings --format json

### email_sender.py
Sends personalised bulk emails via Gmail SMTP from a CSV contact list with HTML template support.
Copy .env.example to .env and add your Gmail App Password.
Usage: python email_sender.py --contacts samples/contacts.csv --template email.html --subject "Hi {name}!"
Use --dry-run to preview without sending.

### pdf_extractor.py
Extracts text from PDF files page by page. Supports batch processing of entire folders.
Usage: python pdf_extractor.py --input report.pdf --output report.txt
Batch: python pdf_extractor.py --input ./pdfs/ --output ./extracted/ --batch

---

## 🧪 Tests

    pip install pytest requests beautifulsoup4 python-dotenv
    pytest tests/ -v

Tests cover pure functions across all scripts and require no network access or external services.

---

## 📂 Sample Files

The `samples/` folder contains ready-to-use test data:

| File | Used by |
|------|---------|
| `samples/dirty.csv` | csv_cleaner.py — messy CSV with whitespace, mixed-case emails, empty rows |
| `samples/contacts.csv` | email_sender.py — example contact list |

---

## 🛠 Customisation

Every script is built to be easy to adapt. Common customisations:
- File type categories in file_organiser.py
- CSS selectors in web_scraper.py
- Email delay timing in email_sender.py
- CSV column targets in csv_cleaner.py

---

## 📬 Hire Me

Looking for a custom Python automation script? Available for freelance projects.

Email: z.degit@gmail.com
GitHub: https://github.com/degitzachary-cell

---

## 📝 License

MIT License — free to use, modify, and distribute with attribution.
