"""
Test suite for python-scripts portfolio.

Covers pure functions that require no network access or external services.

Run:
    pytest tests/ -v
"""

import csv
import os
import sys
import pytest

# Add repo root to path so scripts can be imported directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# age_validator
# ---------------------------------------------------------------------------
from age_validator import classify_age


class TestClassifyAge:
    @pytest.mark.parametrize("age,expected", [
        (0,  "Child"),
        (5,  "Child"),
        (12, "Child"),
        (13, "Teenager"),
        (17, "Teenager"),
        (18, "Adult"),
        (30, "Adult"),
        (64, "Adult"),
        (65, "Senior"),
        (90, "Senior"),
    ])
    def test_classify_age(self, age, expected):
        assert classify_age(age) == expected


# ---------------------------------------------------------------------------
# csv_cleaner
# ---------------------------------------------------------------------------
from csv_cleaner import clean_row, clean_csv


class TestCleanRow:
    def test_strips_whitespace_from_values(self):
        assert clean_row({"name": "  Alice  "})["name"] == "Alice"

    def test_strips_whitespace_from_keys(self):
        result = clean_row({"  name  ": "Alice"})
        assert "name" in result

    def test_normalises_email_to_lowercase(self):
        assert clean_row({"email": "  USER@EXAMPLE.COM  "})["email"] == "user@example.com"

    def test_email_address_column_also_normalised(self):
        assert clean_row({"email_address": "USER@X.COM"})["email_address"] == "user@x.com"

    def test_empty_string_becomes_none(self):
        assert clean_row({"phone": ""})["phone"] is None

    def test_non_email_field_preserves_case(self):
        assert clean_row({"city": "NEW YORK"})["city"] == "NEW YORK"

    def test_non_string_value_unchanged(self):
        assert clean_row({"count": 42})["count"] == 42


class TestCleanCsv:
    def test_removes_all_empty_rows(self, tmp_path):
        src = tmp_path / "in.csv"
        dst = tmp_path / "out.csv"
        src.write_text("name,email\nAlice,alice@example.com\n,,\nBob,bob@example.com\n")
        summary = clean_csv(str(src), str(dst))
        assert summary["rows_read"] == 3
        assert summary["rows_written"] == 2
        assert summary["rows_skipped"] == 1

    def test_output_file_is_created(self, tmp_path):
        src = tmp_path / "in.csv"
        dst = tmp_path / "out.csv"
        src.write_text("name,email\nAlice,alice@example.com\n")
        clean_csv(str(src), str(dst))
        assert dst.exists()

    def test_output_is_valid_csv(self, tmp_path):
        src = tmp_path / "in.csv"
        dst = tmp_path / "out.csv"
        src.write_text("name,email\n  Alice  ,  ALICE@EXAMPLE.COM  \n")
        clean_csv(str(src), str(dst))
        rows = list(csv.DictReader(dst.open()))
        assert rows[0]["name"] == "Alice"
        assert rows[0]["email"] == "alice@example.com"

    def test_missing_input_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            clean_csv("/nonexistent.csv", str(tmp_path / "out.csv"))


# ---------------------------------------------------------------------------
# file_organiser
# ---------------------------------------------------------------------------
from file_organiser import get_category, organise_folder


class TestGetCategory:
    @pytest.mark.parametrize("filename,expected", [
        ("photo.jpg",    "Images"),
        ("photo.PNG",    "Images"),
        ("photo.jpeg",   "Images"),
        ("report.pdf",   "Documents"),
        ("report.DOCX",  "Documents"),
        ("clip.mp4",     "Videos"),
        ("clip.MOV",     "Videos"),
        ("song.mp3",     "Audio"),
        ("song.WAV",     "Audio"),
        ("backup.zip",   "Archives"),
        ("backup.TAR",   "Archives"),
        ("script.py",    "Code"),
        ("page.html",    "Code"),
        ("data.csv",     "Data"),
        ("data.SQL",     "Data"),
        ("weird.xyz",    "Other"),
        ("no_extension", "Other"),
    ])
    def test_get_category(self, filename, expected):
        assert get_category(filename) == expected


