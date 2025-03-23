"""
Module docstring
"""

import pandas as pd
from typing import List, Dict

class ExcelWriter:
    """
    Class docstring
    """
    def __init__(self, transactions: List[Dict], summary: List[Dict], output_path: str):
        self.transactions = transactions
        self.summary = summary
        self.output_path = output_path

    def write(self):
        """
        Writes data to an Excel file with two sheets: 'Details' and 'Summary'.
        """
        df_transactions = pd.DataFrame(self.transactions)
        df_summary = pd.DataFrame(self.summary)

        with pd.ExcelWriter(self.output_path, engine='openpyxl') as writer:
            df_transactions.to_excel(writer, sheet_name="Details", index=False)
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
