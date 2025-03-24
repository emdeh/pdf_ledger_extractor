"""
Module to parse a general ledger PDF into transaction and summary data.
"""

from typing import List, Tuple, Dict
import re
import pdfplumber

class LedgerParser:
    """
    Parses a general ledger PDF and returns transactions and account summaries.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.transactions: List[Dict] = []
        self.summary: List[Dict] = []
        self.current_account_id = None
        self.current_account_desc = None
        self.current_beginning_balance = None

        # Pattern for account header, e.g., "1-2210 Cash Account"
        self.account_header_pattern = re.compile(r"^(\d-\d{4})\s+(.*)$")
        # Pattern for beginning balance (captures amount, optionally with a '$')
        self.beginning_balance_pattern = re.compile(r"Beginning Balance:\s*\$?([\d,.\-]+)")
        # Pattern for total line, capturing four amounts:
        # total debit, total credit, total net activity, total ending balance.
        self.total_line_pattern = re.compile(
            r"Total:\s*\$?([\d,.\-]+)\s+\$?([\d,.\-]+)\s+\$?([\d,.\-]+)\s+\$?([\d,.\-]+)"
        )
        # Updated transaction pattern:
        # Expecting a transaction row like:
        # TRX0001AB 01/07/2023 Opening Entry $500.00 $0.00 001 $500.00 $1500.00
        # Group 1: Transaction ID (TRX followed by 4 digits)
        # Group 2: Src (2 letters)
        # Group 3: Date (DD/MM/YYYY)
        # Group 4: Memo (non-greedy)
        # Group 5: Debit
        # Group 6: Credit
        # Group 7: Job No.
        # Group 8: Net Activity
        # Group 9: Ending Balance
        self.transaction_pattern = re.compile(
            r"^(TRX\d{4})([A-Z]{2})\s+(\d{1,2}/\d{1,2}/\d{4})\s+(.*?)\s+\$?([\d,.\-]+)\s+\$?([\d,.\-]+)\s+(\S+)\s+\$?([\d,.\-]+)\s+\$?([\d,.\-]+)$"
        )

    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Opens the PDF, processes each page line-by-line, and populates the transactions
        and summary lists.
        Returns:
            Tuple containing a list of transactions and a list of summary entries.
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split("\n")
                for line in lines:
                    self._process_line(line)
        return self.transactions, self.summary

    def _process_line(self, line: str):
        """
        Processes a single line of text to determine whether it is an account header,
        beginning balance, transaction row, or a total row.
        """
        # 1. Check for an account header (e.g., "1-2210 Cash Account")
        header_match = self.account_header_pattern.match(line)
        if header_match:
            self.current_account_id = header_match.group(1)
            self.current_account_desc = header_match.group(2)
            return

        # 2. Check for 'Beginning Balance:' line
        bb_match = self.beginning_balance_pattern.search(line)
        if bb_match:
            self.current_beginning_balance = bb_match.group(1)
            return

        # 3. Check for a transaction row.
        txn_match = self.transaction_pattern.match(line)
        if txn_match and self.current_account_id is not None:
            txn = {
                "account_id": self.current_account_id,
                "account_desc": self.current_account_desc,
                "trans_id": txn_match.group(1),
                "src": txn_match.group(2),
                "date": txn_match.group(3),
                "memo": txn_match.group(4).strip(),
                "debit": txn_match.group(5),
                "credit": txn_match.group(6),
                "job_no": txn_match.group(7),
                "net_activity": txn_match.group(8),
                "ending_balance": txn_match.group(9)
            }
            self.transactions.append(txn)
            return

        # 4. Check for the 'Total:' line and capture four totals.
        if "Total:" in line:
            total_match = self.total_line_pattern.search(line)
            if total_match and self.current_account_id is not None:
                summary_entry = {
                    "account_id": self.current_account_id,
                    "account_desc": self.current_account_desc,
                    "beginning_balance": self.current_beginning_balance,
                    "total_debit": total_match.group(1),
                    "total_credit": total_match.group(2),
                    "total_net_activity": total_match.group(3),
                    "total_ending_balance": total_match.group(4)
                }
                self.summary.append(summary_entry)
                # Reset current account context for the next account block.
                self.current_account_id = None
                self.current_account_desc = None
                self.current_beginning_balance = None
            return
