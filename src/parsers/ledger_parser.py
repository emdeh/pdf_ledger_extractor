"""
    Module docstring
"""

import pdfplumber
import re
from typing import List, Tuple, Dict

class LedgerParser:
    """
    Class docstring
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.transactions: List[Dict] = []
        self.summary: List[Dict] = []
        self.current_account_id = None
        self.current_account_desc = None
        self.current_beginning_balance = None


        # Regex patterns to detect different ledger components.
        self.account_header_pattern = re.compile(r"^(\d-\d{4})\s+(.*)$")
        self.beginning_balance_pattern = re.compile(r"Beginning Balance:\s*(.*)")
        self.total_line_pattern = re.compile(r"^Total:\s*(.*)$")
        # This transaction pattern is a starting point and may need tuning.
        self.transaction_pattern = re.compile(
            r"^(\S+)\s+([A-Z]{2})\s+(\d{1,2}/\d{1,2}/\d{4})\s+(.*?)\s+([\d,.\-]+)?\s+([\d,.\-]+)?\s+(\S*)\s+([\d,.\-]+)?\s+([\d,.\-]+)?$"
        )

    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Parses the ledger PDF and returns transactions and account summary.
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                lines = page.extract_text().split("\n")
                for line in lines:
                    self._process_line(line)
        return self.transactions, self.summary

    def _process_line(self, line: str):
        """
        Processes a single line from the PDF to identify ledger components.
        """

        # 1. Detect an account header line (e.g., "1-2210 Some Account Descritpion").
        header_match = self.account_header_pattern.match(line)
        if header_match:
            self.current_account_id = header_match.group(1)
            self.current_account_desc = header_match.group(2)
            return

        # 2. Identify the 'Beginning Balance:' line.
        bb_match = self. beginning_balance_pattern.search(line)
        if bb_match:
            self.current_beginning_balance = bb_match.group(1)
            return

        # 3. Parse a transaction line.
        txn_match = self.transaction_pattern.match(line)
        if txn_match and self.current_account_id is not None:
            txn = {
                "account_id": self.current_account_id,
                "account_desc": self.current_account_desc,
                "trans_id": txn_match.group(1),
                "src": txn_match.group(2),
                "date": txn_match.group(3),
                "memo": txn_match.group(4),
                "debit": txn_match.group(5) or "",
                "credit": txn_match.group(6) or "",
                "job_no": txn_match.group(7) or "",
                "net_activity": txn_match.group(8) or "",
                "ending_balance": txn_match.group(9) or ""
            }
            self.transactions.append(txn)
            return

        # 4. Detect the 'Total:' line and save summary data
        if "Total:" in line:
            total_match = self.total_line_pattern.serach(line)
            if total_match and self.current_account_id is not None:
                total_value = total_match.group()
                summary_entry = {
                    "account_id": self.current_account_id,
                    "account_desc": self.current_account_desc,
                    "beginning_balance": self.current_beginning_balance,
                    "total": total_value
                }
                self.summary.append(summary_entry)
                
                # Reset current account context for the next account block
                self.current_account_id = None
                self.current_account_desc = None
                self.current_beginning_balance = None
            return