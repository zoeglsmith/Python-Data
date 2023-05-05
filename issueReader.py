import psycopg2
import openpyxl

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('dataset.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

# Arrays for specific phrases
phrases = ["bug", "problems", "issue" "cause", "it was", "error"]

trueSentences = []
falseSentences = []

# A function to check if a sentence contains a specific phrase, with spell-checking


def contains_phrase(sentence, phrase):
    # Create variations of the phrase with and without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for an exact match or variations with case-insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True


# Check each sentence for the phrases
for row in sheet.iter_rows(min_row=2, min_col=1, max_col=3):
    issue_num = str(row[0].value)
    sentence = str(row[2].value)

    found = False
    for phrase in phrases:
        if contains_phrase(sentence, phrase):
            trueSentences.append((issue_num, sentence))
            found = True
            break
    if not found:
        falseSentences.append((issue_num, sentence))


# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="trueIssuesdb",
    user="zoe",
    password="password"
)

# Create a cursor object
cursor = conn.cursor()

# Insert the true sentences and their corresponding issue numbers into the "sentences" table
for issue_num, sentence in trueSentences:
    cursor.execute(
        "INSERT INTO sentences (issue_num, sentence) VALUES (%s, %s)", (issue_num, sentence))

# Commit the changes to the database
conn.commit()

# Close the cursor and database connections
cursor.close()
conn.close()

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="falseIssues",
    user="zoe",
    password="password"
)

# Create a cursor object
cursor = conn.cursor()

# Create tables
cursor.execute("""
    CREATE TABLE bug (
        id SERIAL PRIMARY KEY,
        issue_num TEXT,
        sentence TEXT
    )
""")
cursor.execute("""
    CREATE TABLE problems (
        id SERIAL PRIMARY KEY,
        issue_num TEXT,
        sentence TEXT
    )
""")
cursor.execute("""
    CREATE TABLE issue (
        id SERIAL PRIMARY KEY,
        issue_num TEXT,
        sentence TEXT
    )
""")
cursor.execute("""
    CREATE TABLE cause (
        id SERIAL PRIMARY KEY,
        issue_num TEXT,
        sentence TEXT
    )
""")
cursor.execute("""
    CREATE TABLE it_was (
        id SERIAL PRIMARY KEY,
        issue_num TEXT,
        sentence TEXT
    )
""")
cursor.execute("""
    CREATE TABLE error (
        id SERIAL PRIMARY KEY,
        issue_num TEXT,
        sentence TEXT
    )
""")


# Insert the false sentences and their corresponding issue numbers into the "sentences" table
for issue_num, sentence in falseSentences:
    cursor.execute(
        "INSERT INTO sentences (issue_num, sentence) VALUES (%s, %s)", (issue_num, sentence))

# Commit the changes to the database
conn.commit()

# Close the cursor and database connections
cursor.close()
conn.close()

# Print the sentences and their corresponding issue numbers
print("\nTRUE SENTENCES:")
for issue_num, sentence in trueSentences:
    print(f"Issue {issue_num}: {sentence}\n")

print("\nFALSE SENTENCES:")
for issue_num, sentence in falseSentences:
    print(f"Issue {issue_num}: {sentence}\n")
