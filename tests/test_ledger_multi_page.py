import os
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

# Constants for page layout
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40

# Column positions (adjusted for A4 portrait)
id_x = MARGIN              # ~40
src_x = id_x + 40          # ~80
date_x = src_x + 25        # ~105
memo_x = date_x + 55       # ~160 (Memo column is bigger)
debit_x = memo_x + 110     # ~270
credit_x = debit_x + 60    # ~330
job_no_x = credit_x + 60   # ~390
net_activity_x = job_no_x + 40  # ~430
ending_balance_x = net_activity_x + 60  # ~490

# List of possible memos
MEMO_OPTIONS = [
    "Opening Entry", "Purchase", "Service Fee", "Refund", "Adjustment",
    "Payment Received", "Discount", "Service Charge", "Miscellaneous", "Rebate"
]

# --- Custom Canvas for Dynamic Page Numbering ---
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        # Draw the footer on the left
        self.drawString(MARGIN, MARGIN - 10, f"Page {self.getPageNumber()} of {page_count}")

def draw_table_header(c, y):
    """Draws the grey header row for the transaction table and returns the new y."""
    header_height = 15
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(MARGIN, y - header_height + 8, (PAGE_WIDTH - 2 * MARGIN), header_height, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(id_x, y, "ID No")
    c.drawString(src_x, y, "Src")
    c.drawString(date_x, y, "Date")
    c.drawString(memo_x, y, "Memo")
    c.drawString(debit_x, y, "Debit")
    c.drawString(credit_x, y, "Credit")
    c.drawString(job_no_x, y, "Job No.")
    c.drawString(net_activity_x, y, "Net Activity")
    c.drawString(ending_balance_x, y, "Ending Balance")
    y -= (header_height + 5)
    return y

def check_page_break(c, y):
    """If y is too low, start a new page and redraw table header; return updated y."""
    if y < MARGIN + 100:  # threshold can be adjusted
        c.showPage()
        y = PAGE_HEIGHT - MARGIN
        y = draw_table_header(c, y)
    return y

def generate_transactions(beginning_balance: float, count: int) -> (list, dict):
    """
    Generate a list of random transactions.
    Returns the list of transactions and a totals dictionary.
    """
    transactions = []
    current_balance = beginning_balance
    total_debit = 0.0
    total_credit = 0.0

    for i in range(1, count + 1):
        trans_id = f"TRX{i:04d}"
        src = "AB"
        day = random.randint(1, 28)
        date = f"{day:02d}/07/2023"
        memo = random.choice(MEMO_OPTIONS)
        if random.choice([True, False]):
            debit = round(random.uniform(10, 500), 2)
            credit = 0.00
            net = debit  # positive
        else:
            debit = 0.00
            credit = round(random.uniform(10, 500), 2)
            net = -credit  # negative
        total_debit += debit
        total_credit += credit
        current_balance += net
        job_no = f"{random.randint(1,999):03d}"
        txn = {
            "id_no": trans_id,
            "src": src,
            "date": date,
            "memo": memo,
            "debit": f"{debit:.2f}",
            "credit": f"{credit:.2f}",
            "job_no": job_no,
            "net": f"{net:.2f}",
            "end_bal": f"{current_balance:.2f}"
        }
        transactions.append(txn)

    totals = {
        "total_debit": f"{total_debit:.2f}",
        "total_credit": f"{total_credit:.2f}",
        "total_net": f"{(total_debit - total_credit):.2f}",
        "total_ending": f"{current_balance:.2f}"
    }
    return transactions, totals

def generate_account_data():
    """
    Generate account blocks according to the pattern:
      Group 1: 2 accounts, no transactions.
      Group 2: 2 accounts, with transactions.
      Group 3: 3 accounts, no transactions.
      Group 4: 2 accounts, with transactions.
      Group 5: 3 accounts, no transactions.
      Group 6: 3 extra accounts, no transactions (at the very end).
    Returns a list of account dictionaries.
    """
    accounts = []
    account_num = 1

    def make_account_id(n):
        return f"{n}-{'%04d' % (2200 + n)}"

    # Group 1: 2 accounts, no transactions.
    for _ in range(2):
        accounts.append({
            "account_id": make_account_id(account_num),
            "account_desc": f"Account {account_num} (No Txns)",
            "beginning_balance": round(random.uniform(500, 5000), 2),
            "transactions": []
        })
        account_num += 1

    # Group 2: 2 accounts, with transactions.
    for _ in range(2):
        beginning = round(random.uniform(500, 5000), 2)
        # For Account 4, double the size (force many transactions).
        if account_num == 4:
            txn_count = 50
        else:
            txn_count = random.randint(5, 20)
        txns, totals = generate_transactions(beginning, txn_count)
        accounts.append({
            "account_id": make_account_id(account_num),
            "account_desc": f"Account {account_num} (With Txns)",
            "beginning_balance": beginning,
            "transactions": txns,
            "totals": totals
        })
        account_num += 1

    # Group 3: 3 accounts, no transactions.
    for _ in range(3):
        accounts.append({
            "account_id": make_account_id(account_num),
            "account_desc": f"Account {account_num} (No Txns)",
            "beginning_balance": round(random.uniform(500, 5000), 2),
            "transactions": []
        })
        account_num += 1

    # Group 4: 2 accounts, with transactions.
    for _ in range(2):
        beginning = round(random.uniform(500, 5000), 2)
        txn_count = random.randint(5, 20)
        txns, totals = generate_transactions(beginning, txn_count)
        accounts.append({
            "account_id": make_account_id(account_num),
            "account_desc": f"Account {account_num} (With Txns)",
            "beginning_balance": beginning,
            "transactions": txns,
            "totals": totals
        })
        account_num += 1

    # Group 5: 3 accounts, no transactions.
    for _ in range(3):
        accounts.append({
            "account_id": make_account_id(account_num),
            "account_desc": f"Account {account_num} (No Txns)",
            "beginning_balance": round(random.uniform(500, 5000), 2),
            "transactions": []
        })
        account_num += 1

    # Group 6: 3 extra accounts, no transactions at the very end.
    for _ in range(3):
        accounts.append({
            "account_id": make_account_id(account_num),
            "account_desc": f"Account {account_num} (No Txns - Extra)",
            "beginning_balance": round(random.uniform(500, 5000), 2),
            "transactions": []
        })
        account_num += 1

    return accounts

def draw_account_block(c, account, y):
    """
    Draws a single account block, including the account header, beginning balance,
    transactions (if any), and a total row.
    Returns the updated y position.
    """
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, f"{account['account_id']}   {account['account_desc']}")
    y -= 20

    c.drawString(MARGIN, y, f"Beginning Balance: ${account['beginning_balance']:.2f}")
    y -= 10

    c.setLineWidth(2)
    c.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)
    y -= 20

    c.setFont("Helvetica", 10)

    if account.get("transactions"):
        for txn in account["transactions"]:
            y = check_page_break(c, y)
            c.drawString(id_x, y, txn["id_no"])
            c.drawString(src_x, y, txn["src"])
            c.drawString(date_x, y, txn["date"])
            c.drawString(memo_x, y, txn["memo"])
            c.drawString(debit_x, y, f"${txn['debit']}")
            c.drawString(credit_x, y, f"${txn['credit']}")
            c.drawString(job_no_x, y, txn["job_no"])
            c.drawString(net_activity_x, y, f"${txn['net']}")
            c.drawString(ending_balance_x, y, f"${txn['end_bal']}")
            y -= 20

        totals = account["totals"]
        y = check_page_break(c, y)
        c.drawString(memo_x, y, "Total:")
        c.drawString(debit_x, y, f"${totals['total_debit']}")
        c.drawString(credit_x, y, f"${totals['total_credit']}")
        c.drawString(net_activity_x, y, f"${totals['total_net']}")
        c.drawString(ending_balance_x, y, f"${totals['total_ending']}")
        y -= 10
    else:
        y = check_page_break(c, y)
        c.drawString(memo_x, y, "Total:")
        c.drawString(debit_x, y, "$0.00")
        c.drawString(credit_x, y, "$0.00")
        c.drawString(net_activity_x, y, "$0.00")
        c.drawString(ending_balance_x, y, f"${account['beginning_balance']:.2f}")
        y -= 10

    c.setLineWidth(1)
    c.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)
    y -= 40
    return y

