import random
import openpyxl
import psycopg2
from psycopg2 import pool
import re

# Constants for database connection
DATABASE_NAME = "issues"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"
DATABASE_POOL_SIZE = 5

# Function to connect to the database using a connection pool
def create_connection_pool():
    return psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=DATABASE_POOL_SIZE,
        host="localhost",
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )

# Connect to the database using the connection pool
conn_pool = create_connection_pool()

# Get a connection from the pool
conn = conn_pool.getconn()

# Create a cursor object
cursor = conn.cursor()

# Fetch all issue codes from the 'issucodes' table
cursor.execute("SELECT code FROM issuecodes")
all_issue_codes = [code[0] for code in cursor.fetchall()]

# Define the number of issue codes you want to select randomly from each prefix
num_codes_per_prefix = 73  # 365 total codes / 5 prefixes = 73 codes per prefix

# Separate the issue codes by their prefixes
issue_codes_by_prefix = {}
for prefix in ['CXF', 'GROOVY', 'HARMONY', 'CASSANDRA', 'INFRA']:
    issue_codes_by_prefix[prefix] = [code for code in all_issue_codes if code.startswith(prefix)]

# Randomly select issue codes from each prefix
selected_issue_codes = []
for prefix in issue_codes_by_prefix:
    selected_issue_codes.extend(random.sample(issue_codes_by_prefix[prefix], num_codes_per_prefix))

# Release the connection back to the pool
conn_pool.putconn(conn)

# Create a new Excel workbook
workbook = openpyxl.Workbook()

# Select the active sheet
sheet = workbook.active

# Write the issue codes to the Excel sheet
for i, issue_code in enumerate(selected_issue_codes, start=1):
    sheet.cell(row=i, column=1, value=issue_code)

# Set the title of the sheet to "random_codes"
sheet.title = "random_codes"

# Save the workbook
workbook.save("random_codes.xlsx")

print("Issue codes printed and exported to an Excel sheet.")
