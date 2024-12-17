import streamlit as st
import pandas as pd
import os

# File where biweekly data will be saved
CSV_FILE = 'biweekly_data.csv'

# Initialize session state
if 'biweekly_data' not in st.session_state:
# Check if the CSV file exists and load it
    if os.path.exists(CSV_FILE):
        st.session_state.biweekly_data = pd.read_csv(CSV_FILE).to_dict(orient='records')  # Load saved data into session_state
    else:
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
remaining_after_savings = biweekly_total - savings_amount  # Remaining after savings (biweekly)
monthly_remaining_after_savings = remaining_after_savings * 2  # Convert to monthly
disposable_income_monthly = monthly_remaining_after_savings - total_fixed_expenses  # Subtract fixed expenses
disposable_income_biweekly = disposable_income_monthly / 2  # Divide by 2 for biweekly

# Display Results
st.write(f"**Remaining after Savings (Biweekly):** ${remaining_after_savings:.2f}")
st.write(f"**Monthly Disposable Income after Expenses:** ${disposable_income_monthly:.2f}")
st.write(f"**Biweekly Disposable Income:** ${disposable_income_biweekly:.2f}")


# Section: Extras and Weekly Spending
st.header("🛒 Weekly Extras")


# Add Extra Income (Optional)
with st.form("add_extra_income"):
    extra_income = st.number_input("Extra Income ($)", min_value=0.0, step=0.01)
    submit_extra_income = st.form_submit_button("Add Extra Income")  # Submit button for extra income
    
    if submit_extra_income:
        st.session_state.current_period['extra_income'] = extra_income  # Save extra income
        
# Show extra income if provided
if 'extra_income' in st.session_state.current_period:
    st.write(f"**Extra Income Added**: ${st.session_state.current_period['extra_income']:.2f}")


# Add Custom Categories Section
st.header("Add Custom Categories")

# Initialize session state for custom categories if it doesn't exist yet
if 'custom_categories' not in st.session_state:
    st.session_state.custom_categories = []

# Input field for a new category
new_category = st.text_input("New Category", key="new_category_input")

# Button to add the new category to the list
if st.button("Add Category", key="add_category_button"):
    if new_category and new_category not in st.session_state.custom_categories:
        st.session_state.custom_categories.append(new_category)
        st.success(f"Category '{new_category}' added!")
        st.experimental_rerun()
    elif new_category in st.session_state.custom_categories:
        st.warning("Category already exists.")

# Show the list of custom categories
st.subheader("Current Custom Categories")
if st.session_state.custom_categories:
    # Display the custom categories with delete option
    for category in st.session_state.custom_categories:
        category_row = st.container()
        with category_row:
            col1, col2 = st.columns([4, 1])
            col1.write(category)
            # Button to delete the category
            if col2.button(f"Delete {category}", key=f"delete_{category}"):
                st.session_state.custom_categories.remove(category)
                st.success(f"Category '{category}' removed!")
                st.experimental_rerun()
                break  # Re-run the loop to update the list immediately

# Add expense using custom categories
st.header("Add Expense")
with st.form("Add Expense"):
    date = st.date_input("Date")
    
    # Combine predefined categories with custom categories
    all_categories = ["Outing", "Gift", "Drinks", "Misc"] + st.session_state.custom_categories
    
    # Category selection (dropdown)
    category = st.selectbox("Category", all_categories)
    description = st.text_input("Description")
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
    add_expense = st.form_submit_button("Add Expense")
    
    if add_expense:
        new_entry = {'Date': date, 'Category': category, 'Description': description, 'Amount': amount}
        # Assuming you're appending the expense to the session_state's extras dataframe
        new_row = pd.DataFrame([new_entry])  # Convert the new entry into a DataFrame
        st.session_state.current_period['extras'] = pd.concat(
            [st.session_state.current_period['extras'], new_row],
            ignore_index=True
        )
        st.success("Expense added successfully!")


# Show the expense table with extras
st.subheader("Extras This Period")
extras_df = st.session_state.current_period['extras']
st.dataframe(extras_df)

# First Add Expense Form
with st.form("Add Expense 1"):  # Use a unique form key
    date = st.date_input("Date")
    all_categories = ["Outing", "Gift", "Drinks", "Misc"] + st.session_state.custom_categories
    category = st.selectbox("Category", all_categories)
    description = st.text_input("Description")
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
    add_expense = st.form_submit_button("Add Expense")
    
    if add_expense:
        new_entry = {'Date': date, 'Category': category, 'Description': description, 'Amount': amount}
        new_row = pd.DataFrame([new_entry])
        st.session_state.current_period['extras'] = pd.concat(
            [st.session_state.current_period['extras'], new_row],
            ignore_index=True
        )
        st.success("Expense added successfully!")
# Second Add Expense Form (if necessary)
with st.form("Add Expense 2"):  # Use a different unique form key
    date = st.date_input("Date")
    all_categories = ["Outing", "Gift", "Drinks", "Misc"] + st.session_state.custom_categories
    category = st.selectbox("Category", all_categories)
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
    # Save the current period to CSV file
    current_period = {
        'income': st.session_state.current_period['income'],
        'expenses': st.session_state.current_period['expenses'],
        'extras': st.session_state.current_period['extras'].to_dict(orient='records')  # Convert dataframe to list of dicts
    }
    
    # Append to CSV file (if CSV exists, append; else, create new CSV)
    current_data = pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else pd.DataFrame()
    new_row = pd.DataFrame([current_period])  # Convert current_period into a DataFrame
    current_data = pd.concat([current_data, new_row], ignore_index=True)
    current_data.to_csv(CSV_FILE, index=False)
    
    # Reset current period
    st.session_state.current_period = {'income': {}, 'expenses': {}, 'extras': pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])}
    st.success("Biweekly period saved!")


# # Show all saved periods
# st.header("📆 All Biweekly Periods")
# if st.session_state.biweekly_data:
#     for i, period in enumerate(st.session_state.biweekly_data):
#         st.subheader(f"Biweekly Period {i + 1}")
#         st.write("**Income**", period['income'])
#         st.write("**Expenses**", period['expenses'])
#         st.write("**Extras**")
#         st.dataframe(period['extras'])

# Show all saved periods
st.header("📆 All Biweekly Periods")
if st.session_state.biweekly_data:
    for i, period in enumerate(st.session_state.biweekly_data):
        st.subheader(f"Biweekly Period {i + 1}")
        st.write("**Income**", period['income'])
        st.write("**Expenses**", period['expenses'])
        
        # Handle extras
        if isinstance(period['extras'], list):
            extras_df = pd.DataFrame(period['extras'])
        elif isinstance(period['extras'], str):
            extras_df = pd.DataFrame(eval(period['extras']))  # Convert string to DataFrame
        else:
            extras_df = period['extras']  # Assume already a DataFrame

        st.write("**Extras**")
        st.dataframe(extras_df)
