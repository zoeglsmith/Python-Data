import psycopg2
import openpyxl

# Constants for database connection
DATABASE_NAME = "issues"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"

# Constants for specific phrases
PHRASES = ["bugs", "problems", "issues", "causes", "it_was", "errors"]

# Function to check if a sentence contains a phrase


def contains_phrase(sentence, phrases):
    for phrase in phrases:
        if phrase.lower() in sentence.lower():
            return True
    return False

# Function to connect to the database using a context manager


def connect_to_database(database_name, database_user, database_password):
    conn = psycopg2.connect(
        host="localhost",
        database=database_name,
        user=database_user,
        password=database_password
    )
    return conn


# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('dataset.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

# Lists to store sentences and issue codes
sentences = []
issueCodes = []

# Check each sentence for the phrases
for row in sheet.iter_rows(min_row=2, min_col=1, max_col=3):
    issue_num = str(row[0].value)
    sentence = str(row[2].value)
    if contains_phrase(sentence, PHRASES):
        sentences.append((issue_num, sentence))
        issueCodes.append((issue_num, issue_num))

# Connect to the database
with connect_to_database(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD) as conn:
    # Create a cursor object
    with conn.cursor() as cursor:
        # Insert the sentences into the "sentences" table
        cursor.executemany(
            "INSERT INTO sentences (issue_num, sentence) VALUES (%s, %s)", sentences)

        # Insert the issue codes into the "issueCodes" table
        cursor.executemany(
            "INSERT INTO issueCodes (issue_num, code) VALUES (%s, %s)", issueCodes)

    # Commit the changes to the database
    conn.commit()
