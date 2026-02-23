"""
File Organiser
--------------
Scans a folder and sorts files into subfolders by type.
Supports --dry-run to preview changes before moving anything.

Demonstrates:
- File system operations with pathlib and shutil
- Command-line arguments with argparse
- Dry-run pattern for safe preview
- Dictionary-driven category mapping

Usage:
    python file_organiser.py /path/to/folder
    python file_organiser.py /path/to/folder --dry-run

Author: Zachary Degitz
"""

import argparse
import shutil
import sys
from pathlib import Path

CATEGORIES: dict[str, list[str]] = {
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".odt", ".rtf"],
    "Videos":    [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio":     [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
    "Archives":  [".zip", ".tar", ".gz", ".bz2", ".rar", ".7z", ".xz"],
    "Code":      [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml",
                  ".sh", ".bat", ".c", ".cpp", ".h", ".java", ".rb", ".go", ".rs"],
    "Data":      [".csv", ".tsv", ".sql", ".db", ".sqlite"],
}


def get_category(filename: str) -> str:
    """Return the category name for a given filename based on its extension."""
    ext = Path(filename).suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def organise_folder(folder_path: str, dry_run: bool = False) -> dict:
    """
    Scan a folder and move files into category subfolders.

    Returns a summary dict with counts per category and skipped items.
    """
    folder = Path(folder_path).resolve()
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")

    moved: dict[str, int] = {}
    skipped = 0

    for item in sorted(folder.iterdir()):
        if item.is_dir():
            skipped += 1
            continue

        category = get_category(item.name)
        dest_dir = folder / category
        dest_file = dest_dir / item.name

        # Avoid naming collision
        if dest_file.exists():
            stem = item.stem
            suffix = item.suffix
            counter = 1
            while dest_file.exists():
                dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        if dry_run:
            print(f"  [dry-run] {item.name}  ->  {category}/")
        else:
            dest_dir.mkdir(exist_ok=True)
            shutil.move(str(item), str(dest_file))
            print(f"  Moved: {item.name}  ->  {category}/")

        moved[category] = moved.get(category, 0) + 1

    return {
        "folder": str(folder),
        "dry_run": dry_run,
        "moved": moved,
        "skipped_dirs": skipped,
        "total_files": sum(moved.values()),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Sort files in a folder into subfolders by type."
    )
    parser.add_argument("folder", help="Path to the folder to organise")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be moved without making any changes",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args()

    label = "DRY RUN — no files will be moved" if args.dry_run else "Organising files..."
    print("=" * 50)
    print(f"  File Organiser  |  {label}")
    print("=" * 50)
    print()

    try:
        summary = organise_folder(args.folder, dry_run=args.dry_run)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print()
    print("-" * 50)
    if summary["total_files"] == 0:
        print("  No files found to organise.")
    else:
        verb = "Would move" if args.dry_run else "Moved"
        print(f"  {verb} {summary['total_files']} file(s):")
        for category, count in sorted(summary["moved"].items()):
            print(f"    {category:<12} {count} file(s)")
        if summary["skipped_dirs"]:
            print(f"  Skipped {summary['skipped_dirs']} subfolder(s).")
    print("=" * 50)


if __name__ == "__main__":
    main()
