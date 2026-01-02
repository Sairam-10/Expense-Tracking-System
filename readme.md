# Expense Tracking System
A full-stack web application designed to track, manage, and visualize daily expenses. This system allows users to fetch data for specific dates, perform bulk updates via an interactive table, and view financial insights through dynamic charts.

## 🚀 Features
Daily Expense Tracking: Fetch and view expenses for any specific date.

Inline Editing: Update expense details directly within a st.data_editor table.

Persistence: Data is stored securely in a MySQL database.

Visual Analytics:

Donut Chart: Visualize budget share by category using Plotly.

Bar Chart: Compare category spending amounts side-by-side.

Error Handling: Robust checks for server connectivity and missing data (404 handling).

## 🛠️ Tech Stack
Frontend: Streamlit

Backend: FastAPI (Python)

Database: MySQL

Visualization: Plotly Express, Pandas

HTTP Client: Requests

## 📋 Requirements
streamlit==1.52.2                                         
pandas==2.2.3                
plotly==6.5.0      
requests==2.32.3    
datetime   
pydantic==2.12.5        
logging  
fastapi==0.127.0  
mysql-connector-python==9.5.0      
contextmanager   
pytest==9.0.2

## Database Setup
Create a database named expense_manager and a table named expenses:
SQL
CREATE DATABASE expense_manager;

USE expense_manager;

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    notes TEXT
);

## Run the Backend (FastAPI)
Navigate to your server directory and start the Uvicorn server:  
uvicorn server:app --reload

## Run the Frontend (Streamlit)
In a new terminal tab, launch the Streamlit app:  
streamlit run app.py

##  Usage  
Add/Update Tab: Select a date and click "Fetch Expenses." If data exists, you can edit the cells directly in the table. Click Save All Changes to sync with the database.

Analytics Tab: Select a start and end date. Click Generate Analytics Report to see your spending distribution in a Donut and Bar chart.

## 📁 Project Structure
├── app.py              # Streamlit frontend code
├── server.py           # FastAPI backend routes
├── db_helper.py        # MySQL database connection and queries
