import pytest
# Use this if running from within the same folder
from . import db_helper

def test_fetch_expenses_for_date_valid_date():
    # 1. Call the function and store the returned list
    expenses = db_helper.fetch_expenses_for_date('expense_manager', '2024-08-15')

    # 2. Perform assertions
    assert len(expenses) == 1
    assert expenses[0]['amount'] == 10
    assert expenses[0]['category'] == 'Shopping'
    assert expenses[0]['notes'] == 'Bought potatoes'


def test_fetch_expenses_for_date_invalid_date():
    # 1. Call the function and store the returned list
    expenses = db_helper.fetch_expenses_for_date('expense_manager', '9999-08-15')

    # 2. Perform assertions
    assert len(expenses) == 0

def test_fetch_expense_summary():
    # 1. Call the function and store the returned list
    expense_summary = db_helper.fetch_expense_summary('expense_manager', '2024-08-01','2024-08-05')

    # 2. Perform assertions
    assert len(expense_summary) == 5
    assert expense_summary[0]['category'] == 'Entertainment'
    assert expense_summary[0]['total'] == 225