def generate_test_ledger(pdf_path: str):
    """
    Generates a test ledger PDF in A4 portrait mode with multiple account blocks.
    The PDF includes accounts with a varying number of randomly generated transactions.
    A dynamic footer is added on the left with the correct total page count.
    """
    c = NumberedCanvas(pdf_path, pagesize=A4)
    y = PAGE_HEIGHT - MARGIN

    # Document Header
    created_date = datetime.now().strftime("Created: %d/%m/%Y %I:%M %p")
    company_name = "Test Company"
    street_address = "123 Test Street"
    suburb = "Testville"
    abn = "ABN: 123456789"
    email = "Email: test@example.com"
    time_period = "July 2023 To June 2024"

    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, y, created_date)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(PAGE_WIDTH - MARGIN, y, company_name)
    y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, "General Ledger [Detail]")
    c.setFont("Helvetica", 12)
    c.drawRightString(PAGE_WIDTH - MARGIN, y, street_address)
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, y, time_period)
    c.setFont("Helvetica", 12)
    c.drawRightString(PAGE_WIDTH - MARGIN, y, suburb)
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawRightString(PAGE_WIDTH - MARGIN, y, abn)
    y -= 20
    c.drawRightString(PAGE_WIDTH - MARGIN, y, email)
    y -= 40

    y = draw_table_header(c, y)
    accounts = generate_account_data()
    for account in accounts:
        y = check_page_break(c, y)
        y = draw_account_block(c, account, y)

    c.save()

if __name__ == "__main__":
    output_dir = os.path.join("tests", "test-files")
    os.makedirs(output_dir, exist_ok=True)
    filename = "test_ledger" + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
    pdf_path = os.path.join(output_dir, filename)
    
    generate_test_ledger(pdf_path)
    print(f"Test ledger PDF generated as '{pdf_path}'")
