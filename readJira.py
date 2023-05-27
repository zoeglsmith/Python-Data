import ssl
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import os
import re
import psycopg2
import openpyxl
import difflib
from psycopg2 import pool
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Set the SSL certificate file path
ssl._create_default_https_context = ssl._create_unverified_context

# Set the NLTK data directory within the 'env' folder
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

# Disable SSL verification for JIRA connection
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Constants for XML file path
XML_FILE_PATH = 'SearchRequest.xml'

# Constants for database connection
DATABASE_NAME = "issues"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"
DATABASE_POOL_SIZE = 5

# Constants for specific phrases
phrases = {
    "issue", "problem", "bug", "error", "fix", "solution", "cause", "concern",
    "dependency", "implementation", "bug fix", "code", "functionality", "support", "validate", "detected", "crash",
    "request", "improve", "unable", "broken", "documentation", "performance", "caused by", "validate", "logic",
    "code", "functionality"
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

# Fetch XML data from file
tree = ET.parse(XML_FILE_PATH)
root = tree.getroot()

# Sets to store unique sentences and issue codes
sentences = set()
issueCodes = set()

# Dictionary to store variations of phrase words found in the sentences
phrase_variations = {}

# Preprocess phrases and create variations
preprocessed_phrases = [stemmer.stem(
    lemmatizer.lemmatize(p.lower())) for p in phrases]
for phrase in phrases:
    matching_phrases = find_matching_phrases(phrase, phrases, lemmatizer)
    if matching_phrases:
        phrase_variations[phrase] = matching_phrases
        print("Found variations for phrase:", phrase)
        print("Variations:", matching_phrases)

# Iterate over issue elements in the XML data
for issue in root.findall('.//item'):
    issue_num = issue.find('key').text
    description = issue.find('description').text
    print("Extracted issue number:", issue_num)

    # Extract text content from description element, ignoring HTML and other tags
    soup = BeautifulSoup(description, 'html.parser')
    description_text = soup.get_text()

    # Extract sentences from the description text using regex pattern
    sentences_list = re.findall(
        r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', description_text)

    # Check if any sentence contains the desired phrases
    if any(contains_phrase(sentence, preprocessed_phrases) for sentence in sentences_list):
        # Store the sentences in the "sentences" set
        sentences.update(sentences_list)
        # Store the issue number in the "issueCodes" set
        issueCodes.add(issue_num)

# Connect to the database using the connection pool
conn_pool = create_connection_pool()

# Get a connection from the pool
conn = conn_pool.getconn()

try:
    # Create a cursor object
    cursor = conn.cursor()

    # Check if there are any valid sentences and issue codes to insert
    if sentences and issueCodes:
        # Convert sets to lists for bulk insertion
        sentence_list = list(sentences)
        issue_code_list = list(issueCodes)

        # Insert the sentences into the "sentences" table
        print("Inserting sentences...")
        cursor.executemany("INSERT INTO sentences (sentence) VALUES (%s)", [
                           (s,) for s in sentence_list])

        # Insert the issue codes into the "issueCodes" table
        print("Inserting issue codes...")
        cursor.executemany("INSERT INTO issueCodes (code) VALUES (%s)", [
                           (c,) for c in issue_code_list])

    # Commit the changes to the database
    conn.commit()
    print("Data insertion completed.")

finally:
    # Release the connection back to the pool
    conn_pool.putconn(conn)

# Print the variations of phrase words found in the sentences
print("\nPhrase Variations:")
for phrase, variations in phrase_variations.items():
    print("Phrase:", phrase)
    print("Variations:", variations)
