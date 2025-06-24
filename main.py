"""
main.py
--------
Entry point for the Personal Finance Management Application.
Handles user interaction and menu navigation.
"""

import getpass
from database import Database
from utils import is_positive_number, format_currency

def main():
    """
    Main function to start the application and handle registration/login.
    """
    db = Database('finance.db')
    print("Welcome to Personal Finance Manager!")
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            if db.register_user(username, password):
                print("Registration successful.")
            else:
                print("Username already exists.")
        elif choice == '2':
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            user_id = db.authenticate_user(username, password)
            if user_id:
                print(f"Welcome back, {username}!")
                user_menu(db, user_id)
            else:
                print("Invalid credentials.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

def user_menu(db, user_id):
    """
    User menu after successful login.
    Allows users to manage transactions, budgets, reports, backup, and restore.
    """
    while True:
        print("\n1. Add Income/Expense\n2. Update Entry\n3. Delete Entry\n4. View Reports\n5. Set Budget\n6. Backup Data\n7. Restore Data\n8. Logout")
        choice = input("Choose an option: ")
        if choice == '1':
            amount = input("Amount: ")
            if not is_positive_number(amount):
                print("Enter a valid positive number.")
                continue
            amount = float(amount)
            category = input("Category (e.g. Food, Rent, Salary): ")
            type_ = input("Type (income/expense): ").lower()
            if type_ not in ['income', 'expense']:
                print("Type must be 'income' or 'expense'.")
                continue
            db.add_transaction(user_id, amount, category, type_)
        elif choice == '2':
            entry_id = input("Entry ID to update: ")
            if not entry_id.isdigit():
                print("Invalid entry ID.")
                continue
            amount = input("New Amount: ")
            if not is_positive_number(amount):
                print("Enter a valid positive number.")
                continue
            amount = float(amount)
            category = input("New Category: ")
            type_ = input("Type (income/expense): ").lower()
            if type_ not in ['income', 'expense']:
                print("Type must be 'income' or 'expense'.")
                continue
            db.update_transaction(int(entry_id), amount, category, type_)
        elif choice == '3':
            entry_id = input("Entry ID to delete: ")
            if not entry_id.isdigit():
                print("Invalid entry ID.")
                continue
            db.delete_transaction(int(entry_id))
        elif choice == '4':
            print("1. Monthly Report\n2. Yearly Report")
            report_type = input("Choose: ")
            if report_type == '1':
                month = input("Month (1-12): ")
                year = input("Year (YYYY): ")
                if not (month.isdigit() and year.isdigit()):
                    print("Invalid month or year.")
                    continue
                db.monthly_report(user_id, int(month), int(year))
            elif report_type == '2':
                year = input("Year (YYYY): ")
                if not year.isdigit():
                    print("Invalid year.")
                    continue
                db.yearly_report(user_id, int(year))
            else:
                print("Invalid report type.")
        elif choice == '5':
            category = input("Category: ")
            limit = input("Monthly Limit: ")
            if not is_positive_number(limit):
                print("Enter a valid positive number.")
                continue
            db.set_budget(user_id, category, float(limit))
        elif choice == '6':
            db.backup()
            print("Backup complete.")
        elif choice == '7':
            db.restore()
            print("Restore complete.")
        elif choice == '8':
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

if __name__ == '__main__':
    main()
