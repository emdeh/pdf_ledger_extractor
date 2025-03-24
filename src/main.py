"""
Main entry point.
Provides functionality to process multiple PDF files in a specified directory,
extract transaction data using a ledger parser, and write the results to Excel files.

Classes:
    LedgerParser: A class to parse ledger information from PDF files.
    ExcelWriter: A class to write parsed data to Excel files.

Functions:
    main(): Main entry point for processing multiple PDFs in a directory. It takes an input
            directory containing PDF files and an optional output directory to save the
            resulting Excel files. If the output directory is not specified, it defaults
            to "output". The function processes each PDF file, extracts transaction data,
            and writes the results to an Excel file.

Usage:
    python main.py <input_directory> [output_directory]

Example:
    python main.py /path/to/pdf_directory /path/to/output_directory
"""

import os
import sys
from parsers.ledger_parser import LedgerParser
from utils.excel_writer import ExcelWriter

def main():
    """
    Main entry point for processing multiple PDFs in a directory.
    Usage: python main.py <input_directory> [output_directory]
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_directory> [output_directory]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    os.makedirs(output_dir, exist_ok=True)

    # Get a list of PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        sys.exit(0)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        # Extract the base name (without extension) to name the Excel file.
        base_name, _ = os.path.splitext(pdf_file)
        output_excel = os.path.join(output_dir, f"{base_name}.xlsx")

        # Instantiate the parser and process the PDF.
        parser = LedgerParser(pdf_path)
        transactions, summary = parser.parse()

        # Instantiate the Excel writer and write the output.
        writer = ExcelWriter(transactions, summary, output_excel)
        writer.write()

        print(f"Processed {pdf_file}. Results written to {output_excel}")

if __name__ == "__main__":
    main()
