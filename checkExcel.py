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

# Connect to the database using the connection pool
conn_pool = create_connection_pool()

# Get a connection from the pool
conn = conn_pool.getconn()

# Create a cursor object
cursor = conn.cursor()

# Fetch all issue codes from the 'issuecodes' table
cursor.execute("SELECT code FROM issuecodes")
all_issue_codes_db = [code[0] for code in cursor.fetchall()]

# Release the connection back to the pool
conn_pool.putconn(conn)

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('random_codes.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

# Read the issue codes from the Excel sheet and store them in a list
issue_codes_excel = [cell.value for cell in sheet['A'][1:366]]

# Check if all issue codes from the Excel sheet are in the database
codes_not_in_database = set(issue_codes_excel) - set(all_issue_codes_db)

if codes_not_in_database:
    print("The following issue codes are not from the database:")
    print(codes_not_in_database)
else:
    print("All issue codes from the Excel sheet are from the database.")

# Close the workbook
workbook.close()
