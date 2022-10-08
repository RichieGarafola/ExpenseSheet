import streamlit as st
import os
from deta import Deta
from dotenv import load_dotenv

# Load the enviornment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(DETA_KEY)

# this is how to create/connect to database. 
db = deta.Base("monthly_reports")

# Insert the values of a single period into database
def insert_period(period, incomes, expenses, comment):
    # Returns the report of a successful creation, otherwise raises an error
    # We will use period as the key 
    return db.put({'key':period, 'incomes':incomes, 'expenses':expenses, 'comment':comment})

# Fetch all periods to fill selection box
def fetch_all_periods():
    # Returns a dict of all periods
    res = db.fetch()
    return res.items

# Get all values from a particular period to plot the data
def get_period(period):
    # If not found, the funtion will return None
    return db.get(period)

# Get all the periods from the database
def get_all_periods():
    # fetch all items from the database
    items = db.fetch_all_periods()
#     isolate the key (period name)
    periods = [item['key'] for item in items]
    return periods
