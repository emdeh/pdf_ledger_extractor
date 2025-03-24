"""
Module to parse a general ledger PDF into transaction and summary data.

This module uses the `pdfplumber` library to extract text from PDF files and 
regular expressions to parse the text into structured data. The main class, 
`LedgerParser`, processes the PDF line-by-line to identify and extract 
transactions and account summaries.
"""

import re
import unicodedata
from typing import List, Tuple, Dict
import pdfplumber


class LedgerParser:
    """
    Parses a general ledger PDF and returns transactions and account summaries.

    Attributes:
        pdf_path (str): Path to the PDF file to be parsed.
        transactions (List[Dict]): List to store parsed transactions.
        summary (List[Dict]): List to store account summaries.
        current_account_id (str): ID of the current account being processed.
        current_account_desc (str): Description of the current account being processed.
        current_beginning_balance (str): Beginning balance of the current account.
        header_lines (List[str]): List to store header lines captured from the first page.
        header_done (bool): Flag set to True once the table header row ("ID No ...") is encountered on a page.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.transactions: List[Dict] = []
        self.summary: List[Dict] = []
        self.current_account_id = None
        self.current_account_desc = None
        self.current_beginning_balance = None

        # Store header lines captured from the first page (to ignore repeats on subsequent pages)
        self.header_lines: List[str] = []

        # This flag indicates when we've passed the header portion of a page.
        self.header_done = False

        # Pattern for account header, e.g. "1-2210 Cash Account" or "10-2210 Some Desc"
        self.account_header_pattern = re.compile(r"^(\d{1,3}-\d{4})\s+(.*)$")

        # Pattern for beginning balance (captures amount, optionally with a '$')
        self.beginning_balance_pattern = re.compile(r"Beginning Balance:\s*\$?([\d,.\-]+)")

        # Updated pattern for total line: allows an optional '-' for negative amounts.
        self.total_line_pattern = re.compile(
            r"Total\s*:\s*\$?(-?[\d,]+\.\d{2})(?:cr)?\s+\$?(-?[\d,]+\.\d{2})(?:cr)?\s+\$?(-?[\d,]+\.\d{2})(?:cr)?\s+\$?(-?[\d,]+\.\d{2})(?:cr)?"
        )

        # Issue: Does not account for $ signs in the memo field.
        # Issue: Does not account for empty memo field.
        self.transaction_pattern = re.compile(
            r"^(?P<trans_id>.+?)\s+(?P<src>[A-Z]{2})\s+(?P<date>\d{1,2}/\d{1,2}/\d{4})\s+(?P<memo>.+?)(?=\s+\$)\s+\$?(?P<amount1>[\d,.\-]+)(?:\s+\$?(?P<amount2>[\d,.\-]+))?$"
        )

    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Parses the PDF file specified by `self.pdf_path` and extracts transactions 
        and summary information.

        Returns:
            Tuple[List[Dict], List[Dict]]: A tuple containing two lists:
                - transactions: A list of dictionaries, each representing a transaction.
                - summary: A list of dictionaries, each representing a summary entry.
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in enumerate(pdf.pages, start=1):
                # Reset header_done at the start of each page.
                self.header_done = False

                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")
                for line in lines:
                    self._process_line(line)

        # If needed, flush the final account if no total row was encountered.
        if self.current_account_id is not None:
            self._flush_account(
                debit="0.00",
                credit="0.00",
                net="0.00",
                ending=self.current_beginning_balance
            )

        return self.transactions, self.summary

    def _process_line(self, line: str):
        """
        Processes a single line of text to determine whether it is:
        - A footer line (ignored)
        - A header line (anything before the table header row "ID No ..." is stored)
        - The table header row (detected by "ID No")
        - An account header
        - A beginning balance line
        - A transaction row
        - A total row
        """
        # Normalise the line to standard unicode form and remove non printable chars.
        line = unicodedata.normalize('NFKC', line)
        line = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', line).strip()

        # 1. Footer lines
        footer_patterns = [
            re.compile(r"^\*\s*Year-End Adjustments\s*$"),
            re.compile(r"^Page\s+\d+\s+of\s+\d+\s*$")
        ]
        for pattern in footer_patterns:
            if pattern.match(line):
                return  # Skip footer lines

        # 2. Capture header lines before the table header row.
        if not self.header_done:
            if "ID No" in line:
                # Once the table header row is seen, mark header_done.
                self.header_done = True
            else:
                if line not in self.header_lines:
                    self.header_lines.append(line)
                return  # Skip further processing of header lines

        # 3. Process account header line (e.g. "1-2210 Cash Account")
        header_match = self.account_header_pattern.match(line)
        if header_match:
            self.current_account_id = header_match.group(1)
            self.current_account_desc = header_match.group(2)
            return

        # 4. Beginning Balance line
        bb_match = self.beginning_balance_pattern.search(line)
        if bb_match:
            self.current_beginning_balance = bb_match.group(1)
            return

        # 5. Transaction row
        # Issue: does not map debits/credits to individual columns
        txn_match = self.transaction_pattern.match(line)
        if txn_match and self.current_account_id is not None:
            txn = {
                "account_id": self.current_account_id,
                "account_desc": self.current_account_desc,
                "trans_id": txn_match.group(1),
                "src": txn_match.group(2),
                "date": txn_match.group(3),
                "memo": txn_match.group(4).strip(),
                "debit/credit": txn_match.group(5),
                "ending_balance": txn_match.group(6)
            }
            self.transactions.append(txn)
            return

        # 6. Total row: directly match using the updated regex.
        total_match = self.total_line_pattern.search(line)
        if total_match and self.current_account_id is not None:
            print(f"DEBUG: Processed Total row for account {self.current_account_id}")
            self._flush_account(
                debit=total_match.group(1),
                credit=total_match.group(2),
                net=total_match.group(3),
                ending=total_match.group(4)
            )
            return

    def _flush_account(self, debit, credit, net, ending):
        """
        Appends a summary entry for the current account, then resets the account context.
        If no ending value is provided, it falls back to the beginning balance.
        """
        summary_entry = {
            "account_id": self.current_account_id,
            "account_desc": self.current_account_desc,
            "beginning_balance": self.current_beginning_balance,
            "total_debit": debit,
            "total_credit": credit,
            "total_net_activity": net,
            "total_ending_balance": ending if ending else self.current_beginning_balance
        }
        self.summary.append(summary_entry)
        # Reset the current account context.
        self.current_account_id = None
        self.current_account_desc = None
        self.current_beginning_balance = None