class TestOrganiseFolder:
    def test_dry_run_leaves_files_in_place(self, tmp_path):
        (tmp_path / "photo.jpg").write_text("img")
        (tmp_path / "report.pdf").write_text("pdf")
        organise_folder(str(tmp_path), dry_run=True)
        assert (tmp_path / "photo.jpg").exists()
        assert (tmp_path / "report.pdf").exists()

    def test_moves_files_into_category_subfolders(self, tmp_path):
        (tmp_path / "photo.jpg").write_text("img")
        (tmp_path / "report.pdf").write_text("pdf")
        summary = organise_folder(str(tmp_path), dry_run=False)
        assert not (tmp_path / "photo.jpg").exists()
        assert (tmp_path / "Images" / "photo.jpg").exists()
        assert (tmp_path / "Documents" / "report.pdf").exists()
        assert summary["total_files"] == 2

    def test_skips_existing_subdirectories(self, tmp_path):
        subdir = tmp_path / "MyFolder"
        subdir.mkdir()
        summary = organise_folder(str(tmp_path), dry_run=False)
        assert subdir.exists()
        assert summary["skipped_dirs"] == 1

    def test_handles_naming_collision(self, tmp_path):
        (tmp_path / "photo.jpg").write_text("original")
        img_dir = tmp_path / "Images"
        img_dir.mkdir()
        (img_dir / "photo.jpg").write_text("existing")
        organise_folder(str(tmp_path), dry_run=False)
        # Both files should exist (original renamed to photo_1.jpg)
        assert (img_dir / "photo.jpg").exists()
        assert (img_dir / "photo_1.jpg").exists()

    def test_missing_folder_raises(self):
        with pytest.raises(FileNotFoundError):
            organise_folder("/nonexistent/path/xyz")


# ---------------------------------------------------------------------------
# web_scraper (requires beautifulsoup4)
# ---------------------------------------------------------------------------
try:
    from bs4 import BeautifulSoup
    from web_scraper import scrape_links, scrape_headings, scrape_metadata
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def _soup(html: str) -> "BeautifulSoup":
    return BeautifulSoup(html, "html.parser")


@pytest.mark.skipif(not BS4_AVAILABLE, reason="beautifulsoup4 not installed")
class TestScrapeHeadings:
    def test_extracts_h1_to_h6(self):
        soup = _soup("<h1>A</h1><h2>B</h2><h3>C</h3><h4>D</h4><h5>E</h5><h6>F</h6>")
        assert len(scrape_headings(soup)) == 6

    def test_correct_level_labels(self):
        soup = _soup("<h1>Title</h1><h2>Sub</h2>")
        headings = scrape_headings(soup)
        assert headings[0]["level"] == "H1"
        assert headings[1]["level"] == "H2"

    def test_strips_whitespace_from_text(self):
        soup = _soup("<h1>  Hello World  </h1>")
        assert scrape_headings(soup)[0]["text"] == "Hello World"

    def test_ignores_non_heading_tags(self):
        soup = _soup("<p>Paragraph</p><span>Span</span><h1>Heading</h1>")
        assert len(scrape_headings(soup)) == 1

    def test_returns_empty_for_no_headings(self):
        soup = _soup("<p>No headings here.</p>")
        assert scrape_headings(soup) == []


@pytest.mark.skipif(not BS4_AVAILABLE, reason="beautifulsoup4 not installed")
class TestScrapeLinks:
    BASE = "https://example.com"

    def test_skips_mailto_links(self):
        soup = _soup('<a href="mailto:x@x.com">Mail</a>')
        assert scrape_links(soup, self.BASE) == []

    def test_skips_hash_anchors(self):
        soup = _soup('<a href="#">Top</a>')
        assert scrape_links(soup, self.BASE) == []

    def test_skips_javascript_links(self):
        soup = _soup('<a href="javascript:void(0)">Click</a>')
        assert scrape_links(soup, self.BASE) == []

    def test_internal_link_flagged_correctly(self):
        soup = _soup('<a href="/about">About</a>')
        links = scrape_links(soup, self.BASE)
        assert links[0]["is_internal"] == "yes"

    def test_external_link_flagged_correctly(self):
        soup = _soup('<a href="https://other.com">Other</a>')
        links = scrape_links(soup, self.BASE)
        assert links[0]["is_internal"] == "no"

    def test_resolves_relative_url(self):
        soup = _soup('<a href="/about">About</a>')
        links = scrape_links(soup, self.BASE)
        assert links[0]["href"] == "https://example.com/about"

    def test_extracts_link_text(self):
        soup = _soup('<a href="/page">Click here</a>')
        links = scrape_links(soup, self.BASE)
        assert links[0]["text"] == "Click here"

    def test_empty_text_replaced_with_placeholder(self):
        soup = _soup('<a href="/page"></a>')
        links = scrape_links(soup, self.BASE)
        assert links[0]["text"] == "(no text)"


