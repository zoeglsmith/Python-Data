import psycopg2
import openpyxl

# Load the Excel file into a workbook object
workbook = openpyxl.load_workbook('dataset.xlsx')

# Select the first sheet in the workbook
sheet = workbook.active

# Arrays for specific phrases
trueForItWas = []
falseForItWas = []

trueForCausedBy = []
falseForCausedBy = []

trueForIssue = []
falseForIssue = []

# Arrays for sentences and their corresponding issue numbers
itWasSentences = []
causedBySentences = []
issueSentences = []
bugSentances = []
falseForBug = []

# A function to check if a sentence contains a specific phrase, with spell-checking


def contains_phrase(sentence, phrase):
    # Create variations of the phrase with and without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for an exact match or variations with case-insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True


# Check each sentence for the phrases "it was" and "caused by"
for row in sheet.iter_rows(min_row=2, min_col=1, max_col=3):
    issue_num = str(row[0].value)
    sentence = str(row[2].value)

    if contains_phrase(sentence, "it was"):
        # trueForItWas.append(sentence)
        itWasSentences.append((issue_num, sentence))
    else:
        falseForItWas.append(sentence)

    if contains_phrase(sentence, "cause"):
        # trueForCausedBy.append(sentence)
        causedBySentences.append((issue_num, sentence))
    else:
        falseForCausedBy.append(sentence)

    if contains_phrase(sentence, "issue"):
        # trueForIssue.append(sentence)
        issueSentences.append((issue_num, sentence))
    else:
        falseForIssue.append(sentence)

    if contains_phrase(sentence, "bug"):
        bugSentances.append((issue_num, sentence))
    else:
        falseForBug.append(sentence)

# # Connect to the PostgreSQL database
# conn = psycopg2.connect(
#     host="localhost",
#     database="issuesdb",
#     user="admin",
#     password="password"
# )


# # Create a cursor object
# cursor = conn.cursor()

# # Insert the sentences and their corresponding issue numbers into the "sentences" table
# for issue_num, sentence in itWasSentences + causedBySentences + issueSentences:
#     cursor.execute(
#         "INSERT INTO sentences (issue_num, sentence) VALUES (%s, %s)", (issue_num, sentence))

# # Commit the changes to the database
# conn.commit()

# # Close the cursor and database connections
# cursor.close()
# conn.close()

# Print the sentences and their corresponding issue numbers
print("\nIT_WAS SENTENCES:")
for issue_num, sentence in itWasSentences:
    print(f"Issue {issue_num}: {sentence}\ne")

print("\nCAUSED_BY SENTENCES:")
for issue_num, sentence in causedBySentences:
    print(f"Issue {issue_num}: {sentence}\n")

print("\nISSUE SENTENCES:")
for issue_num, sentence in issueSentences:
    print(f"Issue {issue_num}: {sentence}\n")

print("\nBUG SENTENCES:")
for issue_num, sentence in bugSentances:
    print(f"Issue {issue_num}: {sentence}\n")
