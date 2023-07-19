from html import unescape
import os
import re
import requests
import ssl
import openpyxl
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import difflib
import psycopg2
from psycopg2 import pool
import logging


# Set the SSL certificate file path
ssl._create_default_https_context = ssl._create_unverified_context

# Constants for database connection
DATABASE_NAME = "issues"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"
DATABASE_POOL_SIZE = 5


# Set up logging
logging.basicConfig(filename='issue_analysis.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Constants for specific phrases
phrases = {
    "issue", "problem", "bug", "error", "fix", "solution", "cause", "dependency",
    "implementation", "bug fix", "crash", "request", "broken", "documentation",
    "performance", "caused by", "it was"
}

# Function to check if a sentence contains any of the phrases
def contains_phrase(sentence, phrases):
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, sentence, re.IGNORECASE):
            return True
    return False

# Function to find matching phrases with variations (typos, plural forms, different endings)
def find_matching_phrases(phrase, phrases, lemmatizer):
    matches = []
    phrase_lemma = lemmatizer.lemmatize(phrase.lower())
    for p in phrases:
        p_lemma = lemmatizer.lemmatize(p.lower())
        if p_lemma == phrase_lemma:
            matches.append(p)
        elif p.lower() == phrase.lower() + "s" or p.lower() + "s" == phrase.lower():
            matches.append(p)
        elif difflib.SequenceMatcher(None, p.lower(), phrase.lower()).ratio() > 0.8:
            matches.append(p)
    return matches

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

# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Regular expression pattern to match the expected issue code format
issue_code_pattern = r"^[A-Z]+-\d{4}$"

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('larger_dataset.xlsx')

# ... (rest of the code)


# Select the first sheet in the workbook
sheet = workbook.active

# Initialize an empty list to store the issue codes
issue_codes = []

# Iterate over all the cells in the first column of the sheet
for cell in sheet['A']:
    # Check if the cell value is not empty and is a valid issue code
    if cell.value and re.match(issue_code_pattern, cell.value):
        issue_codes.append(cell.value)

# Close the workbook
workbook.close()

# Create a folder to store the downloaded issue reports
issue_report_folder = "issue_reports"
if not os.path.exists(issue_report_folder):
    os.makedirs(issue_report_folder)

# Function to download the XML version of an issue report
def download_issue_report(issue_id):
    issue_report_url = "https://issues.apache.org/jira/si/jira.issueviews:issue-xml/{issue_id}/{issue_id}.xml"
    url = issue_report_url.format(issue_id=issue_id)
    print(f"Downloading XML for issue {issue_id}...")
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(issue_report_folder, f"{issue_id}.xml")
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"XML downloaded for issue {issue_id}")
        return file_path
    else:
     logging.warning(f"Failed to download XML for issue {issue_id}")
    return None

# Connect to the database using the connection pool
conn_pool = create_connection_pool()

# Get a connection from the pool
conn = conn_pool.getconn()

# Keep track of the number of issue codes processed and inserted
total_issue_codes = len(issue_codes)
processed_issue_codes = 0
inserted_records = 0

try:
    # Create a cursor object
    cursor = conn.cursor()

    # Check each issue code
    for issue_code in issue_codes:
        processed_issue_codes += 1


        # Insert the issue code into the database
        cursor.execute("""
            INSERT INTO issueCodes (code)
            VALUES (%s)
        """, (issue_code,))
        inserted_records += cursor.rowcount


        # Download the XML file for the issue
        xml_file = download_issue_report(issue_code)

        if xml_file:
            # Parse the XML file
            with open(xml_file, "r") as file:
                xml_content = file.read()
            soup = BeautifulSoup(xml_content, "xml")

            # Extract comments from the XML
            comments = soup.select("comments > comment")

            # Iterate over the comments
            for comment in comments:
        # Extract date and author from the comment
                date = comment.get("created", None)
                author = comment.get("author", None)

                # Assign default values if the attributes are missing
                if date is None:
                    date = "Unknown Date"
                if author is None:
                    author = "Unknown Author"

                # Extract content from the comment
                comment_text = unescape(comment.text.strip())

                # Remove HTML tags from the comment text
                comment_text = re.sub("<.*?>", "", comment_text)

                # Normalize the comment by stemming and lemmatizing
                normalized_comment = ' '.join([stemmer.stem(lemmatizer.lemmatize(word.lower())) for word in comment_text.split()])

                # Check if the normalized comment contains any of the phrases
                if contains_phrase(normalized_comment, phrases):
                    causal = True
                else:
                    causal = False

                # Insert the comment into the database
                cursor.execute("""
                    INSERT INTO sentences (code, date, author, content, causal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (issue_code, date, author, normalized_comment, causal))

            # Commit the changes to the database
            conn.commit()


except psycopg2.errors.InFailedSqlTransaction:
    # Handle the failed transaction error here
    logging.error("Transaction failed. Rolling back changes...")
    conn.rollback()

except Exception as e:
    # Handle other unexpected errors
    logging.error(f"An unexpected error occurred: {str(e)}")

finally:
    # Release the connection back to the pool
    conn_pool.putconn(conn)

# Print completion message and summary
logging.info("Issue report analysis completed.")
logging.info(f"Total issue codes: {total_issue_codes}")
logging.info(f"Processed issue codes: {processed_issue_codes}")
logging.info(f"Inserted records: {inserted_records}")