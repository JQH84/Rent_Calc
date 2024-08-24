import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state variables
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category'])
if 'house_pool' not in st.session_state:
    st.session_state.house_pool = 0
if 'expense_categories' not in st.session_state:
    st.session_state.expense_categories = ['Rent', 'Utilities', 'Credit Card', 'Groceries', 'Transportation', 'Other']

def add_transaction(date, description, amount, category):
    new_transaction = pd.DataFrame({'Date': [date], 'Description': [description], 'Amount': [amount], 'Category': [category]})
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)

def calculate_rent_split(total_rent):
    individual_share = total_rent / 4
    roommates_contribution = 850 * 2
    your_share = total_rent - roommates_contribution
    excess = max(0, roommates_contribution - (individual_share * 2))
    return individual_share, your_share, excess

st.title("Rent and Expenses Calculator")

# Weekly income input
st.subheader("Weekly Income")
payday = st.date_input("Payday", value=datetime.now())
weekly_income = st.number_input("Weekly Income", min_value=0.0, value=0.0, step=0.01)
if st.button("Add Weekly Income"):
    savings = weekly_income * 0.3
    expenses_budget = weekly_income * 0.7
    add_transaction(payday, "Weekly Income", weekly_income, "Income")
    add_transaction(payday, "Savings (30%)", -savings, "Savings")
    st.write(f"Amount available for expenses (70%): ${expenses_budget:.2f}")

# Expense tracking
st.subheader("Add Expense")
expense_date = st.date_input("Expense Date", value=datetime.now())
expense_description = st.text_input("Expense Description")
expense_amount = st.number_input("Expense Amount", min_value=0.0, value=0.0, step=0.01)
expense_category = st.selectbox("Expense Category", st.session_state.expense_categories)
if st.button("Add Expense"):
    add_transaction(expense_date, expense_description, -expense_amount, expense_category)
    st.success(f"Expense of ${expense_amount:.2f} added to {expense_category} category.")

# Monthly rent and roommates contribution
st.subheader("Monthly Rent")
rent_due_date = st.date_input("Rent Due Date", value=datetime.now().replace(day=1))
total_rent = st.number_input("Total Rent", min_value=0.0, value=3299.29, step=0.01)
if st.button("Calculate Rent Split"):
    individual_share, your_share, excess = calculate_rent_split(total_rent)
    st.write(f"Individual share: ${individual_share:.2f}")
    st.write(f"Your share: ${your_share:.2f}")
    st.write(f"Excess for house pool: ${excess:.2f}")
    st.session_state.house_pool += excess
    add_transaction(rent_due_date, "Rent Payment", -total_rent, "Rent")
    add_transaction(rent_due_date, "Roommates Contribution", 850 * 2, "Income")

# Display transactions
st.subheader("Transaction History")
st.dataframe(st.session_state.transactions)

# Display house pool
st.subheader("House Money Pool")
st.write(f"Current balance: ${st.session_state.house_pool:.2f}")

# Calculate and display summary
st.subheader("Summary")
total_income = st.session_state.transactions[st.session_state.transactions['Amount'] > 0]['Amount'].sum()
total_expenses = abs(st.session_state.transactions[st.session_state.transactions['Amount'] < 0]['Amount'].sum())
balance = total_income - total_expenses

expense_breakdown = st.session_state.transactions[st.session_state.transactions['Amount'] < 0].groupby('Category')['Amount'].sum().abs()

st.write(f"Total Income: ${total_income:.2f}")
st.write(f"Total Expenses: ${total_expenses:.2f}")
st.write(f"Current Balance: ${balance:.2f}")

st.subheader("Expense Breakdown")
st.bar_chart(expense_breakdown)

# Display remaining budget from 70% allocation
expenses_from_allocation = st.session_state.transactions[
    (st.session_state.transactions['Amount'] < 0) & 
    (st.session_state.transactions['Category'] != 'Savings')
]['Amount'].sum()
total_allocation = st.session_state.transactions[st.session_state.transactions['Description'] == 'Weekly Income']['Amount'].sum() * 0.7
remaining_budget = total_allocation + expenses_from_allocation  # expenses are negative, so we add them

st.subheader("Budget Status")
st.write(f"Total 70% Allocation: ${total_allocation:.2f}")
st.write(f"Total Expenses: ${abs(expenses_from_allocation):.2f}")
st.write(f"Remaining Budget: ${remaining_budget:.2f}")