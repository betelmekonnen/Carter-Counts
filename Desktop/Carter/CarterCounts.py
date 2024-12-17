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
    tax_percent = st.slider("Tax (%)", 0, 100, 10)

# Calculate totals
# if biweekly_net > 0 and biweekly_deductions >= 0:
#     biweekly_total = biweekly_net - biweekly_deductions
#     monthly_total = biweekly_total * 2
#     post_tax_savings = biweekly_total * (1 - (savings_percent + tax_percent) / 100)
# Calculate total and post-savings/tax available funds
biweekly_total = biweekly_net - biweekly_deductions
monthly_total = biweekly_total * 2
post_tax_savings = biweekly_total * (1 - (savings_percent + tax_percent) / 100)

    # Display totals
    st.write(f"**Biweekly Total**: ${biweekly_total:.2f}")
    st.write(f"**Monthly Total**: ${monthly_total:.2f}")
    st.write(f"**Available Funds after Savings & Taxes**: ${post_tax_savings:.2f}")


    st.session_state.current_period['income'] = {
        'biweekly_net': biweekly_net,
        'biweekly_deductions': biweekly_deductions,
        'savings_percent': savings_percent,
        'tax_percent': tax_percent,
        'post_tax_savings': post_tax_savings
    }
else:
    st.warning("⚠️ Please enter valid Income details (Net Revenue and Deductions).")

# Section: Fixed Expenses
st.header("📑 Fixed Monthly Expenses")
fixed_expenses = {
    'Rent': st.number_input("Rent ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Car Payment': st.number_input("Car Payment ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Utilities': st.number_input("Utilities ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Subscriptions': st.number_input("Subscriptions ($)", min_value=0.0, step=0.01, format="%.2f"),
    'Misc': st.number_input("Misc ($)", min_value=0.0, step=0.01, format="%.2f")
}

if sum(fixed_expenses.values()) > 0:
    st.write(f"**Total Fixed Expenses**: ${sum(fixed_expenses.values()):.2f}")
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
        
# # Show All Saved Periods
# st.header("📆 All Biweekly Periods")
# if st.session_state.biweekly_data:
#     for i, period in enumerate(st.session_state.biweekly_data):
#         st.subheader(f"Biweekly Period {i + 1}")
#         st.write("**Income**", json.loads(period['income']))
#         st.write("**Expenses**", json.loads(period['expenses']))
#         st.write("**Extras**")
#         extras_df = pd.DataFrame(json.loads(period['extras']))
#         st.dataframe(extras_df)

#         # Edit and Delete Buttons
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button(f"Edit Period {i + 1}", key=f"edit_{i}"):
#                 st.session_state.current_period = {
#                     'income': json.loads(period['income']),
#                     'expenses': json.loads(period['expenses']),
#                     'extras': pd.DataFrame(json.loads(period['extras']))
#                 }
#                 st.session_state.edit_index = i
#                 st.experimental_rerun()
#         with col2:
#             if st.button(f"Delete Period {i + 1}", key=f"delete_{i}"):
#                 st.session_state.delete_confirm = i
#                 st.experimental_rerun()
# Show All Saved Periods
st.header("📆 All Biweekly Periods")
if st.session_state.biweekly_data:
    for i, period in enumerate(st.session_state.biweekly_data):
        st.subheader(f"Biweekly Period {i + 1}")
        
        # Safe loading of JSON fields with validation
        try:
            income = json.loads(period['income']) if isinstance(period['income'], str) else {}
            expenses = json.loads(period['expenses']) if isinstance(period['expenses'], str) else {}
            extras_df = pd.DataFrame(json.loads(period['extras'])) if isinstance(period['extras'], str) else pd.DataFrame()
        except (json.JSONDecodeError, TypeError):
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
                st.experimental_rerun()
        with col2:
            if st.button(f"Delete Period {i + 1}", key=f"delete_{i}"):
                st.session_state.delete_confirm = i
                st.experimental_rerun()


# Confirmation Dialog for Deletion
if st.session_state.delete_confirm is not None:
    st.warning("Are you sure you want to delete this period?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete"):
            st.session_state.biweekly_data.pop(st.session_state.delete_confirm)
            pd.DataFrame(st.session_state.biweekly_data).to_csv(CSV_FILE, index=False)
            st.session_state.delete_confirm = None
            st.success("Period deleted successfully!")
            st.experimental_rerun()
    with col2:
        if st.button("Cancel"):
            st.session_state.delete_confirm = None
            st.experimental_rerun()
