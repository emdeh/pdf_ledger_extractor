# Ledger Parser and Excel Exporter

This repository contains a Python tool to extract ledger data from PDF files and export it to Excel spreadsheets. It uses the [pdfplumber](https://github.com/jsvine/pdfplumber) library to extract text from PDFs and regular expressions to parse that text into structured data. The parsed data is then written to Excel using [pandas](https://pandas.pydata.org/) and [openpyxl](https://openpyxl.readthedocs.io/).

## Features

- **Multi-PDF Processing:** Processes all PDF files in a specified directory.
- **Data Extraction:** Parses ledger PDFs to extract transactions and account summary information.
- **Robust Parsing:** Handles multi-page PDFs with repeated headers and footers.
- **Excel Output:** Exports the data to Excel with two sheets:
  - **Details:** Individual transaction rows.
  - **Summary:** Account summary information.

## Repository Structure

```bash
├── requirements.txt
├── .gitignore
├── README.md
├── src
│   ├── main.py
│   ├── parsers
│   │   ├── __init__.py
│   │   └── ledger_parser.py
│   └── utils
│       ├── __init__.py
│       └── excel_writer.py
└── tests
    ├── __init__.py
    ├── test_ledger_multi_page.py # A script devleoped to cosntruct dummy ledgers - (developed by giving ChatGPT a written description of the target data)
    └── test_ledger_single_page.py # Earlier iteration of the multi page script abov.
```

## Installation

1. **Clone the Repository:**

   Open your terminal and run:
   ```bash
   git clone https://github.com/emdeh/ledger-parser.git
   cd ledger-parser
   ```

2. **Set Up a Virtual Environment:**

   Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies:**

   Install `requirements.txt`
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The main script processes all PDF files in a given input directory and creates an Excel file for each PDF in the specified output directory.

### Command-Line Usage

```bash
python main.py <input_directory> [output_directory]
```

- `<input_directory>`: Path to the directory containing your PDF files.
- `[output_directory]`: (Optional) Directory where the Excel files will be saved. If not specified, the default is `output`.

### Example

To process all PDFs in the `./pdfs` directory and write the results to the `./excel_outputs` directory, run:

```bash
python main.py ./pdfs ./excel_outputs
```

Each PDF (e.g. `ledger1.pdf`) will produce a corresponding Excel file (e.g. `ledger1.xlsx`).

## How It Works

### LedgerParser (`parsers/ledger_parser.py`)

- **Text Extraction:** Opens a PDF using `pdfplumber` and reads it page-by-page.
- **Parsing Logic:** Uses regular expressions to identify:
  - **Account Headers:** Lines like `1-2210 Cash Account` (supports one to three digits before the dash).
  - **Beginning Balance:** Lines like `Beginning Balance: $1000.00`.
  - **Transaction Rows:** Lines formatted as, for example:

    `TRX0001AB 01/07/2023 Opening Entry $500.00 $0.00 001 $500.00 $1500.00`.
  - **Total Rows:** Lines starting with `Total:` that include **four** amounts.
- **Header Handling:** Captures header information from the first page (i.e. anything before the table header row:

    `ID No., Src, Date, Memo, Debit, Credit, Job No., Net Activity, Ending Balance`
    
    and ignores repeated header details on subsequent pages.
- **Final Flush:** If an account block doesn’t have a total row by the end of the document, it flushes the account with zero totals.

### ExcelWriter (utils/excel_writer.py)

- **Data Conversion:** Converts the lists of transactions and summary data into pandas DataFrames.
- **Excel Export:** Writes two sheets:
  - **Details:** Contains all individual transaction records.
  - **Summary:** Contains one row per account summarising the ledger.
- **Error Handling:** Raises an error if either the transactions or summary data is empty.

### Main Script (main.py)

- **Directory Input:** Takes an input directory (and an optional output directory) from the command line.
- **File Processing:** Iterates over each PDF file in the input directory, processes it with `LedgerParser`, and writes the output using `ExcelWriter`.
- **Output Naming:** Each Excel file is named after the corresponding PDF (e.g. `my_ledger.pdf` becomes `my_ledger.xlsx`).
