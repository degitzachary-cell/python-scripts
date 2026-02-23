"""
PDF Text Extractor
------------------
Extracts text content from PDF files, page by page.
Supports single file extraction or batch processing of entire folders.

Demonstrates:
- PDF text extraction with PyMuPDF (fitz)
- Batch file processing with pathlib
- Output to TXT files
- Command-line arguments with argparse
- Progress reporting for long-running tasks

Dependencies:
    pip install pymupdf

Usage:
    # Single file -> TXT
    python pdf_extractor.py --input report.pdf --output report.txt

    # Batch: all PDFs in a folder -> individual TXT files
    python pdf_extractor.py --input ./pdfs/ --output ./extracted/ --batch

Author: Zachary Degitz
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: Missing dependency. Run: pip install pymupdf")
    sys.exit(1)


def extract_pdf(input_path: str | Path, output_path: str | Path) -> dict:
    """
    Extract all text from a single PDF file and write it to a TXT file.

    Each page is separated by a clear divider. Returns a summary dict.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(input_path))
    total_pages = len(doc)
    total_chars = 0

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"Source: {input_path.name}\n")
        out.write(f"Pages : {total_pages}\n")
        out.write("=" * 60 + "\n\n")

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            total_chars += len(text)
            out.write(f"--- Page {page_num} of {total_pages} ---\n")
            out.write(text.strip() if text.strip() else "(no text on this page)")
            out.write("\n\n")

    doc.close()

    return {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "pages": total_pages,
        "characters": total_chars,
    }


def batch_extract(input_dir: str | Path, output_dir: str | Path) -> dict:
    """
    Extract text from all PDF files in a folder.

    Each PDF produces a corresponding .txt file in output_dir.
    Returns a summary dict with counts.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise ValueError(f"Path is not a directory: {input_dir}")

    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        return {"processed": 0, "failed": 0, "output_dir": str(output_dir)}

    output_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    failed = 0

    for pdf_file in pdf_files:
        out_file = output_dir / (pdf_file.stem + ".txt")
        try:
            result = extract_pdf(pdf_file, out_file)
            print(f"  OK  {pdf_file.name}  ({result['pages']} pages, {result['characters']:,} chars)")
            processed += 1
        except (FileNotFoundError, ValueError, fitz.FileDataError) as e:
            print(f"  ERR {pdf_file.name}  -> {e}")
            failed += 1

    return {
        "processed": processed,
        "failed": failed,
        "output_dir": str(output_dir),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files (single file or batch folder)."
    )
    parser.add_argument("--input", required=True, help="Path to a PDF file or a folder of PDFs")
    parser.add_argument("--output", required=True, help="Output TXT file path, or output folder for --batch")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all PDF files in the input folder",
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  PDF Text Extractor")
    print("=" * 55)

    if args.batch:
        print(f"  Mode   : Batch")
        print(f"  Input  : {args.input}")
        print(f"  Output : {args.output}")
        print()
        try:
            summary = batch_extract(args.input, args.output)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return

        print()
        print("-" * 55)
        print(f"  Processed : {summary['processed']}  |  Failed: {summary['failed']}")
        if summary["processed"]:
            print(f"  Output folder: {summary['output_dir']}")
    else:
        print(f"  Mode   : Single file")
        print(f"  Input  : {args.input}")
        print(f"  Output : {args.output}")
        print()
        try:
            result = extract_pdf(args.input, args.output)
            print(f"  Pages      : {result['pages']}")
            print(f"  Characters : {result['characters']:,}")
            print()
            print(f"  Saved to: {result['output_file']}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")

    print("=" * 55)


if __name__ == "__main__":
    main()
