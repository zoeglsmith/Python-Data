import psycopg2
import openpyxl

# Constants for database connection
DATABASE_NAME = "issuesdb"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"

# Constants for specific phrases and their corresponding table names
PHRASES = {
    "bug": "bugs",
    "problems": "problems",
    "issue": "issues",
    "cause": "causes",
    "it was": "it_was",
    "error": "errors"
}

# Function to check if a sentence contains phrase, with spell-checking


def contains_phrase(sentence, phrases):
    # Iterate over each phrase and its variations
    for phrase in phrases:
        variations = [phrase, phrase.replace(
            " ", ""), phrase.replace(" ", "_")]

        # Check for exact match or variations with case-insensitivity
        for variation in variations:
            if variation.lower() in sentence.lower():
                return True
    return False


# Function to create a table in the database


# Function to create a table in the database
def create_table(cursor, table_name):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            issue_num TEXT,
            sentence TEXT
        )
    """)


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

# Arrays for true and false sentences
trueIssues = []
falseIssues = []

# Check each sentence for the phrases
for row in sheet.iter_rows(min_row=2, min_col=1, max_col=3):
    issue_num = str(row[0].value)
    sentence = str(row[2].value)
found_phrases = contains_phrase(sentence, PHRASES.keys())
if found_phrases:
    for phrase in PHRASES:
        trueIssues.append((issue_num, sentence, phrase))
    else:
        falseIssues.append((issue_num, sentence))

# Connect to the database
with connect_to_database(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD) as conn:
    # Create a cursor object
    with conn.cursor() as cursor:
        # Create tables
        create_table(cursor, "sentences")
        for table_name in PHRASES.values():
            create_table(cursor, table_name)

        # Insert the true sentences into the respective tables
        for issue_num, sentence, phrase in trueIssues:
            table_name = PHRASES[phrase]
            cursor.execute(
                f"INSERT INTO {table_name} (issue_num, sentence) VALUES (%s, %s)", (issue_num, sentence))

        # Insert the false sentences into the "sentences" table
        for issue_num, sentence in falseIssues:
            cursor.execute(
                "INSERT INTO sentences (issue_num, sentence) VALUES (%s, %s)", (issue_num, sentence))

    # Commit the changes to the database
    conn.commit()

# Print the true and false sentences
print("\nTRUE SENTENCES:")
for issue_num, sentence, phrase in trueIssues:
    print(f"Issue {issue_num} ({phrase}): {sentence}")

print("\nFALSE SENTENCES:")
for issue_num, sentence in falseIssues:
    print(f"Issue {issue_num}: {sentence}")
