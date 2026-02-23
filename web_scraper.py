"""
Web Scraper
-----------
Scrapes links, headings, or page metadata from any public webpage
and exports the results to CSV or JSON.

Demonstrates:
- HTTP requests with custom headers
- HTML parsing with BeautifulSoup
- Flexible output formats (CSV and JSON)
- Command-line arguments with argparse
- URL normalisation with urllib.parse

Dependencies:
    pip install requests beautifulsoup4

Usage:
    python web_scraper.py --url https://example.com --output links.csv --extract links
    python web_scraper.py --url https://example.com --output headings.json --extract headings --format json
    python web_scraper.py --url https://example.com --output meta.csv --extract metadata

Author: Zachary Degitz
"""

import argparse
import csv
import json
import sys
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Missing dependencies. Run: pip install requests beautifulsoup4")
    sys.exit(1)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PythonScraper/1.0; +https://github.com/degitzachary-cell)"
    )
}


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a URL and return a parsed BeautifulSoup object."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Could not connect to: {url}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error {e.response.status_code} for: {url}")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out for: {url}")
    return BeautifulSoup(response.text, "html.parser")


def scrape_links(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """
    Extract all hyperlinks from the page.

    Returns a list of dicts with keys: text, href, is_internal.
    """
    base_domain = urlparse(base_url).netloc
    results = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        full_url = urljoin(base_url, href)
        link_domain = urlparse(full_url).netloc
        results.append({
            "text": tag.get_text(strip=True) or "(no text)",
            "href": full_url,
            "is_internal": "yes" if link_domain == base_domain else "no",
        })
    return results


def scrape_headings(soup: BeautifulSoup) -> list[dict]:
    """
    Extract all heading elements (h1–h6) from the page.

    Returns a list of dicts with keys: level, text.
    """
    results = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        results.append({
            "level": tag.name.upper(),
            "text": tag.get_text(strip=True),
        })
    return results


def scrape_metadata(soup: BeautifulSoup, url: str) -> list[dict]:
    """
    Extract page metadata: title, description, and Open Graph tags.

    Returns a list of dicts with keys: property, content.
    """
    results = []

    title_tag = soup.find("title")
    results.append({
        "property": "title",
        "content": title_tag.get_text(strip=True) if title_tag else "",
    })
    results.append({"property": "url", "content": url})

    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property") or ""
        content = meta.get("content") or ""
        if name and content:
            results.append({"property": name, "content": content})

    return results


def save_results(data: list[dict], output_path: str, fmt: str) -> None:
    """Write results to a CSV or JSON file."""
    if not data:
        print("  Warning: no data to save.")
        return

    if fmt == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        fieldnames = list(data[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape links, headings, or metadata from a webpage and export to CSV/JSON."
    )
    parser.add_argument("--url", required=True, help="URL of the page to scrape")
    parser.add_argument("--output", required=True, help="Path to write the output file")
    parser.add_argument(
        "--extract",
        choices=["links", "headings", "metadata"],
        default="links",
        help="What to extract: links, headings, or metadata (default: links)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        dest="fmt",
        help="Output format: csv or json (default: csv)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args()

    print("=" * 50)
    print("  Web Scraper")
    print("=" * 50)
    print(f"  URL     : {args.url}")
    print(f"  Extract : {args.extract}")
    print(f"  Format  : {args.fmt.upper()}")
    print(f"  Output  : {args.output}")
    print()

    try:
        print("  Fetching page...")
        soup = fetch_page(args.url)

        if args.extract == "links":
            data = scrape_links(soup, args.url)
        elif args.extract == "headings":
            data = scrape_headings(soup)
        else:
            data = scrape_metadata(soup, args.url)

        save_results(data, args.output, args.fmt)
        print(f"  Found {len(data)} item(s).")
        print(f"  Saved to: {args.output}")

    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
