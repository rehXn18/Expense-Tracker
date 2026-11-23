#!/usr/bin/env python3
"""
Terminal-Based Expense Tracker Application
Fulfilling all functional requirements from the Expense Tracker Problem Statement:
1. Add income and expenses (with amount, date, category, and description)
2. Select from predefined or custom expense categories (Food, Transportation, Shopping, Bills, Entertainment, etc.)
3. Edit and delete transactions
4. View full transaction history
5. Search and filter transactions (by date, category, amount range, or keyword)
6. Automatically calculate total income, total expenses, and remaining balance
7. Set and monitor monthly overall and category-wise budgets
8. Generate daily, weekly, and monthly financial reports
9. View graphical representations (ASCII terminal bar charts) of expenses
10. Load sample dataset from the problem statement (₹40,000 income, ₹23,000 expenses)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

DATA_FILE = "expenses_data.json"

DEFAULT_EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Shopping",
    "Bills",
    "Entertainment",
    "Education",
    "Healthcare",
    "Other",
]

DEFAULT_INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Investments",
    "Other Income",
]


class ExpenseTracker:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.transactions = []
        self.budgets = {
            "monthly_overall": 0.0,
            "categories": {}
        }
        self.next_id = 1
        self.load_data()

    def load_data(self):
        """Load transactions and budgets from a local JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.transactions = data.get("transactions", [])
                    self.budgets = data.get("budgets", {"monthly_overall": 0.0, "categories": {}})
                    if self.transactions:
                        self.next_id = max(t["id"] for t in self.transactions) + 1
                    else:
                        self.next_id = 1
            except (json.JSONDecodeError, IOError):
                print("Warning: Could not read data file. Starting with an empty ledger.")

    def save_data(self):
        """Save transactions and budgets to a local JSON file."""
        data = {
            "transactions": self.transactions,
            "budgets": self.budgets
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    # -------------------------------------------------------------------------
    # Core Transaction Operations
    # -------------------------------------------------------------------------
    def add_transaction(self, t_type, amount, category, date_str, description):
        """Record a new income or expense transaction."""
        transaction = {
            "id": self.next_id,
            "type": t_type,  # 'Income' or 'Expense'
            "amount": round(float(amount), 2),
            "category": category,
            "date": date_str,  # YYYY-MM-DD
            "description": description.strip()
        }
        self.transactions.append(transaction)
        self.next_id += 1
        self.save_data()
        return transaction

    def edit_transaction(self, t_id, amount=None, category=None, date_str=None, description=None):
        """Edit an existing transaction by ID."""
        for t in self.transactions:
            if t["id"] == t_id:
                if amount is not None:
                    t["amount"] = round(float(amount), 2)
                if category is not None:
                    t["category"] = category
                if date_str is not None:
                    t["date"] = date_str
                if description is not None:
                    t["description"] = description.strip()
                self.save_data()
                return True
        return False

    def delete_transaction(self, t_id):
        """Delete a transaction by ID."""
        for i, t in enumerate(self.transactions):
            if t["id"] == t_id:
                removed = self.transactions.pop(i)
                self.save_data()
                return removed
        return None

    def get_summary(self, transactions=None):
        """Calculate total income, total expenses, and remaining balance."""
        tx_list = transactions if transactions is not None else self.transactions
        total_income = sum(t["amount"] for t in tx_list if t["type"] == "Income")
        total_expenses = sum(t["amount"] for t in tx_list if t["type"] == "Expense")
        remaining_balance = total_income - total_expenses
        return total_income, total_expenses, remaining_balance

    # -------------------------------------------------------------------------
    # Formatting & Display Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def format_currency(amount):
        return f"₹{amount:,.2f}"

    def print_transactions_table(self, transactions, title="Transaction History"):
        print(f"\n{'=' * 78}")
        print(f" {title}")
        print(f"{'=' * 78}")
        if not transactions:
            print(" No transactions found.")
            print(f"{'=' * 78}")
            return

        header = f" {'ID':<4} | {'Date':<10} | {'Type':<8} | {'Category':<15} | {'Amount':>12} | {'Description'}"
        print(header)
        print(f"{'-' * 78}")
        for t in sorted(transactions, key=lambda x: (x["date"], x["id"])):
            amt_str = self.format_currency(t["amount"])
            print(f" {t['id']:<4} | {t['date']:<10} | {t['type']:<8} | {t['category']:<15} | {amt_str:>12} | {t['description']}")
        print(f"{'-' * 78}")
        inc, exp, bal = self.get_summary(transactions)
        print(f" Total Income: {self.format_currency(inc)}   |   Total Expenses: {self.format_currency(exp)}   |   Balance: {self.format_currency(bal)}")
        print(f"{'=' * 78}")

    # -------------------------------------------------------------------------
    # Budgeting & Monitoring
    # -------------------------------------------------------------------------
    def set_monthly_budget(self, amount):
        self.budgets["monthly_overall"] = round(float(amount), 2)
        self.save_data()

    def set_category_budget(self, category, amount):
        self.budgets["categories"][category] = round(float(amount), 2)
        self.save_data()

    def display_budget_status(self, year_month=None):
        """Show remaining budget for the specified YYYY-MM (defaults to current month)."""
        if not year_month:
            year_month = datetime.now().strftime("%Y-%m")

        month_expenses = [
            t for t in self.transactions
            if t["type"] == "Expense" and t["date"].startswith(year_month)
        ]
        total_month_exp = sum(t["amount"] for t in month_expenses)
        cat_spending = defaultdict(float)
        for t in month_expenses:
            cat_spending[t["category"]] += t["amount"]

        print(f"\n{'=' * 72}")
        print(f" Budget Status for Month: {year_month}")
        print(f"{'=' * 72}")

        overall_limit = self.budgets.get("monthly_overall", 0.0)
        if overall_limit > 0:
            rem = overall_limit - total_month_exp
            pct = (total_month_exp / overall_limit) * 100
            status = "WITHIN BUDGET" if rem >= 0 else "OVER BUDGET!"
            print(f" Monthly Overall Limit : {self.format_currency(overall_limit)}")
            print(f" Total Spent           : {self.format_currency(total_month_exp)} ({pct:.1f}%)")
            print(f" Remaining Budget      : {self.format_currency(rem)} [{status}]")
        else:
            print(" Monthly Overall Limit : Not Set")
            print(f" Total Spent           : {self.format_currency(total_month_exp)}")

        cat_budgets = self.budgets.get("categories", {})
        if cat_budgets:
            print(f"\n {'Category':<16} | {'Budget Limit':>14} | {'Spent':>14} | {'Remaining':>14} | {'Status'}")
            print(f" {'-' * 68}")
            for cat, limit in sorted(cat_budgets.items()):
                if limit <= 0:
                    continue
                spent = cat_spending.get(cat, 0.0)
                rem = limit - spent
                status = "OK" if rem >= 0 else "EXCEEDED"
                print(
                    f" {cat:<16} | {self.format_currency(limit):>14} | "
                    f"{self.format_currency(spent):>14} | {self.format_currency(rem):>14} | {status}"
                )
        else:
            print("\n No category-wise budgets set yet.")
        print(f"{'=' * 72}")

    # -------------------------------------------------------------------------
    # Financial Reports (Daily, Weekly, Monthly)
    # -------------------------------------------------------------------------
    def generate_reports(self, period="monthly"):
        print(f"\n{'=' * 72}")
        print(f" {period.capitalize()} Financial Summary Report")
        print(f"{'=' * 72}")
        if not self.transactions:
            print(" No transactions available to generate reports.")
            print(f"{'=' * 72}")
            return

        grouped = defaultdict(lambda: {"Income": 0.0, "Expense": 0.0})
        for t in self.transactions:
            try:
                dt = datetime.strptime(t["date"], "%Y-%m-%d")
            except ValueError:
                continue

            if period == "daily":
                key = t["date"]
            elif period == "weekly":
                iso_year, iso_week, _ = dt.isocalendar()
                key = f"{iso_year}-W{iso_week:02d}"
            else:  # monthly
                key = dt.strftime("%Y-%m")

            grouped[key][t["type"]] += t["amount"]

        print(f" {'Period':<14} | {'Total Income':>16} | {'Total Expenses':>16} | {'Net Balance':>16}")
        print(f" {'-' * 68}")
        for key in sorted(grouped.keys()):
            inc = grouped[key]["Income"]
            exp = grouped[key]["Expense"]
            bal = inc - exp
            print(
                f" {key:<14} | {self.format_currency(inc):>16} | "
                f"{self.format_currency(exp):>16} | {self.format_currency(bal):>16}"
            )
        print(f"{'=' * 72}")

    # -------------------------------------------------------------------------
    # Graphical Visualization (Terminal ASCII Charts)
    # -------------------------------------------------------------------------
    def display_expense_chart(self):
        """Render an ASCII horizontal bar chart of expenses by category."""
        expenses = [t for t in self.transactions if t["type"] == "Expense"]
        print(f"\n{'=' * 74}")
        print(" Graphical Representation of Expenses by Category")
        print(f"{'=' * 74}")
        if not expenses:
            print(" No expense records found to visualize.")
            print(f"{'=' * 74}")
            return

        cat_totals = defaultdict(float)
        for t in expenses:
            cat_totals[t["category"]] += t["amount"]

        total_exp = sum(cat_totals.values())
        max_val = max(cat_totals.values()) if cat_totals else 1.0
        max_bar_width = 30

        for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
            bar_len = int((amt / max_val) * max_bar_width) if max_val > 0 else 0
            bar = "█" * max(bar_len, 1)
            pct = (amt / total_exp) * 100 if total_exp > 0 else 0
            print(f" {cat:<15} | {bar:<30} | {self.format_currency(amt):>11} ({pct:5.1f}%)")

        print(f"{'-' * 74}")
        inc, exp, bal = self.get_summary()
        print(f" Total Income   : {self.format_currency(inc)}")
        print(f" Total Expenses : {self.format_currency(exp)}")
        print(f" Balance        : {self.format_currency(bal)}")
        print(f"{'=' * 74}")

    # -------------------------------------------------------------------------
    # Sample Data Loader (Matches Problem Statement Example)
    # -------------------------------------------------------------------------
    def load_sample_example(self):
        """Populate the exact example from the Problem Statement document."""
        today = datetime.now().strftime("%Y-%m-%d")
        sample_items = [
            ("Income", 40000, "Salary", today, "Monthly income"),
            ("Expense", 6000, "Food", today, "Monthly groceries and dining"),
            ("Expense", 3000, "Transportation", today, "Commute and fuel"),
            ("Expense", 5000, "Shopping", today, "Clothes and essentials"),
            ("Expense", 7000, "Bills", today, "Electricity, internet, utilities"),
            ("Expense", 2000, "Entertainment", today, "Movies and outings"),
        ]
        for t_type, amount, cat, dt, desc in sample_items:
            self.add_transaction(t_type, amount, cat, dt, desc)
        self.set_monthly_budget(30000)


# =============================================================================
# Interactive CLI Input Helpers
# =============================================================================
def prompt_float(prompt_text, allow_empty=False):
    while True:
        val = input(prompt_text).strip()
        if allow_empty and val == "":
            return None
        try:
            num = float(val)
            if num <= 0:
                print(" Please enter a positive amount greater than 0.")
                continue
            return num
        except ValueError:
            print(" Invalid number. Please enter a numeric value (e.g., 2500).")


def prompt_date(prompt_text, default_today=True, allow_empty=False):
    today_str = datetime.now().strftime("%Y-%m-%d")
    while True:
        val = input(prompt_text).strip()
        if val == "":
            if allow_empty:
                return None
            if default_today:
                return today_str
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            print(" Invalid date format. Please use YYYY-MM-DD (e.g., 2026-11-23).")


def choose_category(categories, allow_empty=False):
    print("\n Available Categories:")
    for idx, cat in enumerate(categories, start=1):
        print(f"  {idx}. {cat}")
    print(f"  {len(categories) + 1}. Custom Category")

    while True:
        choice = input(" Select category number (or press Enter to skip): " if allow_empty else " Select category number: ").strip()
        if allow_empty and choice == "":
            return None
        if choice.isdigit():
            c_num = int(choice)
            if 1 <= c_num <= len(categories):
                return categories[c_num - 1]
            elif c_num == len(categories) + 1:
                custom = input(" Enter custom category name: ").strip()
                if custom:
                    return custom
        print(" Invalid selection. Please try again.")


# =============================================================================
# Main Terminal Menu Loop
# =============================================================================
def run_cli():
    tracker = ExpenseTracker()

    while True:
        inc, exp, bal = tracker.get_summary()
        print("\n" + "=" * 56)
        print("          PERSONAL EXPENSE TRACKER (CLI)")
        print("=" * 56)
        print(f" Income: {tracker.format_currency(inc)}  |  Expenses: {tracker.format_currency(exp)}  |  Balance: {tracker.format_currency(bal)}")
        print("-" * 56)
        print("  1. Add Income")
        print("  2. Add Expense")
        print("  3. View All Transactions")
        print("  4. Edit or Delete a Transaction")
        print("  5. Search & Filter Transactions")
        print("  6. Set or Monitor Budgets")
        print("  7. Generate Financial Reports (Daily / Weekly / Monthly)")
        print("  8. View Expense Charts (ASCII Graph)")
        print("  9. Load Sample Data from Problem Statement (₹40,000 example)")
        print("  0. Exit")
        print("=" * 56)

        choice = input(" Enter your choice (0-9): ").strip()

        if choice == "1":
            print("\n--- Add Income ---")
            amt = prompt_float(" Enter income amount (₹): ")
            cat = choose_category(DEFAULT_INCOME_CATEGORIES)
            dt = prompt_date(f" Enter date [YYYY-MM-DD] (press Enter for today): ")
            desc = input(" Enter description: ").strip() or "Income"
            tx = tracker.add_transaction("Income", amt, cat, dt, desc)
            print(f" -> Added Income #{tx['id']} of {tracker.format_currency(tx['amount'])} under '{tx['category']}'.")

        elif choice == "2":
            print("\n--- Add Expense ---")
            amt = prompt_float(" Enter expense amount (₹): ")
            cat = choose_category(DEFAULT_EXPENSE_CATEGORIES)
            dt = prompt_date(f" Enter date [YYYY-MM-DD] (press Enter for today): ")
            desc = input(" Enter description: ").strip() or cat
            tx = tracker.add_transaction("Expense", amt, cat, dt, desc)
            print(f" -> Added Expense #{tx['id']} of {tracker.format_currency(tx['amount'])} under '{tx['category']}'.")

        elif choice == "3":
            tracker.print_transactions_table(tracker.transactions, "Complete Transaction History")

        elif choice == "4":
            tracker.print_transactions_table(tracker.transactions)
            if not tracker.transactions:
                continue
            action = input("\n Enter 'E' to Edit, 'D' to Delete, or press Enter to cancel: ").strip().upper()
            if action not in ("E", "D"):
                continue
            t_id_str = input(" Enter Transaction ID: ").strip()
            if not t_id_str.isdigit():
                print(" Invalid ID.")
                continue
            t_id = int(t_id_str)

            if action == "D":
                removed = tracker.delete_transaction(t_id)
                if removed:
                    print(f" -> Deleted Transaction #{t_id} ({removed['category']} - {tracker.format_currency(removed['amount'])}).")
                else:
                    print(f" -> Transaction ID #{t_id} not found.")
            elif action == "E":
                target = next((t for t in tracker.transactions if t["id"] == t_id), None)
                if not target:
                    print(f" -> Transaction ID #{t_id} not found.")
                    continue
                print(f" Editing Transaction #{t_id} (press Enter to keep current value):")
                new_amt = prompt_float(f"  Amount [{target['amount']}]: ", allow_empty=True)
                cats = DEFAULT_INCOME_CATEGORIES if target["type"] == "Income" else DEFAULT_EXPENSE_CATEGORIES
                new_cat = choose_category(cats, allow_empty=True)
                new_dt = prompt_date(f"  Date [{target['date']}]: ", default_today=False, allow_empty=True)
                new_desc = input(f"  Description [{target['description']}]: ").strip()
                tracker.edit_transaction(
                    t_id,
                    amount=new_amt,
                    category=new_cat,
                    date_str=new_dt,
                    description=new_desc if new_desc != "" else None
                )
                print(f" -> Updated Transaction #{t_id}.")

        elif choice == "5":
            print("\n--- Search & Filter Transactions ---")
            print("  1. Filter by Category")
            print("  2. Filter by Date or Month (e.g., 2026-11-23 or 2026-11)")
            print("  3. Filter by Minimum/Maximum Amount")
            print("  4. Search by Description Keyword")
            sub = input(" Select filter option (1-4): ").strip()
            results = []
            if sub == "1":
                kw = input(" Enter category name: ").strip().lower()
                results = [t for t in tracker.transactions if kw in t["category"].lower()]
            elif sub == "2":
                dt_prefix = input(" Enter date (YYYY-MM-DD) or month (YYYY-MM): ").strip()
                results = [t for t in tracker.transactions if t["date"].startswith(dt_prefix)]
            elif sub == "3":
                min_a = prompt_float(" Minimum amount (press Enter for no minimum): ", allow_empty=True) or 0.0
                max_a = prompt_float(" Maximum amount (press Enter for no maximum): ", allow_empty=True) or float("inf")
                results = [t for t in tracker.transactions if min_a <= t["amount"] <= max_a]
            elif sub == "4":
                kw = input(" Enter keyword: ").strip().lower()
                results = [t for t in tracker.transactions if kw in t["description"].lower() or kw in t["category"].lower()]
            else:
                print(" Invalid filter option.")
                continue
            tracker.print_transactions_table(results, "Filtered Transactions")

        elif choice == "6":
            print("\n--- Budget Management ---")
            print("  1. View Current Budget Status")
            print("  2. Set Monthly Overall Budget")
            print("  3. Set Category-Wise Monthly Budget")
            sub = input(" Select option (1-3): ").strip()
            if sub == "1":
                ym = input(" Enter month [YYYY-MM] (press Enter for current month): ").strip() or None
                tracker.display_budget_status(ym)
            elif sub == "2":
                amt = prompt_float(" Enter monthly overall budget limit (₹): ")
                tracker.set_monthly_budget(amt)
                print(f" -> Monthly overall budget set to {tracker.format_currency(amt)}.")
            elif sub == "3":
                cat = choose_category(DEFAULT_EXPENSE_CATEGORIES)
                amt = prompt_float(f" Enter monthly budget limit for '{cat}' (₹): ")
                tracker.set_category_budget(cat, amt)
                print(f" -> Budget for '{cat}' set to {tracker.format_currency(amt)}.")

        elif choice == "7":
            print("\n--- Generate Financial Reports ---")
            print("  1. Daily Summary")
            print("  2. Weekly Summary")
            print("  3. Monthly Summary")
            sub = input(" Select report type (1-3): ").strip()
            period_map = {"1": "daily", "2": "weekly", "3": "monthly"}
            if sub in period_map:
                tracker.generate_reports(period_map[sub])
            else:
                print(" Invalid report option.")

        elif choice == "8":
            tracker.display_expense_chart()

        elif choice == "9":
            tracker.load_sample_example()
            print(" -> Loaded sample data from the Problem Statement!")
            tracker.print_transactions_table(tracker.transactions, "Sample Problem Statement Data")
            tracker.display_expense_chart()

        elif choice == "0":
            print(" Goodbye! Your data is saved in", tracker.data_file)
            break
        else:
            print(" Invalid choice. Please select an option from 0 to 9.")


def run_demo():
    """Run an automated demonstration of the example from the Problem Statement."""
    demo_file = "/tmp/demo_expenses.json"
    if os.path.exists(demo_file):
        os.remove(demo_file)

    tracker = ExpenseTracker(data_file=demo_file)
    tracker.load_sample_example()
    tracker.set_category_budget("Food", 7500)
    tracker.set_category_budget("Transportation", 4000)
    tracker.set_category_budget("Shopping", 5000)
    tracker.set_category_budget("Bills", 8000)
    tracker.set_category_budget("Entertainment", 3000)

    tracker.print_transactions_table(tracker.transactions, "Problem Statement Example Transactions")
    tracker.display_budget_status()
    tracker.generate_reports("monthly")
    tracker.display_expense_chart()

    if os.path.exists(demo_file):
        os.remove(demo_file)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_cli()