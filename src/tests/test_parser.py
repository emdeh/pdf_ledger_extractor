import pytest
from parsers.ledger_parser import parse_ledger

def test_parse_ledger():
    transactions, summary = parse_ledger("sample_ledger.pdf")
    assert len(summary) > 0
    # Add more assertions...
