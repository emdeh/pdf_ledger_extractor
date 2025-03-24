"""
This module provides functionality to write transaction and summary data to an Excel file.

Classes:
    ExcelWriter: A class to handle writing transaction and summary data to an Excel file with two sheets.

Usage example:
    transactions = [
        {"date": "2023-01-01", "amount": 100, "description": "Transaction 1"},
        {"date": "2023-01-02", "amount": 200, "description": "Transaction 2"}
    ]
    summary = [
        {"total_transactions": 2, "total_amount": 300}
    ]
    output_path = "output.xlsx"
    
    writer = ExcelWriter(transactions, summary, output_path)
    writer.write()
"""

from typing import List, Dict
import pandas as pd

class ExcelWriter:
    """
    Class to write transaction and summary data to an Excel file.

    Attributes:
        transactions (List[Dict]): A list of dictionaries containing transaction data.
        summary (List[Dict]): A list of dictionaries containing summary data.
        output_path (str): The file path where the Excel file will be saved.

    Methods:
        write():
            Writes the transaction and summary data to an Excel file with two sheets: 'Details' and 'Summary'.
    """
    def __init__(self, transactions: List[Dict], summary: List[Dict], output_path: str):
        self.transactions = transactions
        self.summary = summary
        self.output_path = output_path

    def write(self):
        """
        This method converts the transactions and summary data into pandas DataFrames
        and writes them to an Excel file specified by the output_path attribute. The
        'Details' sheet contains the transactions data, and the 'Summary' sheet contains
        the summary data.

        Attributes:
            transactions (list): A list of dictionaries containing transaction data.
            summary (list): A list of dictionaries containing summary data.
            output_path (str): The file path where the Excel file will be saved.

        Raises:
            ValueError: If transactions or summary data is not provided.
            IOError: If there is an issue writing the Excel file to the specified path.
        """
        if not self.transactions:
            raise ValueError("No transactions data provided.")
        if not self.summary:
            raise ValueError("No summary data provided.")

        df_transactions = pd.DataFrame(self.transactions)
        df_summary = pd.DataFrame(self.summary)

        try:
            with pd.ExcelWriter(self.output_path, engine='openpyxl') as writer:
                df_transactions.to_excel(writer, sheet_name="Details", index=False)
                df_summary.to_excel(writer, sheet_name="Summary", index=False)
        except IOError as e:
            raise IOError(f"Error writing Excel file to {self.output_path}: {e}")
