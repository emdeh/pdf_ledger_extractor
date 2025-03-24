#### DOES NOT INCLUDE PAGE NUMBERS WHICH IS USED BY THE PARSER LOGIC - USE THE MULTIPAGE VERSION ####

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

def generate_test_ledger(pdf_path: str):
    """
    Generates a test ledger PDF in A4 portrait mode with aligned columns.
    Adjust column positions (id_x, src_x, date_x, etc.) as needed to fit everything on the page.
    """

    # Use A4 instead of letter
    width, height = A4  # A4 portrait: ~595 x 842 points
    margin = 40
    y = height - margin

    # Right column x coordinate (for right-justified text)
    right_x = width - margin

    # Header details
    created_date = datetime.now().strftime("Created: %d/%m/%Y %I:%M %p")
    company_name = "Test Company"
    street_address = "123 Test Street"
    suburb = "Testville"
    abn = "ABN: 123456789"
    email = "Email: test@example.com"
    time_period = "July 2023 To June 2024"

    # ---------------------------
    # Draw Document Header
    # ---------------------------
    # Row 1: Created date (left) & Company name (right)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, created_date)

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(right_x, y, company_name)
    y -= 20

    # Row 2: Left: "General Ledger [Detail]" & Right: Street Address
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "General Ledger [Detail]")

    c.setFont("Helvetica", 12)
    c.drawRightString(right_x, y, street_address)
    y -= 20

    # Row 3: Left: Time Period & Right: Suburb
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, time_period)

    c.setFont("Helvetica", 12)
    c.drawRightString(right_x, y, suburb)
    y -= 20

    # Row 4 & 5: ABN & Email (right-aligned)
    c.setFont("Helvetica", 10)
    c.drawRightString(right_x, y, abn)
    y -= 20

    c.drawRightString(right_x, y, email)
    y -= 40  # extra spacing after header

    # ---------------------------
    # Define Column X Positions
    # ---------------------------
    # We'll space columns so they fit within A4 portrait (width ~595).
    # Start at 'margin' and increment for each column. Tweak as needed.
    id_x = margin              # ~40
    src_x = id_x + 40          # ~80
    date_x = src_x + 25        # ~105
    memo_x = date_x + 55       # ~160 (Memo column is bigger)
    debit_x = memo_x + 110     # ~270
    credit_x = debit_x + 60    # ~330
    job_no_x = credit_x + 60   # ~390
    net_activity_x = job_no_x + 40  # ~430
    ending_balance_x = net_activity_x + 60  # ~490

    # Ensure we don't exceed right margin
    # The last column is at x=490; right margin is 595-40=555 => OK

    # ---------------------------
    # Table Header in Grey Band
    # ---------------------------
    header_height = 15
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Light grey background
    c.rect(margin, y - header_height + 8, (width - 2*margin), header_height, fill=1, stroke=0)
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
    y -= header_height + 5

    # ---------------------------
    # First Account Block
    # ---------------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "1-2210   Cash Account")
    y -= 20

    c.drawString(margin, y, "Beginning Balance: $1000.00")
    y -= 10

    c.setLineWidth(2)
    c.line(margin, y, width - margin, y)
    y -= 20

    # Transaction data
    c.setFont("Helvetica", 10)
    transactions = [
        {
            "id_no": "TRX0001",
            "src": "AB",
            "date": "01/07/2023",
            "memo": "Opening Entry",
            "debit": "500.00",
            "credit": "0.00",
            "job_no": "001",
            "net": "500.00",
            "end_bal": "1500.00"
        },
        {
            "id_no": "TRX0002",
            "src": "AB",
            "date": "05/07/2023",
            "memo": "Purchase",
            "debit": "0.00",
            "credit": "200.00",
            "job_no": "002",
            "net": "-200.00",
            "end_bal": "1300.00"
        },
        {
            "id_no": "TRX0003",
            "src": "AB",
            "date": "08/07/2023",
            "memo": "Service Fee",
            "debit": "25.00",
            "credit": "0.00",
            "job_no": "003",
            "net": "25.00",
            "end_bal": "1325.00"
        },
        {
            "id_no": "TRX0004",
            "src": "AB",
            "date": "10/07/2023",
            "memo": "Refund",
            "debit": "0.00",
            "credit": "50.00",
            "job_no": "004",
            "net": "50.00",
            "end_bal": "1275.00"
        },
        {
            "id_no": "TRX0005",
            "src": "AB",
            "date": "12/07/2023",
            "memo": "Adjustment",
            "debit": "0.00",
            "credit": "75.00",
            "job_no": "005",
            "net": "-75.00",
            "end_bal": "1200.00"
        },
        {
            "id_no": "TRX0006",
            "src": "AB",
            "date": "15/07/2023",
            "memo": "Payment Received",
            "debit": "300.00",
            "credit": "0.00",
            "job_no": "006",
            "net": "300.00",
            "end_bal": "1500.00"
        },
        {
            "id_no": "TRX0007",
            "src": "AB",
            "date": "18/07/2023",
            "memo": "Purchase",
            "debit": "0.00",
            "credit": "150.00",
            "job_no": "007",
            "net": "-150.00",
            "end_bal": "1350.00"
        },
        {
            "id_no": "TRX0008",
            "src": "AB",
            "date": "20/07/2023",
            "memo": "Discount",
            "debit": "0.00",
            "credit": "30.00",
            "job_no": "008",
            "net": "30.00",
            "end_bal": "1320.00"
        },
        {
            "id_no": "TRX0009",
            "src": "AB",
            "date": "22/07/2023",
            "memo": "Service Charge",
            "debit": "40.00",
            "credit": "0.00",
            "job_no": "009",
            "net": "40.00",
            "end_bal": "1360.00"
        },
        {
            "id_no": "TRX0010",
            "src": "AB",
            "date": "25/07/2023",
            "memo": "Miscellaneous",
            "debit": "0.00",
            "credit": "20.00",
            "job_no": "010",
            "net": "-20.00",
            "end_bal": "1340.00"
        },
    ]

    # Draw each transaction in columns
    for txn in transactions:
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

    # Total row for the first account
    c.drawString(memo_x, y, "Total:")
    c.drawString(debit_x, y, "$500.00")
    c.drawString(credit_x, y, "$200.00")
    c.drawString(net_activity_x, y, "$300.00")
    c.drawString(ending_balance_x, y, "$1300.00")
    y -= 10

    c.setLineWidth(1)
    c.line(margin, y, width - margin, y)
    y -= 40

    # ---------------------------
    # Second Account Block (No transactions)
    # ---------------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "2-3456   Savings Account")
    y -= 20

    c.drawString(margin, y, "Beginning Balance: $2000.00")
    y -= 10
    c.setLineWidth(2)
    c.line(margin, y, width - margin, y)
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(memo_x, y, "Total:")
    c.drawString(debit_x, y, "$0.00")
    c.drawString(credit_x, y, "$0.00")
    c.drawString(net_activity_x, y, "$0.00")
    c.drawString(ending_balance_x, y, "$2000.00")
    y -= 10

    c.setLineWidth(1)
    c.line(margin, y, width - margin, y)
    y -= 20

    c.save()

if __name__ == "__main__":
    # Save the PDF in tests/test-files
    output_dir = os.path.join("tests", "test-files")
    os.makedirs(output_dir, exist_ok=True)
    filename = "test_ledger" + datetime.now().strftime("%Y%m%d%H%M%S" + ".pdf")
    pdf_path = os.path.join(output_dir, filename)
    
    generate_test_ledger(pdf_path)
    print(f"Test ledger PDF generated as '{pdf_path}'")

    