import mysql.connector
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db_cursor(database, commit = False):
    connection = None
    cursor = None
    try:
        logger.info(f'Attempting to create a connection with database: {database}')
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Pappu@1995',
            database=database
        )

        if connection.is_connected():
            logger.info("Connection Successful")
            cursor = connection.cursor(dictionary=True)
            yield cursor

            if commit:
                connection.commit()
                logging.info("Changes committed.")

    except mysql.connector.Error as err:
        # This will now catch the "Wrong Database Name" error and log it
        logger.error(f"Error: {err}")
        raise  # Re-raises the error so the function caller knows it failed

    finally:
        # Check if cursor was ever created before closing
        if cursor:
            cursor.close()

        # Check if connection was ever created before closing
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed.")

def fetch_all_records(db_name):
    with get_db_cursor(db_name, commit = False) as cursor:
        logger.info(f'Fetching all records in the database: {db_name}')
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)
        return expenses


def fetch_expenses_for_date(db_name, expense_date):
    with get_db_cursor(db_name, commit=False) as cursor:
        logger.info(f'Fetching all expenses in the database {db_name} for {expense_date}')
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)
        return expenses

def insert_expenses(db_name, expense_date, amount, category, notes):
    with get_db_cursor(db_name, commit=True) as cursor:
        logger.info(f'Inserting expense data into the database {db_name} with expense_date {expense_date}')
        query = "INSERT INTO expenses(expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (expense_date, amount, category, notes))

def delete_expenses_for_date(db_name, expense_date):
    with get_db_cursor(db_name, commit = True) as cursor:
        logger.info(f'Deleting expense data in the database {db_name} for the expense_date {expense_date}')
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))

def update_expenses(db_name, expense_id, expense_date, amount, category, notes):
    query = """
        UPDATE expenses 
        SET expense_date = %s, amount = %s, category = %s, notes = %s 
        WHERE id = %s
    """
    # Using your existing get_db_cursor with commit=True
    with get_db_cursor(db_name, commit=True) as cursor:
        logger.info(f"Updating expense ID {expense_id} in {db_name}")
        cursor.execute(query, (expense_date, amount, category, notes, expense_id))

def fetch_expense_summary(db_name, start_date, end_date):
    with get_db_cursor(db_name, commit=False) as cursor:
        logger.info(f'Fetching expense summary from the database {db_name} between the expense_dates {start_date} and {end_date}')
        cursor.execute('''SELECT category, sum(amount) as total
                       FROM expenses
                       WHERE expense_date BETWEEN %s AND %s
                       GROUP BY category;''', (start_date, end_date))
        expense_summary = cursor.fetchall()
        for expense in expense_summary:
            print(expense)
        return expense_summary

# --- Execution ---
# fetch_all_records('expense_manager')
# fetch_expenses_for_date('expense_manager', '2024-08-02')
# insert_expenses("expense_manager",   "2024-09-20", 300, "Food", "Panipuri")
# fetch_expenses_for_date('expense_manager', '2024-09-20')
# delete_expenses_for_date('expense_manager', '2024-09-20')
# fetch_expense_summary('expense_manager', '2024-08-01','2024-08-05')
