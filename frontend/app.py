import streamlit as st
from datetime import datetime
import requests
import plotly.express as px
import pandas as pd

API_URL = "http://localhost:8000"
db_name = 'expense_manager'

st.title("Expense Management")
tab1, tab2 = st.tabs(["Add/Update", "Analytics"])

# --- SESSION STATE INITIALIZATION ---
# This keeps your data alive when you click "Save"
if "expenses_list" not in st.session_state:
    st.session_state.expenses_list = None

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_date = st.date_input("Select Date", datetime(2024, 8, 1))
    with col2:
        fetch_button = st.button("Fetch Expenses")

    # --- 1. FETCH LOGIC ---
    if fetch_button:
        try:
            url = f"{API_URL}/get_expenses/{db_name}/{selected_date.strftime('%Y-%m-%d')}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data:
                    st.session_state.expenses_list = data
                else:
                    # Clear the list if no data found for the new date
                    st.session_state.expenses_list = None
                    st.info("No expenses found for this date.")
            else:
                # IMPORTANT: Clear the old data if there is a server error (like 404)
                st.session_state.expenses_list = None
                st.error(f"Error: {response.status_code}, No data exists for {selected_date}")

        except requests.exceptions.ConnectionError:
            st.session_state.expenses_list = None  # Clear on connection error too
            st.error("FastAPI server is not running!")

    # --- 2. DISPLAY & UPDATE LOGIC ---
    # This is OUTSIDE the fetch_button block so it stays visible
    if st.session_state.expenses_list:
        st.subheader(f"Expenses for {selected_date}")

        # We edit the data stored in session_state
        edited_expenses = st.data_editor(
            st.session_state.expenses_list,
            use_container_width=True,
            num_rows="dynamic",
            column_config={"id": st.column_config.NumberColumn("ID", disabled=True)},
            key="editor"
        )

        if st.button("Save All Changes", type="primary"):
            try:
                update_res = requests.post(
                    f"{API_URL}/update_expenses/{db_name}",
                    json=edited_expenses
                )
                if update_res.status_code == 200:
                    st.success("Successfully updated!")
                    # Update state and refresh
                    st.session_state.expenses_list = edited_expenses
                    st.rerun()
                else:
                    st.error(f"Update failed: {update_res.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    st.divider()  # Adds a nice visual line between the search and the add form
    st.subheader("Add a New Expense")

    # Create the form
    with st.form("add_expense_form", clear_on_submit=True):
        # Create inputs side-by-side using columns
        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            new_date = st.date_input("Date", datetime.now())
        with f_col2:
            new_category = st.selectbox("Category", ["Food", "Entertainment", "Shopping", "Rent", "Other"])
        with f_col3:
            new_amount = st.number_input("Amount", min_value=0.0, step=1.0)

        new_notes = st.text_input("Notes (Optional)")

        # The submit button
        submit_button = st.form_submit_button("Save to Database")

        if submit_button:
            # 1. Validation: Make sure the amount is not zero
            if new_amount <= 0:
                st.error("Please enter an amount greater than 0.")
            else:
                # 2. Package the data into a dictionary (JSON)
                payload = {
                    "expense_date": new_date.strftime("%Y-%m-%d"),
                    "category": new_category,
                    "amount": new_amount,
                    "notes": new_notes
                }

                # 3. Send the data to FastAPI
                try:
                    response = requests.post(f"{API_URL}/add_expense/{db_name}", json=payload)

                    if response.status_code == 200:
                        st.toast("Expense added successfully!", icon="✅")
                        # Refresh the page so the table above updates
                        st.rerun()
                    else:
                        st.error(f"Failed to add expense: {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the server. Is FastAPI running?")

    st.divider()
    st.subheader("Delete Records")

    # We create a column layout to put the button next to a warning
    warn_col, btn_col = st.columns([3, 1])

    with warn_col:
        st.warning(f"Careful: This will delete ALL expenses for {selected_date}")

    with btn_col:
        if st.button("Delete All for Date", type="primary"):  # type="primary" makes the button red
            try:
                response = requests.delete(f"{API_URL}/delete_expenses/{db_name}/{selected_date}")
                if response.status_code == 200:
                    st.success("Deleted!")
                    st.rerun()  # Refresh to show the empty table
                else:
                    st.error("Delete failed.")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.header("Analytics & Insights")

    col1, col2 = st.columns(2)
    with col1:
        start_dt = st.date_input("Start Date", datetime(2024, 8, 1))
    with col2:
        end_dt = st.date_input("End Date", datetime(2024, 8, 31))

    if st.button("Generate Analytics Report"):
        query_params = {
            "start_date": start_dt.strftime('%Y-%m-%d'),
            "end_date": end_dt.strftime('%Y-%m-%d')
        }

        try:
            response = requests.get(f"{API_URL}/expense_summary/{db_name}", params=query_params)

            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)

                    # --- TOTAL METRIC ---
                    total_spent = df['total'].sum()
                    st.metric("Total Spending", f"{total_spent:,.2f}")
                    st.divider()

                    # --- CHART 1: PIE CHART (UP) ---
                    st.subheader("Budget Distribution")
                    fig_pie = px.pie(
                        df, values='total', names='category',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)

                    st.divider()  # Adds a line between the two charts

                    # --- CHART 2: BAR CHART (DOWN) ---
                    st.subheader("Category Comparison")
                    df_sorted = df.sort_values(by="total", ascending=False)
                    fig_bar = px.bar(
                        df_sorted, x='category', y='total',
                        text='total', color='category',
                        labels={'total': 'Amount', 'category': 'Category'}
                    )
                    fig_bar.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                    st.plotly_chart(fig_bar, use_container_width=True)

                    # --- RAW DATA ---
                    with st.expander("Show detailed data table"):
                        # Ensure it's a number
                        df_sorted['total'] = pd.to_numeric(df_sorted['total'])

                        st.dataframe(
                            df_sorted,
                            use_container_width=True,
                            column_config={
                                "total": st.column_config.NumberColumn(
                                    "Total Amount",
                                    format="%.2f"  # This strictly limits the display to 2 decimals
                                )
                            },
                            hide_index=True
                        )
                else:
                    st.info(f"No records found between {start_dt} and {end_dt}.")
            else:
                st.error(f"Server Error {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to FastAPI.")