import streamlit as st
import pandas as pd

# Initialize session state
if 'biweekly_data' not in st.session_state:
    st.session_state.biweekly_data = []

if 'current_period' not in st.session_state:
    st.session_state.current_period = {'income': {}, 'expenses': {}, 'extras': pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])}

# Title
st.title("Carter Counts!")

# Section: Income Input
st.header("💰 Income Details")
col1, col2 = st.columns(2)

with col1:
    biweekly_net = st.number_input("Biweekly Net Revenue ($)", min_value=0.0, step=0.01)
    biweekly_deductions = st.number_input("Biweekly Deductions ($)", min_value=0.0, step=0.01)

with col2:
    savings_percent = st.slider("Savings (%)", 0, 100, 10)
    tax_percent = st.slider("Tax (%)", 0, 100, 10)

# Calculate total and post-savings/tax available funds
biweekly_total = biweekly_net - biweekly_deductions
monthly_total = biweekly_total * 2
post_tax_savings = biweekly_total * (1 - (savings_percent + tax_percent) / 100)

st.write(f"**Biweekly Total**: ${biweekly_total:.2f}")
st.write(f"**Monthly Total**: ${monthly_total:.2f}")
st.write(f"**Available Funds after Savings & Taxes**: ${post_tax_savings:.2f}")

# Savings breakdown visualization
savings_amount = biweekly_total * (savings_percent / 100)
st.write(f"**Savings at {savings_percent}%**: ${savings_amount:.2f}")
st.write(f"**Remaining after Savings**: ${biweekly_total - savings_amount:.2f}")

# Save Income Details
st.session_state.current_period['income'] = {
    'biweekly_net': biweekly_net,
    'biweekly_deductions': biweekly_deductions,
    'savings_percent': savings_percent,
    'tax_percent': tax_percent,
    'post_tax_savings': post_tax_savings
}

# Section: Fixed Expenses
st.header("📑 Fixed Monthly Expenses")
fixed_expenses = {
    'Rent': st.number_input("Rent ($)", min_value=0.0, step=0.01),
    'Car Payment': st.number_input("Car Payment ($)", min_value=0.0, step=0.01),
    'Car Insurance': st.number_input("Car Insurance ($)", min_value=0.0, step=0.01),  # Added Car Insurance
    'Fidelity': st.number_input("Fidelity ($)", min_value=0.0, step=0.01),  # Added Fidelity
    'Subscriptions': st.number_input("Subscriptions ($)", min_value=0.0, step=0.01),
    'Gym': st.number_input("Gym ($)", min_value=0.0, step=0.01),
    'Groceries': st.number_input("Groceries ($)", min_value=0.0, step=0.01),  # Added Groceries
    'Renters Insurance': st.number_input("Renters Insurance ($)", min_value=0.0, step=0.01),  # Added Renters Insurance
    'Internet': st.number_input("Internet ($)", min_value=0.0, step=0.01),
    'Electricity': st.number_input("Electricity ($)", min_value=0.0, step=0.01),  # Added Electricity
    'Utilities': st.number_input("Utilities ($)", min_value=0.0, step=0.01)
}
total_fixed_expenses = sum(fixed_expenses.values())
st.write(f"**Total Fixed Expenses**: ${total_fixed_expenses:.2f}")

# Save Expenses
st.session_state.current_period['expenses'] = fixed_expenses

# Section: Disposable Income Calculation
disposable_income_monthly = post_tax_savings - total_fixed_expenses
disposable_income_biweekly = disposable_income_monthly / 2

st.write(f"**Monthly Disposable Income after Expenses**: ${disposable_income_monthly:.2f}")
st.write(f"**Biweekly Disposable Income**: ${disposable_income_biweekly:.2f}")


# Section: Extras and Weekly Spending
st.header("🛒 Weekly Extras")

# # Add Extra Income (Optional) - Make sure to include the submit button in the form
# with st.form("add_extra_income"):
#     extra_income = st.number_input("Extra Income ($)", min_value=0.0, step=0.01)
#     submit_extra_income = st.form_submit_button("Add Extra Income")  # Added submit button
    
#     if submit_extra_income:
#         st.session_state.current_period['extra_income'] = extra_income  # Save extra income

# # Show extra income if provided
# if 'extra_income' in st.session_state.current_period:
#     st.write(f"**Extra Income Added**: ${st.session_state.current_period['extra_income']:.2f}")

# # Add new expense and categories
# with st.form("Add Expense"):
#     date = st.date_input("Date")
#     category = st.selectbox("Category", ["Outing", "Gift", "Drinks", "Misc"] + list(st.session_state.current_period['custom_categories']))
#     description = st.text_input("Description")
#     amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
#     add_expense = st.form_submit_button("Add Expense")
    
#     if add_expense:
#         new_entry = {'Date': date, 'Category': category, 'Description': description, 'Amount': amount}
#         st.session_state.current_period['extras'] = st.session_state.current_period['extras'].append(new_entry, ignore_index=True)

# Add new expense
with st.form("Add Expense"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Outing", "Gift", "Drinks", "Misc"])
    description = st.text_input("Description")
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
    add_expense = st.form_submit_button("Add Expense")
    
    if add_expense:
        new_entry = {'Date': date, 'Category': category, 'Description': description, 'Amount': amount}
        st.session_state.current_period['extras'] = st.session_state.current_period['extras'].append(new_entry, ignore_index=True)
        
# Show expense table
st.subheader("Extras This Period")
extras_df = st.session_state.current_period['extras']
st.dataframe(extras_df)

# Calculate totals for extras
total_extras = extras_df['Amount'].sum()
st.write(f"**Total Extras Spending**: ${total_extras:.2f}")

# Biweekly Limit Check
biweekly_limit = st.number_input("Set Biweekly Extras Limit ($)", min_value=0.0, step=0.01, value=200.0)
remaining_after_expenses = post_tax_savings - total_fixed_expenses - total_extras
st.write(f"**Remaining Funds after Expenses & Extras**: ${remaining_after_expenses:.2f}")

if total_extras > biweekly_limit:
    st.error(f"⚠️ You've exceeded your biweekly limit by ${total_extras - biweekly_limit:.2f}")
else:
    st.success(f"🎉 You're under your limit by ${biweekly_limit - total_extras:.2f}")

# Save Period
if st.button("Save Period"):
    st.session_state.biweekly_data.append(st.session_state.current_period)
    st.session_state.current_period = {'income': {}, 'expenses': {}, 'extras': pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])}
    st.success("Biweekly period saved!")

# Show all saved periods
st.header("📆 All Biweekly Periods")
if st.session_state.biweekly_data:
    for i, period in enumerate(st.session_state.biweekly_data):
        st.subheader(f"Biweekly Period {i + 1}")
        st.write("**Income**", period['income'])
        st.write("**Expenses**", period['expenses'])
        st.write("**Extras**")
        st.dataframe(period['extras'])

# Allow user to add custom categories
st.header("Add Custom Categories")
if 'custom_categories' not in st.session_state:
    st.session_state.custom_categories = []

new_category = st.text_input("New Category")
if st.button("Add Category"):
    if new_category and new_category not in st.session_state.custom_categories:
        st.session_state.custom_categories.append(new_category)
        st.success(f"Category '{new_category}' added!")
    elif new_category in st.session_state.custom_categories:
        st.warning("Category already exists.")


