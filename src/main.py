"""
Module docstring
"""

import sys
from parsers.ledger_parser import LedgerParser
from utils.excel_writer import ExcelWriter

def main():
    """
    Main entry point for the script.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_path> [output_excel_path]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output_ledger.xlsx"

    # Instantiate and use the LedgerParser
    parser = LedgerParser(pdf_path)
    transactions, summary = parser.parse()

    # Instantiate and use the ExcelWriter
    writer = ExcelWriter(transactions, summary, output_path)
    writer.write()

    print(f"Parsing complete! Results written to {output_path}")

if __name__ == "__main__":
    main()
