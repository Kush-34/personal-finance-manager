"""
database.py
-----------
Handles all database operations using SQLite3.
Includes user, transaction, and budget management, as well as backup and restore.
"""

import sqlite3
import shutil
import os
from utils import format_currency

class Database:
    def __init__(self, db_name):
        """
        Initialize the database connection and create tables.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """
        Create tables for users, transactions, and budgets if they don't exist.
        Note: 'budget_limit' is used instead of 'limit' to avoid SQL reserved word conflicts.
        """
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount REAL,
                        category TEXT,
                        type TEXT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        category TEXT,
                        budget_limit REAL,
                        UNIQUE(user_id, category))''')
        self.conn.commit()

    def register_user(self, username, password):
        """
        Register a new user. Returns True if successful, False if username exists.
        """
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        """
        Authenticate user and return user_id if credentials are correct.
        """
        c = self.conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
        return result[0] if result else None

    def add_transaction(self, user_id, amount, category, type_):
        """
        Add a new income or expense transaction.
        If expense, checks against budget and warns if exceeded.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO transactions (user_id, amount, category, type) VALUES (?, ?, ?, ?)", (user_id, amount, category, type_))
        self.conn.commit()
        if type_ == 'expense':
            # Check if budget is set and warn if exceeded
            c.execute("SELECT budget_limit FROM budgets WHERE user_id=? AND category=?", (user_id, category))
            row = c.fetchone()
            if row:
                budget_limit = row[0]
                c.execute("""
                    SELECT SUM(amount) FROM transactions
                    WHERE user_id=? AND category=? AND type='expense'
                    AND strftime('%m', date)=strftime('%m', 'now')
                    AND strftime('%Y', date)=strftime('%Y', 'now')
                """, (user_id, category))
                total = c.fetchone()[0] or 0
                if total > budget_limit:
                    print(f"Warning: You have exceeded your budget limit for {category} ({format_currency(total)} > {format_currency(budget_limit)})!")

    def update_transaction(self, entry_id, amount, category, type_):
        """
        Update an existing transaction by ID.
        """
        c = self.conn.cursor()
        c.execute("UPDATE transactions SET amount=?, category=?, type=? WHERE id=?", (amount, category, type_, entry_id))
        self.conn.commit()

    def delete_transaction(self, entry_id):
        """
        Delete a transaction by its ID.
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM transactions WHERE id=?", (entry_id,))
        self.conn.commit()

    def monthly_report(self, user_id, month, year):
        """
        Display all transactions for a given month/year and show totals.
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT id, date, category, type, amount FROM transactions
            WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
            ORDER BY date
        """, (user_id, f"{month:02d}", str(year)))
        rows = c.fetchall()
        print("\n--- Monthly Report ---")
        print("ID | Date                | Category | Type    | Amount")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]:<3}| {row[1]:<19}| {row[2]:<9}| {row[3]:<7}| {format_currency(row[4])}")
        c.execute("""
            SELECT type, SUM(amount) FROM transactions
            WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
            GROUP BY type
        """, (user_id, f"{month:02d}", str(year)))
        summary = dict(c.fetchall())
        income = summary.get('income', 0)
        expense = summary.get('expense', 0)
        print(f"\nTotal Income: {format_currency(income)}")
        print(f"Total Expense: {format_currency(expense)}")
        print(f"Savings: {format_currency(income - expense)}")

    def yearly_report(self, user_id, year):
        """
        Display total income, expenses, and savings for a given year.
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT type, SUM(amount) FROM transactions
            WHERE user_id=? AND strftime('%Y', date)=?
            GROUP BY type
        """, (user_id, str(year)))
        summary = dict(c.fetchall())
        income = summary.get('income', 0)
        expense = summary.get('expense', 0)
        print("\n--- Yearly Report ---")
        print(f"Total Income: {format_currency(income)}")
        print(f"Total Expense: {format_currency(expense)}")
        print(f"Savings: {format_currency(income - expense)}")

    def set_budget(self, user_id, category, limit):
        """
        Set or update a monthly budget limit for a category.
        """
        c = self.conn.cursor()
        c.execute("""
            INSERT INTO budgets (user_id, category, budget_limit)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, category) DO UPDATE SET budget_limit=excluded.budget_limit
        """, (user_id, category, limit))
        self.conn.commit()
        print(f"Budget set for {category}: {format_currency(limit)}")

    def backup(self):
        """
        Create a backup of the database file.
        """
        self.conn.commit()
        shutil.copyfile(self.db_name, self.db_name + ".bak")

    def restore(self):
        """
        Restore the database from the backup file.
        """
        if os.path.exists(self.db_name + ".bak"):
            self.conn.close()
            shutil.copyfile(self.db_name + ".bak", self.db_name)
            self.conn = sqlite3.connect(self.db_name)
            print("Database restored from backup.")
        else:
            print("No backup found.")
