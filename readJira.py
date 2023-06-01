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

# Set the SSL certificate file path
ssl._create_default_https_context = ssl._create_unverified_context

# Constants for database connection
DATABASE_NAME = "issues"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"
DATABASE_POOL_SIZE = 5

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

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('larger_dataset.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

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
        print(f"Failed to download XML for issue {issue_id}")
        return None

# Connect to the database using the connection pool
conn_pool = create_connection_pool()

# Get a connection from the pool
conn = conn_pool.getconn()

try:
    # Create a cursor object
    cursor = conn.cursor()

    # Check each row in the sheet
    for row in sheet.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True):
        issue_code = row[0]

        # Download the XML file for the issue
        xml_file = download_issue_report(issue_code)

        if xml_file:
            # Parse the XML file
            with open(xml_file, "r") as file:
                xml_content = file.read()
            soup = BeautifulSoup(xml_content, "xml")

            # Extract comments from the XML
            comments = soup.select("item > comments > comment")

            # Variables to store causal and non-causal comments
            causal_comments = []
            non_causal_comments = []

            # Iterate over the comments
            for comment in comments:
                comment_text = comment.text.strip()

                # Remove HTML tags from the comment text
                comment_text = re.sub("<.*?>", "", comment_text)

                # Normalize the comment by stemming and lemmatizing
                normalized_comment = ' '.join([stemmer.stem(lemmatizer.lemmatize(word.lower())) for word in comment_text.split()])

                # Debug print statements
                print("Comment:", comment_text)
                print("Normalized Comment:", normalized_comment)
                print("Contains Phrase:", contains_phrase(normalized_comment, phrases))

                # Check if the normalized comment contains any of the phrases
                if contains_phrase(normalized_comment, phrases):
                    causal_comments.append(comment_text)
                    print("Table: causal_comments")
                else:
                    non_causal_comments.append(comment_text)
                    print("Table: non_causal_comments")
                    
                    # Check if the issue code exists in the issueCodes table
            cursor.execute("SELECT code FROM issueCodes WHERE code = %s", (issue_code,))
            existing_code = cursor.fetchone()

# If the issue code doesn't exist, insert it into the issueCodes table
            if not existing_code:
                 cursor.execute("INSERT INTO issueCodes (code) VALUES (%s)", (issue_code,))

            # Store the information in the database
            if causal_comments:
                # Insert the causal comments into the "causal_comments" table
               cursor.executemany("""
                    INSERT INTO sentences (code, content, causal)
                     VALUES (%s, %s, %s)
                    ON CONFLICT (code) DO UPDATE SET content = excluded.content, causal = excluded.causal
                 """, [(issue_code, comment, True) for comment in causal_comments])


            if non_causal_comments:
                # Insert the non-causal comments into the "non_causal_comments" table
                cursor.executemany("""
                     INSERT INTO sentences (code, content, causal)
                     VALUES (%s, %s, %s)
                     ON CONFLICT (code) DO UPDATE SET content = excluded.content, causal = excluded.causal
                    """, [(issue_code, comment, False) for comment in non_causal_comments])
            # Commit the changes to the database
            conn.commit()

finally:
    # Release the connection back to the pool
    conn_pool.putconn(conn)

# Print completion message
print("Issue report analysis completed.")
