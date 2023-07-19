import random
import openpyxl
import psycopg2
from psycopg2 import pool

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

# Function to fetch all issue codes from the 'issuecodes' table
def get_all_issue_codes():
    conn = conn_pool.getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM issuecodes")
    issue_codes = [code[0] for code in cursor.fetchall()]
    conn_pool.putconn(conn)
    return issue_codes

# Connect to the database using the connection pool
conn_pool = create_connection_pool()

# Get all issue codes from the database
all_issue_codes = get_all_issue_codes()

# Define the number of issue codes you want to select randomly from each prefix
num_codes_per_prefix = 73  # 365 total codes / 5 prefixes = 73 codes per prefix

# Separate the issue codes by their prefixes
issue_codes_by_prefix = {}
for prefix in ['CXF', 'GROOVY', 'HARMONY', 'CASSANDRA', 'INFRA']:
    issue_codes_by_prefix[prefix] = [code for code in all_issue_codes if code.startswith(prefix)]

# Randomly select issue codes from each prefix
selected_issue_codes = set()  # Use a set to ensure uniqueness
for prefix in issue_codes_by_prefix:
    selected_issue_codes.update(random.sample(issue_codes_by_prefix[prefix], num_codes_per_prefix))

# Check if we have exactly 365 unique issue codes
if len(selected_issue_codes) != 365:
    print("Error: Unable to select 365 unique issue codes.")
    exit()

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
