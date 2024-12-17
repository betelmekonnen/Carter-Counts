import streamlit as st
import pandas as pd
import os
import json
import xlsxwriter

# File where biweekly data will be saved
CSV_FILE = 'biweekly_data.csv'

# Initialize session state
if 'biweekly_data' not in st.session_state:
    if os.path.exists(CSV_FILE):
        data = pd.read_csv(CSV_FILE)
        st.session_state.biweekly_data = data.to_dict(orient='records')
    else:
        st.session_state.biweekly_data = []

if 'current_period' not in st.session_state:
    st.session_state.current_period = {
        'income': {},
        'expenses': {},
        'extras': pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])
    }

if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Title
st.title("Carter Counts!")

# Export/Import Section
st.header("📤 Export/📥 Import Data")

# Export buttons
col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="Export as CSV",
        data=pd.DataFrame(st.session_state.biweekly_data).to_csv(index=False).encode('utf-8'),
        file_name="biweekly_data.csv",
        mime="text/csv"
    )
with col2:
    if st.session_state.biweekly_data:
        df = pd.DataFrame(st.session_state.biweekly_data)
        excel_buffer = pd.ExcelWriter("biweekly_data.xlsx", engine='xlsxwriter')
        df.to_excel(excel_buffer, index=False, sheet_name='Data')
        excel_buffer.close()
        st.download_button(
            label="Export as Excel",
            data=open("biweekly_data.xlsx", "rb"),
            file_name="biweekly_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Import file
st.subheader("Import Data")
uploaded_file = st.file_uploader("Upload a CSV or Excel file to import data", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            imported_data = pd.read_csv(uploaded_file).to_dict(orient='records')
        elif uploaded_file.name.endswith('.xlsx'):
            imported_data = pd.read_excel(uploaded_file).to_dict(orient='records')
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")

        if imported_data:
            st.session_state.biweekly_data.extend(imported_data)
            pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
            st.success("Data imported successfully!")
    except Exception as e:
        st.error(f"Error importing data: {e}")

# Section: Income Input
st.header("💰 Income Details")
col1, col2 = st.columns(2)

# Prepopulate income fields if data exists from a prior session
income_data = st.session_state.current_period.get('income', {})
biweekly_net = st.number_input("Biweekly Net Revenue ($)", min_value=0.0, step=0.01, format="%.2f", value=income_data.get('biweekly_net', 0.0))
biweekly_deductions = st.number_input("Biweekly Deductions ($)", min_value=0.0, step=0.01, format="%.2f", value=income_data.get('biweekly_deductions', 0.0))

with col2:
    savings_percent = st.slider("Savings (%)", 0, 100, 10)

# Calculate totals
biweekly_total = biweekly_net - biweekly_deductions
monthly_total = biweekly_total * 2

# Correct calculation: directly calculate savings from net income
savings_amount = biweekly_total * (savings_percent / 100)
post_savings_funds = biweekly_total - savings_amount

# Display totals
st.write(f"**Biweekly Total**: ${biweekly_total:.2f}")
st.write(f"**Monthly Total**: ${monthly_total:.2f}")
st.write(f"**Savings at {savings_percent}%**: ${savings_amount:.2f}")
st.write(f"**Remaining Funds after Savings**: ${post_savings_funds:.2f}")

# Save updated values to session state
st.session_state.current_period['income'] = {
    'biweekly_net': biweekly_net,
    'biweekly_deductions': biweekly_deductions,
    'savings_percent': savings_percent,
    'post_savings_funds': post_savings_funds
}

# Section: Fixed Expenses
st.header("📑 Fixed Monthly Expenses")

# Prepopulate expense fields if data exists from a prior session
expenses_data = st.session_state.current_period.get('expenses', {})
fixed_expenses = {
    'Rent': st.number_input("Rent ($)", min_value=0.0, step=0.01, format="%.2f", value=expenses_data.get('Rent', 0.0)),
    'Car Payment': st.number_input("Car Payment ($)", min_value=0.0, step=0.01, format="%.2f", value=expenses_data.get('Car Payment', 0.0)),
    'Car Insurance': st.number_input("Car Insurance ($)", min_value=0.0, step=0.01, value=expenses_data.get('Car Insurance', 0.0)),
    'Utilities': st.number_input("Utilities ($)", min_value=0.0, step=0.01, format="%.2f", value=expenses_data.get('Utilities', 0.0)),
    'Subscriptions': st.number_input("Subscriptions ($)", min_value=0.0, step=0.01, format="%.2f", value=expenses_data.get('Subscriptions', 0.0)),
    'Gym': st.number_input("Gym ($)", min_value=0.0, step=0.01, value=expenses_data.get('Gym', 0.0)),
    'Groceries': st.number_input("Groceries ($)", min_value=0.0, step=0.01, value=expenses_data.get('Groceries', 0.0)),
    'Renters Insurance': st.number_input("Renters Insurance ($)", min_value=0.0, step=0.01, value=expenses_data.get('Renters Insurance', 0.0)),
    'Internet': st.number_input("Internet ($)", min_value=0.0, step=0.01, value=expenses_data.get('Internet', 0.0)),
    'Electricity': st.number_input("Electricity ($)", min_value=0.0, step=0.01, value=expenses_data.get('Electricity', 0.0)),
}
total_fixed_expenses = sum(fixed_expenses.values())
st.write(f"**Total Fixed Expenses**: ${total_fixed_expenses:.2f}")

if total_fixed_expenses > 0:
    st.session_state.current_period['expenses'] = fixed_expenses
else:
    st.warning("⚠️ Please enter at least one fixed expense.")

# Section: Extras
# This section will work as before, with the option to add new extra expenses.

# Save and Edit Data

# Save and load data as before, ensure data is updated with each edit
if st.button("Save Period"):
    income = st.session_state.current_period['income']
    expenses = st.session_state.current_period['expenses']
    extras = st.session_state.current_period['extras']

    if not income or not expenses or extras.empty:
        st.error("⚠️ Please ensure Income, Expenses, and at least one Extra expense are filled before saving.")
    else:
        # Ensure all columns in 'extras' are serializable
        extras_serializable = extras.copy()
        extras_serializable['Date'] = extras_serializable['Date'].apply(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else str(x))

        current_period = {
            'income': json.dumps(income),
            'expenses': json.dumps(expenses),
            'extras': json.dumps(extras_serializable.to_dict(orient='records'))  # Convert DataFrame to list of dictionaries
        }

        if st.session_state.edit_index is not None:  # Editing existing period
            st.session_state.biweekly_data[st.session_state.edit_index] = current_period
            st.session_state.edit_index = None
            st.success("Period updated successfully!")
        else:  # Adding new period
            st.session_state.biweekly_data.append(current_period)
            st.success("New period saved!")

        # Save to CSV
        try:
            pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
        except Exception as e:
            st.error(f"Error saving data: {e}")

        # Reset current period
        st.session_state.current_period = {
            'income': {}, 
            'expenses': {}, 
            'extras': pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])
        }
