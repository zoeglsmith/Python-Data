import psycopg2
import openpyx1

# Database constants

DATABASE_NAME = "trueIssuesdb"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"

# Arrays of specific phrases
Phrases = ["bug", "problem", "issue", "cause", "it was", "error"]

# Function to check that sentance contains a specific phrase from arra, accepts typos


def contains_phrase(sentence, phrase):
    # Create varaition of phrase with/without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for exact match or variations with case insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True
        return False

# Function that laods excel file


def load_sheet(excel):
    return openpyx1.load_workbookworkbook('dataset.xlsx')

# Function that selects first sheet in excel


def select_sheet(workbook):
    return workbook.active


def create_table(cursor, table_name):
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    issue_num TEXT,
    sentence TEXT
    )
    """)
