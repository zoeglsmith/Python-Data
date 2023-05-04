# import enchant  # PyEnchant library for spell-checking
import pandas as pd
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

# A function to check if a sentence contains a specific phrase, with spell-checking


def contains_phrase(sentence, phrase):
    # Create variations of the phrase with and without spaces
    variations = [phrase, phrase.replace(" ", ""), phrase.replace(" ", "_")]

    # Check for an exact match or variations with case-insensitivity
    for variation in variations:
        if variation.lower() in sentence.lower():
            return True


# Check each sentence for the phrases "it was" and "caused by"
for cell in sheet['C']:
    sentence = str(cell.value)
    if contains_phrase(sentence, "it was"):
        trueForItWas.append(sentence)
    else:
        falseForItWas.append(sentence)

for cell in sheet['C']:
    sentence = str(cell.value)
    if contains_phrase(sentence, "cause"):
        trueForCausedBy.append(sentence)
    else:
        falseForCausedBy.append(sentence)


for cell in sheet['C']:
    sentence = str(cell.value)
    if contains_phrase(sentence, "issue"):
        falseForIssue.append(sentence)
    else:
        falseForIssue.append(sentence)

# Print the results
print("IT_WAS ARRAYS:")
print("True statements:", trueForItWas)
print("False statements:", falseForItWas)


print("CAUSED_BY ARRAYS:")
print("TRUE statements:", trueForCausedBy)
print("FALSE statements:", falseForCausedBy)

print("ISSUE ARRAYS:")
print("TRUE statements:", falseForIssue)
print("FALSE statements:", falseForIssue)
