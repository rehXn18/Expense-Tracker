# Personal Expense Tracker (Python CLI)

A simple, menu-driven terminal application in Python to record, categorize, monitor, and analyze personal income and expenses.

## Project Overview
Managing daily expenses manually makes it hard to track where money goes or stick to a monthly budget. This application lets users log income and expenses across categories (Food, Transportation, Shopping, Bills, Entertainment, etc.), monitor monthly budgets, generate summary reports, and view ASCII expense charts directly in the terminal.

## Calculation & Budget Rules
- **Total Expenses** = Sum of all expense transactions
- **Remaining Balance** = `Total Income - Total Expenses`
- **Budget Status** = Compares monthly spending against overall and category limits (`WITHIN BUDGET` / `OVER BUDGET!`)
- **Example:** With a monthly income of **₹40,000** and expenses across Food (₹6,000), Transportation (₹3,000), Shopping (₹5,000), Bills (₹7,000), and Entertainment (₹2,000), the system calculates **Total Expenses = ₹23,000** and **Remaining Balance = ₹17,000**.

## Key Features
- **Manage Transactions:** Add, edit, delete, and view income and expense records.
- **Search & Filter:** Filter history by category, date/month (`YYYY-MM`), amount range, or keyword.
- **Budget Tracking:** Set and monitor overall monthly and category-wise spending limits.
- **Reports & Charts:** View daily, weekly, and monthly summaries plus terminal ASCII bar charts.

## Project Structure
- `expense_tracker.py` — Main Python CLI application
- `expenses_data.json` — Auto-generated local file that stores transactions and budgets
- `README.md` — Project documentation

## Requirements & How to Run
- **Requirements:** Python 3.x (uses only standard library modules—no external installations needed)
- **Run Interactive App (Windows):**
  ```bash
  python expense_tracker.py
  ```
- **Run Sample Demo (₹40,000 example):**
  ```bash
  python expense_tracker.py --demo
  ```

## Python Concepts Demonstrated
- **Object-Oriented Programming (OOP):** `ExpenseTracker` class encapsulating all data and methods
- **File Handling:** Persistent local storage using the `json` and `os` modules
- **Data Structures:** Lists of dictionaries, list comprehensions, and `collections.defaultdict`
- **Date & Exception Handling:** Input validation using `datetime` and `try-except` blocks

## Important Notes
- Data saves automatically to `expenses_data.json` after every change.
- Pressing **Enter** on the date prompt automatically uses today's date.

## Future Improvements
- Export reports to CSV/Excel files
- Add SQLite database support
- Build a Tkinter GUI or web dashboard