from typing import List, Optional
from fastapi import FastAPI, HTTPException
from datetime import date
from pydantic import BaseModel
import logging

logging.basicConfig(
    level=logging.DEBUG,
    force=True,
    format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r"C:\code\python-practice\project_expense_tracking\backend\expense_activity.log"),  # Saves to a file
        logging.StreamHandler()  # Also prints to your screen
    ]
)

from . import db_helper

app = FastAPI()

logger = logging.getLogger(__name__)
logger.info("SERVER STARTED")

# Use this for GET requests (fetching from DB)
class Expense(BaseModel):
    id: int
    expense_date: date
    category: str
    amount: float
    notes: Optional[str] = None

@app.get("/get_expenses/{db_name}/{expense_date}", response_model = List[Expense])
def get_expenses(db_name: str, expense_date: date):
    expenses = db_helper.fetch_expenses_for_date(db_name, expense_date)

    # 3. Handle the 'No Data' case for the user
    if not expenses:
        # This sends a proper 404 error back to the browser
        raise HTTPException(
            status_code=404,
            detail=f"Expenses for {expense_date} are not available in database {db_name}"
        )

    return expenses

# Use this for POST requests (adding to DB)
class ExpenseCreate(BaseModel):
    expense_date: date
    category: str
    amount: float
    notes: Optional[str] = None

@app.post("/add_expense/{db_name}")
def add_expense(db_name: str, expense: ExpenseCreate): # Using the version without ID
    db_helper.insert_expenses(
        db_name=db_name,
        expense_date=expense.expense_date,
        amount=expense.amount,
        category=expense.category,
        notes=expense.notes
    )
    return {"message": "Success"}

# DELETE Route
@app.delete("/delete_expenses/{db_name}/{expense_date}")
def delete_expenses(db_name: str, expense_date: date):
    try:
        db_helper.delete_expenses_for_date(db_name, expense_date)
        return {"message": f"All expenses for {expense_date} deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#update
@app.post("/update_expenses/{db_name}")
def update_expenses_endpoint(db_name: str, expenses: list[Expense]):
    try:
        # Loop through each expense sent from the Streamlit editor
        for exp in expenses:
            db_helper.update_expenses(
                db_name=db_name,
                expense_id=exp.id, # Using the id to target the specific row
                expense_date=exp.expense_date,
                amount=exp.amount,
                category=exp.category,
                notes=exp.notes
            )
        return {"status": "success", "message": f"Updated {len(expenses)} records"}
    except Exception as e:
        logger.error(f"Error updating records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


#Analytics
@app.get("/expense_summary/{db_name}")
def get_expense_summary_route(db_name: str, start_date: str, end_date: str):
    try:
        # We pass the dates directly to your existing helper function
        summary = db_helper.fetch_expense_summary(db_name, start_date, end_date)
        return summary
    except Exception as e:
        logger.error(f"Error fetching summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