@pytest.mark.skipif(not BS4_AVAILABLE, reason="beautifulsoup4 not installed")
class TestScrapeMetadata:
    def test_extracts_title(self):
        soup = _soup("<html><head><title>My Page</title></head><body></body></html>")
        meta = scrape_metadata(soup, "https://example.com")
        titles = [m for m in meta if m["property"] == "title"]
        assert titles[0]["content"] == "My Page"

    def test_extracts_meta_description(self):
        soup = _soup('<html><head><meta name="description" content="A test page."></head></html>')
        meta = scrape_metadata(soup, "https://example.com")
        descriptions = [m for m in meta if m["property"] == "description"]
        assert descriptions[0]["content"] == "A test page."

    def test_includes_url(self):
        soup = _soup("<html></html>")
        meta = scrape_metadata(soup, "https://example.com")
        urls = [m for m in meta if m["property"] == "url"]
        assert urls[0]["content"] == "https://example.com"


# ---------------------------------------------------------------------------
# email_sender (requires python-dotenv)
# ---------------------------------------------------------------------------
try:
    from email_sender import load_contacts, render_template
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@pytest.mark.skipif(not DOTENV_AVAILABLE, reason="python-dotenv not installed")
class TestLoadContacts:
    def test_loads_all_rows(self, tmp_path):
        f = tmp_path / "contacts.csv"
        f.write_text("name,email\nAlice,alice@example.com\nBob,bob@example.com\n")
        contacts = load_contacts(str(f))
        assert len(contacts) == 2

    def test_row_data_is_correct(self, tmp_path):
        f = tmp_path / "contacts.csv"
        f.write_text("name,email\nAlice,alice@example.com\n")
        contacts = load_contacts(str(f))
        assert contacts[0]["name"] == "Alice"
        assert contacts[0]["email"] == "alice@example.com"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_contacts("/nonexistent/contacts.csv")

    def test_missing_name_column_raises(self, tmp_path):
        f = tmp_path / "contacts.csv"
        f.write_text("fullname,email\nAlice,alice@example.com\n")
        with pytest.raises(ValueError, match="name"):
            load_contacts(str(f))

    def test_missing_email_column_raises(self, tmp_path):
        f = tmp_path / "contacts.csv"
        f.write_text("name,address\nAlice,123 Main St\n")
        with pytest.raises(ValueError, match="email"):
            load_contacts(str(f))


@pytest.mark.skipif(not DOTENV_AVAILABLE, reason="python-dotenv not installed")
class TestRenderTemplate:
    def test_substitutes_contact_fields(self, tmp_path):
        t = tmp_path / "email.html"
        t.write_text("<p>Hi {name}, your email is {email}.</p>")
        result = render_template(str(t), {"name": "Alice", "email": "alice@example.com"})
        assert "Alice" in result
        assert "alice@example.com" in result

    def test_missing_template_file_raises(self):
        with pytest.raises(FileNotFoundError):
            render_template("/nonexistent/email.html", {"name": "Alice", "email": "x@x.com"})

    def test_missing_placeholder_raises(self, tmp_path):
        t = tmp_path / "email.html"
        t.write_text("<p>Hi {name}, welcome to {company}.</p>")
        with pytest.raises(ValueError, match="company"):
            render_template(str(t), {"name": "Alice", "email": "alice@example.com"})
