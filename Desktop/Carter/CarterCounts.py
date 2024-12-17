import streamlit as st
import pandas as pd
import os
import json
import xlsxwriter


# File where biweekly data will be saved
CSV_FILE = 'biweekly_data.csv'
import os
import pandas as pd
import streamlit as st

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
st.title("🧮Carter Counts!")

# Export/Import Section
st.subheader("📤 Export/📥 Import Data")

# Export buttons
col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="Export as CSV🗂️",
        data=pd.DataFrame(st.session_state.biweekly_data).to_csv(index=False).encode('utf-8'),
        file_name="biweekly_data.csv",
        mime="text/csv"
    )
with col2:
    # Create an Excel file in memory for download
    if st.session_state.biweekly_data:
        df = pd.DataFrame(st.session_state.biweekly_data)
        excel_buffer = pd.ExcelWriter("biweekly_data.xlsx", engine='xlsxwriter')
        df.to_excel(excel_buffer, index=False, sheet_name='Data')
        excel_buffer.close()
        st.download_button(
            label="Export as Excel🗂️",
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
            st.error("Unsupported file format. Please upload a CSV or Excel file.", icon="🚨")

        if imported_data:
            st.session_state.biweekly_data.extend(imported_data)
            pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
            st.success("Data imported successfully!", icon="✅")
    except Exception as e:
        st.error(f"Error importing data: {e}", icon="🚨")

# Section: Income Input
st.header("💰 Income Details")
col1, col2 = st.columns(2)
with col1:
    biweekly_net = st.number_input("Biweekly Net Revenue ($)", min_value=0.0, step=0.01, format="%.2f")
    biweekly_deductions = st.number_input("Biweekly Deductions ($)", min_value=0.0, step=0.01, format="%.2f")
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
fixed_expenses = {
    'Rent': st.number_input("Rent ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Car Payment': st.number_input("Car Payment ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Car Insurance': st.number_input("Car Insurance ($)", min_value=0.0, step=0.01),
    'Utilities': st.number_input("Utilities ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Subscriptions': st.number_input("Subscriptions ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Gym': st.number_input("Gym ($)", min_value=0.0, step=0.01),
    'Groceries': st.number_input("Groceries ($)", min_value=0.0, step=0.01),
    'Renters Insurance': st.number_input("Renters Insurance ($)", min_value=0.0, step=0.01),
    'Internet': st.number_input("Internet ($)", min_value=0.0, step=0.01),
    'Electricity': st.number_input("Electricity ($)", min_value=0.0, step=0.01),
}
total_fixed_expenses = sum(fixed_expenses.values())
st.write(f"**Total Fixed Expenses**: ${total_fixed_expenses:.2f}")

if total_fixed_expenses > 0:
    st.session_state.current_period['expenses'] = fixed_expenses
else:
    st.warning("⚠️ Please enter at least one fixed expense.",icon="⚠️")

# Section: Extras Expenses
st.header("🛒 Daily Expenses")
with st.form("Add Expense"):
    date = st.date_input("Date")
    category = st.text_input("Category")
    description = st.text_input("Description")
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01, format="%.2f")
    add_expense = st.form_submit_button("Add Expense")

    if add_expense:
        if not category or not description or amount <= 0:
            st.error("⚠️ Please fill in all fields for Daily Expenses (Date, Category, Description, and Amount).", icon="🚨")
        else:
            new_row = {'Date': date, 'Category': category, 'Description': description, 'Amount': amount}
            st.session_state.current_period['extras'] = pd.concat(
                [st.session_state.current_period['extras'], pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("Expense added successfully!", icon="✅")

st.subheader("Daily Expenses This Period")
st.dataframe(st.session_state.current_period['extras'])

# Save Period with Validation
if st.button("Save Period"):
    income = st.session_state.current_period['income']
    expenses = st.session_state.current_period['expenses']
    extras = st.session_state.current_period['extras']

    if not income or not expenses or extras.empty:
        st.error("⚠️ Please ensure Income, Expenses, and at least one Daily expense are filled before saving.", icon="🚨")
    else:
        # Ensure all columns in 'extras' are serializable
        # Convert the 'Date' column to string (ISO format)
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
            st.success("Period updated successfully!", icon="✅")
        else:  # Adding new period
            st.session_state.biweekly_data.append(current_period)
            st.success("New period saved!", icon="✅")

        # Save to CSV
        try:
            pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
        except Exception as e:
            st.error(f"Error saving data: {e}", icon="🚨")

        # Reset current period
        st.session_state.current_period = {
            'income': {}, 
            'expenses': {}, 
            'extras': pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])
        }

# Show All Saved Periods
st.header("📆 All Biweekly Periods")
if st.session_state.biweekly_data:
    for i, period in enumerate(st.session_state.biweekly_data):
        st.subheader(f"Biweekly Period {i + 1}")
        try:
            income = json.loads(period['income'])
            expenses = json.loads(period['expenses'])
            extras_df = pd.DataFrame(json.loads(period['extras']))
        except (json.JSONDecodeError, TypeError, ValueError):
            st.error(f"Error loading data for Period {i + 1}. Skipping this period.", icon="🚨")
            continue

        st.write("**Income**", income)
        st.write("**Expenses**", expenses)
        st.write("**Daily Expenses**")
        st.dataframe(extras_df)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Edit Period {i + 1}", key=f"edit_{i}"):
                st.session_state.current_period = {
                    'income': income,
                    'expenses': expenses,
                    'extras': extras_df
                }
                st.session_state.edit_index = i

        with col2:
            if st.button(f"Delete Period {i + 1}", key=f"delete_{i}"):
                st.session_state.delete_confirm = i

# Confirmation Dialog for Deletion
if st.session_state.delete_confirm is not None:
    st.warning(f"Are you sure you want to delete Biweekly Period {st.session_state.delete_confirm + 1}?",icon="⚠️")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete"):
            st.session_state.biweekly_data.pop(st.session_state.delete_confirm)
            try:
                pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
                st.success("Period deleted successfully!", icon="✅")
            except Exception as e:
                st.error(f"Error saving data: {e}", icon="🚨")
            st.session_state.delete_confirm = None

    with col2:
        if st.button("Cancel"):
            st.session_state.delete_confirm = None
# Clear All Data Section
if st.button("Clear All Data"):
    st.session_state.biweekly_data = []
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    st.success("All data cleared successfully!", icon="✅")
