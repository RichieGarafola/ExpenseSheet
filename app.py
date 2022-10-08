# Initialize required libraries

# open-source app framework
import streamlit as st 
from streamlit_option_menu import option_menu
# open-source interactive data visualization library
import plotly.graph_objects as go
# Calendrical calculation modules
import calendar
# Basic date and time types
from datetime import datetime

# local import (all custom functions are here)
import database as db


#####################
# Settings
####################

incomes = ['Salary', 'Blog', 'Other Income']
expenses = ['Rent', 'Utilities', 'Groceries', 'Car', 'Other Expenses', 'Savings']
currency = 'USD'
page_title = "Income and Expense Tracker"
page_icon = ":money_with_wings:"
layout = "wide"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

###################
# Dropdown values for selecting the period
##################

# get the year from the datetime module, add the next year by + 1
years = [datetime.today().year, datetime.today().year + 1]
# get the months from by using the month_name on the calendar object
# Jan starts from index position 1
months = list(calendar.month_name[1:])

#############
# Database Interface
#############


# Get all the periods from the database
def get_all_periods():
    # fetch all items from the database
    items = db.fetch_all_periods()
#     isolate the key (period name)
    periods = [item['key'] for item in items]
    return periods


##########
# Hide Streamlit Style
##########

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
            



###############
# Navigation Menu
###############
selected = option_menu(
    menu_title=None,
    options = ["Data Entry", "Data Visualization"],
    icons = ["pencil-fill", "bar-char-fill"],
    orientation = "horizontal",
)


###################
# Input and save periods
##################
if selected == "Data Entry":
    # Inform the user the currency that the data entry will be using
    st.header(f"Data Entry in {currency}")
    # Create an entry form with 2 columns month and year
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key= "month")
        col2.selectbox("Select Year:", years, key= "year")

        # add a divider by using "---"
        "---"
        # create an expander element holding the income list 
        with st.expander("Income"):
            # Iterate over each item in the income list,
            # within each iteration there will be a number input
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)

        # create an expander element holding the expenses list         
        with st.expander("Expenses"):
            # Iterate over each item in the expense list,
            # within each iteration there will be a number input
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)

        # Create an expander element holding the comments.        
        # Using the text_area() widget, create a place holder for comments to be left.        
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here...")

        # add a divider by using "---"        
        "---"
        # assign the form_submit_button() to the submitted variable displaying "Save Data"
        submitted = st.form_submit_button("Save Data")

        # if the button is clicked, send all the values to database
        if submitted:
            # collect the values from each input field
            # like a dictionary, get the values from the session state by using the keys, "year", "month"
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            # instead of typing out all income categories, use dictionary comprehension
            # loop over each value in the income list
            # and get the value for each item by using the session_state
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for income in expenses}        
            db.insert_period(period, incomes, expenses, comment)
            # st.write(f"incomes: {incomes}")
            # st.write(f"expenses: {expenses}")
            st.success("Date Saved!")
        
###############
# Plot Periods
###############
if selected == "Data Visualization":
    st.header("Data Visualization")
    with st.form("saved_periods"):
        # Hardcode period for now
        # period = st.selectbox("Select Period:", ["2022_March"])
        period = st.selectbox("Select Period:", get_all_periods())
        # assign the form_submit_button() to the submitted variable displaying "Plot Period"
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            period_data = db.get_period(period)
            comment = period_data.get('comment')
            expenses = period_data.get('expenses')
            incomes = period_data.get('incomes')
            
            # Dummy data 
            # comment = "Some Comment"
            # incomes = {'Salary': 1500, 'Blog':50, 'Other Income':10}
            # expenses = {'Rent':600, 'Utilities':20, 'Groceries': 300,
            #             'car':100, 'Other Expenses':50, 'Saving': 10}

            # Create Metrics 
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income} {currency}")
            col2.metric("Total Expense", f"{total_expense} {currency}")
            col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
            st.text(f"Comment: {comment}")
        
        
###############
# Sankey Chart
##############

            # Create Sankey Chart
            label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) +  list(expenses.values())

            # Data to dict, dict to Sankey
            link = dict(source = source, target = target, value = value)
            node = dict(label = label, pad = 20, thickness = 30, color = "#E694FF")
            data = go.Sankey(link = link, node = node)

            # Plot it
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0,r=0,t=5,b=5))
            st.plotly_chart(fig, use_container_width=True)
