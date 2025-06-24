"""
utils.py
--------
Utility functions for input validation and formatting.
"""

def is_positive_number(value):
    """
    Check if the value is a positive number.
    Returns True if positive float, else False.
    """
    try:
        return float(value) > 0
    except ValueError:
        return False

def format_currency(amount):
    """
    Format a number as currency (Indian Rupees).
    """
    return f"₹{amount:,.2f}"
