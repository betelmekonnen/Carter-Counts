import streamlit as st
import pandas as pd
import os
import json

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
    'Groceries': st.number_input("Groceries ($)", min_value=0.0, step=0.01),  # Added Groceries
    'Renters Insurance': st.number_input("Renters Insurance ($)", min_value=0.0, step=0.01),  # Added Renters Insurance
    'Internet': st.number_input("Internet ($)", min_value=0.0, step=0.01),
    'Electricity': st.number_input("Electricity ($)", min_value=0.0, step=0.01),  # Added Electricity
}
total_fixed_expenses = sum(fixed_expenses.values())
st.write(f"**Total Fixed Expenses**: ${total_fixed_expenses:.2f}")

# Save to session state if total > 0
if total_fixed_expenses > 0:
    st.session_state.current_period['expenses'] = fixed_expenses
else:
    st.warning("⚠️ Please enter at least one fixed expense.")

# Section: Extras
st.header("🛒 Weekly Extras")
with st.form("Add Expense"):
    date = st.date_input("Date")
    category = st.text_input("Category")
    description = st.text_input("Description")
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01, format="%.2f")
    add_expense = st.form_submit_button("Add Expense")

    if add_expense:
        if not category or not description or amount <= 0:
            st.error("⚠️ Please fill in all fields for Extras (Date, Category, Description, and Amount).")
        else:
            new_row = {'Date': date, 'Category': category, 'Description': description, 'Amount': amount}
            st.session_state.current_period['extras'] = pd.concat(
                [st.session_state.current_period['extras'], pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("Expense added successfully!")

st.subheader("Extras This Period")
st.dataframe(st.session_state.current_period['extras'])

# Save Period
if st.button("Save Period"):
    income = st.session_state.current_period['income']
    expenses = st.session_state.current_period['expenses']
    extras = st.session_state.current_period['extras']

    if not income or not expenses or extras.empty:
        st.error("⚠️ Please ensure Income, Expenses, and at least one Extra expense are filled before saving.")
    else:
        current_period = {
            'income': json.dumps(income),
            'expenses': json.dumps(expenses),
            'extras': json.dumps(extras.to_dict(orient='records'))
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
        
# Show All Saved Periods
st.header("📆 All Biweekly Periods")

if st.session_state.biweekly_data:
    for i, period in enumerate(st.session_state.biweekly_data):
        # Validate the data before processing
        if not period or not isinstance(period, dict):
            st.error(f"Biweekly Period {i + 1} contains invalid data. Skipping this period.")
            continue
        
        st.subheader(f"Biweekly Period {i + 1}")
        
        # Safe loading of JSON fields with validation
        try:
            income = json.loads(period['income']) if period['income'] and isinstance(period['income'], str) else {}
            expenses = json.loads(period['expenses']) if period['expenses'] and isinstance(period['expenses'], str) else {}
            extras_df = pd.DataFrame(json.loads(period['extras'])) if period['extras'] and isinstance(period['extras'], str) else pd.DataFrame()
        except (json.JSONDecodeError, TypeError, ValueError):
            st.error(f"Error loading data for Period {i + 1}. Skipping this period.")
            continue

        # Display loaded data
        st.write("**Income**", income)
        st.write("**Expenses**", expenses)
        st.write("**Extras**")
        st.dataframe(extras_df)

        # Edit and Delete Buttons
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
    st.warning(f"Are you sure you want to delete Biweekly Period {st.session_state.delete_confirm + 1}?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete"):
            # Safely delete the period
            st.session_state.biweekly_data.pop(st.session_state.delete_confirm)
            
            # Save updated data
            try:
                pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
                st.success("Period deleted successfully!")
            except Exception as e:
                st.error(f"Error saving data: {e}")
            
            # Reset confirmation state
            st.session_state.delete_confirm = None

    with col2:
        if st.button("Cancel"):
            st.session_state.delete_confirm = None

# # Show All Saved Periods
# st.header("📆 All Biweekly Periods")

# if st.session_state.biweekly_data:
#     for i, period in enumerate(st.session_state.biweekly_data):
#         st.subheader(f"Biweekly Period {i + 1}")
        
#         # Safe loading of JSON fields with validation
#         try:
#             income = json.loads(period['income']) if isinstance(period['income'], str) else {}
#             expenses = json.loads(period['expenses']) if isinstance(period['expenses'], str) else {}
#             extras_df = pd.DataFrame(json.loads(period['extras'])) if isinstance(period['extras'], str) else pd.DataFrame()
#         except (json.JSONDecodeError, TypeError):
#             st.error(f"Error loading data for Period {i + 1}. Skipping this period.")
#             continue

#         # Display loaded data
#         st.write("**Income**", income)
#         st.write("**Expenses**", expenses)
#         st.write("**Extras**")
#         st.dataframe(extras_df)

#         # Edit and Delete Buttons
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button(f"Edit Period {i + 1}", key=f"edit_{i}"):
#                 st.session_state.current_period = {
#                     'income': income,
#                     'expenses': expenses,
#                     'extras': extras_df
#                 }
#                 st.session_state.edit_index = i
#                 # No rerun needed here, Streamlit will update UI naturally

#         with col2:
#             if st.button(f"Delete Period {i + 1}", key=f"delete_{i}"):
#                 st.session_state.delete_confirm = i
#                 # No rerun here; let the confirmation section handle it

# # Confirmation Dialog for Deletion
# if st.session_state.delete_confirm is not None:
#     st.warning(f"Are you sure you want to delete Biweekly Period {st.session_state.delete_confirm + 1}?")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Yes, Delete"):
#             # Delete the selected period
#             st.session_state.biweekly_data.pop(st.session_state.delete_confirm)
#             # Save updated data
#             try:
#                 pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
#                 st.success("Period deleted successfully!")
#             except Exception as e:
#                 st.error(f"Error saving data: {e}")
#             # Reset delete confirmation
#             st.session_state.delete_confirm = None
#             # No rerun needed, Streamlit refreshes automatically

#     with col2:
#         if st.button("Cancel"):
#             # Reset delete confirmation
#             st.session_state.delete_confirm = None


# # Confirmation Dialog for Deletion
# if st.session_state.delete_confirm is not None:
#     st.warning("Are you sure you want to delete this period?")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Yes, Delete"):
#             # Delete the selected period
#             st.session_state.biweekly_data.pop(st.session_state.delete_confirm)
            
#             # Update CSV file
#             try:
#                 pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
#                 st.success("Period deleted successfully!")
#             except Exception as e:
#                 st.error(f"Error saving data: {e}")

#             # Reset delete_confirm state
#             st.session_state.delete_confirm = None
            
#             # No need to rerun explicitly, Streamlit will re-render
#     with col2:
#         if st.button("Cancel"):
#             # Reset delete_confirm state
#             st.session_state.delete_confirm = None

