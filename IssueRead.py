import ssl
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import os
import re
import psycopg2
import openpyxl

# Set the SSL certificate file path
ssl._create_default_https_context = ssl._create_unverified_context

# Set the NLTK data directory within the 'env' folder
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

nltk.download('wordnet')


# Constants for database connection
DATABASE_NAME = "issues"
DATABASE_USER = "zoe"
DATABASE_PASSWORD = "password"

# Constants for specific phrases
PHRASES = ["bugs", "problem", "issues", "cause", "it was", "errors"]

# Function to check if a sentence contains a phrase


def contains_phrase(sentence, phrases):
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, sentence, re.IGNORECASE):
            print("Found phrase:", phrase)
            return True
    print("No matching phrase found.")
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


# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('dataset.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

# Lists to store sentences and issue codes
sentences = []
issueCodes = []

# Check each sentence for the phrases
for row in sheet.iter_rows(min_row=2, min_col=1, max_col=3, values_only=True):
    issue_num = str(row[0])
    sentence = str(row[2])
    print("Extracted sentence:", sentence)
    print("Extracted issue number:", issue_num)

    # Normalize the sentence by stemming and lemmatizing
    normalized_sentence = ' '.join([
        stemmer.stem(lemmatizer.lemmatize(word.lower(), wordnet.VERB))
        for word in sentence.split()
    ])

    # Check if the normalized sentence contains any of the phrases
    if contains_phrase(normalized_sentence, PHRASES):
        # Store the sentence in the "sentences" list
        sentences.append((sentence,))
        # Store the issue number in the "issueCodes" list
        issueCodes.append((issue_num,))

# Connect to the database
with connect_to_database(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD) as conn:
    # Create a cursor object
    with conn.cursor() as cursor:
        # Insert the sentences into the "sentences" table
        print("Inserting sentences...")
        cursor.executemany(
            "INSERT INTO sentences (sentence) VALUES (%s)", sentences)

        # Insert the issue codes into the "issueCodes" table
        print("Inserting issue codes...")
        cursor.executemany(
            "INSERT INTO issueCodes (code) VALUES (%s)", issueCodes)

    # Commit the changes to the database
    conn.commit()
    print("Data insertion completed.")
