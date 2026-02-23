"""
Bulk Email Sender
-----------------
Sends personalised emails to a list of contacts from a CSV file
using Gmail SMTP and an HTML template.

Demonstrates:
- SMTP email sending with smtplib
- HTML email composition with email.mime
- CSV contact list processing
- Template variable substitution
- Secure credential loading from .env
- Dry-run mode for safe previewing

Setup:
    1. Enable 2-Factor Authentication on your Gmail account
    2. Generate an App Password at myaccount.google.com/apppasswords
    3. Create a .env file in this directory:
           EMAIL_ADDRESS=you@gmail.com
           EMAIL_PASSWORD=your_app_password

Contacts CSV format (required columns: name, email):
    name,email,company
    Alice,alice@example.com,Acme Corp
    Bob,bob@example.com,Globex

HTML template example (email.html):
    <p>Hi {name},</p>
    <p>Welcome to {company}. This email was sent to {email}.</p>

Dependencies:
    pip install python-dotenv

Usage:
    python email_sender.py --contacts contacts.csv --template email.html --subject "Hi {name}!"
    python email_sender.py --contacts contacts.csv --template email.html --subject "Hello" --dry-run

Author: Zachary Degitz
"""

import argparse
import csv
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: Missing dependency. Run: pip install python-dotenv")
    sys.exit(1)


def load_contacts(csv_path: str) -> list[dict]:
    """
    Read a CSV file of contacts.

    Each row becomes a dict; 'name' and 'email' columns are required.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Contacts file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contacts = [row for row in reader]

    if not contacts:
        raise ValueError("Contacts file is empty.")

    for col in ("name", "email"):
        if col not in contacts[0]:
            raise ValueError(f"Contacts CSV is missing required column: '{col}'")

    return contacts


def render_template(template_path: str, contact: dict) -> str:
    """
    Read an HTML template file and substitute contact fields.

    Any {column_name} placeholder in the template is replaced
    with the corresponding value from the contact dict.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    try:
        return template.format_map(contact)
    except KeyError as e:
        raise ValueError(f"Template references missing contact field: {e}")


def send_email(
    smtp: smtplib.SMTP_SSL,
    sender: str,
    contact: dict,
    subject: str,
    html_body: str,
) -> None:
    """Compose and send a single HTML email via an open SMTP connection."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject.format_map(contact)
    msg["From"] = sender
    msg["To"] = contact["email"]
    msg.attach(MIMEText(html_body, "html"))
    smtp.sendmail(sender, contact["email"], msg.as_string())


def main():
    parser = argparse.ArgumentParser(
        description="Send personalised bulk emails via Gmail from a CSV contact list."
    )
    parser.add_argument("--contacts", required=True, help="Path to the contacts CSV file")
    parser.add_argument("--template", required=True, help="Path to the HTML email template")
    parser.add_argument("--subject", required=True, help="Email subject (supports {name} etc.)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview emails without sending anything",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Seconds to wait between each send (default: 1.0)",
    )
    args = parser.parse_args()

    load_dotenv()
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not args.dry_run:
        if not email_address or not email_password:
            print("Error: EMAIL_ADDRESS and EMAIL_PASSWORD must be set in your .env file.")
            sys.exit(1)

    print("=" * 55)
    label = "DRY RUN — no emails will be sent" if args.dry_run else "Sending emails..."
    print(f"  Bulk Email Sender  |  {label}")
    print("=" * 55)

    try:
        contacts = load_contacts(args.contacts)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return

    print(f"  Contacts loaded : {len(contacts)}")
    print(f"  Subject         : {args.subject}")
    print()

    sent = 0
    failed = 0

    smtp_conn = None
    if not args.dry_run:
        try:
            smtp_conn = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtp_conn.login(email_address, email_password)
        except smtplib.SMTPAuthenticationError:
            print("Error: Gmail authentication failed. Check your App Password in .env.")
            return
        except smtplib.SMTPException as e:
            print(f"Error: Could not connect to Gmail SMTP: {e}")
            return

    try:
        for i, contact in enumerate(contacts, 1):
            name = contact.get("name", "")
            email = contact.get("email", "")
            print(f"  [{i}/{len(contacts)}] {name} <{email}>", end="")

            try:
                html_body = render_template(args.template, contact)
                if args.dry_run:
                    print("  -> [skipped]")
                else:
                    send_email(smtp_conn, email_address, contact, args.subject, html_body)
                    print("  -> Sent")
                    if i < len(contacts):
                        time.sleep(args.delay)
                sent += 1
            except (FileNotFoundError, ValueError) as e:
                print(f"  -> Failed ({e})")
                failed += 1
    finally:
        if smtp_conn:
            smtp_conn.quit()

    print()
    print("-" * 55)
    action = "Would send" if args.dry_run else "Sent"
    print(f"  {action}: {sent}  |  Failed: {failed}")
    print("=" * 55)


if __name__ == "__main__":
    main()
